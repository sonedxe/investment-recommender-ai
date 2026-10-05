import { afterEach, describe, expect, it, vi } from 'vitest'
import { fixtures } from './__fixtures__'
import { ApiError, getContextDefaults, getMarketEstimates, interpret, recommend } from './client'

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

async function caught(promise: Promise<unknown>): Promise<ApiError> {
  try {
    await promise
  } catch (err) {
    if (err instanceof ApiError) return err
    throw err
  }
  throw new Error('expected an ApiError')
}

afterEach(() => vi.unstubAllGlobals())

describe('api client', () => {
  it('posts JSON to /api/interpret and /api/recommend with the abort signal', async () => {
    const fetchMock = vi.fn(async (url: string) =>
      jsonResponse(url.endsWith('/interpret') ? fixtures.interpretRisk() : fixtures.recommendNeutral()),
    )
    vi.stubGlobal('fetch', fetchMock)
    const signal = new AbortController().signal
    const conversation = [{ role: 'user' as const, content: 'Quiero invertir S/ 5000 por 3 años' }]

    expect((await interpret({ conversation }, { signal })).question?.field).toBe('perfil_riesgo')
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit]
    expect(url).toBe('/api/interpret')
    expect(init).toMatchObject({ method: 'POST', signal, headers: { 'Content-Type': 'application/json' } })
    expect(JSON.parse(init.body as string)).toEqual({ conversation })

    const body = { profile: { amount: 5000, risk_profile: 'conservador' as const, horizon_years: 3 }, seed: 42 }
    expect((await recommend(body)).technical.convergence.seed).toBe(42)
    expect(fetchMock.mock.calls[1][0]).toBe('/api/recommend')
  })

  it('gets the context defaults and the market estimates', async () => {
    const fetchMock = vi.fn(async (url: string) =>
      jsonResponse(url.endsWith('/defaults') ? fixtures.contextDefaults() : fixtures.marketEstimates()),
    )
    vi.stubGlobal('fetch', fetchMock)
    expect((await getContextDefaults()).factors).toHaveLength(2)
    expect((await getMarketEstimates()).categories).toHaveLength(5)
    expect(fetchMock.mock.calls.map((c) => c[0])).toEqual(['/api/context/defaults', '/api/market/estimates'])
  })

  it('reports a network failure', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    const err = await caught(getContextDefaults())
    expect([err.kind, err.status]).toEqual(['network', null])
  })

  it('reports an HTTP status', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('boom', { status: 503 })))
    const err = await caught(getContextDefaults())
    expect([err.kind, err.status]).toEqual(['http', 503])
  })

  it('reports a 422 with the validation message', async () => {
    const detail = [{ loc: ['body', 'conversation'], msg: 'List should have at least 1 item', type: 'too_short' }]
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ detail }, 422)))
    const err = await caught(interpret({ conversation: [] }))
    expect([err.kind, err.status, err.message]).toEqual(['validation', 422, 'conversation: List should have at least 1 item'])

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ detail: 'provide exactly one horizon' }, 422)))
    expect((await caught(getContextDefaults())).message).toBe('provide exactly one horizon')
  })

  it('reports an aborted request', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new DOMException('aborted', 'AbortError')))
    expect((await caught(getContextDefaults())).kind).toBe('aborted')
  })
})
