"""HTTP contracts (Pydantic v2, English snake_case).

Field ids inside the interpretation (``missing``, ``question.field``,
``evidence`` keys) are the interpretation-schema ids: ``monto_invertir``,
``horizonte``, ``perfil_riesgo``, ``ahorro_total``, ``cobertura_emergencia_meses``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ai.generative.schema import ALL_FIELDS
from ai.shared.types import HorizonLabel, RiskProfile

Mode = Literal["offline", "llm"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ------------------------------------------------------------------ interpret


class Turn(_Strict):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)
    field: str | None = Field(default=None, description="Field the assistant turn asked for")

    @field_validator("field")
    @classmethod
    def _known_field(cls, value: str | None) -> str | None:
        if value is not None and value not in ALL_FIELDS:
            raise ValueError(f"field must be one of {list(ALL_FIELDS)}")
        return value


class InterpretRequest(_Strict):
    conversation: list[Turn] = Field(min_length=1, max_length=60)

    @model_validator(mode="after")
    def _has_user_turn(self) -> InterpretRequest:
        if not any(t.role == "user" and t.content.strip() for t in self.conversation):
            raise ValueError("conversation needs at least one non-empty user turn")
        return self


class InterpretedProfileOut(BaseModel):
    amount: float | None
    horizon_years: float | None
    horizon_label: HorizonLabel | None
    risk_profile: RiskProfile | None
    lambda_base: float | None
    total_savings: float | None
    emergency_months: float | None


class QuestionOptionOut(BaseModel):
    value: str
    label: str


class QuestionOut(BaseModel):
    field: str
    text: str
    hint: str | None
    options: list[QuestionOptionOut] | None
    free_input: bool
    unit: str | None


class InterpretResponse(BaseModel):
    mode: Mode
    provider: str
    profile: InterpretedProfileOut
    evidence: dict[str, str]
    missing: list[str]
    question: QuestionOut | None
    complete: bool
    assumptions: list[str]
    absorption_assumed: bool
    rejected: list[str]
    contradictions: list[str]
    source: Literal["llm", "offline"]
    prompt_version: str


# ------------------------------------------------------------------ recommend


class ProfileIn(_Strict):
    amount: float = Field(gt=0, le=1e9, description="Amount to invest in soles")
    risk_profile: RiskProfile
    horizon_years: float | None = Field(default=None, ge=0, le=100)
    horizon_label: HorizonLabel | None = None
    total_savings: float | None = Field(default=None, gt=0, le=1e10)
    emergency_months: float | None = Field(default=None, ge=0, le=600)
    lambda_base: float | None = Field(
        default=None,
        description="Accepted so /api/interpret profiles can be posted as-is; ignored, "
        "lambda_base is always derived server-side from risk_profile",
    )

    @model_validator(mode="after")
    def _one_horizon(self) -> ProfileIn:
        if (self.horizon_years is None) == (self.horizon_label is None):
            raise ValueError("provide exactly one of horizon_years or horizon_label")
        return self


class ContextIn(_Strict):
    political: float = Field(default=0.0, ge=-1, le=1)
    macro: float = Field(default=0.0, ge=-1, le=1)


class SwitchesIn(_Strict):
    fuzzy: bool = True
    context: bool = True


class RecommendRequest(_Strict):
    profile: ProfileIn
    context: ContextIn | None = Field(default=None, description="Omit when not informed (neutral assumption)")
    switches: SwitchesIn = SwitchesIn()
    seed: int | None = Field(default=None, ge=0, le=2**32 - 1)


class AllocationOut(BaseModel):
    category: Literal["stocks", "mixed", "debt", "bonds", "term"]
    name: str
    weight: float
    amount: float


class ScenarioOut(BaseModel):
    name: str
    amount: float


class ScenarioTextOut(BaseModel):
    label: str
    text: str
    amount: float


class ValidationOut(BaseModel):
    passed: bool
    attempts: int
    errors: list[str]
    fallback: bool


class ExplanationOut(BaseModel):
    summary: str
    paragraphs: list[str]
    scenarios: list[ScenarioTextOut]
    assumptions: list[str]
    source: Literal["llm", "offline"]
    prompt_version: str
    validation: ValidationOut


class ParamRowOut(BaseModel):
    category: str
    name: str
    mu: float
    sigma: float
    mu_adj: float
    sigma_adj: float
    context_adj: float
    source: Literal["data", "prior"]


class PointOut(BaseModel):
    x: float
    y: float


class CurveOut(BaseModel):
    label: str
    points: list[PointOut]


class HorizonOut(BaseModel):
    enabled: bool
    years: float | None
    label: str | None
    memberships: dict[str, float]
    curves: list[CurveOut]


class AbsorptionOut(BaseModel):
    enabled: bool
    points: list[PointOut]
    c: float
    membership_at_c: float | None
    centroid: float
    r: float | None
    e: float | None
    assumed: bool
    ratio_memberships: dict[str, float]
    emergency_memberships: dict[str, float]


class RuleOut(BaseModel):
    kind: Literal["horizon", "absorption", "context"]
    id: str
    condition: str
    effect: str
    activation: float | None
    applied: bool


class ScoreOut(BaseModel):
    return_term: float
    context_term: float
    risk_term: float
    penalty_term: float
    fuzzy_reward: float
    total: float
    expected_return: float
    sigma: float
    sigma_max: float | None
    membership_at_c: float | None


class ConvergenceOut(BaseModel):
    best: list[float]
    mean: list[float]
    generations: int
    converged: bool
    seed: int


class TechnicalOut(BaseModel):
    params: list[ParamRowOut]
    lambda_base: float
    m_h: float
    lambda_eff: float
    horizon: HorizonOut
    absorption: AbsorptionOut
    rules: list[RuleOut]
    score: ScoreOut
    convergence: ConvergenceOut
    max_weight: float


class RecommendProfileOut(BaseModel):
    amount: float
    risk_profile: RiskProfile
    horizon_years: float | None
    horizon_label: HorizonLabel | None
    total_savings: float | None
    emergency_months: float | None


class RecommendResponse(BaseModel):
    mode: Mode
    provider: str
    amount: float
    profile: RecommendProfileOut
    allocation: list[AllocationOut]
    expected_return: float
    sigma: float
    c: float
    scenarios: list[ScenarioOut]
    explanation: ExplanationOut
    assumptions: list[str]
    switches: SwitchesIn
    technical: TechnicalOut


# -------------------------------------------------------------- context/market


class FactorLevelOut(BaseModel):
    value: float
    label: str


class FactorOut(BaseModel):
    id: Literal["political", "macro"]
    label: str
    description: str
    value: float
    levels: list[FactorLevelOut]


class ContextDefaultsResponse(BaseModel):
    factors: list[FactorOut]
    c_max: float
    beta_tend: float


class CategoryEstimateOut(BaseModel):
    category: str
    name: str
    source: Literal["data", "prior"]
    months: int
    prior_mean: float
    prior_sd: float
    data_mean: float | None
    data_sigma: float | None
    posterior_mean: float
    posterior_sd: float
    sigma: float
    trend: float


class MarketEstimatesResponse(BaseModel):
    categories: list[CategoryEstimateOut]
    mu: list[float]
    sigma: list[float]
    correlation: list[list[float]]
    trend: list[float]
    estimated_pairs: list[tuple[str, str]]
    psd_repaired: bool
