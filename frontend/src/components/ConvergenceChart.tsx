interface Props {
  historial: number[]
}

export default function ConvergenceChart({ historial }: Props) {
  const w = 560
  const h = 160
  const pad = { l: 46, r: 10, t: 12, b: 24 }

  if (historial.length === 0) return null

  const min = Math.min(...historial)
  const max = Math.max(...historial)
  const rango = max - min || 1e-9

  const x = (i: number) => pad.l + (i / (historial.length - 1)) * (w - pad.l - pad.r)
  const y = (v: number) => pad.t + (1 - (v - min) / rango) * (h - pad.t - pad.b)

  const puntos = historial.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ')

  const ticks = [min, min + rango / 2, max]

  return (
    <div className="convergencia">
      <svg viewBox={`0 0 ${w} ${h}`} role="img" aria-label="Convergencia del algoritmo genético">
        {ticks.map((t) => (
          <g key={t}>
            <line x1={pad.l} x2={w - pad.r} y1={y(t)} y2={y(t)} className="grid" />
            <text x={pad.l - 6} y={y(t) + 4} textAnchor="end" className="tick">
              {t.toFixed(3)}
            </text>
          </g>
        ))}
        <polyline points={puntos} fill="none" className="linea-convergencia" />
        <text x={w / 2} y={h - 6} textAnchor="middle" className="tick">
          Generación (1 a {historial.length})
        </text>
      </svg>
      <p className="nota">
        Evolución del mejor puntaje (fitness) del algoritmo genético por generación: cómo la
        población de portafolios candidatos fue mejorando hasta converger.
      </p>
    </div>
  )
}
