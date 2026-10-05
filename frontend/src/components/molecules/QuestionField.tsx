import { useId } from 'react'
import type { QuestionFieldProps } from '../../types/ui'
import { cx } from '../../lib/format'

/** One clarification question: native radio options and/or a free numeric input. */
export function QuestionField({ question, hint, options, freeInput, value, onChange, error }: QuestionFieldProps) {
  const groupId = useId()
  const freeId = `${groupId}-free`
  return (
    <fieldset className="iw-question">
      <legend className="iw-question__text">{question}</legend>
      {hint && <p className="iw-question__hint">{hint}</p>}
      {options && (
        <div className="iw-choices">
          {options.map((o) => {
            const on = value === o.value
            return (
              <label key={o.value} className={cx('iw-choice', on && 'is-on')}>
                <input type="radio" name={groupId} value={o.value} checked={on} onChange={() => onChange?.(o.value)} />
                <span>{o.label}</span>
              </label>
            )
          })}
        </div>
      )}
      {freeInput && (
        <div className="iw-free">
          <label htmlFor={freeId} className="iw-label">
            {freeInput.label}
          </label>
          <div className="iw-free__row">
            {freeInput.prefix && <span className="iw-free__affix">{freeInput.prefix}</span>}
            <input
              id={freeId}
              className="iw-input"
              type="text"
              inputMode="decimal"
              value={freeInput.value || ''}
              placeholder={freeInput.placeholder}
              onChange={(e) => freeInput.onChange?.(e.target.value)}
            />
            {freeInput.unit && <span className="iw-free__affix">{freeInput.unit}</span>}
          </div>
        </div>
      )}
      {error && <p className="iw-hint iw-hint--error">{error}</p>}
    </fieldset>
  )
}
