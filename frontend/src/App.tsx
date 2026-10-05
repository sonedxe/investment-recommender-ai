import { useCallback, useEffect, useRef, useState } from 'react'
import {
  interpret,
  recommend,
  type FactoresContexto,
  type Interpretacion,
  type Interruptores,
  type PerfilUsuario,
  type RecommendResponse,
} from './api'
import ContextPanel from './components/ContextPanel'
import ConvergenceChart from './components/ConvergenceChart'
import PortfolioChart from './components/PortfolioChart'
import TechnicalPanel from './components/TechnicalPanel'

const EJEMPLO =
  'Tengo 30 años, quiero invertir S/ 5000 de mis S/ 20000 de ahorro, no me gusta ' +
  'arriesgar mucho y no los necesitaré por unos 3 años, tengo un fondo de emergencia para 4 meses'

export default function App() {
  const [turnos, setTurnos] = useState<string[]>([])
  const [entrada, setEntrada] = useState('')
  const [interpretacion, setInterpretacion] = useState<Interpretacion | null>(null)
  const [recomendacion, setRecomendacion] = useState<RecommendResponse | null>(null)
  const [perfil, setPerfil] = useState<PerfilUsuario | null>(null)
  const [factores, setFactores] = useState<FactoresContexto>({ s_pol: 0, s_mac: 0 })
  const [interruptores, setInterruptores] = useState<Interruptores>({ difuso: true, contexto: true })
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const pedirRecomendacion = useCallback(
    async (p: PerfilUsuario, f: FactoresContexto, i: Interruptores) => {
      setCargando(true)
      setError(null)
      try {
        setRecomendacion(await recommend(p, f, i))
      } catch (e) {
        setError(`No se pudo calcular la recomendación: ${(e as Error).message}. ¿Está el backend encendido?`)
      } finally {
        setCargando(false)
      }
    },
    [],
  )

  const analizar = async () => {
    const texto = entrada.trim()
    if (!texto || cargando) return
    const nuevosTurnos = [...turnos, texto]
    setTurnos(nuevosTurnos)
    setEntrada('')
    setCargando(true)
    setError(null)
    try {
      const interp = await interpret(nuevosTurnos.join('\n'))
      setInterpretacion(interp)
      if (interp.completo) {
        const p: PerfilUsuario = {
          monto_invertir: interp.monto_invertir!,
          horizonte_anios: interp.horizonte_anios,
          horizonte_etiqueta: interp.horizonte_etiqueta,
          lambda_base: interp.lambda_base!,
          ahorro_total: interp.ahorro_total,
          cobertura_emergencia_meses: interp.cobertura_emergencia_meses,
          absorcion_declinada: interp.absorcion_declinada,
        }
        setPerfil(p)
        await pedirRecomendacion(p, factores, interruptores)
      }
    } catch (e) {
      setError(`No se pudo interpretar el texto: ${(e as Error).message}. ¿Está el backend encendido?`)
    } finally {
      setCargando(false)
      inputRef.current?.focus()
    }
  }

  // Si ya hay un perfil completo y cambian los factores o interruptores,
  // recalcular automáticamente (facilita las pruebas de ablación).
  useEffect(() => {
    if (perfil) void pedirRecomendacion(perfil, factores, interruptores)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [factores, interruptores])

  const reiniciar = () => {
    setTurnos([])
    setEntrada('')
    setInterpretacion(null)
    setRecomendacion(null)
    setPerfil(null)
    setFactores({ s_pol: 0, s_mac: 0 })
    setInterruptores({ difuso: true, contexto: true })
    setError(null)
    inputRef.current?.focus()
  }

  const esperandoAclaracion = interpretacion !== null && !interpretacion.completo

  return (
    <main>
      <div className="disclaimer">
        ⚠️ Herramienta <strong>educativa</strong> con fines académicos (curso de Software
        Inteligente). <strong>No es asesoría financiera real.</strong>
      </div>

      <h1>InvestWise</h1>
      <p className="subtitle">
        Recomendador de inversiones con IA · mercado peruano · IA generativa + algoritmo
        genético + razonamiento bajo incertidumbre
      </p>

      <section className="card">
        <h2>{esperandoAclaracion ? 'Necesito un dato más' : 'Cuéntame tu situación'}</h2>

        {turnos.length > 0 && (
          <div className="conversacion">
            {turnos.map((t, i) => (
              <p key={i} className="turno-usuario">🧑 {t}</p>
            ))}
            {esperandoAclaracion && (
              <p className="turno-sistema">🤖 {interpretacion.pregunta_aclaracion}</p>
            )}
          </div>
        )}

        {turnos.length === 0 && (
          <p className="nota">
            Escríbelo con tus palabras: cuánto quieres invertir, por cuánto tiempo no
            necesitarás el dinero, qué tan dispuesto estás a asumir bajadas, cuáles son tus
            ahorros y si tienes un fondo de emergencia. Si falta algo, te preguntaré antes de
            calcular.
          </p>
        )}

        <textarea
          ref={inputRef}
          value={entrada}
          onChange={(e) => setEntrada(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              void analizar()
            }
          }}
          placeholder={
            esperandoAclaracion
              ? 'Escribe tu respuesta… (o “prefiero no decirlo” si es un dato personal)'
              : `Por ejemplo: ${EJEMPLO}`
          }
          rows={esperandoAclaracion ? 2 : 4}
        />
        <div className="acciones">
          <button onClick={() => void analizar()} disabled={cargando || !entrada.trim()}>
            {cargando ? 'Procesando…' : esperandoAclaracion ? 'Responder' : 'Obtener recomendación'}
          </button>
          {turnos.length > 0 && (
            <button className="secundario" onClick={reiniciar} disabled={cargando}>
              Nueva consulta
            </button>
          )}
        </div>
        {error && <p className="down">{error}</p>}
      </section>

      <ContextPanel
        factores={factores}
        interruptores={interruptores}
        onChange={(f, i) => {
          setFactores(f)
          setInterruptores(i)
        }}
      />

      {recomendacion && (
        <>
          <section className="card">
            <h2>Tu recomendación</h2>
            <div className="explicacion">
              {recomendacion.explicacion.split('\n\n').map((p, i) => (
                <p key={i}>{p}</p>
              ))}
            </div>
            <p className="nota">
              Explicación generada en modo {recomendacion.modo_explicacion === 'api' ? 'API (LLM)' : 'offline (sin conexión a API)'}.
            </p>
          </section>

          <section className="card">
            <h2>Distribución del portafolio</h2>
            <PortfolioChart portafolio={recomendacion.portafolio} />
            <table className="tabla-portafolio">
              <thead>
                <tr><th>Categoría</th><th>Peso</th><th>Monto aprox.</th><th>Retorno esp.</th><th>Riesgo</th></tr>
              </thead>
              <tbody>
                {recomendacion.portafolio.map((p) => (
                  <tr key={p.categoria} className={p.peso < 0.005 ? 'atenuado' : ''}>
                    <td>{p.nombre}</td>
                    <td>{(p.peso * 100).toFixed(1)}%</td>
                    <td>S/ {p.monto_soles.toLocaleString('es-PE', { maximumFractionDigits: 0 })}</td>
                    <td>{(p.mu_ajustado * 100).toFixed(1)}%</td>
                    <td>{(p.sigma_ajustado * 100).toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="card">
            <h2>Convergencia del algoritmo genético</h2>
            <ConvergenceChart historial={recomendacion.resultado.historial_convergencia} />
          </section>

          <TechnicalPanel data={recomendacion} />
        </>
      )}

      <footer>
        InvestWise · Proyecto académico — Software Inteligente · Categorías representativas del
        mercado peruano (promedios históricos de referencia), no productos específicos.
      </footer>
    </main>
  )
}
