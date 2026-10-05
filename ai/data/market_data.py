"""Datos históricos REALES del mercado peruano, documentados y citables.

Reemplaza a las series sintéticas de la versión anterior. Cada serie declara:
- sus valores y años,
- la fuente exacta (documento, entidad y URL),
- qué celdas son observaciones directas y cuáles son estimaciones
  documentadas (marcadas con `observado=False` y su método).

Detalle completo, citas y método de recolección: `docs/FUENTES_DE_DATOS.md`.
Fecha de recolección: octubre 2026.

Resumen de fuentes:
- Fondos mutuos (acciones, mixtos, deuda): Boletines mensuales de diciembre de
  la Asociación de Administradoras de Fondos Mutuos del Perú (AAFMP/FMP),
  tabla "Rentabilidades Promedio" (fuente de datos: SMV), años 2019-2025.
- Depósito a plazo fijo: Banco Mundial, indicador FR.INR.DPST "Deposit
  interest rate (%)" (fuente: FMI, Estadísticas Financieras Internacionales,
  reportado por el BCRP), 2019-2022; y TREA de depósitos a plazo en soles
  publicada por la SBS y bancos (BBVA), 2025-2026.
- Bonos soberanos (BTP): rendimiento del bono a 10 años en soles (BCRP vía
  CEIC y Trading Economics; curva de Bonos del Tesoro en Moody's Local PE;
  emisión PEN 6.85% 2035 del MEF), puntos 2020-2026.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Observacion:
    """Un punto de la serie: valor anual (%) y si es observación directa."""

    anio: int
    valor_pct: float
    observado: bool = True
    nota: str = ""


@dataclass
class SerieMercado:
    """Serie histórica documentada de una categoría de inversión."""

    categoria: str
    concepto: str                      # qué mide el valor anual
    fuente_corta: str                  # para mostrar en la app / docs
    cita: str                          # referencia completa con URL
    observaciones: list[Observacion] = field(default_factory=list)

    def valores_decimales(self) -> list[float]:
        return [o.valor_pct / 100.0 for o in self.observaciones]

    def anios(self) -> list[int]:
        return [o.anio for o in self.observaciones]


# ---------------------------------------------------------------------------
# 1-3. FONDOS MUTUOS POR TIPO (rentabilidad anual en soles, año calendario)
# Fuente: boletines AAFMP de diciembre de cada año, tabla "Rentabilidades
# Promedio" (dato de la SMV). 100% observaciones directas.
# ---------------------------------------------------------------------------

_CITA_AAFMP = (
    "Asociación de Administradoras de Fondos Mutuos del Perú (AAFMP), "
    "Boletín mensual de diciembre de {anio}, tabla 'Rentabilidades Promedio' "
    "(fuente de datos: SMV). https://fondosmutuos.pe/estadisticas/"
)

FONDOS_ACCIONES = SerieMercado(
    categoria="fondos_acciones",
    concepto="Rentabilidad anual promedio de fondos mutuos de acciones, en soles",
    fuente_corta="AAFMP (boletines de diciembre, dato SMV)",
    cita=_CITA_AAFMP,
    observaciones=[
        Observacion(2019, -1.10),
        Observacion(2020, -1.60),
        Observacion(2021, 4.74),
        Observacion(2022, -6.23),
        Observacion(2023, 17.41),
        Observacion(2024, 8.13),
        Observacion(2025, 34.28),
    ],
)

FONDOS_MIXTOS = SerieMercado(
    categoria="fondos_mixtos",
    concepto="Rentabilidad anual promedio de fondos mutuos mixtos, en soles",
    fuente_corta="AAFMP (boletines de diciembre, dato SMV)",
    cita=_CITA_AAFMP,
    observaciones=[
        Observacion(2019, 3.68),
        Observacion(2020, 1.60),
        Observacion(2021, -0.31),
        Observacion(2022, 0.05),
        Observacion(2023, 10.57),
        Observacion(2024, 7.89),
        Observacion(2025, 16.70),
    ],
)

FONDOS_DEUDA = SerieMercado(
    categoria="fondos_deuda",
    concepto="Rentabilidad anual promedio de fondos mutuos de deuda, en soles",
    fuente_corta="AAFMP (boletines de diciembre, dato SMV)",
    cita=_CITA_AAFMP,
    observaciones=[
        Observacion(2019, 3.83),
        Observacion(2020, 2.46),
        Observacion(2021, -1.14),
        Observacion(2022, 2.43),
        Observacion(2023, 7.72),
        Observacion(2024, 5.11),
        Observacion(2025, 4.94),
    ],
)

# ---------------------------------------------------------------------------
# 4. BONOS SOBERANOS (BTP) — rendimiento del bono a 10 años en soles.
# Supuesto documentado: el retorno anual se aproxima con el rendimiento
# (yield) al cierre del año (inversor que mantiene al vencimiento).
# ---------------------------------------------------------------------------

BONOS_SOBERANOS = SerieMercado(
    categoria="bonos_soberanos",
    concepto="Rendimiento (yield) del bono soberano peruano a 10 años en soles",
    fuente_corta="BCRP vía CEIC / Trading Economics; MEF",
    cita=(
        "BCRP, 'Rendimiento del bono del gobierno peruano a 10 años (PEN)', "
        "vía CEIC (mínimo histórico dic-2020: 3.633%; ago-2026: 6.189%) "
        "https://www.ceicdata.com/en/peru/government-bond-yield/government-bond-yield-10-years-pen ; "
        "Trading Economics, Peru 10-Year Government Bond Yield (oct-2026: 6.35%, +0.54 interanual; "
        "sep-2026: 6.33%, +0.45 interanual) https://tradingeconomics.com/peru/government-bond-yield ; "
        "Moody's Local PE, 'Evolución de variables de mercado y fondos mutuos en Perú' (dic-2025), "
        "curva de Bonos del Tesoro al 24/12/2024; MEF, emisión bono PEN 6.85% 12-ago-2035 (jun-2025)."
    ),
    observaciones=[
        Observacion(2020, 3.633, True, "Mínimo histórico dic-2020 (CEIC/BCRP)"),
        Observacion(
            2024, 7.00, False,
            "Lectura aproximada de la curva de Bonos del Tesoro al 24/12/2024 "
            "(gráfico Moody's Local PE dic-2025, rango 10Y ~6.9-7.1%)",
        ),
        Observacion(
            2025, 5.85, False,
            "Promedio de los valores interanuales reportados por Trading Economics "
            "para sep/oct-2025 (6.33%-0.45 y 6.35%-0.54); consistente con la "
            "emisión soberana PEN cupón 6.85% de jun-2025 (MEF)",
        ),
        Observacion(2026, 6.189, True, "Ago-2026 (CEIC/BCRP)"),
    ],
)

# ---------------------------------------------------------------------------
# 5. DEPÓSITO A PLAZO FIJO — tasa de interés de depósitos (promedio anual).
# ---------------------------------------------------------------------------

DEPOSITO_PLAZO_FIJO = SerieMercado(
    categoria="deposito_plazo_fijo",
    concepto="Tasa de interés anual de depósitos a plazo en soles (promedio del sistema)",
    fuente_corta="Banco Mundial / FMI-IFS (dato BCRP); SBS-BBVA",
    cita=(
        "Banco Mundial, indicador FR.INR.DPST 'Deposit interest rate (%) - Peru' "
        "(fuente: FMI, Estadísticas Financieras Internacionales; reportado por el BCRP): "
        "2019: 3.67, 2020: 1.861, 2021: 0.697, 2022: 4.821. "
        "https://api.worldbank.org/v2/country/PER/indicator/FR.INR.DPST ; "
        "BBVA Perú, Depósito a Plazo: TREA soles a 1 año 4.40% (vigente 15-21 sep 2026) "
        "https://www.bbva.pe/personas/productos/inversiones/depositos/deposito-plazo.html ; "
        "SBS, Tasas de interés por tipo de depósito, sistema bancario MN (sep-2026)."
    ),
    observaciones=[
        Observacion(2019, 3.67),
        Observacion(2020, 1.861),
        Observacion(2021, 0.697),
        Observacion(2022, 4.821),
        Observacion(
            2025, 4.40, False,
            "TREA de referencia del sistema (BBVA, sep-2026); la serie FR.INR.DPST "
            "del Banco Mundial aún no publica 2023-2025",
        ),
    ],
)

SERIES_MERCADO: dict[str, SerieMercado] = {
    "fondos_acciones": FONDOS_ACCIONES,
    "fondos_mixtos": FONDOS_MIXTOS,
    "fondos_deuda": FONDOS_DEUDA,
    "bonos_soberanos": BONOS_SOBERANOS,
    "deposito_plazo_fijo": DEPOSITO_PLAZO_FIJO,
}


def historial_decimal() -> dict[str, list[float]]:
    """Devuelve {categoria: [retornos anuales en decimales]} (contrato bayesiano)."""
    return {cat: s.valores_decimales() for cat, s in SERIES_MERCADO.items()}
