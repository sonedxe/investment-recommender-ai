import type { ClarificationScreenProps } from '../../types/ui'
import { DisclaimerNotice } from '../atoms/DisclaimerNotice'
import { AppHeader } from '../organisms/AppHeader'
import { ClarificationForm } from '../organisms/ClarificationForm'

export function ClarificationScreen({ input, offline, ...form }: ClarificationScreenProps) {
  return (
    <div className="iw-screen">
      <AppHeader offline={offline} step="Aclaración" />
      <main className="iw-page">
        <h1 className="iw-h1">Una pregunta más</h1>
        {input && (
          <blockquote className="iw-quote">
            <p className="iw-quote__label">Lo que escribiste</p>
            <p>{`“${input}”`}</p>
          </blockquote>
        )}
        <ClarificationForm {...form} />
      </main>
      <div className="iw-page iw-page--foot">
        <DisclaimerNotice />
      </div>
    </div>
  )
}
