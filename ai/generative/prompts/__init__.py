"""Versioned prompt templates (``<name>.v<N>.md``); the version id is logged with each answer."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Prompt:
    text: str
    version: str

    def render(self, **values: str) -> str:
        """Replace ``{key}`` placeholders without touching the JSON braces of the examples."""
        text = self.text
        for key, value in values.items():
            text = text.replace("{" + key + "}", value)
        return text


@lru_cache(maxsize=None)
def load_prompt(name: str, version: int = 1) -> Prompt:
    """Load ``prompts/<name>.v<version>.md``; raises ``FileNotFoundError`` if missing."""
    version_id = f"{name}.v{version}"
    path = PROMPTS_DIR / f"{version_id}.md"
    return Prompt(text=path.read_text(encoding="utf-8").strip(), version=version_id)
