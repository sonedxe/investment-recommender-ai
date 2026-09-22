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

export async function fetchPing(): Promise<PingResponse> {
  const res = await fetch('/api/ping')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function fetchHealth(): Promise<{ status: string }> {
  const res = await fetch('/health')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}