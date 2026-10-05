export interface ModuleStatus {
  module: string
  status: string
  mode?: string
}

export interface PingResponse {
  status: string
  modules: {
    generative: ModuleStatus
    heuristic: ModuleStatus
    uncertainty: ModuleStatus
  }
}

// ---- Interpretación (Módulo 1, entrada) ----

export interface Interpretacion {
  monto_invertir: number | null
  horizonte_anios: number | null
  horizonte_etiqueta: 'corto' | 'mediano' | 'largo' | null
  lambda_base: number | null
  perfil_riesgo: string | null
  ahorro_total: number | null
  cobertura_emergencia_meses: number | null
  absorcion_declinada: boolean
  completo: boolean
  pregunta_aclaracion: string | null
  campos_detectados: Record<string, string>
  modo: string
}

// ---- Recomendación (flujo completo) ----

export interface PerfilUsuario {
  monto_invertir: number
  horizonte_anios: number | null
  horizonte_etiqueta: string | null
  lambda_base: number
  ahorro_total: number | null
  cobertura_emergencia_meses: number | null
  absorcion_declinada: boolean
}

export interface FactoresContexto {
  s_pol: number
  s_mac: number
}

export interface Interruptores {
  difuso: boolean
  contexto: boolean
}

export interface CategoriaPortafolio {
  categoria: string
  nombre: string
  descripcion: string
  peso: number
  monto_soles: number
  mu_base: number
  sigma_base: number
  mu_ajustado: number
  sigma_ajustado: number
  c_ajuste: number
  s_tend: number
}

export interface RecommendResponse {
  explicacion: string
  modo_explicacion: 'offline' | 'api'
  portafolio: CategoriaPortafolio[]
  resultado: {
    fitness: number
    E_portafolio: number
    C_contexto: number
    sigma_portafolio: number
    penalizacion: number
    retorno_esperado: number
    historial_convergencia: number[]
    generaciones: number
    poblacion: number
  }
  difuso: {
    activo: boolean
    pertenencias: Record<string, Record<string, number>>
    m_H: number
    CA: number
    sigma_max: number
    lambda_ef: number
    lambda_base: number
    ca_asumida: boolean
    r: number | null
    E: number | null
  }
  contexto: {
    activo: boolean
    s_pol: number
    s_mac: number
    factores_por_categoria: Record<string, Record<string, number>>
  }
  mercado: {
    mu: number[]
    sigma: number[]
    s_tend: number[]
    covarianza: number[][]
  }
}

// ---- Llamadas a la API ----

async function post<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function fetchPing(): Promise<PingResponse> {
  const res = await fetch('/api/ping')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export function interpret(texto: string): Promise<Interpretacion> {
  return post<Interpretacion>('/api/interpret', { texto })
}

export function recommend(
  perfil: PerfilUsuario,
  contexto: FactoresContexto,
  interruptores: Interruptores,
  seed = 42,
): Promise<RecommendResponse> {
  return post<RecommendResponse>('/api/recommend', { perfil, contexto, interruptores, seed })
}
