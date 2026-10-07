// Backend contract (snake_case) -> design-system props (camelCase). No presentational component imports the API.
import { formatFraction, formatMoney, formatNumber } from '../lib/format'
import type {
  AllocationItem,
  ContextLevel,
  Factor,
  FreeInput,
  MembershipChartProps,
  Question,
  ResultScreenProps,
  Rule,
  ScoreBreakdownProps,
  TechnicalData,
  UnderstoodItem,
} from '../types/ui'
import type {
  ContextDefaultsResponse,
  ContextIn,
  FieldId,
  HorizonLabel,
  InterpretResponse,
  QuestionOut,
  RecommendResponse,
  RiskProfile,
  TechnicalOut,
} from './types'

export const ABSORPTION_FIELDS: readonly FieldId[] = ['ahorro_total', 'cobertura_emergencia_meses']
export const REFUSAL_TEXT = 'Prefiero no responder'

const RISK_LABEL: Record<RiskProfile, string> = {
  muy_conservador: 'Muy baja',
  conservador: 'Baja',
  moderado: 'Media',
  agresivo: 'Alta',
  muy_agresivo: 'Muy alta',
}
const RISK_PHRASE: Record<RiskProfile, string> = {
  muy_conservador: 'con muy poca tolerancia al riesgo',
  conservador: 'con poca tolerancia al riesgo',
  moderado: 'con una tolerancia al riesgo media',
  agresivo: 'con bastante tolerancia al riesgo',
  muy_agresivo: 'con mucha tolerancia al riesgo',
}
const HORIZON_LABEL: Record<HorizonLabel, string> = { corto: 'Corto plazo', mediano: 'Mediano plazo', largo: 'Largo plazo' }
const HORIZON_PHRASE: Record<HorizonLabel, string> = { corto: 'a corto plazo', mediano: 'a mediano plazo', largo: 'a largo plazo' }
const FREE_INPUT_LABEL: Record<FieldId, string> = {
  monto_invertir: 'Monto a invertir',
  horizonte: 'O escribe los años',
  perfil_riesgo: 'Tu respuesta',
  ahorro_total: 'Ahorro total',
  cobertura_emergencia_meses: 'Meses que podrías cubrir',
}
const CATEGORY_NOTES: Record<AllocationItem['categoryId'], string> = {
  stocks: 'Pueden crecer más y también bajar más.',
  mixed: 'Combinan acciones y deuda.',
  debt: 'Prestan a empresas; bajas moderadas.',
  bonds: 'Préstamos al Estado peruano.',
  term: 'Monto y plazo acordados con el banco.',
}

function years(n: number): string {
  return `${formatNumber(n, Number.isInteger(n) ? 0 : 1)} ${n === 1 ? 'año' : 'años'}`
}
function months(n: number): string {
  return `${formatNumber(n, Number.isInteger(n) ? 0 : 1)} ${n === 1 ? 'mes' : 'meses'}`
}
function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1)
}
/** Avoids rendering `−0.0000` for a zero term the backend sends as -0.0. */
function clean(n: number): number {
  return Object.is(n, -0) ? 0 : n
}

// ------------------------------------------------------------------ interpretation

/** Data understood so far, one row per interpretation field, in the design-system order. */
export function toUnderstood(res: InterpretResponse): UnderstoodItem[] {
  const p = res.profile
  const asked = res.question?.field
  const horizon = p.horizon_years != null ? years(p.horizon_years) : p.horizon_label ? HORIZON_LABEL[p.horizon_label] : null
  const rows: { key: string; field: FieldId; label: string; value: string | null }[] = [
    { key: 'amount', field: 'monto_invertir', label: 'Monto a invertir', value: p.amount != null ? formatMoney(p.amount) : null },
    { key: 'risk', field: 'perfil_riesgo', label: 'Tolerancia al riesgo', value: p.risk_profile ? RISK_LABEL[p.risk_profile] : null },
    { key: 'horizon', field: 'horizonte', label: 'Horizonte', value: horizon },
    { key: 'savings', field: 'ahorro_total', label: 'Ahorro total', value: p.total_savings != null ? formatMoney(p.total_savings) : null },
    {
      key: 'emergency',
      field: 'cobertura_emergencia_meses',
      label: 'Fondo de emergencia',
      value: p.emergency_months != null ? months(p.emergency_months) : null,
    },
  ]
  return rows.map(({ key, field, label, value }): UnderstoodItem => {
    const optional = ABSORPTION_FIELDS.includes(field)
    if (value !== null) {
      const evidence = res.evidence[field]
      return { key, label, value, state: 'understood', note: evidence ? `Dijiste: “${evidence}”` : undefined }
    }
    if (field === asked) return { key, label, value: null, state: 'asked' }
    if (optional && (res.rejected.includes(field) || res.absorption_assumed)) {
      return { key, label, value: 'No informado', state: 'assumed', note: 'Capacidad media' }
    }
    return { key, label, value: null, state: 'missing', note: optional ? 'Opcional' : undefined }
  })
}

/** One clarification question: closed options, or a free input whose unit `soles` becomes the `S/` prefix. */
export function toQuestion(q: QuestionOut): Question {
  const question: Question = { question: q.text, hint: q.hint ?? undefined }
  if (q.options) question.options = q.options.map((o) => ({ value: o.value, label: o.label }))
  if (q.free_input) {
    const free: FreeInput = { label: FREE_INPUT_LABEL[q.field] }
    if (q.unit === 'soles') free.prefix = 'S/'
    else if (q.unit) free.unit = q.unit
    question.freeInput = free
  }
  return question
}

/** User turn sent back to /api/interpret: the option label (natural language) or the number with its unit. */
export function answerContent(q: QuestionOut, value: string): string {
  const option = q.options?.find((o) => o.value === value)
  if (option) return option.label
  const text = value.trim()
  if (q.unit === 'soles') return `S/ ${text}`
  return q.unit ? `${text} ${q.unit}` : text
}

/** Absorption fields may be declined; critical fields (amount, horizon, risk) never offer a skip. */
export function canSkip(q: QuestionOut): boolean {
  return ABSORPTION_FIELDS.includes(q.field)
}

/**
 * `Pregunta N de M`: N counts the assistant questions so far (the current one included, `askedFields`
 * in conversation order); M adds the fields still pending after this one.
 */
export function questionProgress(res: InterpretResponse, askedFields: FieldId[]): { step: number; totalSteps: number } {
  const step = Math.max(1, askedFields.length)
  const current = res.question?.field
  const pending = res.missing.filter((f) => f !== current && !askedFields.includes(f) && !res.rejected.includes(f))
  return { step, totalSteps: step + pending.length }
}

// ------------------------------------------------------------------ recommendation

export function toAllocation(res: RecommendResponse): AllocationItem[] {
  return res.allocation.map((a) => ({
    categoryId: a.category,
    name: a.name,
    pct: a.weight * 100,
    amount: a.amount,
    note: CATEGORY_NOTES[a.category],
  }))
}

/** `Pensando en tus S/ 5,000.00, en unos 3 años y con poca tolerancia al riesgo, esta es una forma de repartirlos.` */
export function toSummary(res: RecommendResponse): string {
  const p = res.profile
  let horizon = 'en el plazo que indicaste'
  if (p.horizon_years != null) horizon = p.horizon_years === 1 ? 'en un año' : `en unos ${years(p.horizon_years)}`
  else if (p.horizon_label) horizon = HORIZON_PHRASE[p.horizon_label]
  return `Pensando en tus ${formatMoney(p.amount)}, ${horizon} y ${RISK_PHRASE[p.risk_profile]}, esta es una forma de repartirlos.`
}

/** User value on the horizon axis; a qualitative label uses the centre of its plateau. */
function horizonValue(t: TechnicalOut): number {
  const h = t.horizon
  if (h.years != null) return h.years
  const curve = h.curves.find((c) => c.label === h.label)
  const top = curve?.points.filter((pt) => pt.y >= 1) ?? []
  return top.length ? (top[0].x + top[top.length - 1].x) / 2 : 0
}

function toMembership(t: TechnicalOut): MembershipChartProps {
  const xs = t.horizon.curves.flatMap((c) => c.points.map((pt) => pt.x))
  return {
    domain: [Math.min(0, ...xs), Math.max(...xs)],
    value: horizonValue(t),
    series: t.horizon.curves.map((c) => ({ id: c.label, name: capitalize(c.label), points: c.points })),
  }
}

function toRules(t: TechnicalOut): Rule[] {
  // Non-applied fuzzy rules (switch off or assumed absorption) have no meaningful activation.
  return t.rules.map((r) => ({
    id: r.id,
    kind: r.kind,
    name: '',
    condition: r.condition,
    effect: r.effect,
    activation: r.applied ? r.activation : null,
  }))
}

function toScore(t: TechnicalOut): ScoreBreakdownProps {
  const s = t.score
  const volatility =
    s.sigma_max == null
      ? 'Sin límite de volatilidad (difuso apagado)'
      : `σ = ${formatFraction(s.sigma, 2)} frente al límite de ${formatFraction(s.sigma_max, 2)}`
  const rows: ScoreBreakdownProps['rows'] = [
    { label: 'Retorno esperado', note: `Σ pesos × μ ajustado = ${formatFraction(s.expected_return, 2)}`, value: clean(s.return_term) },
    { label: 'Ajuste por contexto', note: 'Σ pesos × ajuste cᵢ', value: clean(s.context_term) },
    { label: 'Penalización por riesgo', note: `λ efectiva × σ del portafolio, con σ = ${formatFraction(s.sigma, 2)}`, value: clean(s.risk_term) },
    { label: 'Penalización por exceso de volatilidad', note: volatility, value: clean(s.penalty_term) },
    {
      label: 'Recompensa difusa',
      note: s.membership_at_c == null ? 'Difuso apagado' : `Pertenencia μ_CA(c) = ${s.membership_at_c.toFixed(2)}`,
      value: clean(s.fuzzy_reward),
    },
  ]
  if (s.strict_total != null) {
    rows.push({
      label: 'Referencia informe v1.1 (estricta)',
      note: 'Fitness §5.2 sin kappa ni gen c, con CA Sugeno',
      value: clean(s.strict_total),
    })
  }
  return { total: clean(s.total), rows }
}

export function toTechnical(t: TechnicalOut): TechnicalData {
  const a = t.absorption
  return {
    params: t.params.map((p) => ({
      categoryId: p.category as AllocationItem['categoryId'],
      name: p.name,
      mu: p.mu,
      sigma: p.sigma,
      muAdj: p.mu_adj,
      sigmaAdj: p.sigma_adj,
      contextAdj: p.context_adj,
      source: p.source,
    })),
    lambdaBase: t.lambda_base,
    mH: t.m_h,
    lambdaEff: t.lambda_eff,
    membership: toMembership(t),
    absorption: {
      curve: a.points,
      c: a.c,
      centroid: a.centroid,
      membershipAtC: a.membership_at_c ?? 0,
      r: a.r,
      e: a.e,
      assumed: a.assumed,
      sugenoCa: a.sugeno_ca ?? null,
      sugenoSigmaMax: a.sugeno_sigma_max ?? null,
    },
    rules: toRules(t),
    score: toScore(t),
    convergence: { values: t.convergence.best },
  }
}

export type ResultData = Pick<
  ResultScreenProps,
  'summary' | 'total' | 'allocation' | 'assumptions' | 'explanation' | 'technical' | 'switches'
>

export function toResult(res: RecommendResponse): ResultData {
  return {
    summary: toSummary(res),
    total: res.amount,
    allocation: toAllocation(res),
    assumptions: res.assumptions,
    explanation: {
      paragraphs: res.explanation.paragraphs,
      scenarios: res.explanation.scenarios.map((s) => ({ label: s.label, text: s.text, amount: s.amount })),
    },
    technical: toTechnical(res.technical),
    switches: { fuzzy: res.switches.fuzzy, context: res.switches.context },
  }
}

// ------------------------------------------------------------------ context

export function levelFromValue(value: number): ContextLevel {
  return value < 0 ? 'adverse' : value > 0 ? 'favorable' : 'neutral'
}

export function valueFromLevel(level: ContextLevel): number {
  return level === 'adverse' ? -1 : level === 'favorable' ? 1 : 0
}

/** Factors with the current selection; `context = null` means not informed (neutral defaults). */
export function toFactors(defaults: ContextDefaultsResponse, context: ContextIn | null): Factor[] {
  return defaults.factors.map((f) => ({
    id: f.id,
    label: f.label,
    description: f.description,
    value: levelFromValue(context?.[f.id] ?? f.value),
  }))
}
