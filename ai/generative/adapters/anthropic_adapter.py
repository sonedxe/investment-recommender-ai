"""Anthropic adapter (Messages API, ``anthropic`` Python SDK 1.x).

Mechanism: one tool, ``responder_json``, whose ``input_schema`` is our schema;
the answer is that tool's ``input`` dict. ``tool_choice`` forces the tool
(``{"type": "tool", "name": ...}``) on models that accept forced tool use. The
current Claude Opus 5.5 / Sonnet 5.5 / Fable 5.1 / Mythos 5.1 reject forced
tool use with HTTP 400, so for them the adapter sends ``{"type": "auto"}`` plus
an explicit instruction and fails (-> offline fallback) if no tool call comes back.

Models: ``model`` (default Haiku 4.5) serves interpretation and clarification;
``explain_model`` (default Sonnet 5.5) serves the explanation, selected when the
request carries ``EXPLAIN_SCHEMA``. One instance, two models: the port stays
unchanged.

Sampling: SDK 1.x removed ``temperature`` from ``messages.create``; it is sent
through ``extra_body`` only to models that still accept it (Haiku 4.5, the 4.6 /
4.5 line). Newer models reject it and run adaptive thinking, whose tokens count
against ``max_tokens``: for them the adapter asks for ``effort: "low"`` and
raises ``max_tokens`` to at least ``THINKING_MIN_TOKENS``.
"""

from __future__ import annotations

from typing import Any

from ai.generative.adapters import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT_S
from ai.generative.port import LanguageModelError
from ai.generative.schema import EXPLAIN_SCHEMA

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_EXPLAIN_MODEL = "claude-sonnet-5-5"
TOOL_NAME = "responder_json"
THINKING_MIN_TOKENS = 4096

_SAMPLING_PREFIXES = ("claude-3", "claude-haiku-4", "claude-sonnet-4", "claude-opus-4-1", "claude-opus-4-5", "claude-opus-4-6")
_NO_FORCED_TOOL_PREFIXES = ("claude-opus-5-5", "claude-sonnet-5-5", "claude-fable-5-1", "claude-mythos-5-1")
_AUTO_INSTRUCTION = f"\n\nEntrega tu respuesta llamando a la herramienta {TOOL_NAME} exactamente una vez."


def accepts_sampling(model: str) -> bool:
    return model.startswith(_SAMPLING_PREFIXES)


def accepts_forced_tool(model: str) -> bool:
    return not model.startswith(_NO_FORCED_TOOL_PREFIXES)


class AnthropicModel:
    """``LanguageModel`` over the Anthropic Messages API with a schema-typed tool."""

    name = "anthropic"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        explain_model: str | None = DEFAULT_EXPLAIN_MODEL,
        *,
        timeout: float = DEFAULT_TIMEOUT_S,
        max_retries: int = DEFAULT_MAX_RETRIES,
        client: Any = None,
    ) -> None:
        if client is None:
            import anthropic  # lazy: ai/ stays importable without the SDK

            client = anthropic.Anthropic(api_key=api_key, timeout=timeout, max_retries=max_retries)
        self._client = client
        self.model = model
        self.explain_model = explain_model or model

    def model_for(self, schema: dict[str, Any]) -> str:
        return self.explain_model if schema is EXPLAIN_SCHEMA or schema == EXPLAIN_SCHEMA else self.model

    def build_request(self, system, messages, schema, *, temperature, max_tokens) -> dict[str, Any]:
        model = self.model_for(schema)
        tool = {"name": TOOL_NAME, "description": "Devuelve la respuesta estructurada.", "input_schema": schema}
        request: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": list(messages),
            "tools": [tool],
        }
        if accepts_forced_tool(model):
            request["tool_choice"] = {"type": "tool", "name": TOOL_NAME}
        else:
            request["tool_choice"] = {"type": "auto"}
            request["system"] = system + _AUTO_INSTRUCTION
        if accepts_sampling(model):
            request["extra_body"] = {"temperature": temperature}
        else:
            request["max_tokens"] = max(max_tokens, THINKING_MIN_TOKENS)
            request["output_config"] = {"effort": "low"}
        return request

    def complete_json(self, system, messages, schema, *, temperature, max_tokens) -> dict[str, Any]:
        import anthropic

        request = self.build_request(system, messages, schema, temperature=temperature, max_tokens=max_tokens)
        try:
            response = self._client.messages.create(**request)
        except anthropic.AnthropicError as exc:
            raise LanguageModelError(f"anthropic: {type(exc).__name__}") from exc
        stop = getattr(response, "stop_reason", None)
        if stop in ("refusal", "max_tokens"):
            raise LanguageModelError(f"anthropic: stop_reason={stop}")
        for block in getattr(response, "content", None) or []:
            if getattr(block, "type", None) == "tool_use" and getattr(block, "name", None) == TOOL_NAME:
                if not isinstance(block.input, dict):
                    raise LanguageModelError("anthropic: tool input is not an object")
                return dict(block.input)
        raise LanguageModelError("anthropic: no tool call in the response")
