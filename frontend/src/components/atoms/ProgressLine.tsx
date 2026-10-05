import type { ProgressLineProps } from '../../types/ui'

export function ProgressLine({ label }: ProgressLineProps) {
  return (
    <div className="iw-progress" role="status">
      <div className="iw-progress__track" aria-hidden="true">
        <span className="iw-progress__bar" />
      </div>
      <p className="iw-progress__label">{label || 'Calculando…'}</p>
    </div>
  )
}
