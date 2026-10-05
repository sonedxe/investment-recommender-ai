import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FactorSelector } from './FactorSelector'

describe('FactorSelector', () => {
  it('is a native radio group named by its legend', () => {
    const onChange = vi.fn()
    render(<FactorSelector label="Panorama político" value="neutral" onChange={onChange} />)
    const group = screen.getByRole('group', { name: 'Panorama político' })
    const radios = screen.getAllByRole('radio')
    expect(group).toContainElement(radios[0])
    expect(radios).toHaveLength(3)
    expect(new Set(radios.map((r) => (r as HTMLInputElement).name)).size).toBe(1)
    expect(screen.getByRole('radio', { name: 'Neutral' })).toBeChecked()
    fireEvent.click(screen.getByRole('radio', { name: 'Adverso' }))
    expect(onChange).toHaveBeenCalledWith('adverse')
  })
})
