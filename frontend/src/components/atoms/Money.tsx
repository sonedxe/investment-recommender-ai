import type { MoneyProps } from '../../types/ui'
import { cx, formatMoney } from '../../lib/format'

export function Money({ value, decimals, signed, strong }: MoneyProps) {
  return <span className={cx('iw-money', strong && 'iw-money--strong')}>{formatMoney(value, decimals, signed)}</span>
}
