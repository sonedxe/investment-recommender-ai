"""Generative AI module.

Interprets the user's free-text request into a structured profile (or a
clarification question) and explains the results in plain language. It talks
to the language model through a provider-agnostic port with adapters for
OpenAI-compatible APIs and Anthropic, plus a deterministic offline mode that
needs no network or API key.
"""

from ai.generative.adapters import OFFLINE, effective_provider


def ping() -> dict:
    """Check that the module responds; ``mode`` is "api" only when an LLM provider is effective."""
    return {
        "module": "generative",
        "status": "ok",
        "mode": "offline" if effective_provider() == OFFLINE else "api",
    }
