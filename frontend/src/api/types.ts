// TypeScript mirrors of the backend HTTP contract (backend/app/api/schemas.py).
// Field names stay snake_case and optionality follows the Pydantic models exactly:
// `T | null` for `X | None` response fields, `?` for request fields with defaults.

export type Mode = 'offline' | 'llm'
export type RiskProfile = 'muy_agresivo' | 'agresivo' | 'moderado' | 'conservador' | 'muy_conservador'
export type HorizonLabel = 'corto' | 'mediano' | 'largo'
export type CategoryKey = 'stocks' | 'mixed' | 'debt' | 'bonds' | 'term'
/** Interpretation-schema field ids. */
export type FieldId = 'monto_invertir' | 'horizonte' | 'perfil_riesgo' | 'ahorro_total' | 'cobertura_emergencia_meses'

// ------------------------------------------------------------------ interpret

export interface Turn {
  role: 'user' | 'assistant'
  content: string
  /** Field the assistant turn asked for. */
  field?: FieldId | null
}

export interface InterpretRequest {
  conversation: Turn[]
}

export interface InterpretedProfileOut {
  amount: number | null
  horizon_years: number | null
  horizon_label: HorizonLabel | null
  risk_profile: RiskProfile | null
  lambda_base: number | null
  total_savings: number | null
  emergency_months: number | null
}

export interface QuestionOptionOut {
  value: string
  label: string
}

export interface QuestionOut {
  field: FieldId
  text: string
  hint: string | null
  options: QuestionOptionOut[] | null
  free_input: boolean
  unit: string | null
}

export interface InterpretResponse {
  mode: Mode
  provider: string
  profile: InterpretedProfileOut
  evidence: Record<string, string>
  missing: FieldId[]
  question: QuestionOut | null
  complete: boolean
  assumptions: string[]
  absorption_assumed: boolean
  rejected: FieldId[]
  contradictions: string[]
  source: 'llm' | 'offline'
  prompt_version: string
}

// ------------------------------------------------------------------ recommend

export interface ProfileIn {
  amount: number
  risk_profile: RiskProfile
  horizon_years?: number | null
  horizon_label?: HorizonLabel | null
  total_savings?: number | null
  emergency_months?: number | null
  lambda_base?: number | null
}

export interface ContextIn {
  political?: number
  macro?: number
}

export interface SwitchesIn {
  fuzzy?: boolean
  context?: boolean
}

export interface RecommendRequest {
  profile: ProfileIn
  /** Omit when not informed (neutral assumption). */
  context?: ContextIn | null
  switches?: SwitchesIn
  seed?: number | null
}

export interface AllocationOut {
  category: CategoryKey
  name: string
  weight: number
  amount: number
}

export interface ScenarioOut {
  name: string
  amount: number
}

export interface ScenarioTextOut {
  label: string
  text: string
  amount: number
}

export interface ValidationOut {
  passed: boolean
  attempts: number
  errors: string[]
  fallback: boolean
}

export interface ExplanationOut {
  summary: string
  paragraphs: string[]
  scenarios: ScenarioTextOut[]
  assumptions: string[]
  source: 'llm' | 'offline'
  prompt_version: string
  validation: ValidationOut
}

export interface ParamRowOut {
  category: string
  name: string
  mu: number
  sigma: number
  mu_adj: number
  sigma_adj: number
  context_adj: number
  source: 'data' | 'prior'
}

export interface PointOut {
  x: number
  y: number
}

export interface CurveOut {
  label: string
  points: PointOut[]
}

export interface HorizonOut {
  enabled: boolean
  years: number | null
  label: string | null
  memberships: Record<string, number>
  curves: CurveOut[]
}

export interface AbsorptionOut {
  enabled: boolean
  points: PointOut[]
  c: number
  membership_at_c: number | null
  centroid: number
  r: number | null
  e: number | null
  assumed: boolean
  ratio_memberships: Record<string, number>
  emergency_memberships: Record<string, number>
}

export interface RuleOut {
  kind: 'horizon' | 'absorption' | 'context'
  id: string
  condition: string
  effect: string
  activation: number | null
  applied: boolean
}

export interface ScoreOut {
  return_term: number
  context_term: number
  risk_term: number
  penalty_term: number
  fuzzy_reward: number
  total: number
  expected_return: number
  sigma: number
  sigma_max: number | null
  membership_at_c: number | null
}

export interface ConvergenceOut {
  best: number[]
  mean: number[]
  generations: number
  converged: boolean
  seed: number
}

export interface TechnicalOut {
  params: ParamRowOut[]
  lambda_base: number
  m_h: number
  lambda_eff: number
  horizon: HorizonOut
  absorption: AbsorptionOut
  rules: RuleOut[]
  score: ScoreOut
  convergence: ConvergenceOut
  max_weight: number
}

export interface RecommendProfileOut {
  amount: number
  risk_profile: RiskProfile
  horizon_years: number | null
  horizon_label: HorizonLabel | null
  total_savings: number | null
  emergency_months: number | null
}

export interface RecommendResponse {
  mode: Mode
  provider: string
  amount: number
  profile: RecommendProfileOut
  allocation: AllocationOut[]
  expected_return: number
  sigma: number
  c: number
  scenarios: ScenarioOut[]
  explanation: ExplanationOut
  assumptions: string[]
  switches: Required<SwitchesIn>
  technical: TechnicalOut
}

// -------------------------------------------------------------- context/market

export interface FactorLevelOut {
  value: number
  label: string
}

export interface FactorOut {
  id: 'political' | 'macro'
  label: string
  description: string
  value: number
  levels: FactorLevelOut[]
}

export interface ContextDefaultsResponse {
  factors: FactorOut[]
  c_max: number
  beta_tend: number
}

export interface CategoryEstimateOut {
  category: string
  name: string
  source: 'data' | 'prior'
  months: number
  prior_mean: number
  prior_sd: number
  data_mean: number | null
  data_sigma: number | null
  posterior_mean: number
  posterior_sd: number
  sigma: number
  trend: number
}

export interface MarketEstimatesResponse {
  categories: CategoryEstimateOut[]
  mu: number[]
  sigma: number[]
  correlation: number[][]
  trend: number[]
  estimated_pairs: [string, string][]
  psd_repaired: boolean
}
