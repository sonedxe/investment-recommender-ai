import { lazy, Suspense } from 'react'
import { AppContainer } from './containers/AppContainer'

// Dev aid: `/?gallery` shows every screen with fixtures; it is loaded on demand and never linked from the UI.
const Gallery = lazy(() => import('./dev/Gallery'))

function wantsGallery(): boolean {
  return typeof window !== 'undefined' && new URLSearchParams(window.location.search).has('gallery')
}

export default function App() {
  if (wantsGallery()) {
    return (
      <Suspense fallback={null}>
        <Gallery />
      </Suspense>
    )
  }
  return <AppContainer />
}
