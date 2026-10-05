import { describe, expect, it } from 'vitest'
import { formatPct } from './format'

describe('formatPct', () => {
  it('shows one decimal only when the rounded value needs it', () => {
    expect(formatPct(40)).toBe('40 %')
    expect(formatPct(40.000000001)).toBe('40 %')
    expect(formatPct(39.96)).toBe('40 %')
    expect(formatPct(12.5)).toBe('12.5 %')
    expect(formatPct(0.3)).toBe('0.3 %')
  })
})
