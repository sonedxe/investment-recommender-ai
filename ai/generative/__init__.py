"""Generative AI module.

Interprets the user's free-text request into a structured profile (or a
clarification question) and explains the results in plain language. It talks
to the language model through a provider-agnostic port with adapters for
OpenAI-compatible APIs and Anthropic, plus a deterministic offline mode that
needs no network or API key.
"""

import os


def ping() -> dict:
    """Check that the module responds (used by the connectivity test)."""
    return {
        "module": "generative",
        "status": "ok",
        "mode": "api" if os.getenv("OPENAI_API_KEY") else "offline",
    }