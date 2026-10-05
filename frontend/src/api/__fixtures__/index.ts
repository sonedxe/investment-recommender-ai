// Real backend responses captured by `frontend/scripts/capture-api-fixtures.py` (offline mode, seed 42).
import type { ContextDefaultsResponse, InterpretResponse, MarketEstimatesResponse, RecommendResponse } from '../types'
import contextDefaultsJson from './context-defaults.json'
import interpretAbsorptionJson from './interpret-absorption-question.json'
import interpretAmountJson from './interpret-amount-question.json'
import interpretRefusalJson from './interpret-refusal-complete.json'
import interpretRiskJson from './interpret-risk-question.json'
import marketEstimatesJson from './market-estimates.json'
import recommendAdverseJson from './recommend-adverse-political.json'
import recommendInformedJson from './recommend-informed-absorption.json'
import recommendNeutralJson from './recommend-neutral.json'
import recommendSwitchesOffJson from './recommend-switches-off.json'

/** Deep copy so a test can tweak a fixture without leaking into the others. */
function copy<T>(value: unknown): T {
  return JSON.parse(JSON.stringify(value)) as T
}

export const fixtures = {
  interpretAmount: () => copy<InterpretResponse>(interpretAmountJson),
  interpretRisk: () => copy<InterpretResponse>(interpretRiskJson),
  interpretAbsorption: () => copy<InterpretResponse>(interpretAbsorptionJson),
  interpretRefusal: () => copy<InterpretResponse>(interpretRefusalJson),
  recommendNeutral: () => copy<RecommendResponse>(recommendNeutralJson),
  recommendAdverse: () => copy<RecommendResponse>(recommendAdverseJson),
  recommendSwitchesOff: () => copy<RecommendResponse>(recommendSwitchesOffJson),
  recommendInformed: () => copy<RecommendResponse>(recommendInformedJson),
  contextDefaults: () => copy<ContextDefaultsResponse>(contextDefaultsJson),
  marketEstimates: () => copy<MarketEstimatesResponse>(marketEstimatesJson),
}
