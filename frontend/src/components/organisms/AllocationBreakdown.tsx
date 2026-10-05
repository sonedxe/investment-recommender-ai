import type { AllocationBreakdownProps } from '../../types/ui'
import { formatMoney } from '../../lib/format'
import { AllocationBar } from '../molecules/AllocationBar'
import { AllocationRow } from '../molecules/AllocationRow'

/** When `total` is omitted it is the sum of the item amounts. */
export function AllocationBreakdown({ title, items, total }: AllocationBreakdownProps) {
  const sum = total ?? items.reduce((s, i) => s + i.amount, 0)
  return (
    <section className="iw-breakdown">
      <h2 className="iw-h2">{title || 'Cómo repartir tu dinero'}</h2>
      <AllocationBar items={items} />
      <ul className="iw-breakdown__list">
        {items.map((i) => (
          <AllocationRow key={i.categoryId} {...i} />
        ))}
      </ul>
      <div className="iw-breakdown__total">
        <span>Total a invertir</span>
        <span className="iw-money iw-money--strong">{formatMoney(sum)}</span>
        <span className="iw-arow__pct">100 %</span>
      </div>
    </section>
  )
}
