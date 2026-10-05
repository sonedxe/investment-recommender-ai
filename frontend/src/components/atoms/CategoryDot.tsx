import type { CategoryDotProps } from '../../types/ui'

export function CategoryDot({ categoryId }: CategoryDotProps) {
  return <span className="iw-dot" style={{ background: `var(--cat-${categoryId})` }} aria-hidden="true" />
}
