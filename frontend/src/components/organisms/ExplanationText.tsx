import type { ExplanationTextProps } from '../../types/ui'
import { formatMoney } from '../../lib/format'

export function ExplanationText({ title, paragraphs, scenarios = [] }: ExplanationTextProps) {
  return (
    <section className="iw-explain">
      <h2 className="iw-h2">{title || 'Por qué esta distribución'}</h2>
      {paragraphs.map((text, i) => (
        <p key={i} className="iw-explain__p">
          {text}
        </p>
      ))}
      {scenarios.length > 0 && (
        <div className="iw-scen">
          <h3 className="iw-h3">Qué podría pasar en un año (estimado)</h3>
          <dl className="iw-scen__list">
            {scenarios.map((s, i) => (
              <div key={i} className="iw-scen__row">
                <dt>{s.label}</dt>
                <dd>
                  <span className="iw-scen__text">{s.text}</span>
                  <span className="iw-money iw-money--strong">{formatMoney(s.amount, 2, true)}</span>
                </dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </section>
  )
}
