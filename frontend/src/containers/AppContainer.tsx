import { useCallback, useEffect, useReducer, useState } from 'react'
import { ApiError, getContextDefaults, interpret, recommend } from '../api/client'
import type { ContextDefaultsResponse } from '../api/types'
import { Button } from '../components'
import { flowReducer, initialFlowState, type FlowError } from '../state/flow'
import { ClarificationContainer } from './ClarificationContainer'
import { ContextContainer } from './ContextContainer'
import { HomeContainer } from './HomeContainer'
import { ResultContainer } from './ResultContainer'
import { useTheme } from './useTheme'
import { BusyView, MessageView } from './views'

function toFlowError(err: unknown): FlowError {
  if (err instanceof ApiError) {
    if (err.kind === 'validation') return { kind: 'validation', message: err.message }
    if (err.kind === 'http' && err.status != null) return { kind: 'http', status: err.status }
  }
  return { kind: 'network' }
}

const KEPT = 'Tu texto se conservó; vuelve a intentarlo en unos segundos.'

function errorCopy(error: FlowError): { title: string; text: string } {
  switch (error.kind) {
    case 'validation':
      return { title: 'No pudimos procesar los datos', text: `Revisa lo que escribiste e inténtalo de nuevo. Detalle: ${error.message}` }
    case 'http':
      return { title: 'El servicio respondió con un error', text: `Código ${error.status}. ${KEPT}` }
    default:
      return { title: 'No pudimos conectar con el servicio', text: `No pudimos conectar con el servicio. ${KEPT}` }
  }
}

type DefaultsState = { status: 'idle' | 'loading' | 'failed' } | { status: 'ready'; data: ContextDefaultsResponse }

/** Owns the flow reducer (conversation, profile, seed, results), performs its requests and the theme. */
export function AppContainer() {
  const [state, dispatch] = useReducer(flowReducer, initialFlowState)
  const [defaults, setDefaults] = useState<DefaultsState>({ status: 'idle' })
  const [theme, toggleTheme] = useTheme()
  const { request, phase, error, offline } = state

  // Perform the request the reducer asked for; a newer request or an unmount aborts it.
  useEffect(() => {
    if (!request) return
    const controller = new AbortController()
    const options = { signal: controller.signal }
    const run =
      request.kind === 'interpret'
        ? interpret({ conversation: request.conversation }, options).then((response) =>
            dispatch({ type: 'interpreted', id: request.id, response }),
          )
        : recommend(request.body, options).then((response) => dispatch({ type: 'recommended', id: request.id, response }))
    run.catch((err: unknown) => {
      if (controller.signal.aborted || (err instanceof ApiError && err.kind === 'aborted')) return
      dispatch({ type: 'failed', id: request.id, error: toFlowError(err) })
    })
    return () => controller.abort()
  }, [request])

  const loadDefaults = useCallback(() => {
    setDefaults({ status: 'loading' })
    getContextDefaults()
      .then((data) => setDefaults({ status: 'ready', data }))
      .catch(() => setDefaults({ status: 'failed' }))
  }, [])

  useEffect(() => {
    if (phase === 'context' && defaults.status === 'idle') loadDefaults()
  }, [phase, defaults.status, loadDefaults])

  let view
  if (error && error.kind !== 'empty') {
    const copy = errorCopy(error)
    const interpreting = state.lastRequest?.kind === 'interpret'
    view = (
      <MessageView
        step={interpreting ? 'Interpretación' : 'Cálculo'}
        heading={interpreting ? 'No pudimos leer tu situación' : 'No pudimos calcular'}
        {...copy}
        offline={offline}
        onRetry={() => dispatch({ type: 'retried' })}
        onBack={() => dispatch({ type: 'errorDismissed' })}
      />
    )
  } else if (phase === 'interpreting' || phase === 'calculating') {
    view = <BusyView stage={phase} offline={offline} />
  } else if (phase === 'clarifying' && state.interpretation) {
    view = (
      <ClarificationContainer
        key={state.conversation.length}
        input={state.text}
        interpretation={state.interpretation}
        conversation={state.conversation}
        offline={offline}
        onAnswer={(content) => dispatch({ type: 'answered', content })}
        onConfirm={() => dispatch({ type: 'assumptionConfirmed' })}
      />
    )
  } else if (phase === 'result' && state.recommendation) {
    view = (
      <ResultContainer
        recommendation={state.recommendation}
        switches={state.switches}
        pending={request !== null}
        offline={offline}
        onSwitchesChange={(switches) => dispatch({ type: 'switchesChanged', switches })}
        onAdjust={() => dispatch({ type: 'contextOpened' })}
      />
    )
  } else if (phase === 'context' && state.recommendation) {
    if (defaults.status === 'ready') {
      view = (
        <ContextContainer
          defaults={defaults.data}
          context={state.context}
          appliedContext={state.appliedContext}
          baseline={state.baseline}
          recommendation={state.recommendation}
          pending={request !== null}
          offline={offline}
          onFactorChange={(id, value) => dispatch({ type: 'factorChanged', id, value })}
          onReset={() => dispatch({ type: 'contextReset' })}
          onBack={() => dispatch({ type: 'contextClosed' })}
        />
      )
    } else if (defaults.status === 'failed') {
      view = (
        <MessageView
          step="Contexto"
          heading="Ajusta el contexto"
          title="No pudimos cargar los factores de contexto"
          text={`No pudimos conectar con el servicio. Vuelve a intentarlo en unos segundos.`}
          offline={offline}
          onRetry={loadDefaults}
          onBack={() => dispatch({ type: 'contextClosed' })}
          backLabel="Volver al resultado"
        />
      )
    } else {
      view = <BusyView stage="calculating" offline={offline} />
    }
  } else {
    view = (
      <HomeContainer
        text={state.text}
        empty={error?.kind === 'empty'}
        offline={offline}
        onChange={(text) => dispatch({ type: 'textChanged', text })}
        onSubmit={() => dispatch({ type: 'submitted' })}
      />
    )
  }

  return (
    <div className="iw-root">
      {view}
      <div className="iw-page iw-page--foot">
        <Button size="sm" variant="quiet" onClick={toggleTheme}>
          {theme === 'light' ? 'Usar tema oscuro' : 'Usar tema claro'}
        </Button>
      </div>
    </div>
  )
}
