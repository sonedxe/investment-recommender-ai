import type { FactoresContexto, Interruptores } from '../api'

interface Props {
  factores: FactoresContexto
  interruptores: Interruptores
  onChange: (factores: FactoresContexto, interruptores: Interruptores) => void
}

const OPCIONES = [
  { valor: -1, etiqueta: 'Adverso' },
  { valor: 0, etiqueta: 'Neutral' },
  { valor: 1, etiqueta: 'Favorable' },
]

function FactorSelector({
  titulo,
  ayuda,
  valor,
  onChange,
}: {
  titulo: string
  ayuda: string
  valor: number
  onChange: (v: number) => void
}) {
  return (
    <div className="factor">
      <div className="factor-header">
        <span className="factor-titulo">{titulo}</span>
        <span className="factor-ayuda" title={ayuda}>?</span>
      </div>
      <div className="factor-opciones">
        {OPCIONES.map((op) => (
          <button
            key={op.valor}
            type="button"
            className={`factor-opcion ${valor === op.valor ? 'seleccionada' : ''} ${
              op.valor < 0 ? 'adverso' : op.valor > 0 ? 'favorable' : 'neutral'
            }`}
            onClick={() => onChange(op.valor)}
          >
            {op.etiqueta}
          </button>
        ))}
      </div>
      <input
        type="range"
        min={-1}
        max={1}
        step={0.25}
        value={valor}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-label={`${titulo} (ajuste fino)`}
      />
      <span className="factor-valor">{valor > 0 ? `+${valor}` : valor}</span>
    </div>
  )
}

export default function ContextPanel({ factores, interruptores, onChange }: Props) {
  return (
    <section className="card">
      <h2>Factores de contexto</h2>
      <p className="nota">
        Supuestos del entorno que ajustan la recomendación. No son predicciones: son
        escenarios que puedes modificar. Por defecto, todo está en Neutral.
      </p>
      <div className="factores">
        <FactorSelector
          titulo="Panorama político"
          ayuda="Qué tan favorable es el entorno político para invertir. Adverso baja retornos esperados y sube el riesgo, sobre todo en acciones."
          valor={factores.s_pol}
          onChange={(v) => onChange({ ...factores, s_pol: v }, interruptores)}
        />
        <FactorSelector
          titulo="Estabilidad económica"
          ayuda="Inflación y tasas estables (favorable) o inestables (adverso)."
          valor={factores.s_mac}
          onChange={(v) => onChange({ ...factores, s_mac: v }, interruptores)}
        />
      </div>
      <details className="interruptores">
        <summary>Opciones avanzadas (pruebas de ablación)</summary>
        <label>
          <input
            type="checkbox"
            checked={interruptores.difuso}
            onChange={(e) =>
              onChange(factores, { ...interruptores, difuso: e.target.checked })
            }
          />
          Ajuste gradual del perfil (lógica difusa)
        </label>
        <label>
          <input
            type="checkbox"
            checked={interruptores.contexto}
            onChange={(e) =>
              onChange(factores, { ...interruptores, contexto: e.target.checked })
            }
          />
          Ajuste por contexto (factores ambientales)
        </label>
      </details>
    </section>
  )
}
