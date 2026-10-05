"""Módulo 4 — Lógica difusa (sección 4.5 del informe técnico v1.1).

Modela dos conceptos imprecisos del perfil del usuario mediante conjuntos
difusos e inferencia de tipo Sugeno de orden cero (cada regla produce un
valor numérico fijo; la salida es el promedio ponderado por el grado de
activación):

1. Horizonte temporal (H, en años) -> multiplicador m_H de la aversión al
   riesgo:  lambda_ef = lambda_base * m_H.
2. Capacidad de absorción de pérdidas (a partir de r = monto/ahorro y
   E = meses de fondo de emergencia) -> CA en [0, 1], que se traduce en la
   volatilidad máxima tolerable:  sigma_max = sigma_piso + alpha * CA.

Las funciones de pertenencia y las bases de reglas son exactamente las de las
secciones 4.5.1 y 4.5.2 del informe; los consecuentes y parámetros globales
vienen del Anexo C.2 (`ai.reference_data`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai.reference_data import (
    ALPHA_CA,
    CA_DEFAULT,
    SIGMA_MAX_SIN_DIFUSO,
    SIGMA_PISO,
    Z_CA,
    Z_HORIZONTE,
)

# Etiquetas cualitativas aceptadas para el horizonte (sección 4.5.1: si el
# usuario solo da una etiqueta, se asigna pertenencia 1 a ella y 0 al resto).
ETIQUETAS_HORIZONTE: dict[str, dict[str, float]] = {
    "corto": {"corto": 1.0, "mediano": 0.0, "largo": 0.0},
    "mediano": {"corto": 0.0, "mediano": 1.0, "largo": 0.0},
    "largo": {"corto": 0.0, "mediano": 0.0, "largo": 1.0},
}


# ---------------------------------------------------------------------------
# Funciones de pertenencia (secciones 4.5.1 y 4.5.2)
# ---------------------------------------------------------------------------

def _trimf(x: float, a: float, b: float, c: float) -> float:
    """Función de pertenencia triangular: 0 fuera de [a, c], 1 en b."""
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)


def membresias_horizonte(H: float) -> dict[str, float]:
    """Pertenencias del horizonte H (años) a {corto, mediano, largo}.

    Corto:   1 si H<=1; baja linealmente hasta 0 en H=3.
    Mediano: triangular con vértices (2, 5, 8).
    Largo:   0 hasta H=6; sube linealmente hasta 1 en H=10.
    """
    H = max(0.0, min(30.0, float(H)))  # universo de discurso [0, 30]
    if H <= 1.0:
        corto = 1.0
    elif H >= 3.0:
        corto = 0.0
    else:
        corto = (3.0 - H) / 2.0
    return {
        "corto": corto,
        "mediano": _trimf(H, 2.0, 5.0, 8.0),
        "largo": 0.0 if H <= 6.0 else (1.0 if H >= 10.0 else (H - 6.0) / 4.0),
    }


def membresias_r(r: float) -> dict[str, float]:
    """Pertenencias de r = monto/ahorro a {bajo, medio, alto}.

    Bajo:  1 si r<=0.2; baja hasta 0 en r=0.4.
    Medio: triangular con vértices (0.2, 0.5, 0.8).
    Alto:  0 hasta r=0.6; sube hasta 1 en r=0.9.
    """
    r = max(0.0, min(1.0, float(r)))
    if r <= 0.2:
        bajo = 1.0
    elif r >= 0.4:
        bajo = 0.0
    else:
        bajo = (0.4 - r) / 0.2
    return {
        "bajo": bajo,
        "medio": _trimf(r, 0.2, 0.5, 0.8),
        "alto": 0.0 if r <= 0.6 else (1.0 if r >= 0.9 else (r - 0.6) / 0.3),
    }


def membresias_E(E: float) -> dict[str, float]:
    """Pertenencias de E (meses de emergencia) a {insuficiente, adecuada}.

    Insuficiente: 1 si E<=1; baja hasta 0 en E=4.
    Adecuada:     0 hasta E=2; sube hasta 1 en E=6 (se satura en E=12).
    """
    E = max(0.0, min(12.0, float(E)))  # se satura en 12 (sección 4.5.2)
    if E <= 1.0:
        insuf = 1.0
    elif E >= 4.0:
        insuf = 0.0
    else:
        insuf = (4.0 - E) / 3.0
    return {
        "insuficiente": insuf,
        "adecuada": 0.0 if E <= 2.0 else (1.0 if E >= 6.0 else (E - 2.0) / 4.0),
    }


# ---------------------------------------------------------------------------
# Inferencia Sugeno de orden cero
# ---------------------------------------------------------------------------

def multiplicador_horizonte(memb: dict[str, float]) -> float:
    """Reglas RH1-RH3: m_H = sum(mu_k * z_k) / sum(mu_k).

    Consecuentes: corto -> 1.5, mediano -> 1.0, largo -> 0.7 (Anexo C.2).
    Si ninguna regla se activa (no debería ocurrir), m_H = 1 (sin modulación).
    """
    pesos = [memb["corto"], memb["mediano"], memb["largo"]]
    zs = [Z_HORIZONTE["corto"], Z_HORIZONTE["mediano"], Z_HORIZONTE["largo"]]
    denom = sum(pesos)
    if denom <= 0:
        return 1.0
    return sum(w * z for w, z in zip(pesos, zs)) / denom


def capacidad_absorcion(memb_r: dict[str, float], memb_E: dict[str, float]) -> float:
    """Reglas RA1-RA6 (operador Y = mínimo) -> CA en [0, 1].

    RA1: r bajo  y E insuficiente -> media (0.50)
    RA2: r bajo  y E adecuada     -> alta  (0.85)
    RA3: r medio y E insuficiente -> baja  (0.20)
    RA4: r medio y E adecuada     -> media (0.50)
    RA5: r alto  y E insuficiente -> baja  (0.20)
    RA6: r alto  y E adecuada     -> media (0.50)
    """
    reglas = [
        (min(memb_r["bajo"], memb_E["insuficiente"]), Z_CA["media"]),
        (min(memb_r["bajo"], memb_E["adecuada"]), Z_CA["alta"]),
        (min(memb_r["medio"], memb_E["insuficiente"]), Z_CA["baja"]),
        (min(memb_r["medio"], memb_E["adecuada"]), Z_CA["media"]),
        (min(memb_r["alto"], memb_E["insuficiente"]), Z_CA["baja"]),
        (min(memb_r["alto"], memb_E["adecuada"]), Z_CA["media"]),
    ]
    denom = sum(w for w, _ in reglas)
    if denom <= 0:
        return CA_DEFAULT
    return sum(w * z for w, z in reglas) / denom


# ---------------------------------------------------------------------------
# Evaluación completa del perfil
# ---------------------------------------------------------------------------

@dataclass
class FuzzyResult:
    """Salida del módulo difuso (contrato de la sección 4.7)."""

    pertenencias: dict[str, dict[str, float]] = field(default_factory=dict)
    m_H: float = 1.0
    CA: float = CA_DEFAULT
    sigma_max: float = SIGMA_MAX_SIN_DIFUSO
    lambda_ef: float = 1.0
    # True si se asumió CA "Media" porque el usuario declinó dar sus datos
    # de absorción (debe declararse visiblemente en la explicación).
    ca_asumida: bool = False
    # r y E efectivamente usados (None si se asumió CA por defecto).
    r: float | None = None
    E: float | None = None


def evaluar_perfil(
    lambda_base: float,
    horizonte_anios: float | None = None,
    horizonte_etiqueta: str | None = None,
    monto_invertir: float | None = None,
    ahorro_total: float | None = None,
    cobertura_emergencia_meses: float | None = None,
    difuso_activo: bool = True,
) -> FuzzyResult:
    """Convierte el perfil del usuario en los parámetros de la optimización.

    Entradas (contrato 4.7):
        horizonte_anios | horizonte_etiqueta, monto_invertir, ahorro_total,
        cobertura_emergencia_meses, lambda_base.
    Salida:
        { pertenencias, m_H, CA, sigma_max, lambda_ef }.

    Con `difuso_activo=False` (interruptor de ablación, sección 4.7): m_H = 1
    y sigma_max = 8 (sin penalización), lambda_ef = lambda_base.
    """
    # --- Horizonte temporal -------------------------------------------------
    if horizonte_anios is not None:
        memb_h = membresias_horizonte(horizonte_anios)
    elif horizonte_etiqueta is not None and horizonte_etiqueta in ETIQUETAS_HORIZONTE:
        memb_h = dict(ETIQUETAS_HORIZONTE[horizonte_etiqueta])
    else:
        # Sin información de horizonte: sin modulación (el loop de
        # clarificación del módulo generativo debería haberlo pedido antes).
        memb_h = {"corto": 0.0, "mediano": 1.0, "largo": 0.0}

    # --- Capacidad de absorción ---------------------------------------------
    ca_asumida = False
    r: float | None = None
    E: float | None = None
    memb_r = {"bajo": 0.0, "medio": 1.0, "alto": 0.0}
    memb_E = {"insuficiente": 0.0, "adecuada": 1.0}

    if (
        monto_invertir is not None
        and ahorro_total is not None
        and ahorro_total > 0
        and cobertura_emergencia_meses is not None
    ):
        r = max(0.0, min(1.0, monto_invertir / ahorro_total))
        E = cobertura_emergencia_meses
        memb_r = membresias_r(r)
        memb_E = membresias_E(E)
        ca = capacidad_absorcion(memb_r, memb_E)
    else:
        # El usuario declinó responder: categoría difusa "Media", declarada
        # de forma visible en la explicación (sección 4.2).
        ca = CA_DEFAULT
        ca_asumida = True

    # --- Salida según el interruptor de ablación -----------------------------
    if not difuso_activo:
        return FuzzyResult(
            pertenencias={"horizonte": memb_h, "r": memb_r, "E": memb_E},
            m_H=1.0,
            CA=ca,
            sigma_max=SIGMA_MAX_SIN_DIFUSO,
            lambda_ef=lambda_base,
            ca_asumida=ca_asumida,
            r=r,
            E=E,
        )

    m_H = multiplicador_horizonte(memb_h)
    sigma_max = SIGMA_PISO + ALPHA_CA * ca
    return FuzzyResult(
        pertenencias={"horizonte": memb_h, "r": memb_r, "E": memb_E},
        m_H=m_H,
        CA=ca,
        sigma_max=sigma_max,
        lambda_ef=lambda_base * m_H,
        ca_asumida=ca_asumida,
        r=r,
        E=E,
    )
