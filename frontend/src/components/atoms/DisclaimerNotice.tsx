import type { DisclaimerNoticeProps } from '../../types/ui'

const DEFAULT_TEXT = {
  strip: 'Herramienta de aprendizaje; no es asesoría financiera.',
  block:
    'InvestWise es un proyecto universitario con fines educativos. Los resultados son ejemplos calculados con supuestos y no constituyen asesoría financiera ni una recomendación de inversión. Antes de invertir, consulta con un profesional autorizado.',
} as const

/** Always visible and never dismissible (brand book). */
export function DisclaimerNotice({ variant = 'block', children }: DisclaimerNoticeProps) {
  return (
    <aside className={`iw-disclaimer iw-disclaimer--${variant}`} aria-label="Aviso educativo">
      <strong>Aviso educativo. </strong>
      {children || DEFAULT_TEXT[variant]}
    </aside>
  )
}
