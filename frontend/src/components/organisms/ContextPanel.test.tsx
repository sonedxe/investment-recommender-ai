import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ContextPanel } from './ContextPanel'

const item = (pct: number) => ({ categoryId: 'bonds' as const, name: 'Bonos soberanos (BTP)', pct, amount: pct * 50 })

describe('ContextPanel', () => {
  it('formats the before and after percentages the same way', () => {
    render(<ContextPanel factors={[]} before={[item(40)]} after={[item(40.000000001)]} changed />)
    const cells = screen.getAllByRole('cell').map((c) => c.textContent)
    expect(cells[0]).toBe('40 % · S/ 2,000.00')
    expect(cells[1]).toBe('40 % · S/ 2,000.00')
  })
})
