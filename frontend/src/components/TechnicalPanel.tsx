import type { RecommendResponse } from '../api'

const pct = (v: number) => `${(v * 100).toFixed(2)}%`
const num = (v: number) => v.toFixed(3)

export default function TechnicalPanel({ data }: { data: RecommendResponse }) {
  const { difuso, contexto, resultado, mercado, portafolio } = data

  return (
    <details className="card tecnico">
      <summary>Ver detalle técnico (para usuarios avanzados y evaluadores)</summary>

      <h3>Descomposición del fitness (modelo ampliado, sección 5.2)</h3>
      <table>
        <tbody>
          <tr><td>Retorno histórico E(P) = Σ wᵢ·μᵢ</td><td>{pct(resultado.E_portafolio)}</td></tr>
          <tr><td>Término contextual C(P) = Σ wᵢ·cᵢ</td><td>{pct(resultado.C_contexto)}</td></tr>
          <tr><td>Riesgo σ′(P) con covarianza ajustada</td><td>{pct(resultado.sigma_portafolio)}</td></tr>
          <tr><td>Penalización φ·max(0, σ′ − σmáx)²</td><td>{resultado.penalizacion.toFixed(4)}</td></tr>
          <tr><td><strong>Fitness final</strong></td><td><strong>{resultado.fitness.toFixed(4)}</strong></td></tr>
        </tbody>
      </table>

      <h3>Módulo difuso {difuso.activo ? '' : '(desactivado)'}</h3>
      <table>
        <tbody>
          <tr>
            <td>Pertenencias del horizonte</td>
            <td>
              corto {num(difuso.pertenencias.horizonte?.corto ?? 0)} · mediano{' '}
              {num(difuso.pertenencias.horizonte?.mediano ?? 0)} · largo{' '}
              {num(difuso.pertenencias.horizonte?.largo ?? 0)}
            </td>
          </tr>
          <tr><td>Multiplicador de aversión m_H</td><td>{difuso.m_H.toFixed(3)}</td></tr>
          <tr><td>λ base → λ efectivo</td><td>{difuso.lambda_base} → {difuso.lambda_ef.toFixed(3)}</td></tr>
          <tr>
            <td>Capacidad de absorción CA{difuso.ca_asumida ? ' (asumida: Media)' : ''}</td>
            <td>{difuso.CA.toFixed(3)}</td>
          </tr>
          <tr><td>Volatilidad máxima tolerable σmáx</td><td>{pct(difuso.sigma_max)}</td></tr>
          {difuso.r != null && difuso.E != null && (
            <tr>
              <td>r = monto/ahorro · E = meses emergencia</td>
              <td>{difuso.r.toFixed(3)} · {difuso.E}</td>
            </tr>
          )}
        </tbody>
      </table>

      <h3>Reglas de contexto {contexto.activo ? '' : '(desactivadas)'}</h3>
      <p className="nota">
        s_pol = {contexto.s_pol} · s_mac = {contexto.s_mac}. Ajustes cᵢ por categoría:
      </p>
      <table>
        <thead>
          <tr><th>Categoría</th><th>cᵢ</th><th>μ → μ′</th><th>σ → σ′</th><th>Tendencia</th></tr>
        </thead>
        <tbody>
          {portafolio.map((p, i) => (
            <tr key={p.categoria}>
              <td>{p.nombre}</td>
              <td>{pct(p.c_ajuste)}</td>
              <td>{pct(p.mu_base)} → {pct(p.mu_ajustado)}</td>
              <td>{pct(p.sigma_base)} → {pct(p.sigma_ajustado)}</td>
              <td>{mercado.s_tend[i].toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Algoritmo genético</h3>
      <p className="nota">
        Población de {resultado.poblacion} portafolios, {resultado.generaciones} generaciones,
        selección por torneo, cruce por promedio ponderado y mutación ~10% con reajuste a 100%.
      </p>

      <h3>Matriz de covarianza estimada (módulo bayesiano)</h3>
      <table>
        <thead>
          <tr><th></th>{portafolio.map((p) => <th key={p.categoria}>{p.nombre.split(' ')[0]}</th>)}</tr>
        </thead>
        <tbody>
          {mercado.covarianza.map((fila, i) => (
            <tr key={i}>
              <td>{portafolio[i].nombre.split(' ')[0]}</td>
              {fila.map((v, j) => <td key={j}>{v.toFixed(5)}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </details>
  )
}
