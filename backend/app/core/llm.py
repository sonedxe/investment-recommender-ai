"""Language-model provider factory driven by ``LLM_PROVIDER`` (offline | openai | anthropic).

``offline`` (default) returns ``None``: the generative core then uses its
deterministic offline extractor and template explanation. ``openai`` and
``anthropic`` build their adapter when the matching API key is set; without the
key (or the SDK) a warning is logged and the app stays offline, never failing
at startup. The adapter is cached per configuration so a request does not
rebuild the SDK client.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache

from ai.generative.adapters import OFFLINE, build_language_model, configured_provider
from ai.generative.port import LanguageModel

logger = logging.getLogger(__name__)

_CONFIG_ENV = (
    "LLM_PROVIDER", "OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL",
    "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "ANTHROPIC_EXPLAIN_MODEL",
)

__all__ = ["OFFLINE", "ProviderInfo", "configured_provider", "get_language_model", "provider_info"]


@dataclass(frozen=True)
class ProviderInfo:
    mode: str  # "offline" | "llm"
    provider: str


@lru_cache(maxsize=4)
def _cached_model(config: tuple[tuple[str, str], ...]) -> LanguageModel | None:
    return build_language_model(env=dict(config))


def get_language_model() -> LanguageModel | None:
    """Return the effective adapter, or ``None`` for offline mode."""
    return _cached_model(tuple((name, os.getenv(name, "")) for name in _CONFIG_ENV))


def provider_info(llm: LanguageModel | None) -> ProviderInfo:
    return ProviderInfo("offline", OFFLINE) if llm is None else ProviderInfo("llm", llm.name)
