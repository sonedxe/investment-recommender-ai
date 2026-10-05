import type { AbsorptionChartProps } from '../../types/ui'
import { CHART_HEIGHT, CHART_WIDTH, interpolate, linePath, scale, type Tick } from '../../lib/chart'
import { AxisLabels, ChartShell, GridY, TicksX, type ChartFact } from './ChartShell'

const M = { l: 52, r: 24, t: 44, b: 52 }
const X_TICKS: Tick[] = [0, 0.2, 0.4, 0.6, 0.8, 1].map((v) => ({ v, label: String(v) }))
const Y_TICKS: Tick[] = [
  { v: 0, label: '0' },
  { v: 0.5, label: '0.5' },
  { v: 1, label: '1' },
]
const SAMPLE_X = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

const formatR = (r: number | null | undefined) => (r == null ? 'No informado' : r.toFixed(2))
const formatE = (e: number | null | undefined) => (e == null ? 'No informado' : `${e.toFixed(1)} meses`)

/**
 * Key chart: aggregated fuzzy set of loss absorption capacity, the c chosen by the genetic algorithm
 * (solid mark) and the centroid (dashed mark). A2 adds μ_CA(c) and the inputs r and E.
 */
export function AbsorptionChart(props: AbsorptionChartProps) {
  const { title, lead, curve, c, centroid, membershipAtC, r, e, assumed } = props
  const sx = scale(0, 1, M.l, CHART_WIDTH - M.r)
  const sy = scale(0, 1, CHART_HEIGHT - M.b, M.t)
  const area = curve.length
    ? `M${sx(curve[0].x).toFixed(1)} ${sy(0).toFixed(1)} ` +
      curve.map((q) => `L${sx(q.x).toFixed(1)} ${sy(q.y).toFixed(1)}`).join(' ') +
      ` L${sx(curve[curve.length - 1].x).toFixed(1)} ${sy(0).toFixed(1)} Z`
    : ''
  const cLeft = c <= centroid
  const alt =
    `Conjunto difuso resultante de capacidad de absorción entre 0 y 1. El algoritmo genético eligió c = ${c.toFixed(2)}, ` +
    `con pertenencia μ_CA(c) = ${membershipAtC.toFixed(2)}, y el centroide del conjunto es ${centroid.toFixed(2)}.`
  const facts: ChartFact[] = [
    ['c elegido por el algoritmo genético:', c.toFixed(2)],
    ['Pertenencia en c, μ_CA(c):', membershipAtC.toFixed(2)],
    ['Centroide del conjunto:', centroid.toFixed(2)],
    ['r (monto / ahorro total):', formatR(r)],
    ['E (fondo de emergencia):', formatE(e)],
  ]
  const table = (
    <table className="iw-table">
      <thead>
        <tr>
          <th scope="col">Capacidad (x)</th>
          <th scope="col" className="is-num">
            Pertenencia
          </th>
        </tr>
      </thead>
      <tbody>
        {SAMPLE_X.map((x) => (
          <tr key={x}>
            <th scope="row">{x.toFixed(1)}</th>
            <td className="is-num">{interpolate(curve, x).toFixed(2)}</td>
          </tr>
        ))}
        <tr>
          <th scope="row">c elegido (AG)</th>
          <td className="is-num">{c.toFixed(2)}</td>
        </tr>
        <tr>
          <th scope="row">μ_CA(c)</th>
          <td className="is-num">{membershipAtC.toFixed(2)}</td>
        </tr>
        <tr>
          <th scope="row">Centroide</th>
          <td className="is-num">{centroid.toFixed(2)}</td>
        </tr>
        <tr>
          <th scope="row">r (monto / ahorro total)</th>
          <td className="is-num">{formatR(r)}</td>
        </tr>
        <tr>
          <th scope="row">E (meses de fondo de emergencia)</th>
          <td className="is-num">{formatE(e)}</td>
        </tr>
      </tbody>
    </table>
  )
  const note = assumed ? (
    <p className="iw-chart__assumed">
      Supuesto: no se informaron el ahorro total ni el fondo de emergencia; se asumió una capacidad media.
    </p>
  ) : null
  return (
    <ChartShell
      title={title || 'Capacidad de absorción: conjunto difuso'}
      lead={lead}
      alt={alt}
      table={table}
      facts={facts}
      note={note}
    >
      <GridY ticks={Y_TICKS} sy={sy} left={M.l} right={CHART_WIDTH - M.r} />
      <TicksX ticks={X_TICKS} sx={sx} base={CHART_HEIGHT - M.b} />
      <path d={area} className="iw-c-area" />
      <path d={linePath(curve, sx, sy)} fill="none" className="iw-c-outline" />
      <line x1={sx(centroid)} x2={sx(centroid)} y1={M.t - 14} y2={CHART_HEIGHT - M.b} className="iw-c-mark iw-c-mark--dash" />
      <line x1={sx(c)} x2={sx(c)} y1={M.t - 14} y2={CHART_HEIGHT - M.b} className="iw-c-mark" />
      <circle cx={sx(c)} cy={sy(membershipAtC)} r={4.5} className="iw-c-dot" stroke="var(--ink)" />
      <text
        x={sx(c) + (cLeft ? -10 : 10)}
        y={sy(membershipAtC) + 4}
        textAnchor={cLeft ? 'end' : 'start'}
        className="iw-c-num"
      >
        {membershipAtC.toFixed(2)}
      </text>
      <text x={sx(c) + (cLeft ? -7 : 7)} y={14} textAnchor={cLeft ? 'end' : 'start'} className="iw-c-label iw-c-label--ink">
        {`c = ${c.toFixed(2)} (algoritmo genético)`}
      </text>
      <text
        x={sx(centroid) + (cLeft ? 7 : -7)}
        y={14}
        textAnchor={cLeft ? 'start' : 'end'}
        className="iw-c-label"
        fill="var(--series-2)"
      >
        {`Centroide = ${centroid.toFixed(2)}`}
      </text>
      <AxisLabels
        xLabel="Capacidad de absorción de pérdidas (0 = baja, 1 = alta)"
        yLabel="Grado de pertenencia"
        left={M.l}
        right={CHART_WIDTH - M.r}
        top={M.t}
        bottom={CHART_HEIGHT - M.b}
      />
    </ChartShell>
  )
}
