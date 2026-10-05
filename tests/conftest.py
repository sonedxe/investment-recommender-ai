"""Test-wide isolation from the developer's real ``.env``.

``backend.app.core.config`` loads ``.env`` on import without overriding variables
that already exist, so pinning them here (before any test module imports the app)
keeps every test offline: no network calls and no API credit spent. Tests that
exercise a provider set its variables explicitly with ``monkeypatch``.
"""

from __future__ import annotations

import os

os.environ["LLM_PROVIDER"] = "offline"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""
