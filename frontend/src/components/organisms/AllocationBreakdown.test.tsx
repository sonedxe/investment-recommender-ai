import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { sample } from '../../fixtures/sample'
import { formatMoney } from '../../lib/format'
import { AllocationBreakdown } from './AllocationBreakdown'

describe('AllocationBreakdown', () => {
  it('shows a total equal to the sum of the amounts when no total is given', () => {
    const items = sample.allocation
    const sum = items.reduce((s, i) => s + i.amount, 0)
    const { container } = render(<AllocationBreakdown items={items} />)
    const total = container.querySelector('.iw-breakdown__total .iw-money')
    expect(total).toHaveTextContent(formatMoney(sum))
    expect(total).toHaveTextContent('S/ 5,000.00')
    expect(screen.getAllByRole('listitem')).toHaveLength(items.length)
  })
})
