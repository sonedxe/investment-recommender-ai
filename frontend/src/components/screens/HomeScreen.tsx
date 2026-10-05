import type { HomeScreenProps } from '../../types/ui'
import { Button } from '../atoms/Button'
import { DisclaimerNotice } from '../atoms/DisclaimerNotice'
import { TextArea } from '../atoms/TextArea'
import { StatusBanner } from '../molecules/StatusBanner'
import { AppHeader } from '../organisms/AppHeader'

export function HomeScreen({ value, onChange, onSubmit, example, onUseExample, offline, error }: HomeScreenProps) {
  return (
    <div className="iw-screen">
      <AppHeader offline={offline} />
      <main className="iw-page iw-home">
        <div className="iw-home__intro">
          <h1 className="iw-h1">Reparte tu dinero entre cinco tipos de inversión</h1>
          <p className="iw-lead">
            Cuéntanos con tus palabras cuánto quieres invertir, por cuánto tiempo y cuánto riesgo aceptas. Te mostramos
            una distribución de ejemplo en soles y te explicamos cada parte.
          </p>
          <ol className="iw-steps">
            <li>
              <strong>Describes tu situación. </strong>Sin formularios largos.
            </li>
            <li>
              <strong>Te preguntamos solo lo que falta. </strong>Una pregunta a la vez.
            </li>
            <li>
              <strong>Recibes la distribución y su explicación. </strong>Con los supuestos a la vista.
            </li>
          </ol>
        </div>
        <form
          className="iw-home__form"
          onSubmit={(e) => {
            e.preventDefault()
            onSubmit?.()
          }}
        >
          {error && (
            <StatusBanner tone="empty" title={error.title}>
              {error.text}
            </StatusBanner>
          )}
          <TextArea
            label="Describe tu situación"
            rows={6}
            value={value}
            onChange={onChange}
            placeholder={example}
            hint="Puedes mencionar el monto, cuánto tienes ahorrado en total, cuándo podrías necesitar el dinero y cuánto riesgo te incomoda."
          />
          {example && (
            <div className="iw-example">
              <p className="iw-example__label">Ejemplo</p>
              <p className="iw-example__text">{`“${example}”`}</p>
              <Button variant="quiet" size="sm" onClick={onUseExample}>
                Usar este ejemplo
              </Button>
            </div>
          )}
          <Button type="submit" variant="primary">
            Calcular distribución
          </Button>
        </form>
      </main>
      <div className="iw-page iw-page--foot">
        <DisclaimerNotice />
      </div>
    </div>
  )
}
