"""OpenAI-compatible adapter (OpenAI, Azure, Groq, Ollama, ... via ``OPENAI_BASE_URL``).

Mechanism (openai-python, Chat Completions): ``response_format`` of type
``json_schema`` with ``strict: false``. Strict mode is NOT used because our
schemas do not satisfy its rules (``evidencia`` is a free-form object and the
scenario items allow extra keys); the core validates every answer with
``ai.generative.schema.validate`` anyway. Providers that reject ``json_schema``
(HTTP 400) get one retry with ``{"type": "json_object"}`` and the schema
appended to the system prompt; that downgrade is remembered for the instance.
``max_tokens`` (not ``max_completion_tokens``) is sent because compatible
providers widely accept it.
"""

from __future__ import annotations

import json
from typing import Any

from ai.generative.adapters import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT_S
from ai.generative.port import LanguageModelError

_SCHEMA_INSTRUCTION = (
    "\n\nResponde SOLO con un objeto JSON que cumpla este JSON Schema, sin texto adicional:\n{schema}"
)


class OpenAICompatibleModel:
    """``LanguageModel`` over the Chat Completions API of any OpenAI-compatible provider."""

    name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str | None = None,
        *,
        timeout: float = DEFAULT_TIMEOUT_S,
        max_retries: int = DEFAULT_MAX_RETRIES,
        client: Any = None,
    ) -> None:
        if client is None:
            import openai  # lazy: ai/ stays importable without the SDK

            client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=timeout, max_retries=max_retries)
        self._client = client
        self.model = model
        self.json_schema_supported = True

    def complete_json(self, system, messages, schema, *, temperature, max_tokens) -> dict[str, Any]:
        import openai

        try:
            if self.json_schema_supported:
                try:
                    return self._call(system, messages, temperature, max_tokens, {
                        "type": "json_schema",
                        "json_schema": {"name": "respuesta", "schema": schema, "strict": False},
                    })
                except openai.BadRequestError:
                    self.json_schema_supported = False
            prompt = system + _SCHEMA_INSTRUCTION.format(schema=json.dumps(schema, ensure_ascii=False))
            return self._call(prompt, messages, temperature, max_tokens, {"type": "json_object"})
        except openai.OpenAIError as exc:
            raise LanguageModelError(f"openai: {type(exc).__name__}") from exc

    def _call(self, system, messages, temperature, max_tokens, response_format) -> dict[str, Any]:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, *messages],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )
        if not response.choices:
            raise LanguageModelError("openai: empty choices")
        choice = response.choices[0]
        if choice.finish_reason == "length":
            raise LanguageModelError("openai: output truncated (max_tokens)")
        if getattr(choice.message, "refusal", None):
            raise LanguageModelError("openai: refusal")
        return parse_json_object(choice.message.content, "openai")


def parse_json_object(text: Any, provider: str) -> dict[str, Any]:
    """Parse ``text`` as a JSON object or raise ``LanguageModelError``."""
    if not isinstance(text, str) or not text.strip():
        raise LanguageModelError(f"{provider}: empty content")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LanguageModelError(f"{provider}: invalid JSON") from exc
    if not isinstance(data, dict):
        raise LanguageModelError(f"{provider}: JSON is not an object")
    return data
