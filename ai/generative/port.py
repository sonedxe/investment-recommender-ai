"""Provider-agnostic port to a language model that answers with JSON.

Adapters (offline, OpenAI-compatible, Anthropic) implement ``LanguageModel``
with the native structured-output mechanism of their provider. The core only
depends on this protocol, so no provider SDK is imported outside the adapters.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


class LanguageModelError(RuntimeError):
    """The provider failed, timed out or returned something that is not JSON."""


@runtime_checkable
class LanguageModel(Protocol):
    """A model that completes a conversation into a JSON object matching ``schema``."""

    name: str

    def complete_json(
        self,
        system: str,
        messages: list[dict[str, Any]],
        schema: dict[str, Any],
        *,
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        """Return the parsed JSON object or raise ``LanguageModelError``."""
        ...
