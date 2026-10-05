// Formatting helpers ported from the design system bundle (`num`, `money`, `pctText`, `frac`, `score`).
// Currency: `S/ 1,250.00` (decimal point, comma thousands, space after S/). Negative sign is U+2212.
import type { Category, CategoryId } from '../types/ui'

export const CATEGORIES: readonly Category[] = [
  { id: 'stocks', name: 'Fondos de acciones' },
  { id: 'mixed', name: 'Fondos mixtos' },
  { id: 'debt', name: 'Fondos de deuda' },
  { id: 'bonds', name: 'Bonos soberanos (BTP)' },
  { id: 'term', name: 'Depósito a plazo fijo' },
]

export function categoryName(id: CategoryId, fallback?: string): string {
  return CATEGORIES.find((c) => c.id === id)?.name ?? fallback ?? id
}

export function cx(...parts: (string | false | null | undefined)[]): string {
  return parts.filter(Boolean).join(' ')
}

export function formatNumber(n: number, decimals = 0): string {
  const abs = Math.abs(n).toFixed(decimals)
  const [int, frac] = abs.split('.')
  const grouped = int.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  const sign = n < 0 && Number(abs) !== 0 ? '−' : ''
  return sign + (frac !== undefined ? `${grouped}.${frac}` : grouped)
}

export function formatMoney(n: number, decimals = 2, signed = false): string {
  const sign = n < 0 ? '−' : signed && n > 0 ? '+' : ''
  return `${sign}S/ ${formatNumber(Math.abs(n), decimals)}`
}

/** Percentage given on a 0–100 scale: `25 %`, `12.5 %`. */
export function formatPct(p: number): string {
  return `${formatNumber(p, Number.isInteger(p) ? 0 : 1)} %`
}

/** Percentage given as a fraction: 0.09 -> `9.0 %`. */
export function formatFraction(p: number, decimals = 1): string {
  return `${formatNumber(p * 100, decimals)} %`
}

/** Signed fraction as percentage: 0.005 -> `+0.5 %`, 0 -> `0.0 %`. */
export function formatSignedFraction(p: number, decimals = 1): string {
  const text = formatFraction(p, decimals)
  return p > 0 && Number((p * 100).toFixed(decimals)) !== 0 ? `+${text}` : text
}

/** Fitness contribution with explicit sign and 4 decimals. */
export function formatScore(v: number): string {
  return (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(4)
}
