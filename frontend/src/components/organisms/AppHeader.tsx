import type { AppHeaderProps } from '../../types/ui'
import { Badge } from '../atoms/Badge'
import { DisclaimerNotice } from '../atoms/DisclaimerNotice'

export function AppHeader({ step, offline }: AppHeaderProps) {
  return (
    <header className="iw-header">
      <div className="iw-header__bar">
        <span className="iw-header__brand">InvestWise</span>
        <span className="iw-header__meta">
          {step && <span className="iw-header__step">{step}</span>}
          {offline && <Badge tone="caution">Modo sin conexión</Badge>}
        </span>
      </div>
      <DisclaimerNotice variant="strip" />
      {offline && (
        <p className="iw-header__offline">
          Sin conexión a la API: se usa el generador local. Los resultados pueden ser menos detallados.
        </p>
      )}
    </header>
  )
}
