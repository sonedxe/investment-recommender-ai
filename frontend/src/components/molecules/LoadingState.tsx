import type { LoadingStateProps, LoadingStepState } from '../../types/ui'
import { ProgressLine } from '../atoms/ProgressLine'

const STEP_LABEL: Record<LoadingStepState, string> = { done: 'Listo', active: 'En curso', pending: 'Pendiente' }

export function LoadingState({ title, steps, note }: LoadingStateProps) {
  return (
    <section className="iw-loading">
      <ProgressLine label={title || 'Calculando tu distribución…'} />
      {steps && (
        <ol className="iw-loading__steps">
          {steps.map((s, i) => (
            <li key={i} className={`iw-loading__step is-${s.state}`}>
              <span>{s.label}</span>
              <span className="iw-loading__state">{STEP_LABEL[s.state]}</span>
            </li>
          ))}
        </ol>
      )}
      <p className="iw-loading__note">{note || 'Suele tardar entre 1 y 3 segundos.'}</p>
    </section>
  )
}
