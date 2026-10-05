import type { ContextScreenProps } from '../../types/ui'
import { Button } from '../atoms/Button'
import { DisclaimerNotice } from '../atoms/DisclaimerNotice'
import { AppHeader } from '../organisms/AppHeader'
import { ContextPanel } from '../organisms/ContextPanel'

export function ContextScreen({ onBack, onReset, offline, ...panel }: ContextScreenProps) {
  return (
    <div className="iw-screen">
      <AppHeader offline={offline} step="Contexto" />
      <main className="iw-page">
        <h1 className="iw-h1">Ajusta el contexto</h1>
        <p className="iw-lead">
          Cambia estos supuestos para ver cómo se reparte tu dinero en otros escenarios. La distribución se recalcula al
          elegir.
        </p>
        <ContextPanel {...panel} />
        <div className="iw-actions">
          <Button variant="primary" onClick={onBack}>
            Volver al resultado
          </Button>
          <Button variant="quiet" onClick={onReset}>
            Restablecer a Neutral
          </Button>
        </div>
        <DisclaimerNotice />
      </main>
    </div>
  )
}
