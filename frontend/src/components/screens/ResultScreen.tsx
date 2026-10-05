import type { ResultScreenProps } from '../../types/ui'
import { formatMoney } from '../../lib/format'
import { Button } from '../atoms/Button'
import { DisclaimerNotice } from '../atoms/DisclaimerNotice'
import { AssumptionList } from '../molecules/AssumptionList'
import { AllocationBreakdown } from '../organisms/AllocationBreakdown'
import { AppHeader } from '../organisms/AppHeader'
import { ExplanationText } from '../organisms/ExplanationText'
import { TechnicalDetail } from '../organisms/TechnicalDetail'

export function ResultScreen(props: ResultScreenProps) {
  const { summary, total, allocation, assumptions, explanation, technical, technicalOpen, onAdjust, offline } = props
  return (
    <div className="iw-screen">
      <AppHeader offline={offline} step="Resultado" />
      <main className="iw-page">
        <h1 className="iw-h1">Tu distribución de ejemplo</h1>
        <p className="iw-lead">{summary}</p>
        <div className="iw-result">
          <div className="iw-result__main">
            <AllocationBreakdown items={allocation} total={total} title={`Cómo repartir ${formatMoney(total)}`} />
          </div>
          <aside className="iw-result__side">
            <AssumptionList items={assumptions} />
            <Button variant="secondary" full onClick={onAdjust}>
              Ajustar el contexto
            </Button>
          </aside>
        </div>
        <ExplanationText {...explanation} />
        <TechnicalDetail
          data={technical}
          open={technicalOpen}
          switches={props.switches}
          onSwitchesChange={props.onSwitchesChange}
        />
        <DisclaimerNotice />
      </main>
    </div>
  )
}
