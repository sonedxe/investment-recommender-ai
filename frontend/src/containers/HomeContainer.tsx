import { HomeScreen } from '../components'

export const EXAMPLE_INPUT =
  'Tengo S/ 5,000 de mis S/ 20,000 de ahorro, no me gusta arriesgar y no los voy a necesitar en unos 3 años'

const EMPTY_ERROR = {
  title: 'No pudimos interpretar tu texto',
  text: 'Cuéntanos al menos cuánto dinero quieres invertir. Por ejemplo: Tengo S/ 5,000 y no me gusta arriesgar.',
}

export interface HomeContainerProps {
  text: string
  empty: boolean
  offline: boolean
  onChange: (text: string) => void
  onSubmit: () => void
}

export function HomeContainer({ text, empty, offline, onChange, onSubmit }: HomeContainerProps) {
  return (
    <HomeScreen
      value={text}
      onChange={onChange}
      onSubmit={onSubmit}
      example={EXAMPLE_INPUT}
      onUseExample={() => onChange(EXAMPLE_INPUT)}
      offline={offline}
      error={empty ? EMPTY_ERROR : undefined}
    />
  )
}
