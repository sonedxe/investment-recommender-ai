// Transversal views composed only from design-system components (no API knowledge).
import { AppHeader, Button, DisclaimerNotice, LoadingState, StatusBanner } from '../components'
import type { LoadingStep } from '../types/ui'

const STEP_LABELS = ['Interpretando tu situación', 'Evaluando combinaciones de inversión', 'Redactando la explicación']

/** Loading steps: interpreting has the first step active; calculating has it done and the second active. */
export function loadingSteps(stage: 'interpreting' | 'calculating'): LoadingStep[] {
  const active = stage === 'interpreting' ? 0 : 1
  return STEP_LABELS.map((label, i) => ({ label, state: i < active ? 'done' : i === active ? 'active' : 'pending' }))
}

export function BusyView({ stage, offline }: { stage: 'interpreting' | 'calculating'; offline?: boolean }) {
  const interpreting = stage === 'interpreting'
  return (
    <div className="iw-screen">
      <AppHeader offline={offline} step={interpreting ? 'Interpretación' : 'Cálculo'} />
      <main className="iw-page">
        <h1 className="iw-h1">{interpreting ? 'Leyendo tu situación' : 'Calculando'}</h1>
        <LoadingState
          title={interpreting ? 'Interpretando lo que escribiste…' : 'Calculando tu distribución…'}
          steps={loadingSteps(stage)}
        />
      </main>
    </div>
  )
}

export interface MessageViewProps {
  step?: string
  heading: string
  title: string
  text: string
  offline?: boolean
  onRetry?: () => void
  onBack?: () => void
  backLabel?: string
}

export function MessageView({ step, heading, title, text, offline, onRetry, onBack, backLabel }: MessageViewProps) {
  return (
    <div className="iw-screen">
      <AppHeader offline={offline} step={step} />
      <main className="iw-page">
        <h1 className="iw-h1">{heading}</h1>
        <StatusBanner tone="error" title={title} action={onRetry ? { label: 'Intentar de nuevo', onClick: onRetry } : undefined}>
          {text}
        </StatusBanner>
        {onBack && (
          <div className="iw-actions">
            <Button variant="quiet" onClick={onBack}>
              {backLabel || 'Volver'}
            </Button>
          </div>
        )}
        <DisclaimerNotice />
      </main>
    </div>
  )
}
