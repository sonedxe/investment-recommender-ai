import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { sample } from '../../fixtures/sample'
import { RulesTable } from './RulesTable'

describe('RulesTable', () => {
  it('shows α for fuzzy rules and no α for context rules', () => {
    render(<RulesTable rules={sample.rules} />)
    const row = (id: string) => screen.getByText(id).closest('tr') as HTMLElement
    expect(within(row('RH1')).getByText('α = 0.67')).toBeInTheDocument()
    expect(within(row('RA2')).getByText('α = 0.33')).toBeInTheDocument()
    expect(row('RC1').textContent).not.toMatch(/α/)
    expect(within(row('RC1')).getByText('No aplica (regla nítida)')).toBeInTheDocument()
  })

  it('groups the rules by kind', () => {
    render(<RulesTable rules={sample.rules} />)
    expect(screen.getByRole('columnheader', { name: 'Horizonte · reglas difusas (RH)' })).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: 'Capacidad de absorción · reglas difusas (RA)' })).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: 'Contexto · reglas nítidas (RC)' })).toBeInTheDocument()
  })
})
