// Example data ported from the design system (`window.InvestWise.sample`), updated for adjustments A1–A5.
// Coherent with the brief: S/ 5,000 out of S/ 20,000 of savings, 3-year horizon, low tolerance.
// For visual checks and tests only; not real recommendations.
import { CATEGORIES } from '../lib/format'
import type {
  AbsorptionChartProps,
  AllocationItem,
  CategoryId,
  ConvergenceChartProps,
  ExplanationTextProps,
  Factor,
  LoadingStep,
  MembershipChartProps,
  ParamRow,
  Point,
  Question,
  Rule,
  ScoreBreakdownProps,
  TechnicalData,
  UnderstoodItem,
} from '../types/ui'

const NOTES: Record<CategoryId, string> = {
  stocks: 'Pueden crecer más y también bajar más.',
  mixed: 'Combinan acciones y deuda.',
  debt: 'Prestan a empresas; bajas moderadas.',
  bonds: 'Préstamos al Estado peruano.',
  term: 'Monto y plazo acordados con el banco.',
}

/** Percentages in category order; amounts are pct × S/ 50 (S/ 5,000 total). */
function allocation(pcts: number[]): AllocationItem[] {
  return CATEGORIES.map((c, i) => ({ categoryId: c.id, name: c.name, pct: pcts[i], amount: pcts[i] * 50, note: NOTES[c.id] }))
}

// Aggregated absorption set: Baja clipped at 0.67 and Media clipped at 0.33 (max–min inference).
function triangle(a: number, b: number, c: number) {
  return (x: number) => (x <= a || x >= c ? 0 : x <= b ? (x - a) / (b - a) : (c - x) / (c - b))
}
function trapezoid(a: number, b: number, c: number, d: number) {
  return (x: number) => (x < a || x > d ? 0 : x < b ? (x - a) / (b - a) : x <= c ? 1 : (d - x) / (d - c))
}
function absorptionCurve(): { curve: Point[]; centroid: number } {
  const low = trapezoid(0, 0, 0.2, 0.5)
  const mid = triangle(0.25, 0.5, 0.75)
  const curve: Point[] = []
  let sumY = 0
  let sumXY = 0
  for (let i = 0; i <= 100; i++) {
    const x = i / 100
    const y = Math.max(Math.min(low(x), 0.67), Math.min(mid(x), 0.33))
    curve.push({ x, y: Math.round(y * 1000) / 1000 })
    sumY += y
    sumXY += x * y
  }
  return { curve, centroid: Math.round((sumXY / sumY) * 100) / 100 }
}

function convergenceValues(): number[] {
  const values: number[] = []
  for (let g = 0; g < 100; g++) values.push(Math.round((0.0566 - 0.0254 * Math.exp(-g / 16)) * 10000) / 10000)
  values[99] = 0.0566
  return values
}

const politics = {
  id: 'politics',
  label: 'Panorama político',
  description: 'Cómo supones que será el entorno político del país en los próximos años.',
}
const macro = {
  id: 'macro',
  label: 'Estabilidad macroeconómica',
  description: 'Inflación, tipo de cambio y crecimiento de la economía.',
}

const params: ParamRow[] = [
  { categoryId: 'stocks', mu: 0.09, sigma: 0.22, muAdj: 0.09, sigmaAdj: 0.22, contextAdj: 0, source: 'data' },
  { categoryId: 'mixed', mu: 0.07, sigma: 0.12, muAdj: 0.07, sigmaAdj: 0.12, contextAdj: 0, source: 'data' },
  { categoryId: 'debt', mu: 0.052, sigma: 0.04, muAdj: 0.052, sigmaAdj: 0.04, contextAdj: 0, source: 'data' },
  { categoryId: 'bonds', mu: 0.06, sigma: 0.07, muAdj: 0.06, sigmaAdj: 0.07, contextAdj: 0, source: 'prior' },
  { categoryId: 'term', mu: 0.04, sigma: 0.005, muAdj: 0.04, sigmaAdj: 0.005, contextAdj: 0, source: 'prior' },
]

const paramsAdverse: ParamRow[] = [
  { categoryId: 'stocks', mu: 0.09, sigma: 0.22, muAdj: 0.075, sigmaAdj: 0.26, contextAdj: -0.015, source: 'data' },
  { categoryId: 'mixed', mu: 0.07, sigma: 0.12, muAdj: 0.062, sigmaAdj: 0.135, contextAdj: -0.008, source: 'data' },
  { categoryId: 'debt', mu: 0.052, sigma: 0.04, muAdj: 0.05, sigmaAdj: 0.045, contextAdj: -0.002, source: 'data' },
  { categoryId: 'bonds', mu: 0.06, sigma: 0.07, muAdj: 0.056, sigmaAdj: 0.08, contextAdj: -0.004, source: 'prior' },
  { categoryId: 'term', mu: 0.04, sigma: 0.005, muAdj: 0.04, sigmaAdj: 0.005, contextAdj: 0, source: 'prior' },
]

const membership: MembershipChartProps = {
  domain: [0, 15],
  value: 3,
  series: [
    { id: 'short', name: 'Corto', points: [{ x: 0, y: 1 }, { x: 2, y: 1 }, { x: 5, y: 0 }, { x: 15, y: 0 }] },
    {
      id: 'medium',
      name: 'Mediano',
      points: [{ x: 0, y: 0 }, { x: 2, y: 0 }, { x: 5, y: 1 }, { x: 9, y: 0 }, { x: 15, y: 0 }],
    },
    { id: 'long', name: 'Largo', points: [{ x: 0, y: 0 }, { x: 5, y: 0 }, { x: 9, y: 1 }, { x: 15, y: 1 }] },
  ],
}

const { curve, centroid } = absorptionCurve()
// r = 5,000 / 20,000; the emergency fund was not mentioned in the example input.
const absorption: AbsorptionChartProps = { curve, c: 0.28, centroid, membershipAtC: 0.67, r: 0.25, e: null, assumed: false }

const rules: Rule[] = [
  {
    id: 'RH1',
    kind: 'horizon',
    activation: 0.67,
    name: 'Horizonte corto',
    condition: 'Pertenencia a Corto = 0.67',
    effect: 'λ efectiva = 4.00 × (1 + 0.50 × 0.67) = 5.34',
  },
  {
    id: 'RA1',
    kind: 'absorption',
    activation: 0.67,
    name: 'Riesgo bajo y horizonte corto',
    condition: 'Tolerancia Baja y Corto = 0.67',
    effect: 'Conjunto Baja recortado en 0.67',
  },
  {
    id: 'RA2',
    kind: 'absorption',
    activation: 0.33,
    name: 'Horizonte mediano',
    condition: 'Pertenencia a Mediano = 0.33',
    effect: 'Conjunto Media recortado en 0.33',
  },
  {
    id: 'RC1',
    kind: 'context',
    activation: null,
    name: 'Contexto neutral',
    condition: 'Panorama político y macro = Neutral',
    effect: 'Δμ = 0.0 %; Δσ = 0.0 % (sin ajuste)',
  },
]

const score: ScoreBreakdownProps = {
  total: 0.0566,
  rows: [
    { label: 'Retorno esperado', note: 'Σ pesos × μ ajustado = 5.50 %', value: 0.055 },
    { label: 'Ajuste por contexto', note: 'Contexto neutral: sin ajuste', value: 0 },
    { label: 'Penalización por riesgo', note: '½ × λ efectiva × σ² = ½ × 5.34 × 0.041²', value: -0.0045 },
    { label: 'Penalización por exceso de volatilidad', note: 'σ = 4.1 % ≤ límite de 5.0 %', value: 0 },
    { label: 'Recompensa difusa', note: '0.0091 × pertenencia(c = 0.28) = 0.0091 × 0.67', value: 0.0061 },
  ],
}

const convergence: ConvergenceChartProps = { values: convergenceValues() }

const question: Question = {
  question: '¿Por cuánto tiempo aproximadamente no necesitarías este dinero?',
  hint: 'Un cálculo aproximado es suficiente.',
  options: [
    { value: 'lt1', label: 'Menos de 1 año' },
    { value: '1-3', label: 'Entre 1 y 3 años' },
    { value: '3-5', label: 'Entre 3 y 5 años' },
    { value: 'gt5', label: 'Más de 5 años' },
  ],
  freeInput: { label: 'O escribe los años', unit: 'años', placeholder: '3' },
}

const questionSavings: Question = {
  question: '¿Cuánto tienes ahorrado en total, aproximadamente?',
  hint: 'Nos ayuda a estimar cuánta baja podrías soportar. Si prefieres no decirlo, continuamos con un supuesto.',
  freeInput: { label: 'Ahorro total', prefix: 'S/', placeholder: '20,000' },
}

const understoodAsk: UnderstoodItem[] = [
  { key: 'amount', label: 'Monto a invertir', value: 'S/ 5,000.00', state: 'understood' },
  { key: 'risk', label: 'Tolerancia al riesgo', value: 'Baja', state: 'understood', note: 'Dijiste: “no me gusta arriesgar”' },
  { key: 'horizon', label: 'Horizonte', value: null, state: 'asked' },
  { key: 'savings', label: 'Ahorro total', value: null, state: 'missing', note: 'Opcional' },
  { key: 'emergency', label: 'Fondo de emergencia', value: null, state: 'missing', note: 'Opcional' },
]

const understoodAssume: UnderstoodItem[] = [
  { key: 'amount', label: 'Monto a invertir', value: 'S/ 5,000.00', state: 'understood' },
  { key: 'risk', label: 'Tolerancia al riesgo', value: 'Baja', state: 'understood' },
  { key: 'horizon', label: 'Horizonte', value: '3 años', state: 'understood' },
  { key: 'savings', label: 'Ahorro total', value: 'No informado', state: 'assumed', note: 'Capacidad media' },
  { key: 'emergency', label: 'Fondo de emergencia', value: 'No informado', state: 'assumed', note: 'Capacidad media' },
]

const explanation: ExplanationTextProps = {
  paragraphs: [
    'Con S/ 5,000.00 y un plazo de unos 3 años, esta distribución prioriza la seguridad: el 55 % está en depósito a plazo fijo y bonos soberanos, donde el valor casi no baja.',
    'Otro 25 % está en fondos de deuda, que suelen rendir algo más que un depósito pero pueden tener pequeñas bajas de un mes a otro.',
    'Solo el 20 % se reparte entre fondos mixtos (15 %) y fondos de acciones (5 %). Son los que más pueden crecer y también los que más pueden bajar.',
    'Dijiste que no te gusta arriesgar y que no necesitarás el dinero por unos 3 años. Por eso la parte en acciones es pequeña.',
    'Es un ejemplo de cálculo, no una promesa. Los montos de abajo son estimaciones para un año.',
  ],
  scenarios: [
    { label: 'Un año favorable', text: 'Tu inversión podría crecer hasta', amount: 520 },
    { label: 'Un año esperado', text: 'Crecimiento promedio estimado', amount: 275 },
    { label: 'Un año malo', text: 'Tu inversión podría bajar hasta', amount: -400 },
  ],
}

const factors: Factor[] = [
  { ...politics, value: 'neutral' },
  { ...macro, value: 'neutral' },
]
const factorsAdverse: Factor[] = [
  { ...politics, value: 'adverse' },
  { ...macro, value: 'neutral' },
]

const loadingSteps: LoadingStep[] = [
  { label: 'Interpretando tu situación', state: 'done' },
  { label: 'Evaluando combinaciones de inversión', state: 'active' },
  { label: 'Redactando la explicación', state: 'pending' },
]

// m_H = 1 + 0.50 × 0.67 = 1.335, so λ_ef = 4.00 × 1.335 = 5.34.
const technical: TechnicalData = {
  params,
  lambdaBase: 4.0,
  mH: 1.335,
  lambdaEff: 5.34,
  membership,
  absorption,
  rules,
  score,
  convergence,
}

export const sample = {
  categories: CATEGORIES,
  exampleInput:
    'Tengo S/ 5,000 de mis S/ 20,000 de ahorro, no me gusta arriesgar y no los voy a necesitar en unos 3 años',
  summary:
    'Pensando en tus S/ 5,000.00, en unos 3 años y con poca tolerancia al riesgo, esta es una forma de repartirlos.',
  total: 5000,
  allocation: allocation([5, 15, 25, 25, 30]),
  allocationAdverse: allocation([3, 12, 25, 28, 32]),
  understoodAsk,
  understoodAssume,
  question,
  questionSavings,
  assumptionText: 'Asumimos una capacidad media para asumir pérdidas.',
  explanation,
  assumptions: [
    'Se asumió un panorama político neutral.',
    'Se asumió una estabilidad macroeconómica neutral.',
    'Los retornos y riesgos de cada categoría son valores de referencia, no garantías.',
  ],
  factors,
  factorsAdverse,
  params,
  paramsAdverse,
  membership,
  absorption,
  rules,
  score,
  convergence,
  loadingSteps,
  technical,
  emptyInputError: {
    title: 'No pudimos interpretar tu texto',
    text: 'Cuéntanos al menos cuánto dinero quieres invertir. Por ejemplo: Tengo S/ 5,000 y no me gusta arriesgar.',
  },
  serviceErrorText:
    'No pudimos conectar con el servicio. Tu texto se conservó; vuelve a intentarlo en unos segundos.',
}
