import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
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
})
