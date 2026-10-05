import type { Rule, RuleKind, RulesTableProps } from '../../types/ui'

const GROUPS: { kind: RuleKind; label: string }[] = [
  { kind: 'horizon', label: 'Horizonte · reglas difusas (RH)' },
  { kind: 'absorption', label: 'Capacidad de absorción · reglas difusas (RA)' },
  { kind: 'context', label: 'Contexto · reglas nítidas (RC)' },
]

/** A1: fuzzy rules show their activation degree α; crisp context rules have none. */
function activationText(rule: Rule): string {
  if (rule.kind === 'context') return 'No aplica (regla nítida)'
  return rule.activation == null ? '—' : `α = ${rule.activation.toFixed(2)}`
}

export function RulesTable({ rules }: RulesTableProps) {
  const groups = GROUPS.map((g) => ({ ...g, rules: rules.filter((r) => r.kind === g.kind) })).filter(
    (g) => g.rules.length > 0,
  )
  return (
    <table className="iw-table iw-table--stack iw-rules">
      <caption className="iw-sr">Reglas activadas: difusas de horizonte y de absorción, y reglas de contexto</caption>
      <thead>
        <tr>
          <th scope="col">Regla</th>
          <th scope="col">Condición</th>
          <th scope="col">Activación</th>
          <th scope="col">Efecto numérico</th>
        </tr>
      </thead>
      {groups.map((g) => (
        <tbody key={g.kind}>
          <tr className="iw-rules__group">
            <th scope="colgroup" colSpan={4}>
              {g.label}
            </th>
          </tr>
          {g.rules.map((r) => (
            <tr key={r.id}>
              <th scope="row">
                <span className="iw-rules__id">{r.id}</span> {r.name}
              </th>
              <td data-label="Condición">{r.condition}</td>
              <td
                data-label="Activación"
                className={r.kind === 'context' ? 'iw-rules__alpha iw-rules__alpha--none' : 'iw-rules__alpha'}
              >
                {activationText(r)}
              </td>
              <td data-label="Efecto" className="iw-rules__effect">
                {r.effect}
              </td>
            </tr>
          ))}
        </tbody>
      ))}
    </table>
  )
}
