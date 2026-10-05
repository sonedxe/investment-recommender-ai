import type { BadgeProps, DataPointProps, DataState } from '../../types/ui'
import { Badge } from '../atoms/Badge'

const STATE_LABEL: Record<DataState, string> = {
  understood: 'Entendido',
  asked: 'Preguntando ahora',
  missing: 'Falta',
  assumed: 'Supuesto',
}
const STATE_TONE: Record<DataState, NonNullable<BadgeProps['tone']>> = {
  understood: 'accent',
  asked: 'neutral',
  missing: 'outline',
  assumed: 'caution',
}

/** Renders a `dt`/`dd` pair; place it inside a `dl` (UnderstoodPanel). */
export function DataPoint({ label, value, state = 'understood', note }: DataPointProps) {
  return (
    <div className={`iw-dp iw-dp--${state}`}>
      <dt className="iw-dp__label">{label}</dt>
      <dd className="iw-dp__value">
        {value ? (
          <span className="iw-dp__text">{value}</span>
        ) : (
          <span className="iw-dp__text iw-dp__text--empty">—</span>
        )}
        <Badge tone={STATE_TONE[state]}>{STATE_LABEL[state]}</Badge>
        {note && <span className="iw-dp__note">{note}</span>}
      </dd>
    </div>
  )
}
