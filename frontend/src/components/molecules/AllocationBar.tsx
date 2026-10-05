import type { AllocationBarProps } from '../../types/ui'
import { categoryName, cx, formatPct } from '../../lib/format'

export function AllocationBar({ items, size, label }: AllocationBarProps) {
  const describe = (i: AllocationBarProps['items'][number]) => `${i.name || categoryName(i.categoryId)} ${formatPct(i.pct)}`
  const ariaLabel = label || `Distribución: ${items.map(describe).join('; ')}`
  return (
    <div className={cx('iw-abar', size === 'sm' && 'iw-abar--sm')} role="img" aria-label={ariaLabel}>
      {items.map((i) => (
        <span
          key={i.categoryId}
          className="iw-abar__seg"
          title={describe(i)}
          style={{ flexGrow: Math.max(i.pct, 0.4), background: `var(--cat-${i.categoryId})` }}
        />
      ))}
    </div>
  )
}
