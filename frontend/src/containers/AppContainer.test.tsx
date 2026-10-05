import { fireEvent, render, screen, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { fixtures } from '../api/__fixtures__'
import type { InterpretRequest, RecommendRequest } from '../api/types'
import { AppContainer } from './AppContainer'
import { THEME_STORAGE_KEY } from './useTheme'

const TEXT = 'Tengo S/ 5000 de mis S/ 20000 de ahorro y no los necesito en unos 3 años'

type Reply = unknown | Error

/** fetch mock answering each route from its own queue; records the JSON bodies sent. */
function mockApi(queues: { interpret?: Reply[]; recommend?: Reply[] }) {
  const sent: { interpret: InterpretRequest[]; recommend: RecommendRequest[] } = { interpret: [], recommend: [] }
  const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
    const route = url.replace('/api/', '')
    let reply: Reply
    if (route === 'context/defaults') reply = fixtures.contextDefaults()
    else if (route === 'interpret' || route === 'recommend') {
      sent[route].push(JSON.parse(init?.body as string))
      reply = queues[route]?.shift()
    } else throw new Error(`unexpected ${url}`)
    if (reply instanceof Error) throw reply
    return new Response(JSON.stringify(reply), { status: 200, headers: { 'Content-Type': 'application/json' } })
  })
  vi.stubGlobal('fetch', fetchMock)
  return sent
}

function submitText() {
  fireEvent.change(screen.getByLabelText('Describe tu situación'), { target: { value: TEXT } })
  fireEvent.click(screen.getByRole('button', { name: 'Calcular distribución' }))
}

/** In-memory Storage: the runtime's own localStorage may be missing (it is optional in Node). */
function memoryStorage(): Storage {
  const data = new Map<string, string>()
  return {
    get length() {
      return data.size
    },
    clear: () => data.clear(),
    getItem: (k) => data.get(k) ?? null,
    key: (i) => [...data.keys()][i] ?? null,
    removeItem: (k) => void data.delete(k),
    setItem: (k, v) => void data.set(k, String(v)),
  }
}

beforeEach(() => vi.stubGlobal('localStorage', memoryStorage()))
afterEach(() => vi.unstubAllGlobals())

describe('AppContainer', () => {
  it('runs the full flow: text -> question -> answer -> result -> context change', async () => {
    const sent = mockApi({
      interpret: [fixtures.interpretRisk(), fixtures.interpretAbsorption(), fixtures.interpretRefusal()],
      recommend: [fixtures.recommendNeutral(), fixtures.recommendAdverse()],
    })
    render(<AppContainer />)
    submitText()

    // Risk question: closed options, no skip for a critical field.
    const group = await screen.findByRole('group', { name: fixtures.interpretRisk().question!.text })
    expect(screen.getByText('Modo sin conexión')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Prefiero no responder' })).toBeNull()
    fireEvent.click(screen.getByRole('button', { name: 'Continuar' }))
    expect(screen.getByText('Elige una opción para continuar.')).toBeInTheDocument()
    fireEvent.click(within(group).getByRole('radio', { name: 'Incómodo: prefiero ir a lo seguro' }))
    fireEvent.click(screen.getByRole('button', { name: 'Continuar' }))

    // Absorption question: may be declined once.
    await screen.findByRole('group', { name: fixtures.interpretAbsorption().question!.text })
    expect(sent.interpret[1].conversation).toEqual([
      { role: 'user', content: TEXT },
      { role: 'assistant', content: fixtures.interpretRisk().question!.text, field: 'perfil_riesgo' },
      { role: 'user', content: 'Incómodo: prefiero ir a lo seguro' },
    ])
    expect(screen.getByText('Pregunta 2 de 2')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Prefiero no responder' }))

    // Declared assumption before calculating.
    const confirm = await screen.findByRole('button', { name: 'Continuar con este supuesto' })
    expect(sent.interpret[2].conversation.slice(-2)).toEqual([
      { role: 'assistant', content: fixtures.interpretAbsorption().question!.text, field: 'cobertura_emergencia_meses' },
      { role: 'user', content: 'Prefiero no responder' },
    ])
    expect(screen.getByRole('status')).toHaveTextContent('asumimos una capacidad media')
    fireEvent.click(confirm)

    // Result.
    expect(await screen.findByRole('heading', { level: 2, name: 'Cómo repartir S/ 5,000.00' })).toBeInTheDocument()
    expect(sent.recommend[0]).toEqual({
      profile: { amount: 5000, risk_profile: 'conservador', horizon_years: 3, total_savings: 20000 },
      switches: { fuzzy: true, context: true },
    })
    expect(screen.getByText(fixtures.recommendNeutral().explanation.paragraphs[0])).toBeInTheDocument()

    // Context: factor change recalculates with the same seed and shows before/after.
    fireEvent.click(screen.getByRole('button', { name: 'Ajustar el contexto' }))
    const political = await screen.findByRole('group', { name: 'Panorama político' })
    fireEvent.click(within(political).getByRole('radio', { name: 'Adverso' }))
    expect(await screen.findByRole('heading', { name: 'Antes y después de tu ajuste' })).toBeInTheDocument()
    expect(sent.recommend[1]).toMatchObject({ context: { political: -1, macro: 0 }, seed: 42 })
    expect(screen.getByRole('columnheader', { name: 'Después (ajustado)' })).toBeInTheDocument()

    // Reset to neutral reuses the first result without another request.
    fireEvent.click(screen.getByRole('button', { name: 'Restablecer a Neutral' }))
    expect(screen.getByRole('heading', { name: 'Distribución con el contexto actual' })).toBeInTheDocument()
    expect(sent.recommend).toHaveLength(2)
  })

  it('shows the error state and retries keeping the text', async () => {
    const sent = mockApi({
      interpret: [new TypeError('Failed to fetch'), new TypeError('Failed to fetch'), fixtures.interpretAmount()],
    })
    render(<AppContainer />)
    submitText()

    const alert = await screen.findByRole('alert')
    expect(alert).toHaveTextContent('No pudimos conectar con el servicio')
    expect(screen.getByRole('heading', { level: 1, name: 'No pudimos leer tu situación' })).toBeInTheDocument()

    // Back to the input: the text is still there.
    fireEvent.click(screen.getByRole('button', { name: 'Volver' }))
    expect(screen.getByLabelText('Describe tu situación')).toHaveValue(TEXT)

    fireEvent.click(screen.getByRole('button', { name: 'Calcular distribución' }))
    fireEvent.click(await screen.findByRole('button', { name: 'Intentar de nuevo' }))
    expect(await screen.findByRole('group', { name: fixtures.interpretAmount().question!.text })).toBeInTheDocument()
    expect(sent.interpret.map((r) => r.conversation)).toEqual(Array(3).fill([{ role: 'user', content: TEXT }]))
  })

  it('recalculates with the same seed when a switch changes in the technical detail', async () => {
    const sent = mockApi({
      interpret: [{ ...fixtures.interpretRefusal(), assumptions: [] }],
      recommend: [fixtures.recommendNeutral(), fixtures.recommendSwitchesOff()],
    })
    render(<AppContainer />)
    submitText()
    await screen.findByRole('heading', { level: 2, name: 'Cómo repartir S/ 5,000.00' })
    fireEvent.click(screen.getByText('Ver detalle técnico'))
    fireEvent.click(screen.getByRole('checkbox', { name: 'Lógica difusa' }))
    expect(screen.getByText('Recalculando la distribución…')).toBeInTheDocument()
    expect(await screen.findByText('Difuso apagado')).toBeInTheDocument()
    expect(sent.recommend[1]).toMatchObject({ seed: 42, switches: { fuzzy: false, context: true } })
    expect(screen.queryByText('Recalculando la distribución…')).toBeNull()
  })

  it('starts a new query from the result and from the context screen', async () => {
    mockApi({
      interpret: [{ ...fixtures.interpretRefusal(), assumptions: [] }, { ...fixtures.interpretRefusal(), assumptions: [] }],
      recommend: [fixtures.recommendNeutral(), fixtures.recommendNeutral()],
    })
    render(<AppContainer />)
    submitText()
    await screen.findByRole('heading', { level: 2, name: 'Cómo repartir S/ 5,000.00' })
    fireEvent.click(screen.getByRole('button', { name: 'Nueva consulta' }))
    expect(screen.getByLabelText('Describe tu situación')).toHaveValue('')

    submitText()
    await screen.findByRole('heading', { level: 2, name: 'Cómo repartir S/ 5,000.00' })
    fireEvent.click(screen.getByRole('button', { name: 'Ajustar el contexto' }))
    await screen.findByRole('group', { name: 'Panorama político' })
    fireEvent.click(screen.getByRole('button', { name: 'Nueva consulta' }))
    expect(screen.getByLabelText('Describe tu situación')).toHaveValue('')
  })

  it('asks for text before calling the API', () => {
    const sent = mockApi({})
    render(<AppContainer />)
    fireEvent.click(screen.getByRole('button', { name: 'Calcular distribución' }))
    expect(screen.getByRole('status')).toHaveTextContent('No pudimos interpretar tu texto')
    expect(sent.interpret).toHaveLength(0)
  })

  it('toggles and persists the theme', () => {
    mockApi({})
    render(<AppContainer />)
    const before = document.documentElement.dataset.theme
    fireEvent.click(screen.getByRole('button', { name: /Usar tema/ }))
    const after = document.documentElement.dataset.theme
    expect(after).not.toBe(before)
    expect(window.localStorage.getItem(THEME_STORAGE_KEY)).toBe(after)
  })

  it('starts from the stored theme and survives a storage that throws', () => {
    mockApi({})
    window.localStorage.setItem(THEME_STORAGE_KEY, 'dark')
    const { unmount } = render(<AppContainer />)
    expect(document.documentElement.dataset.theme).toBe('dark')
    unmount()

    const broken = memoryStorage()
    broken.getItem = () => {
      throw new Error('blocked')
    }
    broken.setItem = broken.getItem
    vi.stubGlobal('localStorage', broken)
    render(<AppContainer />)
    fireEvent.click(screen.getByRole('button', { name: /Usar tema/ }))
    expect(['light', 'dark']).toContain(document.documentElement.dataset.theme)
  })
})
