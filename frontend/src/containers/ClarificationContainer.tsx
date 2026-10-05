import { useState } from 'react'
import { answerContent, canSkip, questionProgress, REFUSAL_TEXT, toQuestion, toUnderstood } from '../api/mappers'
import type { InterpretResponse, Turn } from '../api/types'
import { ClarificationScreen } from '../components'
import { askedFields } from '../state/flow'

export interface ClarificationContainerProps {
  input: string
  interpretation: InterpretResponse
  conversation: Turn[]
  offline: boolean
  onAnswer: (content: string) => void
  onConfirm: () => void
}

/** One question at a time; once complete with a declared assumption, asks to continue with it. */
export function ClarificationContainer(props: ClarificationContainerProps) {
  const { input, interpretation, conversation, offline, onAnswer, onConfirm } = props
  const [value, setValue] = useState('')
  const [error, setError] = useState<string | undefined>()
  const understood = toUnderstood(interpretation)
  const q = interpretation.question

  if (!q) {
    return (
      <ClarificationScreen
        input={input}
        offline={offline}
        understood={understood}
        assumption={interpretation.assumptions.join(' ')}
        onSubmit={onConfirm}
      />
    )
  }

  const change = (v: string) => {
    setValue(v)
    setError(undefined)
  }
  const question = toQuestion(q)
  if (question.freeInput) {
    const optionChosen = q.options?.some((o) => o.value === value)
    question.freeInput = { ...question.freeInput, value: optionChosen ? '' : value, onChange: change }
  }
  const { step, totalSteps } = questionProgress(interpretation, askedFields(conversation))

  return (
    <ClarificationScreen
      input={input}
      offline={offline}
      understood={understood}
      step={step}
      totalSteps={totalSteps}
      question={question}
      value={value}
      onChange={change}
      error={error}
      onSubmit={() => {
        if (!value.trim()) setError(q.options ? 'Elige una opción para continuar.' : 'Escribe un valor para continuar.')
        else onAnswer(answerContent(q, value))
      }}
      skipLabel={canSkip(q) ? REFUSAL_TEXT : undefined}
      onSkip={() => onAnswer(REFUSAL_TEXT)}
    />
  )
}
