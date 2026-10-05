import { describe, expect, it } from 'vitest'
import { generationTicks } from './chart'

describe('generationTicks', () => {
  it('reaches past 100 when more generations ran', () => {
    expect(generationTicks(150).map((t) => t.v)).toEqual([1, 50, 100, 150])
    expect(generationTicks(230).map((t) => t.v)).toEqual([1, 50, 100, 150, 200])
  })

  it('uses a nice step for short runs', () => {
    expect(generationTicks(100).map((t) => t.v)).toEqual([1, 20, 40, 60, 80, 100])
    expect(generationTicks(48).map((t) => t.v)).toEqual([1, 10, 20, 30, 40])
    expect(generationTicks(1).map((t) => t.v)).toEqual([1])
    expect(generationTicks(150).map((t) => t.label)).toEqual(['1', '50', '100', '150'])
  })
})
