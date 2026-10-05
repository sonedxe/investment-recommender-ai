import type { ReactNode } from 'react'
import type { TechnicalDetailProps } from '../../types/ui'
import { Switches } from '../molecules/Switches'
import { AbsorptionChart } from './AbsorptionChart'
import { ConvergenceChart } from './ConvergenceChart'
import { MembershipChart } from './MembershipChart'
import { ParameterTable } from './ParameterTable'
import { RulesTable } from './RulesTable'
import { ScoreBreakdown } from './ScoreBreakdown'

function Section({ title, desc, children }: { title: string; desc?: string; children: ReactNode }) {
  return (
    <section className="iw-tech__sec">
      <h3 className="iw-h3">{title}</h3>
      {desc && <p className="iw-tech__desc">{desc}</p>}
      {children}
    </section>
  )
}

function Figure({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="iw-lambda__label">{label}</p>
      <p className="iw-lambda__value">{value}</p>
    </div>
  )
}

/** Collapsed by default; native `summary` works with keyboard and screen readers. */
export function TechnicalDetail({ data, open, onToggle, switches, onSwitchesChange }: TechnicalDetailProps) {
  return (
    <details className="iw-tech" open={!!open} onToggle={onToggle}>
      <summary className="iw-tech__summary">
        <span>Ver detalle técnico</span>
        <span className="iw-tech__hint">Para evaluación académica</span>
      </summary>
      <div className="iw-tech__body">
        {switches && (
          <Section
            title="Interruptores del cálculo"
            desc="Apaga un módulo para ver cómo cambia el resultado sin él. Sirve para comparar, no para decidir."
          >
            <Switches value={switches} onChange={onSwitchesChange} />
          </Section>
        )}
        <Section title="Retorno esperado (μ) y riesgo (σ)" desc="Valores por categoría antes y después del ajuste por contexto.">
          <ParameterTable rows={data.params} />
        </Section>
        <Section title="Aversión al riesgo (λ)" desc="La aversión declarada se ajusta según el horizonte del usuario.">
          <div className="iw-lambda">
            <Figure label="λ base (declarada)" value={data.lambdaBase.toFixed(2)} />
            <span className="iw-lambda__op" aria-hidden="true">
              ×
            </span>
            <Figure label="m_H (multiplicador por horizonte)" value={data.mH.toFixed(3)} />
            <span className="iw-lambda__arrow" aria-hidden="true">
              →
            </span>
            <Figure label="λ efectiva (tras horizonte)" value={data.lambdaEff.toFixed(2)} />
          </div>
          <p className="iw-sr">
            {`λ efectiva = λ base × m_H = ${data.lambdaBase.toFixed(2)} × ${data.mH.toFixed(3)} = ${data.lambdaEff.toFixed(2)}`}
          </p>
        </Section>
        <Section title="Horizonte difuso" desc="Pertenencia del horizonte del usuario a cada conjunto.">
          <MembershipChart {...data.membership} />
        </Section>
        <Section
          title="Capacidad de absorción"
          desc="Gráfico clave: conjunto difuso agregado, el valor c elegido por el algoritmo genético y el centroide."
        >
          <AbsorptionChart {...data.absorption} />
        </Section>
        <Section title="Reglas activadas">
          <RulesTable rules={data.rules} />
        </Section>
        <Section title="Desglose del puntaje" desc="Cómo se compone el puntaje del portafolio elegido.">
          <ScoreBreakdown {...data.score} />
        </Section>
        <Section title="Convergencia">
          <ConvergenceChart {...data.convergence} />
        </Section>
      </div>
    </details>
  )
}
