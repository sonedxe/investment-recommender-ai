import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Money } from './Money'

describe('Money', () => {
  it('formats soles with comma thousands and two decimals', () => {
    render(<Money value={1250} />)
    expect(screen.getByText('S/ 1,250.00')).toBeInTheDocument()
  })

  it('uses a minus sign for negatives and a plus sign when signed', () => {
    const { rerender } = render(<Money value={-400} />)
    expect(screen.getByText('−S/ 400.00')).toBeInTheDocument()
    rerender(<Money value={520} signed />)
    expect(screen.getByText('+S/ 520.00')).toBeInTheDocument()
  })
})
