import { Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'
import { WelcomePage } from '@/pages/WelcomePage'
import { CourseCreationPage } from '@/pages/CourseCreationPage'
import { CourseDesignPage } from '@/pages/CourseDesignPage'

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Suspense fallback={
          <div className="flex items-center justify-center h-screen">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
              <p className="text-gray-600">正在加载...</p>
            </div>
          </div>
        }>
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/create" element={<CourseCreationPage />} />
            <Route path="/design" element={<CourseDesignPage />} />
          </Routes>
        </Suspense>
      </Router>
    </ErrorBoundary>
  )
}

export default App