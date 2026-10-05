import { useId } from 'react'
import type { ContextPanelProps } from '../../types/ui'
import { categoryName, formatMoney, formatNumber, formatPct } from '../../lib/format'
import { CategoryDot } from '../atoms/CategoryDot'
import { AllocationBar } from '../molecules/AllocationBar'
import { FactorSelector } from '../molecules/FactorSelector'

/** Change in percentage points, rounded to one decimal. */
function delta(before: number, after: number): string {
  const d = Math.round((after - before) * 10) / 10
  if (d === 0) return 'Sin cambio'
  return `${d > 0 ? '+' : '−'}${formatNumber(Math.abs(d), Number.isInteger(d) ? 0 : 1)} pts`
}

export function ContextPanel(props: ContextPanelProps) {
  const { factors, onChange, before, after = [], changed, note } = props
  const beforeLabel = props.beforeLabel || 'Antes'
  const afterLabel = props.afterLabel || 'Después'
  const groupId = useId()
  return (
    <section className="iw-context">
      <div className="iw-context__factors">
        {factors.map((f) => (
          <FactorSelector
            key={f.id}
            name={groupId + f.id}
            label={f.label}
            description={f.description}
            value={f.value}
            onChange={(v) => onChange?.(f.id, v)}
          />
        ))}
      </div>
      <div className="iw-context__compare">
        <h2 className="iw-h3">{changed ? 'Antes y después de tu ajuste' : 'Distribución con el contexto actual'}</h2>
        <div className="iw-context__bars">
          <div>
            <p className="iw-context__barlabel">{beforeLabel}</p>
            <AllocationBar items={before} size="sm" />
          </div>
          {changed && (
            <div>
              <p className="iw-context__barlabel">{afterLabel}</p>
              <AllocationBar items={after} size="sm" />
            </div>
          )}
        </div>
        <table className="iw-table iw-table--stack">
          <caption className="iw-sr">Comparación de la distribución antes y después del ajuste</caption>
          <thead>
            <tr>
              <th scope="col">Categoría</th>
              <th scope="col" className="is-num">
                {beforeLabel}
              </th>
              {changed && (
                <th scope="col" className="is-num">
                  {afterLabel}
                </th>
              )}
              {changed && (
                <th scope="col" className="is-num">
                  Cambio
                </th>
              )}
            </tr>
          </thead>
          <tbody>
            {before.map((b, i) => {
              const a = after[i] || b
              return (
                <tr key={b.categoryId}>
                  <th scope="row">
                    <CategoryDot categoryId={b.categoryId} /> {b.name || categoryName(b.categoryId)}
                  </th>
                  <td className="is-num" data-label={beforeLabel}>
                    {`${formatPct(b.pct)} · ${formatMoney(b.amount)}`}
                  </td>
                  {changed && (
                    <td className="is-num" data-label={afterLabel}>
                      {`${formatPct(a.pct)} · ${formatMoney(a.amount)}`}
                    </td>
                  )}
                  {changed && (
                    <td className="is-num iw-delta" data-label="Cambio">
                      {delta(b.pct, a.pct)}
                    </td>
                  )}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <p className="iw-context__note">
        {note ||
          'Estos factores son supuestos que tú eliges para ver cómo cambia la distribución. No son predicciones sobre el futuro del país.'}
      </p>
    </section>
  )
}
