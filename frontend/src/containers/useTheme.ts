import { useCallback, useEffect, useState } from 'react'

export type Theme = 'light' | 'dark'
export const THEME_STORAGE_KEY = 'investwise-theme'

/** Stored choice first, then the system preference; storage may be unavailable (private mode, blocked). */
export function initialTheme(): Theme {
  try {
    const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') return stored
  } catch {
    // Storage unavailable: fall through to the system preference.
  }
  try {
    if (window.matchMedia?.('(prefers-color-scheme: dark)').matches) return 'dark'
  } catch {
    // matchMedia unavailable.
  }
  return 'light'
}

/** Light/dark theme applied as `data-theme` on <html> and persisted in localStorage. */
export function useTheme(): [Theme, () => void] {
  const [theme, setTheme] = useState<Theme>(initialTheme)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])

  const toggle = useCallback(() => {
    setTheme((prev) => {
      const next: Theme = prev === 'light' ? 'dark' : 'light'
      try {
        window.localStorage.setItem(THEME_STORAGE_KEY, next)
      } catch {
        // Not persisted; the choice still applies to this session.
      }
      return next
    })
  }, [])

  return [theme, toggle]
}
