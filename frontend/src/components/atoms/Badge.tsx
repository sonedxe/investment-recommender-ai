import type { BadgeProps } from '../../types/ui'

export function Badge({ tone = 'neutral', children }: BadgeProps) {
  return <span className={`iw-badge iw-badge--${tone}`}>{children}</span>
}
