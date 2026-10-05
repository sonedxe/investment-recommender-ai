import type { ButtonProps } from '../../types/ui'
import { cx } from '../../lib/format'

export function Button({ variant = 'primary', size, full, disabled, type = 'button', onClick, children }: ButtonProps) {
  return (
    <button
      type={type}
      className={cx('iw-btn', `iw-btn--${variant}`, size === 'sm' && 'iw-btn--sm', full && 'iw-btn--full')}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
