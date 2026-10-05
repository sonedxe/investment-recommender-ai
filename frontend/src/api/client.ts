// Thin fetch client for the backend `/api/*` routes (proxied by Vite in development).
import type {
  ContextDefaultsResponse,
  InterpretRequest,
  InterpretResponse,
  MarketEstimatesResponse,
  RecommendRequest,
  RecommendResponse,
} from './types'

export type ApiErrorKind = 'network' | 'http' | 'validation' | 'aborted'

/** `network`: no response; `http`: non-2xx status; `validation`: 422 with the server message; `aborted`: cancelled. */
export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status: number | null

  constructor(kind: ApiErrorKind, message: string, status: number | null = null) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind
    this.status = status
  }
}

export interface RequestOptions {
  signal?: AbortSignal
}

const BASE = '/api'

interface ValidationDetail {
  loc?: (string | number)[]
  msg?: string
}

/** FastAPI sends `detail` as a string (HTTPException) or as a list of validation errors. */
function validationMessage(body: unknown): string {
  const detail = (body as { detail?: unknown } | null)?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((d: ValidationDetail) => [d.loc?.slice(1).join('.'), d.msg].filter(Boolean).join(': '))
      .join('; ')
  }
  return 'Datos no válidos'
}

async function request<T>(path: string, init: RequestInit, options: RequestOptions = {}): Promise<T> {
  let res: Response
  try {
    res = await fetch(BASE + path, { ...init, signal: options.signal })
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError') throw new ApiError('aborted', 'Request aborted')
    throw new ApiError('network', err instanceof Error ? err.message : 'Network error')
  }
  if (res.status === 422) {
    const body: unknown = await res.json().catch(() => null)
    throw new ApiError('validation', validationMessage(body), 422)
  }
  if (!res.ok) throw new ApiError('http', `HTTP ${res.status}`, res.status)
  return (await res.json()) as T
}

function post<T>(path: string, body: unknown, options?: RequestOptions): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }, options)
}

export function interpret(body: InterpretRequest, options?: RequestOptions): Promise<InterpretResponse> {
  return post('/interpret', body, options)
}

export function recommend(body: RecommendRequest, options?: RequestOptions): Promise<RecommendResponse> {
  return post('/recommend', body, options)
}

export function getContextDefaults(options?: RequestOptions): Promise<ContextDefaultsResponse> {
  return request('/context/defaults', { method: 'GET' }, options)
}

export function getMarketEstimates(options?: RequestOptions): Promise<MarketEstimatesResponse> {
  return request('/market/estimates', { method: 'GET' }, options)
}
