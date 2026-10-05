import { useState } from 'react'
import { toResult } from '../api/mappers'
import type { RecommendResponse } from '../api/types'
import { ResultScreen } from '../components'
import type { Switches } from '../state/flow'

export interface ResultContainerProps {
  recommendation: RecommendResponse
  switches: Switches
  pending: boolean
  offline: boolean
  onSwitchesChange: (next: Switches) => void
  onAdjust: () => void
  onRestart: () => void
}

export function ResultContainer({ recommendation, switches, pending, offline, onSwitchesChange, onAdjust, onRestart }: ResultContainerProps) {
  const [technicalOpen, setTechnicalOpen] = useState(false)
  const data = toResult(recommendation)
  return (
    <ResultScreen
      {...data}
      technicalOpen={technicalOpen}
      onTechnicalToggle={setTechnicalOpen}
      pending={pending}
      offline={offline}
      onAdjust={onAdjust}
      onRestart={onRestart}
      // The switches show the requested selection while a recalculation is pending.
      switches={switches}
      onSwitchesChange={onSwitchesChange}
    />
  )
}
