import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { sample } from '../../fixtures/sample'
import { TechnicalDetail } from './TechnicalDetail'

describe('TechnicalDetail', () => {
  it('shows λ base × m_H = λ efectiva and the cᵢ and source columns', () => {
    render(<TechnicalDetail data={sample.technical} open />)
    expect(screen.getByText('λ efectiva = λ base × m_H = 4.00 × 1.335 = 5.34')).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: 'Ajuste por contexto (cᵢ)' })).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: 'Fuente' })).toBeInTheDocument()
  })

  it('renders the switches only when they are provided', () => {
    const { rerender } = render(<TechnicalDetail data={sample.technical} open />)
    expect(screen.queryByRole('checkbox')).toBeNull()
    rerender(<TechnicalDetail data={sample.technical} open switches={{ fuzzy: true, context: false }} />)
    expect(screen.getByRole('checkbox', { name: 'Lógica difusa' })).toBeChecked()
    expect(screen.getByRole('checkbox', { name: 'Reglas de contexto' })).not.toBeChecked()
  })

  it('ignores toggle events from the nested "ver los mismos datos en tabla" panels', () => {
    const onToggle = vi.fn()
    const { container } = render(<TechnicalDetail data={sample.technical} open onToggle={onToggle} />)
    const nested = container.querySelector('details.iw-chart__details') as HTMLDetailsElement
    nested.open = true
    fireEvent(nested, new Event('toggle'))
    expect(onToggle).not.toHaveBeenCalled()
  })

  it('reports the real open state of its own panel', () => {
    const onToggle = vi.fn()
    const { container } = render(<TechnicalDetail data={sample.technical} open={false} onToggle={onToggle} />)
    const own = container.querySelector('details.iw-tech') as HTMLDetailsElement
    own.open = true
    fireEvent(own, new Event('toggle'))
    expect(onToggle).toHaveBeenCalledWith(true)
  })
})
