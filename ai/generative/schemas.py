"""Estructuras de datos del módulo de IA generativa (contrato sección 4.7)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Interpretacion:
    """Salida de la interpretación del texto del usuario.

    Contrato (sección 4.7):
        { monto_invertir, horizonte_anios | horizonte_etiqueta, lambda_base,
          ahorro_total, cobertura_emergencia_meses, completo: bool,
          pregunta_aclaracion?: string }
    """

    monto_invertir: float | None = None
    horizonte_anios: float | None = None
    horizonte_etiqueta: str | None = None      # "corto" | "mediano" | "largo"
    lambda_base: float | None = None           # aversión al riesgo declarada
    ahorro_total: float | None = None
    cobertura_emergencia_meses: float | None = None
    # True si el usuario declinó explícitamente dar los datos de absorción:
    # el sistema continúa con CA "Media" y lo declara en la explicación.
    absorcion_declinada: bool = False
    completo: bool = False
    pregunta_aclaracion: str | None = None
    # Trazabilidad: qué se detectó y de dónde (para el panel técnico).
    campos_detectados: dict[str, str] = field(default_factory=dict)
    modo: str = "offline"                       # "api" | "offline"

    def perfil_riesgo(self) -> str | None:
        """Etiqueta cualitativa asociada a lambda_base (para mostrar)."""
        if self.lambda_base is None:
            return None
        if self.lambda_base >= 1.5:
            return "conservador"
        if self.lambda_base >= 0.6:
            return "moderado"
        return "agresivo"

    def a_dict(self) -> dict:
        return {
            "monto_invertir": self.monto_invertir,
            "horizonte_anios": self.horizonte_anios,
            "horizonte_etiqueta": self.horizonte_etiqueta,
            "lambda_base": self.lambda_base,
            "perfil_riesgo": self.perfil_riesgo(),
            "ahorro_total": self.ahorro_total,
            "cobertura_emergencia_meses": self.cobertura_emergencia_meses,
            "absorcion_declinada": self.absorcion_declinada,
            "completo": self.completo,
            "pregunta_aclaracion": self.pregunta_aclaracion,
            "campos_detectados": self.campos_detectados,
            "modo": self.modo,
        }
