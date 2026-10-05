// Component gallery (dev aid, reachable at /?gallery and not linked from the UI): every screen rendered with fixtures.
import { useEffect, useState } from 'react'
import {
  AppHeader,
  Button,
  ClarificationScreen,
  ContextScreen,
  DisclaimerNotice,
  HomeScreen,
  LoadingState,
  ResultScreen,
  StatusBanner,
} from '../components'
import { sample } from '../fixtures/sample'
import type { ContextLevel, Factor, SwitchState } from '../types/ui'

type Theme = 'light' | 'dark'
type View = 'home' | 'clarify' | 'assume' | 'result' | 'context' | 'states'

const VIEWS: { id: View; label: string }[] = [
  { id: 'home', label: 'Inicio' },
  { id: 'clarify', label: 'Aclaración' },
  { id: 'assume', label: 'Aclaración con supuesto' },
  { id: 'result', label: 'Resultado' },
  { id: 'context', label: 'Contexto' },
  { id: 'states', label: 'Estados' },
]

function StatesGallery() {
  return (
    <>
      <div className="iw-screen">
        <AppHeader step="Cálculo" />
        <main className="iw-page">
          <h1 className="iw-h1">Calculando</h1>
          <LoadingState steps={sample.loadingSteps} />
        </main>
      </div>
      <div className="iw-screen">
        <AppHeader step="Cálculo" />
        <main className="iw-page">
          <h1 className="iw-h1">No pudimos calcular</h1>
          <StatusBanner tone="error" action={{ label: 'Intentar de nuevo' }}>
            {sample.serviceErrorText}
          </StatusBanner>
          <DisclaimerNotice />
        </main>
      </div>
      <HomeScreen offline example={sample.exampleInput} />
      <HomeScreen example={sample.exampleInput} value="hola" error={sample.emptyInputError} />
    </>
  )
}

export default function Gallery() {
  const [theme, setTheme] = useState<Theme>('light')
  const [view, setView] = useState<View>('home')
  const [text, setText] = useState('')
  const [answer, setAnswer] = useState('1-3')
  const [factors, setFactors] = useState<Factor[]>(sample.factors)
  const [switches, setSwitches] = useState<SwitchState>({ fuzzy: true, context: true })

  useEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])

  const changed = factors.some((f) => f.value !== 'neutral')
  const setFactor = (id: string, value: ContextLevel) =>
    setFactors((prev) => prev.map((f) => (f.id === id ? { ...f, value } : f)))

  return (
    <div className="iw-root">
      <nav aria-label="Galería de componentes" className="iw-page iw-actions" style={{ paddingBlock: 0 }}>
        {VIEWS.map((v) => (
          <Button key={v.id} size="sm" variant={view === v.id ? 'primary' : 'secondary'} onClick={() => setView(v.id)}>
            {v.label}
          </Button>
        ))}
        <Button size="sm" variant="quiet" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
          {theme === 'light' ? 'Tema oscuro' : 'Tema claro'}
        </Button>
      </nav>
      {view === 'home' && (
        <HomeScreen
          value={text}
          onChange={setText}
          example={sample.exampleInput}
          onUseExample={() => setText(sample.exampleInput)}
        />
      )}
      {view === 'clarify' && (
        <ClarificationScreen
          input="Tengo S/ 5,000 y no me gusta arriesgar."
          understood={sample.understoodAsk}
          step={1}
          totalSteps={2}
          question={sample.question}
          value={answer}
          onChange={setAnswer}
        />
      )}
      {view === 'assume' && (
        <ClarificationScreen
          input="Tengo S/ 5,000, no me gusta arriesgar y no los necesito por 3 años."
          understood={sample.understoodAssume}
          step={2}
          totalSteps={2}
          assumption={sample.assumptionText}
        />
      )}
      {view === 'result' && (
        <ResultScreen
          summary={sample.summary}
          total={sample.total}
          allocation={sample.allocation}
          assumptions={sample.assumptions}
          explanation={sample.explanation}
          technical={sample.technical}
          onAdjust={() => setView('context')}
          switches={switches}
          onSwitchesChange={setSwitches}
        />
      )}
      {view === 'context' && (
        <ContextScreen
          factors={factors}
          onChange={setFactor}
          before={sample.allocation}
          after={changed ? sample.allocationAdverse : sample.allocation}
          changed={changed}
          beforeLabel={changed ? 'Antes (Neutral)' : undefined}
          afterLabel={changed ? 'Después (ajustado)' : undefined}
          onBack={() => setView('result')}
          onReset={() => setFactors(sample.factors)}
        />
      )}
      {view === 'states' && <StatesGallery />}
    </div>
  )
}
