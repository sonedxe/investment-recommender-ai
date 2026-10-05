import { describe, expect, it } from 'vitest'
import { fixtures } from './__fixtures__'
import {
  answerContent,
  canSkip,
  levelFromValue,
  questionProgress,
  toAllocation,
  toFactors,
  toQuestion,
  toResult,
  toSummary,
  toTechnical,
  toUnderstood,
  valueFromLevel,
} from './mappers'

const byKey = (items: ReturnType<typeof toUnderstood>) => Object.fromEntries(items.map((i) => [i.key, i]))

describe('interpretation mappers', () => {
  it('maps the understood data with states, labels and evidence notes', () => {
    const rows = byKey(toUnderstood(fixtures.interpretAmount()))
    expect(rows.amount).toEqual({ key: 'amount', label: 'Monto a invertir', value: null, state: 'asked' })
    expect(rows.risk).toMatchObject({ label: 'Tolerancia al riesgo', value: 'Baja', state: 'understood', note: 'Dijiste: “sin arriesgar mucho”' })
    expect(rows.horizon).toMatchObject({ label: 'Horizonte', value: null, state: 'missing', note: undefined })
    expect(rows.savings).toMatchObject({ label: 'Ahorro total', state: 'missing', note: 'Opcional' })
    expect(rows.emergency).toMatchObject({ label: 'Fondo de emergencia', state: 'missing', note: 'Opcional' })
  })

  it('formats understood values and marks the asked absorption field', () => {
    const rows = byKey(toUnderstood(fixtures.interpretAbsorption()))
    expect(rows.amount.value).toBe('S/ 5,000.00')
    expect(rows.horizon.value).toBe('3 años')
    expect(rows.savings.value).toBe('S/ 20,000.00')
    expect(rows.emergency.state).toBe('asked')
  })

  it('marks a declined absorption field as assumed', () => {
    const rows = byKey(toUnderstood(fixtures.interpretRefusal()))
    expect(rows.emergency).toMatchObject({ value: 'No informado', state: 'assumed', note: 'Capacidad media' })
    expect(rows.savings.state).toBe('understood')
  })

  it('shows a qualitative horizon and an informed emergency fund', () => {
    const res = fixtures.interpretRefusal()
    res.profile.horizon_years = null
    res.profile.horizon_label = 'largo'
    res.profile.emergency_months = 4
    res.rejected = []
    const rows = byKey(toUnderstood(res))
    expect(rows.horizon.value).toBe('Largo plazo')
    expect(rows.emergency).toMatchObject({ value: '4 meses', state: 'understood' })
  })

  it('maps a free amount question with the S/ prefix', () => {
    const q = toQuestion(fixtures.interpretAmount().question!)
    expect(q).toEqual({
      question: '¿Cuánto dinero quieres invertir, en soles?',
      hint: 'Por ejemplo: S/ 3,000.',
      freeInput: { label: 'Monto a invertir', prefix: 'S/' },
    })
  })

  it('maps the risk question to its five options without free input', () => {
    const q = toQuestion(fixtures.interpretRisk().question!)
    expect(q.options?.map((o) => o.value)).toEqual(['muy_conservador', 'conservador', 'moderado', 'agresivo', 'muy_agresivo'])
    expect(q.options?.[1].label).toBe('Incómodo: prefiero ir a lo seguro')
    expect(q.freeInput).toBeUndefined()
  })

  it('maps the absorption question with its unit', () => {
    const q = toQuestion(fixtures.interpretAbsorption().question!)
    expect(q.freeInput).toEqual({ label: 'Meses que podrías cubrir', unit: 'meses' })
  })

  it('builds the user turn from an option label or a number with its unit', () => {
    expect(answerContent(fixtures.interpretRisk().question!, 'conservador')).toBe('Incómodo: prefiero ir a lo seguro')
    expect(answerContent(fixtures.interpretAmount().question!, ' 5000 ')).toBe('S/ 5000')
    expect(answerContent(fixtures.interpretAbsorption().question!, '4')).toBe('4 meses')
  })

  it('offers a skip only for absorption fields, never for the horizon', () => {
    expect(canSkip(fixtures.interpretAbsorption().question!)).toBe(true)
    expect(canSkip(fixtures.interpretAmount().question!)).toBe(false)
    expect(canSkip(fixtures.interpretRisk().question!)).toBe(false)
    expect(canSkip({ ...fixtures.interpretAmount().question!, field: 'horizonte' })).toBe(false)
  })

  it('counts the question progress', () => {
    expect(questionProgress(fixtures.interpretAmount(), ['monto_invertir'])).toEqual({ step: 1, totalSteps: 4 })
    expect(questionProgress(fixtures.interpretAbsorption(), ['cobertura_emergencia_meses'])).toEqual({ step: 1, totalSteps: 1 })
    expect(questionProgress(fixtures.interpretRisk(), ['horizonte', 'perfil_riesgo'])).toEqual({ step: 2, totalSteps: 4 })
  })
})

describe('recommendation mappers', () => {
  it('maps the allocation: pct = weight × 100 and amounts as returned', () => {
    const res = fixtures.recommendNeutral()
    const items = toAllocation(res)
    expect(items.map((i) => i.categoryId)).toEqual(['stocks', 'mixed', 'debt', 'bonds', 'term'])
    items.forEach((item, i) => {
      expect(item.pct).toBeCloseTo(res.allocation[i].weight * 100, 10)
      expect(item.amount).toBe(res.allocation[i].amount)
      expect(item.name).toBe(res.allocation[i].name)
      expect(item.note).toBeTruthy()
    })
    expect(items.reduce((s, i) => s + i.pct, 0)).toBeCloseTo(100, 6)
    expect(items.reduce((s, i) => s + i.amount, 0)).toBeCloseTo(res.amount, 2)
  })

  it('keeps the totals for every captured result', () => {
    for (const res of [fixtures.recommendAdverse(), fixtures.recommendSwitchesOff(), fixtures.recommendInformed()]) {
      const items = toAllocation(res)
      expect(items.reduce((s, i) => s + i.pct, 0)).toBeCloseTo(100, 6)
      expect(items.reduce((s, i) => s + i.amount, 0)).toBeCloseTo(res.amount, 2)
    }
  })

  it('maps the result screen data', () => {
    const res = fixtures.recommendNeutral()
    const data = toResult(res)
    expect(data.summary).toBe(
      'Pensando en tus S/ 5,000.00, en unos 3 años y con poca tolerancia al riesgo, esta es una forma de repartirlos.',
    )
    expect(data.total).toBe(5000)
    expect(data.assumptions).toEqual(res.assumptions)
    expect(data.explanation.paragraphs).toEqual(res.explanation.paragraphs)
    expect(data.explanation.scenarios).toEqual(res.explanation.scenarios)
    expect(data.switches).toEqual({ fuzzy: true, context: true })
  })

  it('builds the summary for a qualitative or one-year horizon', () => {
    const res = fixtures.recommendNeutral()
    res.profile.horizon_years = null
    res.profile.horizon_label = 'corto'
    res.profile.risk_profile = 'muy_agresivo'
    expect(toSummary(res)).toBe(
      'Pensando en tus S/ 5,000.00, a corto plazo y con mucha tolerancia al riesgo, esta es una forma de repartirlos.',
    )
    res.profile.horizon_label = null
    res.profile.horizon_years = 1
    expect(toSummary(res)).toContain('en un año y')
  })

  it('maps the technical parameters and lambda', () => {
    const t = toTechnical(fixtures.recommendNeutral().technical)
    expect(t.params[0]).toEqual({
      categoryId: 'stocks',
      name: 'Fondos de acciones',
      mu: 0.11883669180994297,
      sigma: 0.2170544859144262,
      muAdj: 0.13883669180994296,
      sigmaAdj: 0.2170544859144262,
      contextAdj: 0.02,
      source: 'data',
    })
    // W15: every category is data-backed (mixed is the SBS AFP Fondo 2 index).
    expect(t.params.map((p) => p.source)).toEqual(['data', 'data', 'data', 'data', 'data'])
    expect([t.lambdaBase, t.mH, t.lambdaEff]).toEqual([2, 1, 2])
  })

  it('maps the horizon membership series and the user value', () => {
    const raw = fixtures.recommendNeutral().technical
    const m = toTechnical(raw).membership
    expect(m.series.map((s) => [s.id, s.name])).toEqual([['corto', 'Corto'], ['mediano', 'Mediano'], ['largo', 'Largo']])
    expect(m.series[0].points).toEqual(raw.horizon.curves[0].points)
    expect(m.value).toBe(3)
    expect(m.domain).toEqual([0, 15])
  })

  it('uses the plateau centre of a qualitative horizon', () => {
    const raw = fixtures.recommendNeutral().technical
    raw.horizon.years = null
    raw.horizon.label = 'largo'
    const top = raw.horizon.curves[2].points.filter((p) => p.y >= 1)
    expect(toTechnical(raw).membership.value).toBe((top[0].x + top[top.length - 1].x) / 2)
  })

  it('maps the absorption chart with an assumed capacity', () => {
    const raw = fixtures.recommendNeutral().technical
    const a = toTechnical(raw).absorption
    expect(a.curve).toEqual(raw.absorption.points)
    expect(a).toMatchObject({
      c: raw.absorption.c,
      centroid: raw.absorption.centroid,
      membershipAtC: raw.absorption.membership_at_c,
      r: null,
      e: null,
      assumed: true,
    })
  })

  it('maps informed absorption inputs and their rule activations', () => {
    const t = toTechnical(fixtures.recommendInformed().technical)
    expect(t.absorption).toMatchObject({ r: 0.25, e: 4, assumed: false, membershipAtC: 0.5 })
    expect(t.rules.find((r) => r.id === 'RA2')?.activation).toBe(0.5)
  })

  it('maps the rules with kind, activation, condition and effect', () => {
    const t = toTechnical(fixtures.recommendNeutral().technical)
    expect(t.rules.find((r) => r.id === 'RH2')).toEqual({
      id: 'RH2',
      kind: 'horizon',
      name: '',
      condition: 'Si el horizonte es mediano',
      effect: 'm_H = 1.0 (cautela base)',
      activation: 0.3333333333333333,
    })
    expect(t.rules.find((r) => r.id === 'RA1')).toMatchObject({ kind: 'absorption', activation: null })
    expect(t.rules.find((r) => r.id === 'RC1')).toMatchObject({ kind: 'context', activation: null })
    const adverse = toTechnical(fixtures.recommendAdverse().technical)
    expect(adverse.rules.find((r) => r.id === 'RC3')?.condition).toBe('Panorama político adverso (s_pol < 0)')
    expect(adverse.params[0].contextAdj).not.toBe(t.params[0].contextAdj)
  })

  it('maps the score rows from the breakdown and the convergence values', () => {
    const raw = fixtures.recommendNeutral().technical
    const t = toTechnical(raw)
    expect(t.score.rows.map((r) => r.label)).toEqual([
      'Retorno esperado',
      'Ajuste por contexto',
      'Penalización por riesgo',
      'Penalización por exceso de volatilidad',
      'Recompensa difusa',
    ])
    const s = raw.score
    expect(t.score.rows.map((r) => r.value)).toEqual([s.return_term, s.context_term, s.risk_term, 0, s.fuzzy_reward])
    expect(Object.is(t.score.rows[3].value, -0)).toBe(false)
    expect(t.score.total).toBe(s.total)
    expect(t.score.rows[4].note).toBe('Pertenencia μ_CA(c) = 1.00')
    expect(t.score.rows[3].note).toBe('σ = 1.82 % frente al límite de 9.50 %')
    // The fitness risk term is λ_ef · σ (not ½ · λ · σ²).
    expect(t.score.rows[2].note).toBe('λ efectiva × σ del portafolio, con σ = 1.82 %')
    expect(t.convergence.values).toEqual(raw.convergence.best)
  })

  it('maps a result with the switches off', () => {
    const res = fixtures.recommendSwitchesOff()
    const data = toResult(res)
    expect(data.switches).toEqual({ fuzzy: false, context: false })
    expect(data.technical.absorption.membershipAtC).toBe(0)
    expect(data.technical.score.rows[4].note).toBe('Difuso apagado')
    expect(data.technical.score.rows[3].note).toBe('Sin límite de volatilidad (difuso apagado)')
    expect(data.technical.rules.filter((r) => r.kind !== 'context').every((r) => r.activation === null)).toBe(true)
  })
})

describe('context mappers', () => {
  it('maps the factor defaults and the current selection', () => {
    const defaults = fixtures.contextDefaults()
    expect(toFactors(defaults, null)).toEqual([
      { id: 'political', label: 'Panorama político', description: defaults.factors[0].description, value: 'neutral' },
      { id: 'macro', label: 'Estabilidad macroeconómica', description: defaults.factors[1].description, value: 'neutral' },
    ])
    expect(toFactors(defaults, { political: -1, macro: 1 }).map((f) => f.value)).toEqual(['adverse', 'favorable'])
  })

  it('converts levels and values both ways', () => {
    for (const level of ['adverse', 'neutral', 'favorable'] as const) expect(levelFromValue(valueFromLevel(level))).toBe(level)
    expect(levelFromValue(-0.5)).toBe('adverse')
  })
})
