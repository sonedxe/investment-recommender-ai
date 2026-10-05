import type { AssumptionListProps } from '../../types/ui'

export function AssumptionList({ title, items }: AssumptionListProps) {
  return (
    <section className="iw-assume">
      <h3 className="iw-assume__title">{title || 'Supuestos aplicados'}</h3>
      <ul className="iw-assume__list">
        {items.map((text, i) => (
          <li key={i}>{text}</li>
        ))}
      </ul>
    </section>
  )
}
