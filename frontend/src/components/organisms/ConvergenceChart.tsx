import type { ConvergenceChartProps } from '../../types/ui'
import { CHART_HEIGHT, CHART_WIDTH, linePath, scale, type Tick } from '../../lib/chart'
import { AxisLabels, ChartShell, GridY, TicksX } from './ChartShell'

const M = { l: 60, r: 24, t: 32, b: 52 }

export function ConvergenceChart({ title, values }: ConvergenceChartProps) {
  const n = values.length
  // Guard added in the port: the bundle assumed at least one generation.
  if (n === 0) return null
  const lo = Math.floor(Math.min(...values) * 100) / 100
  const hi = Math.ceil(Math.max(...values) * 100) / 100
  const sx = scale(1, Math.max(n, 2), M.l, CHART_WIDTH - M.r)
  const sy = scale(lo, hi === lo ? lo + 0.01 : hi, CHART_HEIGHT - M.b, M.t)
  const yTicks: Tick[] = [0, 1, 2, 3].map((i) => {
    const v = lo + ((hi - lo) * i) / 3
    return { v, label: v.toFixed(3) }
  })
  const xTicks: Tick[] = [1, 25, 50, 75, 100].filter((g) => g <= n).map((g) => ({ v: g, label: String(g) }))
  const points = values.map((v, i) => ({ x: i + 1, y: v }))
  const first = points[0]
  const last = points[points.length - 1]
  const generations = [1, 5, 10, 20, 30, 50, 75, 100].filter((g) => g <= n)
  const alt =
    `Mejor puntaje del portafolio por generación del algoritmo genético, de ${first.y.toFixed(4)} en la generación 1 ` +
    `a ${last.y.toFixed(4)} en la generación ${n}.`
  const table = (
    <table className="iw-table">
      <thead>
        <tr>
          <th scope="col">Generación</th>
          <th scope="col" className="is-num">
            Mejor puntaje
          </th>
        </tr>
      </thead>
      <tbody>
        {generations.map((g) => (
          <tr key={g}>
            <th scope="row">{g}</th>
            <td className="is-num">{values[g - 1].toFixed(4)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
  return (
    <ChartShell
      title={title || 'Convergencia del algoritmo genético'}
      alt={alt}
      table={table}
      facts={[
        ['Generaciones:', String(n)],
        ['Mejor puntaje final:', last.y.toFixed(4)],
      ]}
    >
      <GridY ticks={yTicks} sy={sy} left={M.l} right={CHART_WIDTH - M.r} />
      <TicksX ticks={xTicks} sx={sx} base={CHART_HEIGHT - M.b} />
      <path d={linePath(points, sx, sy)} fill="none" className="iw-c-outline iw-c-outline--thick" />
      <circle cx={sx(first.x)} cy={sy(first.y)} r={4} className="iw-c-dot" stroke="var(--accent)" />
      <circle cx={sx(last.x)} cy={sy(last.y)} r={4.5} className="iw-c-fill" />
      <text x={sx(first.x) + 8} y={sy(first.y) - 8} className="iw-c-num">
        {`Inicio: ${first.y.toFixed(4)}`}
      </text>
      <text x={sx(last.x) - 8} y={sy(last.y) + 20} textAnchor="end" className="iw-c-label iw-c-label--ink">
        {`Final: ${last.y.toFixed(4)}`}
      </text>
      <AxisLabels
        xLabel="Generación"
        yLabel="Mejor puntaje"
        left={M.l}
        right={CHART_WIDTH - M.r}
        top={M.t}
        bottom={CHART_HEIGHT - M.b}
      />
    </ChartShell>
  )
}
