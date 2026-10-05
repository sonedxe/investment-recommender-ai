import type { ScoreBreakdownProps } from '../../types/ui'
import { formatScore } from '../../lib/format'

export function ScoreBreakdown({ rows, total }: ScoreBreakdownProps) {
  const sum = total ?? rows.reduce((s, r) => s + r.value, 0)
  return (
    <table className="iw-table iw-ledger">
      <caption className="iw-sr">Desglose del puntaje del portafolio</caption>
      <thead>
        <tr>
          <th scope="col">Componente</th>
          <th scope="col">Detalle</th>
          <th scope="col" className="is-num">
            Aporte
          </th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i}>
            <th scope="row">{r.label}</th>
            <td className="iw-ledger__note">{r.note}</td>
            <td className="is-num">{formatScore(r.value)}</td>
          </tr>
        ))}
      </tbody>
      <tfoot>
        <tr>
          <th scope="row" colSpan={2}>
            Puntaje total
          </th>
          <td className="is-num">{formatScore(sum)}</td>
        </tr>
      </tfoot>
    </table>
  )
}
