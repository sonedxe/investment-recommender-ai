"""Scripted ``LanguageModel`` double for the generative tests (no network)."""

from __future__ import annotations

from typing import Any

from ai.generative.port import LanguageModelError


class FakeLLM:
    """Returns the scripted responses in order; an Exception instance is raised instead."""

    name = "fake"

    def __init__(self, *responses: Any) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def complete_json(self, system, messages, schema, *, temperature, max_tokens):
        self.calls.append({"system": system, "messages": messages, "schema": schema, "temperature": temperature})
        if not self.responses:
            raise LanguageModelError("no scripted response left")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response
