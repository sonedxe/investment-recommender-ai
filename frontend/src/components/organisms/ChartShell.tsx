// Shared frame of the SVG charts (internal helper, not one of the 32 design-system components).
import { useId, type ReactNode } from 'react'
import { CHART_HEIGHT, CHART_WIDTH, type Scale, type Tick } from '../../lib/chart'

export type ChartFact = [label: string, value: string]

interface ChartShellProps {
  title: string
  lead?: string
  /** Text alternative, rendered as the SVG `desc`. */
  alt: string
  facts?: ChartFact[]
  /** Equivalent data table, rendered inside a `details`. */
  table?: ReactNode
  /** Extra content between the facts and the table. */
  note?: ReactNode
  children: ReactNode
}

export function ChartShell({ title, lead, alt, facts, table, note, children }: ChartShellProps) {
  const id = useId()
  return (
    <figure className="iw-chart">
      <figcaption className="iw-chart__title">{title}</figcaption>
      {lead && <p className="iw-chart__lead">{lead}</p>}
      <svg
        viewBox={`0 0 ${CHART_WIDTH} ${CHART_HEIGHT}`}
        className="iw-chart__svg"
        role="img"
        aria-labelledby={`${id}t ${id}d`}
      >
        <title id={`${id}t`}>{title}</title>
        <desc id={`${id}d`}>{alt}</desc>
        {children}
      </svg>
      {facts && (
        <ul className="iw-chart__facts">
          {facts.map(([label, value], i) => (
            <li key={i}>
              {`${label} `}
              <strong>{value}</strong>
            </li>
          ))}
        </ul>
      )}
      {note}
      {table && (
        <details className="iw-chart__details">
          <summary>Ver los mismos datos en tabla</summary>
          {table}
        </details>
      )}
    </figure>
  )
}

export function GridY({ ticks, sy, left, right }: { ticks: Tick[]; sy: Scale; left: number; right: number }) {
  return (
    <>
      {ticks.map((t) => {
        const y = sy(t.v)
        return (
          <g key={`y${t.v}`}>
            <line x1={left} x2={right} y1={y} y2={y} className="iw-c-grid" />
            <text x={left - 8} y={y + 4} textAnchor="end" className="iw-c-tick">
              {t.label}
            </text>
          </g>
        )
      })}
    </>
  )
}

export function TicksX({ ticks, sx, base }: { ticks: Tick[]; sx: Scale; base: number }) {
  return (
    <>
      {ticks.map((t) => {
        const x = sx(t.v)
        return (
          <g key={`x${t.v}`}>
            <line x1={x} x2={x} y1={base} y2={base + 5} className="iw-c-axis" />
            <text x={x} y={base + 20} textAnchor="middle" className="iw-c-tick">
              {t.label}
            </text>
          </g>
        )
      })}
    </>
  )
}

export function AxisLabels({ xLabel, yLabel, left, right, top, bottom }: {
  xLabel: string
  yLabel: string
  left: number
  right: number
  top: number
  bottom: number
}) {
  const midY = (top + bottom) / 2
  return (
    <>
      <text x={(left + right) / 2} y={CHART_HEIGHT - 8} textAnchor="middle" className="iw-c-axislabel">
        {xLabel}
      </text>
      <text x={12} y={midY} textAnchor="middle" transform={`rotate(-90 12 ${midY})`} className="iw-c-axislabel">
        {yLabel}
      </text>
    </>
  )
}
