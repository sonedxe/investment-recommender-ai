import { toAllocation, toFactors, valueFromLevel } from '../api/mappers'
import type { ContextDefaultsResponse, ContextIn, RecommendResponse } from '../api/types'
import { ContextScreen } from '../components'
import { isNeutral, type FactorId } from '../state/flow'

export interface ContextContainerProps {
  defaults: ContextDefaultsResponse
  context: ContextIn | null
  appliedContext: ContextIn | null
  baseline: RecommendResponse | null
  recommendation: RecommendResponse
  pending: boolean
  offline: boolean
  onFactorChange: (id: FactorId, value: number) => void
  onReset: () => void
  onBack: () => void
  onRestart: () => void
}

/** Before = latest neutral result with the same switches; after = the current (adjusted) result. */
export function ContextContainer(props: ContextContainerProps) {
  const { defaults, context, appliedContext, baseline, recommendation, pending, offline } = props
  const sameSwitches =
    baseline != null &&
    baseline.switches.fuzzy === recommendation.switches.fuzzy &&
    baseline.switches.context === recommendation.switches.context
  const before = sameSwitches ? baseline : recommendation
  const changed = !isNeutral(appliedContext) && before !== recommendation
  return (
    <ContextScreen
      factors={toFactors(defaults, context)}
      onChange={(id, level) => props.onFactorChange(id as FactorId, valueFromLevel(level))}
      before={toAllocation(before)}
      after={toAllocation(recommendation)}
      changed={changed}
      beforeLabel={changed ? 'Antes (Neutral)' : undefined}
      afterLabel={changed ? 'Después (ajustado)' : undefined}
      note={pending ? 'Recalculando la distribución con los factores elegidos…' : undefined}
      onBack={props.onBack}
      onReset={props.onReset}
      onRestart={props.onRestart}
      offline={offline}
    />
  )
}
