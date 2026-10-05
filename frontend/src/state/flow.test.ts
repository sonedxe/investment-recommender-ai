import { describe, expect, it } from 'vitest'
import { fixtures } from '../api/__fixtures__'
import type { RecommendRequest } from '../api/types'
import { askedFields, flowReducer, initialFlowState, isNeutral, type FlowEvent, type FlowState } from './flow'

const TEXT = 'Tengo S/ 5000 de mis S/ 20000 de ahorro, no me gusta arriesgar y no los necesito en unos 3 años'

function run(state: FlowState, ...events: FlowEvent[]): FlowState {
  return events.reduce(flowReducer, state)
}
const reqId = (s: FlowState) => s.request?.id ?? -1
const body = (s: FlowState) => (s.request?.kind === 'recommend' ? s.request.body : null) as RecommendRequest

function submitted(): FlowState {
  return run(initialFlowState, { type: 'textChanged', text: TEXT }, { type: 'submitted' })
}
function clarifying(): FlowState {
  const s = submitted()
  return flowReducer(s, { type: 'interpreted', id: reqId(s), response: fixtures.interpretAbsorption() })
}
function assuming(): FlowState {
  const s = flowReducer(clarifying(), { type: 'answered', content: 'Prefiero no responder' })
  return flowReducer(s, { type: 'interpreted', id: reqId(s), response: fixtures.interpretRefusal() })
}
function result(): FlowState {
  const s = flowReducer(assuming(), { type: 'assumptionConfirmed' })
  return flowReducer(s, { type: 'recommended', id: reqId(s), response: fixtures.recommendNeutral() })
}
function inContext(): FlowState {
  return flowReducer(result(), { type: 'contextOpened' })
}

describe('flow reducer: input', () => {
  it('keeps the typed text', () => {
    expect(flowReducer(initialFlowState, { type: 'textChanged', text: 'hola' }).text).toBe('hola')
  })

  it('flags an empty submission without requesting', () => {
    const s = run(initialFlowState, { type: 'textChanged', text: '   ' }, { type: 'submitted' })
    expect([s.phase, s.error, s.request]).toEqual(['input', { kind: 'empty' }, null])
    expect(flowReducer(s, { type: 'textChanged', text: 'Tengo' }).error).toBeNull()
  })

  it('input -> interpreting with the first user turn', () => {
    const s = submitted()
    expect(s.phase).toBe('interpreting')
    expect(s.request).toEqual({ id: 1, kind: 'interpret', conversation: [{ role: 'user', content: TEXT }] })
  })
})

describe('flow reducer: interpretation', () => {
  it('interpreting -> clarifying appends the assistant turn with its field', () => {
    const s = clarifying()
    expect(s.phase).toBe('clarifying')
    expect(s.conversation[1]).toMatchObject({ role: 'assistant', field: 'cobertura_emergencia_meses' })
    expect(askedFields(s.conversation)).toEqual(['cobertura_emergencia_meses'])
    expect([s.offline, s.request]).toEqual([true, null])
  })

  it('ignores a stale response', () => {
    const s = submitted()
    expect(flowReducer(s, { type: 'interpreted', id: 99, response: fixtures.interpretAbsorption() })).toBe(s)
  })

  it('clarifying -> interpreting sends the whole conversation with the answer', () => {
    const s = flowReducer(clarifying(), { type: 'answered', content: '4 meses' })
    expect(s.phase).toBe('interpreting')
    expect(s.request?.kind === 'interpret' && s.request.conversation.map((t) => t.role)).toEqual(['user', 'assistant', 'user'])
    expect(flowReducer(clarifying(), { type: 'answered', content: '  ' }).phase).toBe('clarifying')
  })

  it('complete with an assumption stays in clarifying until confirmed', () => {
    const s = assuming()
    expect([s.phase, s.request]).toEqual(['clarifying', null])
    expect(s.profile).toEqual({ amount: 5000, risk_profile: 'conservador', horizon_years: 3, total_savings: 20000 })
    const next = flowReducer(s, { type: 'assumptionConfirmed' })
    expect(next.phase).toBe('calculating')
    expect(body(next)).toEqual({ profile: s.profile, switches: { fuzzy: true, context: true } })
  })

  it('complete without assumptions goes straight to calculating', () => {
    const s = submitted()
    const response = { ...fixtures.interpretRefusal(), assumptions: [] }
    expect(flowReducer(s, { type: 'interpreted', id: reqId(s), response }).phase).toBe('calculating')
  })

  it('a complete response without a usable profile is a validation error', () => {
    const s = submitted()
    const response = fixtures.interpretRefusal()
    response.profile.amount = null
    const next = flowReducer(s, { type: 'interpreted', id: reqId(s), response })
    expect([next.phase, next.error?.kind]).toEqual(['input', 'validation'])
  })
})

describe('flow reducer: calculation and recalculation', () => {
  it('calculating -> result keeps the seed and the neutral baseline', () => {
    const s = result()
    expect(s.phase).toBe('result')
    expect(s.seed).toBe(42)
    expect(s.baseline).toBe(s.recommendation)
  })

  it('switches change -> recalculation with the same seed, screen stays', () => {
    const s = flowReducer(result(), { type: 'switchesChanged', switches: { fuzzy: false, context: false } })
    expect([s.phase, body(s).seed, body(s).switches]).toEqual(['result', 42, { fuzzy: false, context: false }])
    const done = flowReducer(s, { type: 'recommended', id: reqId(s), response: fixtures.recommendSwitchesOff() })
    expect([done.phase, done.switches, done.request]).toEqual(['result', { fuzzy: false, context: false }, null])
  })

  it('result <-> context', () => {
    expect(inContext().phase).toBe('context')
    expect(flowReducer(inContext(), { type: 'contextClosed' }).phase).toBe('result')
  })

  it('factor change -> recalculation with the context and the same seed', () => {
    const s = flowReducer(inContext(), { type: 'factorChanged', id: 'political', value: -1 })
    expect([s.phase, body(s).context, body(s).seed]).toEqual(['context', { political: -1, macro: 0 }, 42])
    const done = flowReducer(s, { type: 'recommended', id: reqId(s), response: fixtures.recommendAdverse() })
    expect(done.appliedContext).toEqual({ political: -1, macro: 0 })
    expect(done.baseline?.allocation).toEqual(fixtures.recommendNeutral().allocation)
    expect(done.recommendation?.allocation).toEqual(fixtures.recommendAdverse().allocation)
    expect(isNeutral(done.appliedContext)).toBe(false)
  })

  it('reset to neutral reuses the baseline without a request', () => {
    let s = flowReducer(inContext(), { type: 'factorChanged', id: 'macro', value: 1 })
    s = flowReducer(s, { type: 'recommended', id: reqId(s), response: fixtures.recommendAdverse() })
    s = flowReducer(s, { type: 'contextReset' })
    expect([s.context, s.request, s.recommendation]).toEqual([null, null, s.baseline])
  })

  it('reset with different switches requests a neutral recalculation', () => {
    const off = { fuzzy: false, context: true }
    let s = flowReducer(inContext(), { type: 'factorChanged', id: 'political', value: -1 })
    s = flowReducer(s, { type: 'recommended', id: reqId(s), response: fixtures.recommendAdverse() })
    s = run(s, { type: 'contextClosed' }, { type: 'switchesChanged', switches: off })
    expect(body(s).context).toEqual({ political: -1, macro: 0 })
    s = flowReducer(s, { type: 'recommended', id: reqId(s), response: { ...fixtures.recommendAdverse(), switches: off } })
    expect(s.baseline?.switches).toEqual({ fuzzy: true, context: true })
    s = run(s, { type: 'contextOpened' }, { type: 'contextReset' })
    expect(s.request?.kind).toBe('recommend')
    expect(body(s).context).toBeUndefined()
    expect(body(s).switches).toEqual(off)
  })
})

describe('flow reducer: errors', () => {
  it('a failed interpretation returns to input keeping the text; retry repeats the request', () => {
    const sent = submitted()
    const failed = flowReducer(sent, { type: 'failed', id: reqId(sent), error: { kind: 'network' } })
    expect([failed.phase, failed.text, failed.error]).toEqual(['input', TEXT, { kind: 'network' }])
    const retried = flowReducer(failed, { type: 'retried' })
    expect(retried.phase).toBe('interpreting')
    expect(retried.request?.kind === 'interpret' && retried.request.conversation).toEqual([{ role: 'user', content: TEXT }])
    expect(retried.request?.id).not.toBe(sent.request?.id)
    expect(retried.error).toBeNull()
  })

  it('a failed answer returns to clarifying without committing the answer', () => {
    const sent = flowReducer(clarifying(), { type: 'answered', content: '4 meses' })
    const failed = flowReducer(sent, { type: 'failed', id: reqId(sent), error: { kind: 'http', status: 500 } })
    expect([failed.phase, failed.conversation.length]).toEqual(['clarifying', 2])
    expect(flowReducer(failed, { type: 'errorDismissed' }).phase).toBe('clarifying')
  })

  it('a failed first calculation retries in calculating', () => {
    const sent = flowReducer(assuming(), { type: 'assumptionConfirmed' })
    const failed = flowReducer(sent, { type: 'failed', id: reqId(sent), error: { kind: 'network' } })
    expect(failed.phase).toBe('input')
    expect(flowReducer(failed, { type: 'retried' }).phase).toBe('calculating')
  })

  it('a failed recalculation keeps the result; dismiss restores the applied selection', () => {
    const sent = flowReducer(inContext(), { type: 'factorChanged', id: 'political', value: 1 })
    const failed = flowReducer(sent, { type: 'failed', id: reqId(sent), error: { kind: 'validation', message: 'x' } })
    expect([failed.phase, failed.recommendation]).toEqual(['context', sent.recommendation])
    expect(flowReducer(failed, { type: 'retried' }).phase).toBe('context')
    expect(flowReducer(failed, { type: 'errorDismissed' }).context).toBeNull()
  })

  it('ignores events that do not apply to the phase', () => {
    const s = submitted()
    for (const e of [
      { type: 'submitted' },
      { type: 'answered', content: 'x' },
      { type: 'assumptionConfirmed' },
      { type: 'retried' },
      { type: 'errorDismissed' },
      { type: 'contextOpened' },
      { type: 'contextClosed' },
      { type: 'contextReset' },
      { type: 'factorChanged', id: 'macro', value: 1 },
      { type: 'switchesChanged', switches: { fuzzy: false, context: false } },
      { type: 'textChanged', text: 'otro' },
      { type: 'recommended', id: reqId(s), response: fixtures.recommendNeutral() },
      { type: 'failed', id: 99, error: { kind: 'network' } },
    ] as FlowEvent[]) {
      expect(flowReducer(s, e)).toBe(s)
    }
  })
})
