"""Modelos de entrada/salida de la API REST (contratos de la sección 4.7)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InterpretRequest(BaseModel):
    """Texto libre del usuario (puede ser la conversación acumulada)."""

    texto: str = Field(..., min_length=1, description="Texto libre o conversación acumulada")


class PerfilUsuario(BaseModel):
    """Perfil estructurado del usuario (salida de la interpretación)."""

    monto_invertir: float = Field(..., gt=0)
    horizonte_anios: float | None = Field(default=None, ge=0, le=30)
    horizonte_etiqueta: str | None = Field(
        default=None, pattern="^(corto|mediano|largo)$"
    )
    lambda_base: float = Field(..., gt=0, le=10)
    ahorro_total: float | None = Field(default=None, gt=0)
    cobertura_emergencia_meses: float | None = Field(default=None, ge=0, le=12)
    absorcion_declinada: bool = False


class FactoresContexto(BaseModel):
    """Factores ambientales configurables desde el panel (sección 4.6.1)."""

    s_pol: float = Field(default=0.0, ge=-1.0, le=1.0, description="Panorama político")
    s_mac: float = Field(default=0.0, ge=-1.0, le=1.0, description="Estabilidad macroeconómica")


class Interruptores(BaseModel):
    """Interruptores de módulo para las pruebas de ablación (sección 4.7)."""

    difuso: bool = True
    contexto: bool = True


class RecommendRequest(BaseModel):
    perfil: PerfilUsuario
    contexto: FactoresContexto = FactoresContexto()
    interruptores: Interruptores = Interruptores()
    seed: int | None = Field(default=42, description="Semilla del algoritmo genético (reproducibilidad)")
