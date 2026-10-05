import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { sample } from '../../fixtures/sample'
import { ClarificationScreen } from './ClarificationScreen'
import { ContextScreen } from './ContextScreen'
import { HomeScreen } from './HomeScreen'
import { ResultScreen } from './ResultScreen'

describe('screens render with fixtures', () => {
  it('HomeScreen', () => {
    render(<HomeScreen example={sample.exampleInput} />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Reparte tu dinero entre cinco tipos de inversión')
    expect(screen.getByLabelText('Describe tu situación')).toBeInTheDocument()
    expect(screen.getAllByRole('complementary', { name: 'Aviso educativo' })).toHaveLength(2)
  })

  it('HomeScreen with an uninterpretable input', () => {
    render(<HomeScreen example={sample.exampleInput} value="hola" error={sample.emptyInputError} />)
    expect(screen.getByRole('status')).toHaveTextContent('No pudimos interpretar tu texto')
  })

  it('ClarificationScreen asks one question as a radio group', () => {
    render(
      <ClarificationScreen
        input="Tengo S/ 5,000 y no me gusta arriesgar."
        understood={sample.understoodAsk}
        step={1}
        totalSteps={2}
        question={sample.question}
        value="1-3"
        onChange={() => {}}
      />,
    )
    expect(screen.getByText('Pregunta 1 de 2')).toBeInTheDocument()
    expect(screen.getByRole('group', { name: sample.question.question })).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: 'Entre 1 y 3 años' })).toBeChecked()
  })

  it('ClarificationScreen declares an assumption', () => {
    render(
      <ClarificationScreen understood={sample.understoodAssume} step={2} totalSteps={2} assumption={sample.assumptionText} />,
    )
    expect(screen.getByRole('status')).toHaveTextContent(sample.assumptionText)
    expect(screen.getByRole('button', { name: 'Continuar con este supuesto' })).toBeInTheDocument()
  })

  it('ResultScreen', () => {
    render(
      <ResultScreen
        summary={sample.summary}
        total={sample.total}
        allocation={sample.allocation}
        assumptions={sample.assumptions}
        explanation={sample.explanation}
        technical={sample.technical}
      />,
    )
    expect(screen.getByRole('heading', { level: 2, name: 'Cómo repartir S/ 5,000.00' })).toBeInTheDocument()
    expect(screen.getByText('Ver detalle técnico')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Ajustar el contexto' })).toBeInTheDocument()
  })

  it('ContextScreen before and after an adjustment', () => {
    render(
      <ContextScreen
        factors={sample.factorsAdverse}
        before={sample.allocation}
        after={sample.allocationAdverse}
        changed
        beforeLabel="Antes (Neutral)"
        afterLabel="Después (Adverso)"
      />,
    )
    expect(screen.getByRole('heading', { name: 'Antes y después de tu ajuste' })).toBeInTheDocument()
    expect(screen.getByRole('group', { name: 'Panorama político' })).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: 'Adverso', checked: true })).toBeInTheDocument()
    expect(screen.getAllByText('−2 pts')).toHaveLength(1)
  })
})
