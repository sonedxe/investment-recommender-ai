"""Orquestador del flujo de datos del sistema (sección 4.1 del informe).

Encadena los módulos en el orden del flujo de 8 etapas:

    3. Módulo bayesiano   -> mu, sigma, covarianza y tendencia por categoría
    4. Módulo difuso      -> lambda_ef y sigma_max a partir del perfil
    5. Reglas de contexto -> mu', sigma' y covarianza ajustados
    6. Algoritmo genético -> mejor portafolio para ese usuario y contexto
    7. IA generativa      -> explicación en lenguaje simple

El módulo bayesiano es independiente del usuario; el difuso depende solo del
perfil; el de contexto combina ambos; el genético requiere todas las salidas
anteriores. Los interruptores de ablación (sección 4.7) permiten desactivar
el difuso (m_H = 1, sigma_max = 8) y/o el contexto (c_i = 0, s' = s).
"""

from __future__ import annotations

from ai import generative, heuristic, uncertainty
from ai.reference_data import CATEGORIAS, DESCRIPCIONES_SIMPLES, NOMBRES
from backend.app.schemas import FactoresContexto, Interruptores, PerfilUsuario


def run_pipeline(
    perfil: PerfilUsuario,
    contexto: FactoresContexto,
    interruptores: Interruptores,
    seed: int | None = 42,
) -> dict:
    """Ejecuta el flujo completo y devuelve el resultado listo para la API."""

    # --- Etapa 3: estimación bayesiana (independiente del usuario) ----------
    mercado = uncertainty.estimate()
    mu = mercado.vector_mu()
    sigma = mercado.vector_sigma()
    s_tend = mercado.vector_s_tend()

    # --- Etapa 4: lógica difusa (depende solo del perfil) -------------------
    difuso = uncertainty.evaluar_perfil(
        lambda_base=perfil.lambda_base,
        horizonte_anios=perfil.horizonte_anios,
        horizonte_etiqueta=perfil.horizonte_etiqueta,
        monto_invertir=perfil.monto_invertir,
        ahorro_total=None if perfil.absorcion_declinada else perfil.ahorro_total,
        cobertura_emergencia_meses=(
            None if perfil.absorcion_declinada else perfil.cobertura_emergencia_meses
        ),
        difuso_activo=interruptores.difuso,
    )

    # --- Etapa 5: reglas de contexto ----------------------------------------
    ctx = uncertainty.apply_context(
        mu=mu,
        sigma=sigma,
        covarianza=mercado.covarianza,
        s_tend=s_tend,
        s_pol=contexto.s_pol,
        s_mac=contexto.s_mac,
        contexto_activo=interruptores.contexto,
    )

    # --- Etapa 6: algoritmo genético ----------------------------------------
    ga = heuristic.optimize_portfolio(
        mu_aj=ctx.mu_aj,
        cov_aj=ctx.covarianza_aj,
        lambda_ef=difuso.lambda_ef,
        sigma_max=difuso.sigma_max,
        mu_base=mu,
        c=ctx.c,
        seed=seed,
    )

    # --- Etapa 7: explicación en lenguaje simple ----------------------------
    explicacion, modo_explicacion = generative.explain(
        {
            # Datos para el modo API (prompt del LLM).
            "portafolio": [
                {"categoria": NOMBRES[c], "peso_pct": round(ga.pesos[i] * 100, 1)}
                for i, c in enumerate(CATEGORIAS)
            ],
            "monto_invertir": perfil.monto_invertir,
            "perfil_riesgo": _perfil_riesgo(perfil.lambda_base),
            "retorno_esperado_pct": round((ga.E_portafolio + ga.C_contexto) * 100, 2),
            "escenario_anio_malo_pct": round(
                (ga.E_portafolio + ga.C_contexto - ga.sigma_portafolio) * 100, 2
            ),
            "horizonte_anios": perfil.horizonte_anios,
            "horizonte_etiqueta": perfil.horizonte_etiqueta,
            "efecto_horizonte": (
                "mas_cauteloso" if difuso.m_H > 1.05 else "mas_tolerante" if difuso.m_H < 0.95 else "neutral"
            ),
            "capacidad_absorcion": difuso.CA,
            "capacidad_absorcion_asumida": difuso.ca_asumida,
            "contexto": {
                "activo": interruptores.contexto,
                "panorama_politico": ctx.s_pol,
                "estabilidad_macroeconomica": ctx.s_mac,
            },
            # Datos para el modo offline (plantilla determinista).
            "offline_kwargs": {
                "monto_invertir": perfil.monto_invertir,
                "perfil_riesgo": _perfil_riesgo(perfil.lambda_base),
                "pesos": ga.pesos,
                "E_portafolio": ga.E_portafolio,
                "C_contexto": ga.C_contexto,
                "sigma_portafolio": ga.sigma_portafolio,
                "horizonte_anios": perfil.horizonte_anios,
                "horizonte_etiqueta": perfil.horizonte_etiqueta,
                "m_H": difuso.m_H,
                "ca_asumida": difuso.ca_asumida,
                "CA": difuso.CA,
                "s_pol": ctx.s_pol,
                "s_mac": ctx.s_mac,
                "contexto_activo": interruptores.contexto,
            },
        }
    )

    # --- Respuesta completa (etapa 8: la interfaz la presenta) ---------------
    return {
        "explicacion": explicacion,
        "modo_explicacion": modo_explicacion,
        "portafolio": [
            {
                "categoria": cat,
                "nombre": NOMBRES[cat],
                "descripcion": DESCRIPCIONES_SIMPLES[cat],
                "peso": ga.pesos[i],
                "monto_soles": round(ga.pesos[i] * perfil.monto_invertir, 2),
                "mu_base": mu[i],
                "sigma_base": sigma[i],
                "mu_ajustado": ctx.mu_aj[i],
                "sigma_ajustado": ctx.sigma_aj[i],
                "c_ajuste": ctx.c[i],
                "s_tend": s_tend[i],
            }
            for i, cat in enumerate(CATEGORIAS)
        ],
        "resultado": {
            "fitness": ga.fitness,
            "E_portafolio": ga.E_portafolio,
            "C_contexto": ga.C_contexto,
            "sigma_portafolio": ga.sigma_portafolio,
            "penalizacion": ga.penalizacion,
            "retorno_esperado": ga.E_portafolio + ga.C_contexto,
            "historial_convergencia": ga.historial_convergencia,
            "generaciones": ga.generaciones,
            "poblacion": ga.poblacion,
        },
        "difuso": {
            "activo": interruptores.difuso,
            "pertenencias": difuso.pertenencias,
            "m_H": difuso.m_H,
            "CA": difuso.CA,
            "sigma_max": difuso.sigma_max,
            "lambda_ef": difuso.lambda_ef,
            "lambda_base": perfil.lambda_base,
            "ca_asumida": difuso.ca_asumida,
            "r": difuso.r,
            "E": difuso.E,
        },
        "contexto": {
            "activo": interruptores.contexto,
            "s_pol": ctx.s_pol,
            "s_mac": ctx.s_mac,
            "factores_por_categoria": ctx.factores,
        },
        "mercado": {
            "mu": mu,
            "sigma": sigma,
            "s_tend": s_tend,
            "covarianza": mercado.covarianza,
        },
    }


def _perfil_riesgo(lambda_base: float) -> str:
    if lambda_base >= 1.5:
        return "conservador"
    if lambda_base >= 0.6:
        return "moderado"
    return "agresivo"
