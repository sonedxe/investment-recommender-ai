// Pure state machine of the recommendation flow (docs/plan/06-frontend.md §4).
// The reducer decides WHAT to request (`state.request`); AppContainer performs it and reports back
// with the request id, so stale responses are ignored. `error` and `offline` are transversal flags.
import type {
  ContextIn,
  FieldId,
  InterpretResponse,
  ProfileIn,
  RecommendRequest,
  RecommendResponse,
  SwitchesIn,
  Turn,
} from '../api/types'

export type Phase = 'input' | 'interpreting' | 'clarifying' | 'calculating' | 'result' | 'context'
export type FactorId = 'political' | 'macro'
export type Switches = Required<SwitchesIn>

export type FlowError =
  | { kind: 'empty' }
  | { kind: 'network' }
  | { kind: 'http'; status: number }
  | { kind: 'validation'; message: string }

export type FlowRequest =
  | { id: number; kind: 'interpret'; conversation: Turn[] }
  | { id: number; kind: 'recommend'; body: RecommendRequest }

export interface FlowState {
  phase: Phase
  /** First user message; survives errors so a retry or a new attempt keeps it. */
  text: string
  conversation: Turn[]
  interpretation: InterpretResponse | null
  profile: ProfileIn | null
  /** Seed of the first result, reused by every recalculation so only the changed input moves the result. */
  seed: number | null
  /** Context selection; null = not informed (the backend assumes neutral and declares it). */
  context: ContextIn | null
  switches: Switches
  recommendation: RecommendResponse | null
  /** Context the current recommendation was computed with. */
  appliedContext: ContextIn | null
  /** Latest result computed with a neutral context: the "before" of the context screen. */
  baseline: RecommendResponse | null
  request: FlowRequest | null
  lastRequest: FlowRequest | null
  /** Phase restored when the in-flight request fails or the error is dismissed. */
  origin: Phase
  error: FlowError | null
  offline: boolean
  nextId: number
}

export type FlowEvent =
  | { type: 'textChanged'; text: string }
  | { type: 'submitted' }
  | { type: 'interpreted'; id: number; response: InterpretResponse }
  | { type: 'answered'; content: string }
  | { type: 'assumptionConfirmed' }
  | { type: 'recommended'; id: number; response: RecommendResponse }
  | { type: 'failed'; id: number; error: FlowError }
  | { type: 'retried' }
  | { type: 'errorDismissed' }
  | { type: 'switchesChanged'; switches: Switches }
  | { type: 'contextOpened' }
  | { type: 'contextClosed' }
  | { type: 'factorChanged'; id: FactorId; value: number }
  | { type: 'contextReset' }
  | { type: 'restarted' }

export const initialFlowState: FlowState = {
  phase: 'input',
  text: '',
  conversation: [],
  interpretation: null,
  profile: null,
  seed: null,
  context: null,
  switches: { fuzzy: true, context: true },
  recommendation: null,
  appliedContext: null,
  baseline: null,
  request: null,
  lastRequest: null,
  origin: 'input',
  error: null,
  offline: false,
  nextId: 1,
}

export function isNeutral(context: ContextIn | null): boolean {
  return !context || ((context.political ?? 0) === 0 && (context.macro ?? 0) === 0)
}

/** Fields the assistant asked for, in conversation order. */
export function askedFields(conversation: Turn[]): FieldId[] {
  return conversation.flatMap((t) => (t.role === 'assistant' && t.field ? [t.field] : []))
}

/** Interpreted profile -> /api/recommend profile; null when a critical field is still missing. */
function toProfile(res: InterpretResponse): ProfileIn | null {
  const p = res.profile
  if (p.amount == null || p.risk_profile == null || (p.horizon_years == null && p.horizon_label == null)) return null
  const profile: ProfileIn = { amount: p.amount, risk_profile: p.risk_profile }
  if (p.horizon_years != null) profile.horizon_years = p.horizon_years
  else profile.horizon_label = p.horizon_label
  if (p.total_savings != null) profile.total_savings = p.total_savings
  if (p.emergency_months != null) profile.emergency_months = p.emergency_months
  return profile
}

function recommendBody(state: FlowState, context: ContextIn | null): RecommendRequest {
  const body: RecommendRequest = { profile: state.profile as ProfileIn, switches: state.switches }
  if (context) body.context = context
  if (state.seed != null) body.seed = state.seed
  return body
}

type RequestSpec = { kind: 'interpret'; conversation: Turn[] } | { kind: 'recommend'; body: RecommendRequest }

function issue(state: FlowState, spec: RequestSpec, phase: Phase, origin: Phase): FlowState {
  const request = { ...spec, id: state.nextId } as FlowRequest
  return { ...state, request, lastRequest: request, phase, origin, error: null, nextId: state.nextId + 1 }
}

function calculate(state: FlowState): FlowState {
  return issue(state, { kind: 'recommend', body: recommendBody(state, state.context) }, 'calculating', 'input')
}

/** Recalculation from the result or context screen: the screen stays while the request is pending. */
function recalculate(state: FlowState, context: ContextIn | null): FlowState {
  const next = { ...state, context }
  const baseline = state.baseline
  const sameSwitches =
    baseline != null && baseline.switches.fuzzy === state.switches.fuzzy && baseline.switches.context === state.switches.context
  if (isNeutral(context) && sameSwitches) {
    return { ...next, recommendation: baseline, appliedContext: context, request: null, error: null }
  }
  return issue(next, { kind: 'recommend', body: recommendBody(next, context) }, state.phase, state.phase)
}

function matches(state: FlowState, id: number, kind: FlowRequest['kind']): boolean {
  return state.request?.id === id && state.request.kind === kind
}

export function flowReducer(state: FlowState, event: FlowEvent): FlowState {
  switch (event.type) {
    case 'textChanged':
      if (state.phase !== 'input') return state
      return { ...state, text: event.text, error: state.error?.kind === 'empty' ? null : state.error }

    case 'submitted': {
      if (state.phase !== 'input' || state.request) return state
      const text = state.text.trim()
      if (!text) return { ...state, error: { kind: 'empty' } }
      const fresh: FlowState = { ...initialFlowState, text: state.text, nextId: state.nextId, offline: state.offline }
      return issue(fresh, { kind: 'interpret', conversation: [{ role: 'user', content: text }] }, 'interpreting', 'input')
    }

    case 'interpreted': {
      if (state.request?.kind !== 'interpret' || !matches(state, event.id, 'interpret')) return state
      const res = event.response
      const asked: Turn[] = res.question ? [{ role: 'assistant', content: res.question.text, field: res.question.field }] : []
      const next: FlowState = {
        ...state,
        conversation: [...state.request.conversation, ...asked],
        interpretation: res,
        offline: res.mode === 'offline',
        request: null,
      }
      if (res.question) return { ...next, phase: 'clarifying' }
      const profile = toProfile(res)
      if (!profile) return { ...next, phase: state.origin, error: { kind: 'validation', message: 'Perfil incompleto' } }
      const withProfile = { ...next, profile }
      // A declared assumption is shown before calculating so the user sees what was assumed.
      return res.assumptions.length > 0 ? { ...withProfile, phase: 'clarifying' } : calculate(withProfile)
    }

    case 'answered': {
      const content = event.content.trim()
      if (state.phase !== 'clarifying' || state.request || !state.interpretation?.question || !content) return state
      const conversation: Turn[] = [...state.conversation, { role: 'user', content }]
      return issue(state, { kind: 'interpret', conversation }, 'interpreting', 'clarifying')
    }

    case 'assumptionConfirmed':
      if (state.phase !== 'clarifying' || state.request || !state.profile || !state.interpretation?.complete) return state
      return calculate(state)

    case 'recommended': {
      if (state.request?.kind !== 'recommend' || !matches(state, event.id, 'recommend')) return state
      const res = event.response
      const appliedContext = state.request.body.context ?? null
      return {
        ...state,
        phase: state.phase === 'calculating' ? 'result' : state.phase,
        recommendation: res,
        appliedContext,
        baseline: isNeutral(appliedContext) ? res : state.baseline,
        seed: res.technical.convergence.seed,
        switches: { fuzzy: res.switches.fuzzy, context: res.switches.context },
        offline: res.mode === 'offline',
        request: null,
      }
    }

    case 'failed':
      if (state.request?.id !== event.id) return state
      return { ...state, request: null, phase: state.origin, error: event.error }

    case 'retried': {
      const last = state.lastRequest
      if (!state.error || state.error.kind === 'empty' || !last || state.request) return state
      if (last.kind === 'interpret') {
        return issue(state, { kind: 'interpret', conversation: last.conversation }, 'interpreting', state.origin)
      }
      const stays = state.origin === 'result' || state.origin === 'context'
      return issue(state, { kind: 'recommend', body: last.body }, stays ? state.origin : 'calculating', state.origin)
    }

    case 'errorDismissed': {
      if (!state.error) return state
      // A failed recalculation leaves the selection where the shown result was computed.
      const switches = state.recommendation
        ? { fuzzy: state.recommendation.switches.fuzzy, context: state.recommendation.switches.context }
        : state.switches
      return { ...state, error: null, phase: state.origin, context: state.appliedContext, switches }
    }

    case 'switchesChanged':
      if (state.phase !== 'result' && state.phase !== 'context') return state
      return recalculate({ ...state, switches: event.switches }, state.context)

    case 'contextOpened':
      return state.phase === 'result' ? { ...state, phase: 'context' } : state

    case 'contextClosed':
      return state.phase === 'context' ? { ...state, phase: 'result' } : state

    case 'factorChanged': {
      if (state.phase !== 'context') return state
      const current = { political: 0, macro: 0, ...state.context }
      return recalculate(state, { ...current, [event.id]: event.value })
    }

    case 'contextReset':
      if (state.phase !== 'context') return state
      return recalculate(state, null)

    case 'restarted':
      // New query: back to an empty input. nextId keeps counting so a late response is ignored.
      if (state.phase !== 'result' && state.phase !== 'context') return state
      return { ...initialFlowState, nextId: state.nextId, offline: state.offline }
  }
}
