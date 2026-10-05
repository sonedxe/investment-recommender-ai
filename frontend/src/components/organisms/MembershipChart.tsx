import type { MembershipChartProps } from '../../types/ui'
import { CHART_HEIGHT, CHART_WIDTH, DASHES, interpolate, linePath, scale, type Tick } from '../../lib/chart'
import { AxisLabels, ChartShell, GridY, TicksX } from './ChartShell'

const M = { l: 52, r: 24, t: 44, b: 52 }
const Y_TICKS: Tick[] = [
  { v: 0, label: '0' },
  { v: 0.5, label: '0.5' },
  { v: 1, label: '1' },
]

export function MembershipChart({ title, series, value, domain = [0, 15], xStep = 3, xLabel }: MembershipChartProps) {
  const sx = scale(domain[0], domain[1], M.l, CHART_WIDTH - M.r)
  const sy = scale(0, 1, CHART_HEIGHT - M.b, M.t)
  const xTicks: Tick[] = []
  for (let v = domain[0]; v <= domain[1]; v += xStep) xTicks.push({ v, label: String(v) })
  const degrees = series.map((s) => ({ id: s.id, name: s.name, value: interpolate(s.points, value) }))
  const alt =
    `Funciones de pertenencia del horizonte de inversión de 0 a ${domain[1]} años. ` +
    `${degrees.map((d) => `${d.name} ${d.value.toFixed(2)}`).join(', ')} para ${value} años.`
  const table = (
    <table className="iw-table">
      <thead>
        <tr>
          <th scope="col">Conjunto</th>
          <th scope="col">Puntos de la función (años: grado)</th>
          <th scope="col" className="is-num">{`Grado en ${value} años`}</th>
        </tr>
      </thead>
      <tbody>
        {series.map((s, i) => (
          <tr key={s.id}>
            <th scope="row">{s.name}</th>
            <td>{s.points.map((q) => `${q.x}: ${q.y.toFixed(2)}`).join(' · ')}</td>
            <td className="is-num">{degrees[i].value.toFixed(2)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
  return (
    <ChartShell
      title={title || 'Horizonte: funciones de pertenencia'}
      alt={alt}
      table={table}
      facts={degrees.map((d) => [`${d.name} en ${value} años:`, d.value.toFixed(2)])}
    >
      <GridY ticks={Y_TICKS} sy={sy} left={M.l} right={CHART_WIDTH - M.r} />
      <TicksX ticks={xTicks} sx={sx} base={CHART_HEIGHT - M.b} />
      {series.map((s, i) => {
        const color = `var(--series-${i + 1})`
        const max = Math.max(...s.points.map((q) => q.y))
        const top = s.points.filter((q) => q.y === max)
        const labelX = top.reduce((a, q) => a + q.x, 0) / top.length
        return (
          <g key={s.id}>
            <path
              d={linePath(s.points, sx, sy)}
              fill="none"
              stroke={color}
              strokeWidth={2.5}
              strokeDasharray={DASHES[i % 3]}
              strokeLinejoin="round"
            />
            <text
              x={Math.min(Math.max(sx(labelX), M.l + 22), CHART_WIDTH - M.r - 30)}
              y={sy(max) - 9}
              textAnchor="middle"
              className="iw-c-label"
              fill={color}
            >
              {s.name}
            </text>
          </g>
        )
      })}
      <line x1={sx(value)} x2={sx(value)} y1={M.t - 14} y2={CHART_HEIGHT - M.b} className="iw-c-mark" />
      <text x={sx(value) + 6} y={14} className="iw-c-label iw-c-label--ink">
        {`Tu horizonte: ${value} años`}
      </text>
      {series.map((s, i) =>
        degrees[i].value > 0 ? (
          <g key={`d${s.id}`}>
            <circle cx={sx(value)} cy={sy(degrees[i].value)} r={4.5} className="iw-c-dot" stroke={`var(--series-${i + 1})`} />
            <text x={sx(value) + 10} y={sy(degrees[i].value) + 4} className="iw-c-num">
              {degrees[i].value.toFixed(2)}
            </text>
          </g>
        ) : null,
      )}
      <AxisLabels
        xLabel={xLabel || 'Horizonte (años)'}
        yLabel="Grado de pertenencia"
        left={M.l}
        right={CHART_WIDTH - M.r}
        top={M.t}
        bottom={CHART_HEIGHT - M.b}
      />
    </ChartShell>
  )
}
