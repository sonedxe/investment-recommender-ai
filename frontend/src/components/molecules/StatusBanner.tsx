import type { StatusBannerProps } from '../../types/ui'
import { Button } from '../atoms/Button'

const DEFAULT_TITLE: Record<NonNullable<StatusBannerProps['tone']>, string> = {
  error: 'No pudimos completar el cálculo',
  offline: 'Sin conexión a la API',
  empty: 'Necesitamos un poco más de información',
  info: 'Información',
}

/** Errors are announced with role="alert"; every other tone with role="status". */
export function StatusBanner({ tone = 'info', title, action, children }: StatusBannerProps) {
  return (
    <div className={`iw-banner iw-banner--${tone}`} role={tone === 'error' ? 'alert' : 'status'}>
      <div className="iw-banner__body">
        <p className="iw-banner__title">{title || DEFAULT_TITLE[tone]}</p>
        {children && <p className="iw-banner__text">{children}</p>}
      </div>
      {action && (
        <div className="iw-banner__action">
          <Button variant="secondary" size="sm" onClick={action.onClick}>
            {action.label}
          </Button>
        </div>
      )}
    </div>
  )
}
