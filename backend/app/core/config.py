"""Configuración mínima del backend (se ampliará con pydantic-settings)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Raíz del repositorio (backend/app/core -> subimos 3 niveles).
BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]