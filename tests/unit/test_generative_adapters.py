"""Adapters with mocked SDK clients (no network), provider factory and ``ping()`` mode."""

from __future__ import annotations

import json
from types import SimpleNamespace

import anthropic
import httpx2
import openai
import pytest

from ai.generative import ping
from ai.generative.adapters import build_language_model, effective_provider
from ai.generative.adapters.anthropic_adapter import TOOL_NAME, THINKING_MIN_TOKENS, AnthropicModel
from ai.generative.adapters.openai_compatible import OpenAICompatibleModel
from ai.generative.port import LanguageModel, LanguageModelError
from ai.generative.schema import CLARIFY_SCHEMA, EXPLAIN_SCHEMA, INTERPRET_SCHEMA

MESSAGES = [{"role": "user", "content": "Quiero invertir S/ 5000"}]
ANSWER = {"pregunta": "¿Cuánto quieres invertir?", "ayuda": None}
_REQUEST = httpx2.Request("POST", "https://example.invalid/v1")


def _status_error(cls, status: int):
    return cls("boom", response=httpx2.Response(status, request=_REQUEST), body=None)


class _Recorder:
    """Records ``create(**kwargs)`` calls and replays scripted results (exceptions are raised)."""

    def __init__(self, *results):
        self.results, self.calls = list(results), []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


# ------------------------------------------------------------------ OpenAI-compatible


def _chat(content, finish_reason="stop", refusal=None):
    message = SimpleNamespace(content=content, refusal=refusal)
    return SimpleNamespace(choices=[SimpleNamespace(message=message, finish_reason=finish_reason)])


def _openai(*results):
    recorder = _Recorder(*results)
    client = SimpleNamespace(chat=SimpleNamespace(completions=recorder))
    return OpenAICompatibleModel(api_key="test", model="gpt-test", client=client), recorder


def test_openai_request_shape_uses_non_strict_json_schema():
    model, rec = _openai(_chat(json.dumps(ANSWER)))
    assert model.complete_json("sistema", MESSAGES, CLARIFY_SCHEMA, temperature=0.3, max_tokens=150) == ANSWER
    call = rec.calls[0]
    assert call["model"] == "gpt-test" and call["temperature"] == 0.3 and call["max_tokens"] == 150
    assert call["messages"][0] == {"role": "system", "content": "sistema"} and call["messages"][1:] == MESSAGES
    fmt = call["response_format"]
    assert fmt["type"] == "json_schema"
    assert fmt["json_schema"]["schema"] is CLARIFY_SCHEMA and fmt["json_schema"]["strict"] is False
    assert isinstance(model, LanguageModel)


def test_openai_falls_back_to_json_object_when_json_schema_is_rejected():
    model, rec = _openai(_status_error(openai.BadRequestError, 400), _chat(json.dumps(ANSWER)), _chat(json.dumps(ANSWER)))
    assert model.complete_json("sistema", MESSAGES, CLARIFY_SCHEMA, temperature=0.3, max_tokens=150) == ANSWER
    retry = rec.calls[1]
    assert retry["response_format"] == {"type": "json_object"}
    assert '"pregunta"' in retry["messages"][0]["content"]  # schema appended to the system prompt
    model.complete_json("sistema", MESSAGES, CLARIFY_SCHEMA, temperature=0.3, max_tokens=150)
    assert rec.calls[2]["response_format"] == {"type": "json_object"}  # downgrade remembered


@pytest.mark.parametrize("error", [
    _status_error(openai.RateLimitError, 429),
    _status_error(openai.AuthenticationError, 401),
    openai.APIConnectionError(request=_REQUEST),
    openai.APITimeoutError(request=_REQUEST),
])
def test_openai_sdk_errors_become_language_model_error(error):
    model, _ = _openai(error)
    with pytest.raises(LanguageModelError):
        model.complete_json("s", MESSAGES, CLARIFY_SCHEMA, temperature=0.3, max_tokens=150)


@pytest.mark.parametrize("response", [
    _chat("{no es json"), _chat("[1, 2]"), _chat(None), _chat('{"a": 1}', finish_reason="length"),
    _chat(None, refusal="no"), SimpleNamespace(choices=[]),
])
def test_openai_invalid_output_becomes_language_model_error(response):
    model, _ = _openai(response)
    with pytest.raises(LanguageModelError):
        model.complete_json("s", MESSAGES, CLARIFY_SCHEMA, temperature=0.3, max_tokens=150)


# ------------------------------------------------------------------ Anthropic


def _message(input_, stop_reason="tool_use", name=TOOL_NAME):
    return SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="tool_use", name=name, input=input_)])


def _anthropic(*results, model="claude-haiku-4-5-20251001", explain_model="claude-sonnet-5-5"):
    recorder = _Recorder(*results)
    client = SimpleNamespace(messages=recorder)
    return AnthropicModel(api_key="test", model=model, explain_model=explain_model, client=client), recorder


def test_anthropic_forces_the_schema_tool_on_haiku():
    model, rec = _anthropic(_message(ANSWER))
    assert model.complete_json("sistema", MESSAGES, CLARIFY_SCHEMA, temperature=0.3, max_tokens=150) == ANSWER
    call = rec.calls[0]
    assert call["model"] == "claude-haiku-4-5-20251001" and call["max_tokens"] == 150 and call["system"] == "sistema"
    assert call["tools"] == [{"name": TOOL_NAME, "description": call["tools"][0]["description"], "input_schema": CLARIFY_SCHEMA}]
    assert call["tool_choice"] == {"type": "tool", "name": TOOL_NAME}
    assert call["extra_body"] == {"temperature": 0.3}  # SDK 1.x has no temperature kwarg
    assert "temperature" not in call and isinstance(model, LanguageModel)


def test_anthropic_explanation_uses_the_explain_model_without_forced_tool_or_sampling():
    model, rec = _anthropic(_message({"resumen": "x"}), _message(ANSWER))
    model.complete_json("sistema", MESSAGES, EXPLAIN_SCHEMA, temperature=0.3, max_tokens=1200)
    call = rec.calls[0]
    assert call["model"] == "claude-sonnet-5-5"
    assert call["tool_choice"] == {"type": "auto"} and TOOL_NAME in call["system"]
    assert "extra_body" not in call and call["output_config"] == {"effort": "low"}
    assert call["max_tokens"] == THINKING_MIN_TOKENS
    model.complete_json("s", MESSAGES, INTERPRET_SCHEMA, temperature=0.0, max_tokens=500)
    assert rec.calls[1]["model"] == "claude-haiku-4-5-20251001"


@pytest.mark.parametrize("error", [
    _status_error(anthropic.RateLimitError, 429),
    _status_error(anthropic.BadRequestError, 400),
    anthropic.APIConnectionError(request=_REQUEST),
    anthropic.APITimeoutError(request=_REQUEST),
])
def test_anthropic_sdk_errors_become_language_model_error(error):
    model, _ = _anthropic(error)
    with pytest.raises(LanguageModelError):
        model.complete_json("s", MESSAGES, CLARIFY_SCHEMA, temperature=0.3, max_tokens=150)


@pytest.mark.parametrize("response", [
    _message("{no es json"),
    _message(ANSWER, name="otra"),
    _message(ANSWER, stop_reason="refusal"),
    _message(ANSWER, stop_reason="max_tokens"),
    SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="{}")]),
])
def test_anthropic_invalid_output_becomes_language_model_error(response):
    model, _ = _anthropic(response)
    with pytest.raises(LanguageModelError):
        model.complete_json("s", MESSAGES, CLARIFY_SCHEMA, temperature=0.3, max_tokens=150)


def test_adapter_failure_makes_the_interpreter_fall_back_to_offline():
    from ai.generative.interpreter import interpret

    model, _ = _anthropic(*[anthropic.APIConnectionError(request=_REQUEST)] * 4)
    result = interpret([{"role": "user", "content": "Quiero invertir S/ 5000 a 3 años, riesgo moderado"}], llm=model)
    assert result.source == "offline" and result.profile.amount == 5000


# ------------------------------------------------------------------ factory and ping


@pytest.mark.parametrize("env", [
    {}, {"LLM_PROVIDER": "offline", "OPENAI_API_KEY": "k"}, {"LLM_PROVIDER": "openai"},
    {"LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "  "}, {"LLM_PROVIDER": "gemini", "OPENAI_API_KEY": "k"},
])
def test_factory_falls_back_to_offline(env):
    assert build_language_model(env=env) is None
    assert effective_provider(env) == "offline"


def test_factory_builds_adapters_when_the_key_is_present():
    built = build_language_model(env={"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "k", "OPENAI_MODEL": "m"})
    assert isinstance(built, OpenAICompatibleModel) and built.model == "m"
    built = build_language_model(env={"LLM_PROVIDER": "Anthropic", "ANTHROPIC_API_KEY": "k"})
    assert isinstance(built, AnthropicModel)
    assert (built.model, built.explain_model) == ("claude-haiku-4-5-20251001", "claude-sonnet-5-5")


def test_backend_factory_reports_the_effective_provider(monkeypatch):
    from backend.app.core.llm import get_language_model, provider_info

    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    info = provider_info(get_language_model())
    assert (info.mode, info.provider) == ("offline", "offline")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    info = provider_info(get_language_model())
    assert (info.mode, info.provider) == ("llm", "anthropic")


@pytest.mark.parametrize(("env", "mode"), [
    ({"LLM_PROVIDER": "offline", "OPENAI_API_KEY": "k"}, "offline"),
    ({"LLM_PROVIDER": "openai"}, "offline"),
    ({"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "k"}, "api"),
    ({"LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "k"}, "api"),
])
def test_ping_mode_follows_the_effective_provider(monkeypatch, env, mode):
    for name in ("LLM_PROVIDER", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    assert ping() == {"module": "generative", "status": "ok", "mode": mode}
