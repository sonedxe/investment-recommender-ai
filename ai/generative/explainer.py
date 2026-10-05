"""Generador de explicaciones en lenguaje simple (sección 6 del informe).

Produce la explicación final siguiendo las reglas obligatorias de la capa de
lenguaje simple:

1. Ningún término técnico sin traducción inmediata en la misma oración.
2. Todo resultado numérico acompañado de un ejemplo concreto en soles.
3. El riesgo se explica con un escenario, no con la palabra aislada.
4. Nombres de categorías siempre con su aclaración entre paréntesis.
5. Una o dos frases sobre cómo influyeron el horizonte y la capacidad de
   absorción, sin nombrar la técnica.
6. Siempre se declaran los supuestos de contexto activos, como supuestos
   ajustables (nunca como predicciones), y cualquier valor asumido por
   defecto porque el usuario no quiso responder.
7. Cierre con el recordatorio de herramienta educativa.
"""

from __future__ import annotations

from ai.reference_data import CATEGORIAS, DESCRIPCIONES_SIMPLES


def _soles(valor: float) -> str:
    """Formatea un monto en soles: S/ 5,000."""
    return f"S/ {valor:,.0f}".replace(",", " ")


def _pct(decimal: float) -> str:
    """Formatea un decimal como porcentaje con un decimal: 12.2%."""
    return f"{decimal * 100:.1f}%"


def _etiqueta_factor(v: float) -> str:
    if v < -0.33:
        return "adverso"
    if v > 0.33:
        return "favorable"
    return "neutral"


def explicar_offline(
    *,
    monto_invertir: float,
    perfil_riesgo: str | None,
    pesos: list[float],
    E_portafolio: float,
    C_contexto: float,
    sigma_portafolio: float,
    horizonte_anios: float | None,
    horizonte_etiqueta: str | None,
    m_H: float,
    ca_asumida: bool,
    CA: float,
    s_pol: float,
    s_mac: float,
    contexto_activo: bool,
) -> str:
    """Redacta la explicación final (modo offline, determinista)."""
    partes: list[str] = []

    # --- 1. Introducción con el perfil entendido ----------------------------
    plazo = (
        f"unos {horizonte_anios:g} años"
        if horizonte_anios is not None
        else f"{horizonte_etiqueta} plazo"
        if horizonte_etiqueta
        else "el plazo que indicaste"
    )
    perfil = perfil_riesgo or "moderado"
    partes.append(
        f"Con base en lo que me contaste —quieres invertir {_soles(monto_invertir)} "
        f"a {plazo} y tu disposición al riesgo es {perfil}—, "
        f"te sugiero repartir tu dinero así:"
    )

    # --- 2. Distribución por categoría (regla 4: nombre con aclaración; ------
    #        regla 2: ejemplo concreto en soles) ------------------------------
    lineas: list[str] = []
    for i, cat in enumerate(CATEGORIAS):
        w = pesos[i]
        if w < 0.005:  # menos del 0.5% no se menciona para no abrumar
            continue
        lineas.append(
            f"- {w * 100:.0f}% en {DESCRIPCIONES_SIMPLES[cat]}: "
            f"aproximadamente {_soles(monto_invertir * w)} de tus {_soles(monto_invertir)}."
        )
    partes.append("\n".join(lineas))

    # --- 3. Retorno esperado con ejemplo en soles ----------------------------
    retorno_total = E_portafolio + C_contexto
    partes.append(
        f"En un año promedio, esta combinación podría rendir alrededor de "
        f"{_pct(retorno_total)}; sobre tus {_soles(monto_invertir)} serían "
        f"unos {_soles(monto_invertir * retorno_total)} en doce meses."
    )

    # --- 4. Escenario de riesgo (regla 3) ------------------------------------
    malo = retorno_total - sigma_portafolio
    if malo < 0:
        partes.append(
            f"El riesgo, dicho con un escenario: en un año malo —uno de esos que "
            f"históricamente ocurre de vez en cuando— el portafolio podría llegar a "
            f"bajar hasta un {_pct(malo)}, es decir, unos "
            f"{_soles(monto_invertir * abs(malo))} menos de lo invertido. En un año "
            f"bueno podría superar el promedio por un margen similar."
        )
    else:
        partes.append(
            f"El riesgo, dicho con un escenario: incluso en un año malo —uno de esos "
            f"que históricamente ocurre de vez en cuando— el rendimiento podría bajar "
            f"hasta alrededor de {_pct(malo)}, es decir, ganarías menos "
            f"(unos {_soles(monto_invertir * max(malo, 0))}), pero no perderías capital "
            f"en ese escenario típico."
        )

    # --- 5. Influencia del horizonte y la absorción (regla 5, sin tecnicismos)
    if m_H > 1.05:
        partes.append(
            "Como piensas necesitar este dinero en un plazo no muy largo, el sistema "
            "fue algo más cauteloso de lo que pediste, para que una caída no te "
            "agarre sin tiempo de recuperarte."
        )
    elif m_H < 0.95:
        partes.append(
            "Como no necesitarás este dinero por muchos años, el sistema aceptó un "
            "poco más de variabilidad, porque hay tiempo de sobra para recuperarse "
            "de las caídas."
        )
    if ca_asumida:
        partes.append(
            "Como preferiste no indicar tus ahorros totales ni tu fondo de "
            "emergencia, asumí una capacidad media para asimilar pérdidas; si me "
            "das esos datos, la recomendación puede ajustarse mejor a ti."
        )
    elif CA < 0.35:
        partes.append(
            "Además, como esta inversión compromete una parte importante de tus "
            "ahorros o tu colchón de emergencia es corto, limité la variabilidad "
            "total para no ponerte en aprietos."
        )
    elif CA > 0.65:
        partes.append(
            "Además, como esta inversión es una parte manejable de tus ahorros y "
            "tienes un fondo de emergencia razonable, el sistema pudo aceptar algo "
            "más de variabilidad en busca de mejor rendimiento."
        )

    # --- 6. Supuestos de contexto (regla 6) ----------------------------------
    if contexto_activo:
        partes.append(
            f"Supuestos de contexto usados (ajustables desde el panel, no son "
            f"predicciones): panorama político {_etiqueta_factor(s_pol)} y "
            f"estabilidad económica {_etiqueta_factor(s_mac)}. Si estos cambian, "
            f"la recomendación podría cambiar."
        )
    else:
        partes.append(
            "Los factores de contexto (política, economía) estaban desactivados: "
            "la recomendación se basó únicamente en los promedios históricos."
        )

    # --- 7. Cierre obligatorio -----------------------------------------------
    partes.append(
        "Recuerda: esta es una herramienta educativa con fines académicos, no "
        "asesoría financiera real. Antes de invertir, consulta con un asesor "
        "certificado."
    )

    return "\n\n".join(partes)
