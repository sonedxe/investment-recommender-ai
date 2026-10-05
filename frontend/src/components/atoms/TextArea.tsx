import { useId, type ChangeEvent } from 'react'
import type { TextAreaProps } from '../../types/ui'
import { cx } from '../../lib/format'

/** Controlled when `onChange` is given; otherwise `value` is only the initial text. */
export function TextArea({ label, hint, error, placeholder, rows = 5, value, onChange }: TextAreaProps) {
  const id = useId()
  const hintId = `${id}-hint`
  const valueProps = onChange
    ? { value: value || '', onChange: (e: ChangeEvent<HTMLTextAreaElement>) => onChange(e.target.value) }
    : { defaultValue: value || '' }
  return (
    <div className="iw-field">
      {label && (
        <label htmlFor={id} className="iw-label">
          {label}
        </label>
      )}
      <textarea
        id={id}
        className={cx('iw-textarea', error && 'is-invalid')}
        rows={rows}
        placeholder={placeholder}
        aria-describedby={hint || error ? hintId : undefined}
        aria-invalid={error ? 'true' : undefined}
        {...valueProps}
      />
      {(error || hint) && (
        <p id={hintId} className={cx('iw-hint', error && 'iw-hint--error')}>
          {error || hint}
        </p>
      )}
    </div>
  )
}
