"""Interpretador offline (modo sin API) del texto del usuario.

Extrae del texto libre en español los campos del contrato de interpretación
(sección 4.7) mediante reglas léxicas y expresiones regulares:

- monto_invertir          : montos (S/, soles, "mil") asociados a "invertir".
- horizonte_anios         : "X años" / "X meses" en contexto de plazo
                            (evita confundir la edad: "tengo 30 años").
- horizonte_etiqueta      : "a corto/mediano/largo plazo".
- lambda_base             : vocabulario de tolerancia al riesgo, con manejo de
                            negaciones ("no me gusta arriesgar" -> conservador).
- ahorro_total            : montos asociados a "ahorro(s)".
- cobertura_emergencia_meses : "fondo de emergencia de X meses", etc.

Requisito formal (sección 4.2): si falta información crítica, NO se asumen
valores en silencio: se devuelve `completo=False` con una pregunta de
aclaración específica. Si el usuario declina dar los datos de absorción, se
marca `absorcion_declinada=True` y el sistema continúa declarándolo.
"""

from __future__ import annotations

import re
import unicodedata

from ai.generative.schemas import Interpretacion

# Mapeo de tolerancia al riesgo -> lambda_base (sección 5.1: conservador
# lambda=2, agresivo lambda=0.2; moderado intermedio).
LAMBDA_CONSERVADOR = 2.0
LAMBDA_MODERADO = 1.0
LAMBDA_AGRESIVO = 0.2


def _normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para reglas léxicas robustas."""
    texto = texto.lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )


def _parse_numero(s: str) -> float:
    """Convierte "5,000" / "20.000" / "1500" / "2.5" a float.

    Regla: grupos de 3 dígitos tras separador => separador de miles (Perú);
    un único separador seguido de 1-2 dígitos => decimal.
    """
    s = s.strip()
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", s):
        return float(re.sub(r"[.,]", "", s))
    return float(s.replace(",", "."))


def _extraer_montos(texto: str) -> list[tuple[float, int, int]]:
    """Devuelve [(valor, inicio, fin)] de cada monto en soles del texto.

    Reconoce "S/ 5000", "S/.5000", "5000 soles", "5 mil", "5 mil soles".
    """
    montos: list[tuple[float, int, int]] = []
    patron = re.compile(
        r"(?:s/\s*\.?\s*|s\.\s*)(\d[\d.,]*)|"      # S/ 5000 | S/. 5000
        r"(\d[\d.,]*)\s*(mil\s+)?(?:soles|sol)\b"  # 5000 soles | 5 mil soles
    )
    for m in patron.finditer(texto):
        crudo = m.group(1) or m.group(2)
        if crudo is None:
            continue
        try:
            valor = _parse_numero(crudo)
        except ValueError:
            continue
        if m.group(3):  # multiplicador "mil"
            valor *= 1000.0
        montos.append((valor, m.start(), m.end()))
    return montos


CLAVES_INVERSION = ["invertir", "inversion", "invertiria", "meter", "colocar", "destinar"]
CLAVES_AHORRO = ["ahorro", "ahorros", "ahorrado", "ahorrados", "guardado"]

# Ventana máxima (caracteres) para asociar un monto a una palabra clave.
VENTANA_CLAVE = 45


def _distancia_min(claves: list[str], pos: int, texto: str) -> float:
    """Distancia en caracteres desde pos a la palabra clave más cercana."""
    mejor = float("inf")
    for clave in claves:
        inicio = 0
        while True:
            idx = texto.find(clave, inicio)
            if idx == -1:
                break
            mejor = min(mejor, abs(idx - pos))
            inicio = idx + 1
    return mejor


def _clasificar_montos(
    texto: str, montos: list[tuple[float, int, int]]
) -> tuple[float | None, float | None, list[float]]:
    """Asigna cada monto al concepto de la palabra clave MÁS CERCANA.

    Ejemplo del informe: "quiero invertir S/ 5000 de mis S/ 20000 de ahorro"
    -> 5000 es monto_invertir (cerca de "invertir") y 20000 es ahorro_total
    (cerca de "ahorro"), aunque ambas palabras estén en la misma frase.

    Devuelve (monto_invertir, ahorro_total, montos_sin_clasificar): los
    montos sin palabra clave cercana quedan disponibles para heurísticas
    posteriores (p. ej. "tengo S/ 8000, ¿en qué los pongo?").
    """
    monto_invertir: float | None = None
    ahorro_total: float | None = None
    sin_clasificar: list[float] = []
    for valor, ini, _ in montos:
        d_inv = _distancia_min(CLAVES_INVERSION, ini, texto)
        d_aho = _distancia_min(CLAVES_AHORRO, ini, texto)
        if d_inv <= d_aho and d_inv <= VENTANA_CLAVE:
            if monto_invertir is None:
                monto_invertir = valor
            else:
                sin_clasificar.append(valor)
        elif d_aho < d_inv and d_aho <= VENTANA_CLAVE:
            if ahorro_total is None:
                ahorro_total = valor
            else:
                sin_clasificar.append(valor)
        else:
            sin_clasificar.append(valor)

    # Segunda pasada: montos SIN símbolo (ni "S/" ni "soles") pero pegados a
    # una palabra clave, p. ej. "mis ahorros totales son 30000". Solo se
    # aceptan cifras >= 100 para no confundir años/meses con dinero.
    if ahorro_total is None:
        m = re.search(
            r"ahorros?(?:\s+totales?)?(?:\s+son|\s+de|\s+es|,)?\s*(?:de\s+)?(\d[\d.,]*)", texto
        ) or re.search(r"(\d[\d.,]*)\s+de\s+ahorros?", texto)
        if m:
            try:
                valor = _parse_numero(m.group(1))
                if valor >= 100:
                    ahorro_total = valor
            except ValueError:
                pass
    if monto_invertir is None:
        m = re.search(
            r"(?:invertir|inversion|destinar)\w*\s+(?:unos\s+|aprox\.?\s+)?(\d[\d.,]*)", texto
        )
        if m:
            try:
                valor = _parse_numero(m.group(1))
                if valor >= 100:
                    monto_invertir = valor
            except ValueError:
                pass
    return monto_invertir, ahorro_total, sin_clasificar


def _extraer_horizonte(texto: str) -> tuple[float | None, str | None]:
    """Extrae (horizonte_anios, horizonte_etiqueta).

    Años/meses en contexto de plazo; excluye la edad ("tengo 30 años").
    Etiquetas: "a corto/mediano/largo plazo".
    """
    etiqueta = None
    m = re.search(r"(corto|mediano|medio|largo)\s+plazo", texto)
    if m:
        etiqueta = {"corto": "corto", "mediano": "mediano", "medio": "mediano", "largo": "largo"}[
            m.group(1)
        ]

    # Años en contexto de plazo (no edad).
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*(anos|anitos)\b", texto):
        antes = texto[max(0, m.start() - 25):m.start()]
        if re.search(r"tengo|cumplo|edad", antes):
            continue  # es la edad del usuario, no el horizonte
        try:
            return float(m.group(1).replace(",", ".")), etiqueta
        except ValueError:
            continue

    # Meses en contexto de plazo (no fondo de emergencia).
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*meses\b", texto):
        antes = texto[max(0, m.start() - 45):m.start()]
        if re.search(r"emergencia|cubrir|cubro|gastos|fondo|vivir", antes):
            continue  # es la cobertura de emergencia
        try:
            meses = float(m.group(1).replace(",", "."))
            return round(meses / 12.0, 2), etiqueta
        except ValueError:
            continue

    return None, etiqueta


def _extraer_lambda(texto: str) -> float | None:
    """Vocabulario de tolerancia al riesgo -> lambda_base (con negaciones)."""
    # Frases conservadoras (incluyen negaciones de "arriesgar").
    conservador = [
        "no me gusta arriesgar", "no quiero arriesgar", "no me gustaria arriesgar",
        "no quiero perder", "conservador", "seguro", "segura", "sin riesgo",
        "poco riesgo", "bajo riesgo", "cauteloso", "cautelosa", "tranquilo",
        "tranquila", "con cuidado", "proteger", "cuidar mi dinero",
    ]
    agresivo = [
        "agresivo", "agresiva", "arriesgado", "arriesgada", "me gusta arriesgar",
        "me gusta el riesgo", "alto riesgo", "mucho riesgo", "maximizar",
        "lo que sea con tal de ganar", "rentabilidad maxima",
    ]
    moderado = [
        "moderado", "moderada", "equilibrado", "equilibrada", "balanceado",
        "balanceada", "intermedio", "intermedia", "ni tanto", "punto medio",
    ]
    for frase in conservador:
        if frase in texto:
            return LAMBDA_CONSERVADOR
    for frase in agresivo:
        if frase in texto:
            return LAMBDA_AGRESIVO
    for frase in moderado:
        if frase in texto:
            return LAMBDA_MODERADO
    return None


def _extraer_cobertura(texto: str) -> float | None:
    """Meses de gastos cubiertos por un fondo aparte (se satura en 12)."""
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*meses\b", texto):
        antes = texto[max(0, m.start() - 45):m.start()]
        despues = texto[m.end():m.end() + 30]
        if re.search(r"emergencia|cubrir|cubro|gastos|fondo|vivir|imprevisto", antes) or re.search(
            r"de gastos|de emergencia", despues
        ):
            try:
                return min(12.0, float(m.group(1).replace(",", ".")))
            except ValueError:
                continue
    if re.search(r"no tengo (fondo|ahorros de) emergencia|sin fondo de emergencia", texto):
        return 0.0
    return None


def _declina_absorcion(texto: str) -> bool:
    return bool(
        re.search(
            r"prefiero no (decir|responder|contestar)|no quiero (decir|responder|contestar)|"
            r"no deseo (decir|responder|contestar)|paso de responder|no te puedo decir",
            texto,
        )
    )


# Preguntas de aclaración (sección 4.2): específicas por campo faltante.
PREGUNTAS = {
    "monto_invertir": "¿Cuánto dinero te gustaría invertir, en soles? (por ejemplo: “quiero invertir S/ 5,000”)",
    "horizonte": "¿Por cuánto tiempo aproximadamente no necesitarías este dinero? (por ejemplo: “unos 3 años”, o “a largo plazo”)",
    "lambda_base": "Ante una posible bajada temporal de tu inversión, ¿qué tan dispuesto estarías a asumirla: prefieres algo seguro aunque gane poco (conservador), un punto medio (moderado) o asumir más variabilidad para ganar más (agresivo)?",
    "absorcion": "Dos últimas preguntas para cuidar tu dinero: ¿cuáles son tus ahorros totales aproximados? Y aparte de lo que invertirías, ¿tienes un fondo de emergencia para cubrir cuántos meses de tus gastos? (Si prefieres no decirlo, escríbelo y continuaré con un supuesto medio, que te mostraré en la explicación.)",
}


def interpretar_offline(texto_usuario: str) -> Interpretacion:
    """Interpreta el texto (o la conversación completa) sin llamar a ninguna API.

    Recibe el texto acumulado de todos los turnos del usuario: así el loop de
    clarificación funciona re-analizando la conversación tras cada respuesta.
    """
    texto = _normalizar(texto_usuario)
    resultado = Interpretacion(modo="offline")
    detectados: dict[str, str] = {}

    montos = _extraer_montos(texto)

    resultado.monto_invertir, resultado.ahorro_total, sin_clasificar = _clasificar_montos(
        texto, montos
    )
    if resultado.monto_invertir is not None:
        detectados["monto_invertir"] = "monto asociado a 'invertir'"
    if resultado.ahorro_total is not None:
        detectados["ahorro_total"] = "monto asociado a 'ahorro(s)'"

    # Si hay un solo monto sin clasificar, se asume que es lo que quiere
    # invertir (caso frecuente: "tengo S/ 8000, ¿en qué los pongo?").
    if resultado.monto_invertir is None and len(sin_clasificar) == 1:
        resultado.monto_invertir = sin_clasificar[0]
        detectados["monto_invertir"] = "único monto mencionado sin clasificar"

    resultado.horizonte_anios, resultado.horizonte_etiqueta = _extraer_horizonte(texto)
    if resultado.horizonte_anios is not None:
        detectados["horizonte"] = f"{resultado.horizonte_anios} años"
    elif resultado.horizonte_etiqueta is not None:
        detectados["horizonte"] = f"etiqueta '{resultado.horizonte_etiqueta}'"

    resultado.lambda_base = _extraer_lambda(texto)
    if resultado.lambda_base is not None:
        detectados["tolerancia"] = f"lambda_base={resultado.lambda_base}"

    resultado.cobertura_emergencia_meses = _extraer_cobertura(texto)
    if resultado.cobertura_emergencia_meses is not None:
        detectados["cobertura"] = f"{resultado.cobertura_emergencia_meses} meses"

    resultado.absorcion_declinada = _declina_absorcion(texto)
    resultado.campos_detectados = detectados

    # --- Completitud y pregunta de aclaración (requisito de la sección 4.2) --
    if resultado.monto_invertir is None:
        resultado.pregunta_aclaracion = PREGUNTAS["monto_invertir"]
    elif resultado.horizonte_anios is None and resultado.horizonte_etiqueta is None:
        resultado.pregunta_aclaracion = PREGUNTAS["horizonte"]
    elif resultado.lambda_base is None:
        resultado.pregunta_aclaracion = PREGUNTAS["lambda_base"]
    elif (
        not resultado.absorcion_declinada
        and (resultado.ahorro_total is None or resultado.cobertura_emergencia_meses is None)
    ):
        resultado.pregunta_aclaracion = PREGUNTAS["absorcion"]
    else:
        resultado.completo = True

    return resultado
