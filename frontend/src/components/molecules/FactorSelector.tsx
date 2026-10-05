import { useId } from 'react'
import type { ContextLevel, FactorSelectorProps } from '../../types/ui'
import { cx } from '../../lib/format'

const OPTIONS: { value: ContextLevel; label: string }[] = [
  { value: 'adverse', label: 'Adverso' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'favorable', label: 'Favorable' },
]

/** Native radio group: keyboard arrows and screen reader announcements work out of the box. */
export function FactorSelector({ label, description, value, onChange, name, note }: FactorSelectorProps) {
  const groupId = useId()
  const groupName = name || groupId
  return (
    <fieldset className="iw-factor">
      <legend className="iw-factor__label">{label}</legend>
      {description && <p className="iw-factor__desc">{description}</p>}
      <div className="iw-seg">
        {OPTIONS.map((o) => {
          const on = value === o.value
          return (
            <label key={o.value} className={cx('iw-seg__opt', on && 'is-on')}>
              <input type="radio" name={groupName} value={o.value} checked={on} onChange={() => onChange?.(o.value)} />
              <span>{o.label}</span>
            </label>
          )
        })}
      </div>
      <p className="iw-factor__note">{note || 'Supuesto configurable, no una predicción.'}</p>
    </fieldset>
  )
}
