import { useCallback } from 'react'
import { Tldraw } from 'tldraw'
import 'tldraw/tldraw.css'
import { useAppStore } from '@/stores/appStore'

export function InfiniteCanvas() {
  const { setSelectedNode, setCanvasViewport, setEditorInstance } = useAppStore()

  const handleMount = useCallback((editor: unknown) => {
    // Store editor instance in app store
    setEditorInstance(editor)

    // Simple event handlers - will be refined as we understand the API better
    let lastSelection: string[] = []
    let lastCamera = { x: 0, y: 0, z: 1 }

    // Polling approach for now to detect changes
    const checkChanges = () => {
      try {
        // Check selection changes
        const currentSelection = (editor as any)?.getSelectedShapeIds ? (editor as any).getSelectedShapeIds() : []
        if (JSON.stringify(currentSelection) !== JSON.stringify(lastSelection)) {
          lastSelection = currentSelection
          if (currentSelection.length === 1) {
            setSelectedNode(currentSelection[0])
          } else {
            setSelectedNode(null)
          }
        }

        // Check camera changes
        const camera = (editor as any)?.getCamera ? (editor as any).getCamera() : { x: 0, y: 0, z: 1 }
        if (camera.x !== lastCamera.x || camera.y !== lastCamera.y || camera.z !== lastCamera.z) {
          lastCamera = camera
          setCanvasViewport({
            x: camera.x,
            y: camera.y,
            zoom: camera.z
          })
        }
      } catch (error) {
        // Silently handle API errors during development
        console.debug('Canvas API call failed:', error)
      }
    }

    // Poll for changes every 100ms
    const interval = setInterval(checkChanges, 100)

    // Cleanup on unmount
    return () => clearInterval(interval)
  }, [setSelectedNode, setCanvasViewport, setEditorInstance])

  return (
    <div className="canvas-container">
      <Tldraw
        onMount={handleMount}
        persistenceKey="pbl-course-canvas"
      />
    </div>
  )
}