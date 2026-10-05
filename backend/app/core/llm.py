"""Language-model provider factory driven by the ``LLM_PROVIDER`` environment variable.

``offline`` (default) returns ``None``: the generative core then uses its
deterministic offline extractor and template explanation. ``openai`` and
``anthropic`` are reserved for the adapters of the next unit; until they exist
they log a warning and fall back to offline.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from ai.generative.port import LanguageModel

logger = logging.getLogger(__name__)

OFFLINE = "offline"
PLANNED_PROVIDERS = ("openai", "anthropic")


@dataclass(frozen=True)
class ProviderInfo:
    mode: str  # "offline" | "llm"
    provider: str


def configured_provider() -> str:
    return os.getenv("LLM_PROVIDER", OFFLINE).strip().lower() or OFFLINE


def get_language_model() -> LanguageModel | None:
    """Return the configured adapter, or ``None`` for offline mode."""
    provider = configured_provider()
    if provider == OFFLINE:
        return None
    if provider in PLANNED_PROVIDERS:
        logger.warning("LLM_PROVIDER=%s has no adapter yet; using offline mode", provider)
        return None
    logger.warning("unknown LLM_PROVIDER=%r; using offline mode", provider)
    return None


def provider_info(llm: LanguageModel | None) -> ProviderInfo:
    return ProviderInfo("offline", OFFLINE) if llm is None else ProviderInfo("llm", llm.name)
