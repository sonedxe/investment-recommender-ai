"""Datos de referencia del sistema (Anexos A y C del informe técnico v1.1).

Centraliza:
- Las 5 categorías de inversión representativas del mercado peruano (Anexo A),
  con sus retornos (mu) y riesgos (sigma) históricos de referencia.
- Los parámetros de las reglas de contexto (Anexo C.1).
- Los parámetros globales del módulo difuso y de contexto (Anexo C.2).

Todos los valores son parámetros iniciales de trabajo, definidos con criterio
de diseño y sujetos a calibración con fuentes (BCRP, SMV, AAFMP) — ver la
advertencia de rigor de la sección 4.6 del informe técnico.

IMPORTANTE: todas las magnitudes se expresan en DECIMALES (12.2% = 0.122),
porque el término cuadrático de la función de aptitud depende de las unidades.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Anexo A — Categorías de inversión de referencia (mercado peruano)
# ---------------------------------------------------------------------------

# Orden canónico de las categorías en todos los vectores/matrices del sistema.
CATEGORIAS: list[str] = [
    "fondos_acciones",
    "fondos_mixtos",
    "fondos_deuda",
    "bonos_soberanos",
    "deposito_plazo_fijo",
]

# Nombres para mostrar en la interfaz.
NOMBRES: dict[str, str] = {
    "fondos_acciones": "Fondos de acciones",
    "fondos_mixtos": "Fondos mixtos",
    "fondos_deuda": "Fondos de deuda",
    "bonos_soberanos": "Bonos soberanos (BTP)",
    "deposito_plazo_fijo": "Depósito a plazo fijo",
}

# Descripción en lenguaje simple de cada categoría (sección 6 del informe:
# ningún nombre de categoría aparece sin aclaración).
DESCRIPCIONES_SIMPLES: dict[str, str] = {
    "fondos_acciones": "fondos de acciones (inversiones en empresas, con mayor potencial de ganancia pero también mayor variabilidad)",
    "fondos_mixtos": "fondos mixtos (combinan acciones y renta fija, es decir, mezclan mayor potencial con algo de estabilidad)",
    "fondos_deuda": "fondos de deuda (renta fija, es decir, inversiones más predecibles y de menor riesgo, como préstamos a empresas o al Estado)",
    "bonos_soberanos": "bonos soberanos (préstamos al Estado peruano, con pagos mayormente predefinidos y bajo riesgo)",
    "deposito_plazo_fijo": "depósito a plazo fijo (ahorro bancario con tasa pactada, el más estable de todos)",
}

# Retorno esperado anual de referencia (mu) por categoría — Anexo A.
MU_REF: dict[str, float] = {
    "fondos_acciones": 0.122,
    "fondos_mixtos": 0.061,
    "fondos_deuda": 0.024,
    "bonos_soberanos": 0.065,
    "deposito_plazo_fijo": 0.045,
}

# Riesgo anual de referencia (sigma) por categoría — Anexo A (punto medio de
# los rangos reportados: ~18-20%, ~8-10%, ~2-3%, ~3-4%, ~0.5%).
SIGMA_REF: dict[str, float] = {
    "fondos_acciones": 0.19,
    "fondos_mixtos": 0.09,
    "fondos_deuda": 0.025,
    "bonos_soberanos": 0.035,
    "deposito_plazo_fijo": 0.005,
}

# ---------------------------------------------------------------------------
# Anexo C.1 — Sensibilidades por categoría (reglas de contexto)
# ---------------------------------------------------------------------------
# b       : precedente estructural (ajuste fijo de retorno), en decimales.
# a_pol   : sensibilidad del retorno al panorama político, en decimales.
# a_mac   : sensibilidad del retorno a la estabilidad macroeconómica, decimales.
# k_pol   : sensibilidad del riesgo al panorama político (adverso), adimensional.
# k_mac   : sensibilidad del riesgo a la estabilidad macroeconómica, adimensional.

CONTEXT_PARAMS: dict[str, dict[str, float]] = {
    "fondos_acciones": {"b": 0.005, "a_pol": 0.030, "a_mac": 0.010, "k_pol": 0.50, "k_mac": 0.20},
    "fondos_mixtos": {"b": 0.003, "a_pol": 0.015, "a_mac": 0.008, "k_pol": 0.25, "k_mac": 0.10},
    "fondos_deuda": {"b": 0.000, "a_pol": 0.005, "a_mac": 0.005, "k_pol": 0.10, "k_mac": 0.05},
    "bonos_soberanos": {"b": 0.002, "a_pol": 0.010, "a_mac": 0.005, "k_pol": 0.20, "k_mac": 0.10},
    "deposito_plazo_fijo": {"b": -0.003, "a_pol": 0.000, "a_mac": 0.003, "k_pol": 0.00, "k_mac": 0.00},
}

# ---------------------------------------------------------------------------
# Anexo C.2 — Parámetros globales
# ---------------------------------------------------------------------------

A_TEND: float = 0.015   # sensibilidad del retorno a la tendencia reciente (a_tend)
C_MAX: float = 0.03     # tope de influencia del contexto sobre el retorno (cmax)

# Consecuentes de las reglas difusas del horizonte (multiplicadores de aversión).
Z_HORIZONTE: dict[str, float] = {"corto": 1.5, "mediano": 1.0, "largo": 0.7}

# Consecuentes de las reglas difusas de capacidad de absorción.
Z_CA: dict[str, float] = {"baja": 0.20, "media": 0.50, "alta": 0.85}

SIGMA_PISO: float = 0.03   # volatilidad mínima tolerable (smax cuando CA = 0)
ALPHA_CA: float = 0.13     # amplitud: smax = sigma_piso + alpha * CA (máx 16%)
PHI: float = 50.0          # coeficiente de penalización de la función de aptitud

# Valor de smax cuando el módulo difuso está desactivado (sin penalización):
# 8.0 = 800% de volatilidad, techo que ningún portafolio real alcanza.
SIGMA_MAX_SIN_DIFUSO: float = 8.0

# Valor de capacidad de absorción asumido cuando el usuario declina responder
# (categoría difusa "Media", declarada visiblemente en la explicación).
CA_DEFAULT: float = Z_CA["media"]
