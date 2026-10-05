import type { UnderstoodPanelProps } from '../../types/ui'
import { DataPoint } from '../molecules/DataPoint'

export function UnderstoodPanel({ title, items }: UnderstoodPanelProps) {
  return (
    <section className="iw-understood" aria-label={title || 'Lo que entendimos'}>
      <h2 className="iw-h3">{title || 'Lo que entendimos hasta ahora'}</h2>
      <dl className="iw-understood__list">
        {items.map((i) => (
          <DataPoint key={i.key} label={i.label} value={i.value} state={i.state} note={i.note} />
        ))}
      </dl>
    </section>
  )
}
