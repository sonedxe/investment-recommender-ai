import type { ClarificationFormProps } from '../../types/ui'
import { Button } from '../atoms/Button'
import { QuestionField } from '../molecules/QuestionField'
import { UnderstoodPanel } from './UnderstoodPanel'

/** Understood data on one side and ONE question on the other; `assumption` declares a default instead. */
export function ClarificationForm(props: ClarificationFormProps) {
  const { understood, step, totalSteps, question, value, onChange, onSubmit, onSkip } = props
  const { skipLabel, submitLabel, assumption, error } = props
  return (
    <form
      className="iw-clarify"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit?.()
      }}
    >
      <div className="iw-clarify__side">
        <UnderstoodPanel items={understood} />
      </div>
      <div className="iw-clarify__main">
        {step ? (
          <p className="iw-clarify__step">
            {`Pregunta ${step}${totalSteps ? ` de ${totalSteps}` : ''}`}
          </p>
        ) : null}
        {assumption ? (
          <div className="iw-assumption" role="status">
            <p className="iw-assumption__title">Continuamos con un supuesto</p>
            <p>{assumption}</p>
            <p className="iw-assumption__sub">Puedes ajustarlo más adelante en el resultado.</p>
          </div>
        ) : (
          <QuestionField
            question={question?.question ?? ''}
            hint={question?.hint}
            options={question?.options}
            freeInput={question?.freeInput}
            value={value}
            onChange={onChange}
            error={error}
          />
        )}
        <div className="iw-clarify__actions">
          <Button type="submit" variant="primary">
            {assumption ? 'Continuar con este supuesto' : submitLabel || 'Continuar'}
          </Button>
          {!assumption && skipLabel && (
            <Button variant="quiet" onClick={onSkip}>
              {skipLabel}
            </Button>
          )}
        </div>
      </div>
    </form>
  )
}
