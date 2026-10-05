// SVG chart helpers ported from the design system bundle. Charts are hand-written SVG (no chart library).
import type { Point } from '../types/ui'

export const CHART_WIDTH = 640
export const CHART_HEIGHT = 300
/** Series are told apart by stroke too: solid, dashed, dotted. */
export const DASHES = ['0', '8 5', '2 4'] as const

export interface Margins {
  l: number
  r: number
  t: number
  b: number
}

export interface Tick {
  v: number
  label: string
}

export type Scale = (v: number) => number

export function scale(d0: number, d1: number, r0: number, r1: number): Scale {
  return (v) => r0 + ((v - d0) / (d1 - d0)) * (r1 - r0)
}

export function linePath(points: Point[], sx: Scale, sy: Scale): string {
  return points.map((p, i) => `${i ? 'L' : 'M'}${sx(p.x).toFixed(1)} ${sy(p.y).toFixed(1)}`).join(' ')
}

/** Linear interpolation over a piecewise-linear curve; 0 outside its support. */
export function interpolate(points: Point[], x: number): number {
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1]
    const b = points[i]
    if (x >= a.x && x <= b.x) return b.x === a.x ? b.y : a.y + ((b.y - a.y) * (x - a.x)) / (b.x - a.x)
  }
  return 0
}
