// Props contract of the presentational components, ported from the design system `components/index.d.ts`
// with the repo adjustments A1–A6 (docs/plan/06-frontend.md §3).
// Conventions: pct goes from 0 to 100; amount is in soles; mu, sigma and contextAdj are fractions (0.09 = 9 %).
import type { ReactNode } from 'react'

export type CategoryId = 'stocks' | 'mixed' | 'debt' | 'bonds' | 'term'
/** Context factor level (A4: renamed from `Tri`, which clashes with the triangular membership function `tri()`). */
export type ContextLevel = 'adverse' | 'neutral' | 'favorable'
export type DataState = 'understood' | 'asked' | 'missing' | 'assumed'
/** A1: fuzzy horizon rules (RH), fuzzy absorption rules (RA) and crisp context rules (RC). */
export type RuleKind = 'horizon' | 'absorption' | 'context'
/** A5: whether a category estimate comes from market data or from the prior. */
export type ParamSource = 'data' | 'prior'

export interface Category {
  id: CategoryId
  name: string
}

export interface AllocationItem {
  categoryId: CategoryId
  name?: string
  pct: number
  amount: number
  note?: string
}
export interface UnderstoodItem {
  key: string
  label: string
  value: string | null
  state: DataState
  note?: string
}
export interface Point {
  x: number
  y: number
}
export interface Series {
  id: string
  name: string
  points: Point[]
}
export interface ParamRow {
  categoryId: CategoryId
  name?: string
  mu: number
  sigma: number
  muAdj: number
  sigmaAdj: number
  /** A5: context adjustment cᵢ applied to this category (fraction). */
  contextAdj?: number
  /** A5: origin of mu and sigma. */
  source?: ParamSource
}
export interface Rule {
  id: string
  name: string
  condition: string
  effect: string
  /** A1 */
  kind: RuleKind
  /** A1: activation degree α in [0, 1]; only meaningful for fuzzy rules. */
  activation?: number | null
}
export interface ScoreRow {
  label: string
  note?: string
  value: number
}
export interface Scenario {
  label: string
  text: string
  amount: number
}
export interface Factor {
  id: string
  label: string
  description?: string
  value: ContextLevel
}
export interface QuestionOption {
  value: string
  label: string
}
export interface FreeInput {
  label: string
  unit?: string
  prefix?: string
  placeholder?: string
  value?: string
  onChange?: (v: string) => void
}
export interface Question {
  question: string
  hint?: string
  options?: QuestionOption[]
  freeInput?: FreeInput
}
/** A6: ablation switches shown in the technical detail. */
export interface SwitchState {
  fuzzy: boolean
  context: boolean
}
export interface TechnicalData {
  params: ParamRow[]
  lambdaBase: number
  /** A3: horizon multiplier m_H, so that lambdaEff = lambdaBase × mH. */
  mH: number
  lambdaEff: number
  membership: MembershipChartProps
  absorption: AbsorptionChartProps
  rules: Rule[]
  score: ScoreBreakdownProps
  convergence: ConvergenceChartProps
}

export type LoadingStepState = 'done' | 'active' | 'pending'
export interface LoadingStep {
  label: string
  state: LoadingStepState
}

// Atoms
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'quiet'
  size?: 'md' | 'sm'
  full?: boolean
  disabled?: boolean
  type?: 'button' | 'submit'
  onClick?: () => void
  children: ReactNode
}
export interface BadgeProps {
  tone?: 'neutral' | 'accent' | 'caution' | 'danger' | 'outline'
  children: ReactNode
}
export interface CategoryDotProps {
  categoryId: CategoryId
}
export interface TextAreaProps {
  label?: string
  hint?: string
  error?: string
  placeholder?: string
  rows?: number
  value?: string
  onChange?: (text: string) => void
}
export interface ProgressLineProps {
  label?: string
}
export interface MoneyProps {
  value: number
  decimals?: number
  signed?: boolean
  strong?: boolean
}
export interface DisclaimerNoticeProps {
  variant?: 'block' | 'strip'
  children?: ReactNode
}

// Molecules
export type AllocationRowProps = AllocationItem
export interface AllocationBarProps {
  items: Pick<AllocationItem, 'categoryId' | 'name' | 'pct'>[]
  size?: 'md' | 'sm'
  label?: string
}
export interface DataPointProps {
  label: string
  value: string | null
  state?: DataState
  note?: string
}
export interface FactorSelectorProps {
  label: string
  description?: string
  value: ContextLevel
  onChange?: (v: ContextLevel) => void
  name?: string
  note?: string
}
export interface QuestionFieldProps extends Question {
  value?: string
  onChange?: (v: string) => void
  error?: string
}
export interface StatusBannerProps {
  tone?: 'error' | 'offline' | 'empty' | 'info'
  title?: string
  action?: { label: string; onClick?: () => void }
  children?: ReactNode
}
export interface AssumptionListProps {
  title?: string
  items: string[]
}
export interface LoadingStateProps {
  title?: string
  steps?: LoadingStep[]
  note?: string
}
export interface SwitchesProps {
  value: SwitchState
  onChange?: (next: SwitchState) => void
  legend?: string
}

// Organisms
export interface AppHeaderProps {
  step?: string
  offline?: boolean
}
export interface AllocationBreakdownProps {
  title?: string
  items: AllocationItem[]
  total?: number
}
export interface UnderstoodPanelProps {
  title?: string
  items: UnderstoodItem[]
}
export interface ClarificationFormProps {
  understood: UnderstoodItem[]
  step?: number
  totalSteps?: number
  question?: Question
  value?: string
  onChange?: (v: string) => void
  onSubmit?: () => void
  onSkip?: () => void
  skipLabel?: string
  submitLabel?: string
  assumption?: string
  error?: string
}
export interface ExplanationTextProps {
  title?: string
  paragraphs: string[]
  scenarios?: Scenario[]
}
export interface ContextPanelProps {
  factors: Factor[]
  onChange?: (id: string, v: ContextLevel) => void
  before: AllocationItem[]
  after?: AllocationItem[]
  changed?: boolean
  beforeLabel?: string
  afterLabel?: string
  note?: string
}
export interface ParameterTableProps {
  rows: ParamRow[]
}
export interface MembershipChartProps {
  title?: string
  series: Series[]
  value: number
  domain?: [number, number]
  xStep?: number
  xLabel?: string
}
export interface AbsorptionChartProps {
  title?: string
  lead?: string
  curve: Point[]
  c: number
  centroid: number
  /** A2: membership of the chosen c in the aggregated set, μ_CA(c). */
  membershipAtC: number
  /** A2: input r = amount to invest / total savings (null when unknown). */
  r?: number | null
  /** A2: input E = emergency fund coverage in months (null when unknown). */
  e?: number | null
  /** A2: true when r and E were not informed and a medium capacity was assumed. */
  assumed?: boolean
}
export interface ConvergenceChartProps {
  title?: string
  values: number[]
}
export interface RulesTableProps {
  rules: Rule[]
}
export interface ScoreBreakdownProps {
  rows: ScoreRow[]
  total?: number
}
export interface TechnicalDetailProps {
  data: TechnicalData
  open?: boolean
  onToggle?: () => void
  /** A6: optional ablation switches; nothing is rendered when absent. */
  switches?: SwitchState
  onSwitchesChange?: (next: SwitchState) => void
}

// Screens
export interface HomeScreenProps {
  value?: string
  onChange?: (t: string) => void
  onSubmit?: () => void
  example?: string
  onUseExample?: () => void
  offline?: boolean
  error?: { title: string; text: string }
}
export interface ClarificationScreenProps extends ClarificationFormProps {
  input?: string
  offline?: boolean
}
export interface ResultScreenProps {
  summary: string
  total: number
  allocation: AllocationItem[]
  assumptions: string[]
  explanation: ExplanationTextProps
  technical: TechnicalData
  technicalOpen?: boolean
  /** Fired when the technical detail is opened or closed. */
  onTechnicalToggle?: () => void
  /** A recalculation is in progress; the current result stays visible. */
  pending?: boolean
  onAdjust?: () => void
  offline?: boolean
  /** A6: forwarded to TechnicalDetail. */
  switches?: SwitchState
  onSwitchesChange?: (next: SwitchState) => void
}
export interface ContextScreenProps extends ContextPanelProps {
  onBack?: () => void
  onReset?: () => void
  offline?: boolean
}
