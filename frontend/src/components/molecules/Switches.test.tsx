import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { Switches } from './Switches'

describe('Switches', () => {
  it('toggles one module and keeps the other', () => {
    const onChange = vi.fn()
    render(<Switches value={{ fuzzy: true, context: true }} onChange={onChange} />)
    fireEvent.click(screen.getByRole('checkbox', { name: 'Reglas de contexto' }))
    expect(onChange).toHaveBeenCalledWith({ fuzzy: true, context: false })
  })
})
