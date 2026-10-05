import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { sample } from '../../fixtures/sample'
import { AbsorptionChart, absorptionLabelLayout } from './AbsorptionChart'

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

  it('keeps the c label inside the plot when c is near the right edge', () => {
    for (const c of [0.8, 0.9, 1]) {
      expect(absorptionLabelLayout(c, 0.5).cAnchor).toBe('end')
    }
    const { container } = render(<AbsorptionChart {...sample.absorption} c={0.95} centroid={0.85} membershipAtC={1} />)
    const label = [...container.querySelectorAll('text')].find((t) => t.textContent?.startsWith('c = 0.95'))
    expect(label?.getAttribute('text-anchor')).toBe('end')
  })

  it('keeps the labels inside near the left edge and puts colliding labels on two rows', () => {
    const low = absorptionLabelLayout(0.05, 0.15)
    expect(low.cAnchor).toBe('start')
    expect(low.centroidAnchor).toBe('start')
    expect(low.centroidRow).toBe(1)
    const high = absorptionLabelLayout(0.95, 0.9)
    expect([high.cAnchor, high.centroidAnchor, high.centroidRow]).toEqual(['end', 'end', 1])
    const middle = absorptionLabelLayout(0.4, 0.6)
    expect([middle.cAnchor, middle.centroidAnchor, middle.centroidRow]).toEqual(['end', 'start', 0])
  })
})
