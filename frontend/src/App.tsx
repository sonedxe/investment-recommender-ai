import { useEffect, useState } from 'react'
import { fetchPing, type PingResponse } from './api'

const MODULE_LABELS: Record<keyof PingResponse['modules'], string> = {
  generative: 'IA Generativa (API)',
  heuristic: 'Algoritmos Heurísticos',
  uncertainty: 'Razonamiento bajo Incertidumbre',
}

export default function App() {
  const [ping, setPing] = useState<PingResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchPing()
      .then(setPing)
      .catch((e) => setError((e as Error).message))
  }, [])

  return (
    <main>
      <h1>Investment Recommender AI</h1>
      <p className="subtitle">
        Software inteligente · IA generativa + heurística + incertidumbre
      </p>

      <section className="card">
        <h2>Estado de la conexión</h2>
        {error ? (
          <p className="down">Backend no disponible: {error}</p>
        ) : !ping ? (
          <p className="pending">Conectando al backend…</p>
        ) : (
          <div className="modules">
            {(Object.keys(ping.modules) as (keyof PingResponse['modules'])[]).map((key) => {
              const mod = ping.modules[key]
              const label = MODULE_LABELS[key]
              const detail = mod.mode ? ` · modo ${mod.mode}` : ''
              return (
                <div key={key} className="module-row">
                  <span className={`dot ${mod.status === 'ok' ? 'ok' : 'down'}`} />
                  <span className="name">{label}</span>
                  <span className="status">
                    {mod.status === 'ok' ? 'conectado' : mod.status}
                    {detail}
                  </span>
                </div>
              )
            })}
          </div>
        )}
      </section>
    </main>
  )
}