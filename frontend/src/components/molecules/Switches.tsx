import type { SwitchesProps, SwitchState } from '../../types/ui'

const SWITCHES: { key: keyof SwitchState; label: string }[] = [
  { key: 'fuzzy', label: 'Lógica difusa' },
  { key: 'context', label: 'Reglas de contexto' },
]

/** A6 (repo addition): ablation switches, native checkboxes. */
export function Switches({ value, onChange, legend }: SwitchesProps) {
  return (
    <fieldset className="iw-switches">
      <legend className="iw-switches__legend">{legend || 'Módulos activos en el cálculo'}</legend>
      {SWITCHES.map((s) => (
        <label key={s.key} className="iw-switch">
          <input
            type="checkbox"
            checked={value[s.key]}
            onChange={(e) => onChange?.({ ...value, [s.key]: e.target.checked })}
          />
          <span>{s.label}</span>
        </label>
      ))}
    </fieldset>
  )
}
