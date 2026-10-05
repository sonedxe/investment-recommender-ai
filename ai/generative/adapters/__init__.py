"""Language-model adapters and the provider selection shared by the backend and ``ping()``.

``LLM_PROVIDER`` picks ``offline`` (default), ``openai`` or ``anthropic``. A
provider is only *effective* when its API key is present; otherwise the app
stays offline (deterministic extractor and template explanation) instead of
failing at startup. The SDKs are imported lazily inside each adapter, so this
package is importable without ``openai`` or ``anthropic`` installed.
"""

from __future__ import annotations

import logging
import os
from typing import Mapping

from ai.generative.port import LanguageModel

logger = logging.getLogger(__name__)

OFFLINE = "offline"
OPENAI = "openai"
ANTHROPIC = "anthropic"
LLM_PROVIDERS = (OPENAI, ANTHROPIC)
_KEY_ENV = {OPENAI: "OPENAI_API_KEY", ANTHROPIC: "ANTHROPIC_API_KEY"}

DEFAULT_TIMEOUT_S = 30.0
DEFAULT_MAX_RETRIES = 1  # one SDK-level retry at most


def _env(env: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if env is None else env


def configured_provider(env: Mapping[str, str] | None = None) -> str:
    """The provider asked for in ``LLM_PROVIDER`` (lower-cased, ``offline`` when unset)."""
    return (_env(env).get("LLM_PROVIDER") or OFFLINE).strip().lower() or OFFLINE


def effective_provider(env: Mapping[str, str] | None = None) -> str:
    """``openai``/``anthropic`` when configured AND its key is set, else ``offline``."""
    provider = configured_provider(env)
    if provider in LLM_PROVIDERS and (_env(env).get(_KEY_ENV[provider]) or "").strip():
        return provider
    return OFFLINE


def build_language_model(provider: str | None = None, env: Mapping[str, str] | None = None) -> LanguageModel | None:
    """Build the adapter for ``provider`` (default: ``LLM_PROVIDER``) or return ``None`` (offline).

    Never raises: a missing key, an unknown provider or a missing SDK log a
    warning (without the key) and fall back to offline.
    """
    values = _env(env)
    provider = (provider or configured_provider(values)).strip().lower()
    if provider == OFFLINE:
        return None
    if provider not in LLM_PROVIDERS:
        logger.warning("unknown LLM_PROVIDER=%r; using offline mode", provider)
        return None
    api_key = (values.get(_KEY_ENV[provider]) or "").strip()
    if not api_key:
        logger.warning("LLM_PROVIDER=%s but %s is empty; using offline mode", provider, _KEY_ENV[provider])
        return None
    try:
        if provider == OPENAI:
            from ai.generative.adapters.openai_compatible import OpenAICompatibleModel

            return OpenAICompatibleModel(
                api_key=api_key,
                model=values.get("OPENAI_MODEL") or "gpt-4o-mini",
                base_url=values.get("OPENAI_BASE_URL") or None,
            )
        from ai.generative.adapters.anthropic_adapter import (
            DEFAULT_EXPLAIN_MODEL,
            DEFAULT_MODEL,
            AnthropicModel,
        )

        return AnthropicModel(
            api_key=api_key,
            model=values.get("ANTHROPIC_MODEL") or DEFAULT_MODEL,
            explain_model=values.get("ANTHROPIC_EXPLAIN_MODEL") or DEFAULT_EXPLAIN_MODEL,
        )
    except ImportError:
        logger.warning("the %s SDK is not installed; using offline mode", provider)
        return None
