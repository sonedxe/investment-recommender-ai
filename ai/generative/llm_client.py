"""Cliente de IA generativa por API (OpenAI o compatible con el protocolo
OpenAI: Azure, Groq, Ollama, etc.).

Se activa solo si hay OPENAI_API_KEY configurada; en caso contrario (o ante
cualquier error de red/formato) el módulo opera en modo offline con el parser
y el explicador deterministas, de modo que la aplicación siempre responde.

El cliente cumple el contrato de la sección 4.7:
- interpretar: texto libre -> JSON con los campos del perfil del usuario.
- explicar:    resultado del portafolio -> texto en lenguaje simple siguiendo
               las reglas obligatorias de la sección 6 (van en el prompt).
"""

from __future__ import annotations

import json
import os

import httpx

from ai.generative.schemas import Interpretacion

TIMEOUT = 30.0


def api_disponible() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _chat_completion(messages: list[dict], *, json_mode: bool = False) -> str:
    """Llama a /chat/completions del proveedor configurado y devuelve el texto."""
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    payload: dict = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    with httpx.Client(timeout=TIMEOUT) as client:
        res = client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        )
        res.raise_for_status()
        data = res.json()
    return data["choices"][0]["message"]["content"]


_SYSTEM_INTERPRET = """Eres el componente de interpretación de un recomendador de inversiones \
peruano. El usuario describe su situación en texto libre (puede ser una \
conversación de varios turnos con preguntas de aclaración). Extrae los datos \
y responde SOLO con un JSON con estas claves:
- "monto_invertir": número en soles (o null si no se sabe)
- "horizonte_anios": número de años (o null)
- "horizonte_etiqueta": "corto" | "mediano" | "largo" (solo si el usuario dio \
una expresión cualitativa sin cifra; si no, null)
- "lambda_base": aversión al riesgo: 2.0 conservador, 1.0 moderado, 0.2 \
agresivo (null si no se puede inferir). Ojo con las negaciones: "no me gusta \
arriesgar" es conservador.
- "ahorro_total": ahorros totales en soles (o null)
- "cobertura_emergencia_meses": meses de gastos cubiertos por un fondo aparte \
(o null)
- "absorcion_declinada": true si el usuario dijo explícitamente que prefiere \
no dar sus ahorros o su fondo de emergencia
- "completo": true solo si monto_invertir, horizonte (años o etiqueta) y \
lambda_base están todos presentes, y (ahorro_total y cobertura están \
presentes o absorcion_declinada es true)
- "pregunta_aclaracion": si completo es false, una pregunta breve y amable en \
español pidiendo SOLO el primer dato faltante; si completo es true, null.
No inventes valores: si un dato no está, usa null. No confundas la edad del \
usuario ("tengo 30 años") con el horizonte de inversión."""


def interpretar_api(texto_usuario: str) -> Interpretacion:
    """Interpreta el texto del usuario mediante la API de LLM.

    Lanza excepción ante cualquier fallo: el llamador hace fallback al modo
    offline.
    """
    contenido = _chat_completion(
        [
            {"role": "system", "content": _SYSTEM_INTERPRET},
            {"role": "user", "content": texto_usuario},
        ],
        json_mode=True,
    )
    data = json.loads(contenido)
    resultado = Interpretacion(
        monto_invertir=_num(data.get("monto_invertir")),
        horizonte_anios=_num(data.get("horizonte_anios")),
        horizonte_etiqueta=data.get("horizonte_etiqueta") or None,
        lambda_base=_num(data.get("lambda_base")),
        ahorro_total=_num(data.get("ahorro_total")),
        cobertura_emergencia_meses=_num(data.get("cobertura_emergencia_meses")),
        absorcion_declinada=bool(data.get("absorcion_declinada", False)),
        completo=bool(data.get("completo", False)),
        pregunta_aclaracion=data.get("pregunta_aclaracion") or None,
        campos_detectados={"origen": "api_llm"},
        modo="api",
    )
    return resultado


def _num(v) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


_SYSTEM_EXPLAIN = """Eres el componente de explicación de un recomendador de inversiones \
educativo para ciudadanos peruanos SIN conocimientos financieros. Redacta la \
explicación final en español, cálida y clara, cumpliendo SIEMPRE estas reglas:
1. Ningún término técnico sin traducción inmediata en la misma oración \
(ej.: "renta fija, es decir, inversiones más predecibles y de menor riesgo").
2. Todo resultado numérico acompañado de un ejemplo concreto en soles.
3. El riesgo se explica con un escenario ("en un año malo, podría bajar hasta \
un X%, es decir, unos S/ Y menos de lo invertido"), nunca con la palabra \
"riesgo" aislada.
4. Las categorías siempre con aclaración entre paréntesis (ej.: "fondos de \
acciones (inversiones en empresas, con mayor potencial de ganancia pero \
también mayor variabilidad)").
5. Explica en una o dos frases cómo influyeron el horizonte y la capacidad de \
absorción del usuario, SIN nombrar técnicas de IA.
6. Declara siempre los supuestos de contexto activos (panorama político, \
estabilidad económica) como supuestos ajustables, nunca como predicciones, y \
cualquier valor asumido por defecto porque el usuario no quiso responder.
7. Cierra siempre recordando que es una herramienta educativa, no asesoría \
financiera real.
Usa como mucho 4-6 párrafos cortos o viñetas."""


def explicar_api(datos: dict) -> str:
    """Genera la explicación final mediante la API de LLM.

    `datos` contiene el portafolio, el perfil del usuario, las pertenencias
    difusas y los factores de contexto (ver backend/services/pipeline.py).
    Lanza excepción ante cualquier fallo: el llamador hace fallback offline.
    """
    return _chat_completion(
        [
            {"role": "system", "content": _SYSTEM_EXPLAIN},
            {
                "role": "user",
                "content": "Explica esta recomendación al usuario. Datos (JSON):\n"
                + json.dumps(datos, ensure_ascii=False, indent=2),
            },
        ]
    )
