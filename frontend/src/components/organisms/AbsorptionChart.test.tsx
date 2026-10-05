import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { sample } from '../../fixtures/sample'
import { AbsorptionChart } from './AbsorptionChart'

describe('AbsorptionChart', () => {
  it('exposes c, centroid and μ_CA(c) in its equivalent table', () => {
    const data = sample.absorption
    render(<AbsorptionChart {...data} />)
    const table = screen.getByRole('table')
    expect(table.closest('details')).not.toBeNull()
    const cell = (header: string) => screen.getByRole('rowheader', { name: header }).nextElementSibling
    expect(cell('c elegido (AG)')).toHaveTextContent(data.c.toFixed(2))
    expect(cell('Centroide')).toHaveTextContent(data.centroid.toFixed(2))
    expect(cell('μ_CA(c)')).toHaveTextContent('0.67')
    expect(cell('r (monto / ahorro total)')).toHaveTextContent('0.25')
    expect(cell('E (meses de fondo de emergencia)')).toHaveTextContent('No informado')
  })

  it('has an accessible SVG with title and description', () => {
    render(<AbsorptionChart {...sample.absorption} />)
    const svg = screen.getByRole('img', { name: /Capacidad de absorción/ })
    expect(svg.querySelector('title')).not.toBeNull()
    expect(svg.querySelector('desc')?.textContent).toMatch(/μ_CA\(c\) = 0\.67/)
  })
})
