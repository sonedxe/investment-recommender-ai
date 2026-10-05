import type { ParamSource, ParameterTableProps } from '../../types/ui'
import { categoryName, cx, formatFraction, formatSignedFraction } from '../../lib/format'
import { CategoryDot } from '../atoms/CategoryDot'

const SOURCE_LABEL: Record<ParamSource, string> = { data: 'Datos de mercado', prior: 'Valor de referencia' }

/** A5: the cᵢ and source columns appear only when at least one row carries them. */
export function ParameterTable({ rows }: ParameterTableProps) {
  const showAdj = rows.some((r) => r.contextAdj != null)
  const showSource = rows.some((r) => r.source != null)
  return (
    <div className="iw-scroll" role="region" tabIndex={0} aria-label="Tabla de retorno y riesgo por categoría">
      <table className="iw-table">
        <caption className="iw-sr">
          Retorno esperado (μ) y riesgo (σ) por categoría, originales y ajustados por contexto
        </caption>
        <thead>
          <tr>
            <th scope="col">Categoría</th>
            <th scope="col" className="is-num">μ original</th>
            <th scope="col" className="is-num">μ ajustado</th>
            <th scope="col" className="is-num">σ original</th>
            <th scope="col" className="is-num">σ ajustado</th>
            {showAdj && <th scope="col" className="is-num">Ajuste por contexto (cᵢ)</th>}
            {showSource && <th scope="col">Fuente</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.categoryId}>
              <th scope="row">
                <CategoryDot categoryId={r.categoryId} /> {r.name || categoryName(r.categoryId)}
              </th>
              <td className="is-num">{formatFraction(r.mu)}</td>
              <td className={cx('is-num', r.muAdj !== r.mu && 'is-changed')}>{formatFraction(r.muAdj)}</td>
              <td className="is-num">{formatFraction(r.sigma)}</td>
              <td className={cx('is-num', r.sigmaAdj !== r.sigma && 'is-changed')}>{formatFraction(r.sigmaAdj)}</td>
              {showAdj && (
                <td className={cx('is-num', !!r.contextAdj && 'is-changed')}>
                  {r.contextAdj == null ? '—' : formatSignedFraction(r.contextAdj, 2)}
                </td>
              )}
              {showSource && <td>{r.source ? SOURCE_LABEL[r.source] : '—'}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
