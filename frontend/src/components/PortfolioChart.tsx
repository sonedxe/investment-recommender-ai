import type { CategoriaPortafolio } from '../api'

const COLORES = ['#4f8ef7', '#9b6ef3', '#35d07f', '#f2b134', '#8b94a7']

function polar(cx: number, cy: number, r: number, angulo: number) {
  return { x: cx + r * Math.cos(angulo), y: cy + r * Math.sin(angulo) }
}

function sectorPath(cx: number, cy: number, r: number, a0: number, a1: number) {
  const p0 = polar(cx, cy, r, a0)
  const p1 = polar(cx, cy, r, a1)
  const grande = a1 - a0 > Math.PI ? 1 : 0
  return `M ${cx} ${cy} L ${p0.x} ${p0.y} A ${r} ${r} 0 ${grande} 1 ${p1.x} ${p1.y} Z`
}

export default function PortfolioChart({ portafolio }: { portafolio: CategoriaPortafolio[] }) {
  const size = 180
  const r = 80
  const cx = size / 2
  const cy = size / 2

  let acumulado = -Math.PI / 2 // empieza arriba
  const sectores = portafolio
    .map((cat, i) => {
      const ang = cat.peso * 2 * Math.PI
      const sector = { ...cat, i, a0: acumulado, a1: acumulado + ang }
      acumulado += ang
      return sector
    })
    .filter((s) => s.peso > 0.0005)

  return (
    <div className="portafolio-grafico">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Distribución del portafolio">
        {sectores.length === 1 ? (
          <circle cx={cx} cy={cy} r={r} fill={COLORES[sectores[0].i % COLORES.length]} />
        ) : (
          sectores.map((s) => (
            <path
              key={s.categoria}
              d={sectorPath(cx, cy, r, s.a0, s.a1)}
              fill={COLORES[s.i % COLORES.length]}
              stroke="#171e2e"
              strokeWidth={1.5}
            >
              <title>{`${s.nombre}: ${(s.peso * 100).toFixed(1)}%`}</title>
            </path>
          ))
        )}
        <circle cx={cx} cy={cy} r={r * 0.55} fill="#171e2e" />
        <text x={cx} y={cy - 4} textAnchor="middle" className="donut-titulo">Portafolio</text>
        <text x={cx} y={cy + 14} textAnchor="middle" className="donut-sub">5 categorías</text>
      </svg>
      <ul className="leyenda">
        {portafolio.map((cat, i) => (
          <li key={cat.categoria}>
            <span className="leyenda-color" style={{ background: COLORES[i % COLORES.length] }} />
            <span className="leyenda-nombre">{cat.nombre}</span>
            <span className="leyenda-pct">{(cat.peso * 100).toFixed(1)}%</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
