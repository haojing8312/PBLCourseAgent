import { Suspense } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<div className="flex items-center justify-center h-screen">Loading...</div>}>
        <AppLayout />
      </Suspense>
    </ErrorBoundary>
  )
}

export default App