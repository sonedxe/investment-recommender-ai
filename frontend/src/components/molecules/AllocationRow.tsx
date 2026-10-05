import type { AllocationRowProps } from '../../types/ui'
import { categoryName, formatMoney, formatPct } from '../../lib/format'
import { CategoryDot } from '../atoms/CategoryDot'

export function AllocationRow({ categoryId, name, pct, amount, note }: AllocationRowProps) {
  return (
    <li className="iw-arow">
      <div className="iw-arow__head">
        <CategoryDot categoryId={categoryId} />
        <span className="iw-arow__name">{name || categoryName(categoryId)}</span>
        <span className="iw-arow__amount">{formatMoney(amount)}</span>
        <span className="iw-arow__pct">{formatPct(pct)}</span>
      </div>
      <div className="iw-arow__track" aria-hidden="true">
        <span
          className="iw-arow__fill"
          style={{ width: `${Math.max(pct, 0.6)}%`, background: `var(--cat-${categoryId})` }}
        />
      </div>
      {note && <p className="iw-arow__note">{note}</p>}
    </li>
  )
}
