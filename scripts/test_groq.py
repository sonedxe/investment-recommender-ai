"""Verificación de la conexión con la API de IA generativa (Groq u otro
proveedor compatible con OpenAI) usando las rutas de código reales del
sistema (`ai.generative`).

Uso:
    1. Configura OPENAI_API_KEY en el archivo .env (raíz del repo).
    2. Desde la raíz:  python scripts/test_groq.py

Muestra el modo detectado, una interpretación de ejemplo y una explicación
generada por la API. Si la API falla, el sistema hace fallback al modo
offline (también se indica).
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

# Consola en UTF-8 (la respuesta del LLM puede traer caracteres Unicode).
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Cargar .env y permitir imports desde la raíz del repo.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from ai import generative  # noqa: E402
from ai.generative import llm_client  # noqa: E402

TEXTO = (
    "Tengo 30 años, quiero invertir S/ 5000 de mis S/ 20000 de ahorro, "
    "no me gusta arriesgar mucho y no los necesitaré por unos 3 años, "
    "tengo un fondo de emergencia para 4 meses"
)


def main() -> None:
    print(f"Proveedor configurado : {llm_client.os.getenv('OPENAI_BASE_URL')}")
    print(f"Modelo configurado    : {llm_client.os.getenv('OPENAI_MODEL')}")
    print(f"API key presente      : {'sí' if llm_client.api_disponible() else 'NO (modo offline)'}")
    print(f"Modo del módulo (ping): {generative.ping()['mode']}")
    print()

    print("== 1. Interpretación del texto de ejemplo ==")
    interp = generative.interpret(TEXTO)
    d = interp.a_dict()
    for k in ("monto_invertir", "horizonte_anios", "horizonte_etiqueta",
              "lambda_base", "ahorro_total", "cobertura_emergencia_meses",
              "completo", "modo"):
        print(f"   {k}: {d[k]}")
    assert interp.modo == "api", "Se esperaba modo 'api': ¿la clave es válida?"
    print()

    print("== 2. Explicación generada por la API ==")
    datos = {
        "portafolio": [
            {"categoria": "Bonos soberanos (BTP)", "peso_pct": 55.0},
            {"categoria": "Fondos de deuda", "peso_pct": 25.0},
            {"categoria": "Depósito a plazo fijo", "peso_pct": 15.0},
            {"categoria": "Fondos de acciones", "peso_pct": 5.0},
        ],
        "monto_invertir": 5000,
        "perfil_riesgo": "conservador",
        "retorno_esperado_pct": 5.8,
        "escenario_anio_malo_pct": 3.1,
        "horizonte_anios": 3,
        "horizonte_etiqueta": None,
        "efecto_horizonte": "mas_cauteloso",
        "capacidad_absorcion": 0.54,
        "capacidad_absorcion_asumida": False,
        "contexto": {"activo": True, "panorama_politico": 0.0, "estabilidad_macroeconomica": 0.0},
        "offline_kwargs": {  # requerido por el fallback offline
            "monto_invertir": 5000, "perfil_riesgo": "conservador",
            "pesos": [0.05, 0.0, 0.25, 0.55, 0.15], "E_portafolio": 0.058,
            "C_contexto": 0.0, "sigma_portafolio": 0.027,
            "horizonte_anios": 3, "horizonte_etiqueta": None,
            "m_H": 1.3, "ca_asumida": False, "CA": 0.54,
            "s_pol": 0.0, "s_mac": 0.0, "contexto_activo": True,
        },
    }
    texto, modo = generative.explain(datos)
    print(f"   (modo: {modo})")
    print()
    print(texto)
    print()
    assert modo == "api", "La explicación vino del fallback offline"
    print("OK: la API de IA generativa responde correctamente.")


if __name__ == "__main__":
    main()
