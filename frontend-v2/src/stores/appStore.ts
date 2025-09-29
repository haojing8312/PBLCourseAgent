import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import type { AppState, Course, WorkflowStep } from '@/types'

interface AppStore extends AppState {
  // Editor instance
  editorInstance: any | null

  // Actions
  setCurrentCourse: (course: Course | null) => void
  setSelectedNode: (nodeId: string | null) => void
  setCanvasViewport: (viewport: { x: number; y: number; zoom: number }) => void
  setSidebarOpen: (open: boolean) => void
  setChatOpen: (open: boolean) => void
  setCurrentWorkflow: (workflow: WorkflowStep[] | null) => void
  setEditorInstance: (editor: any | null) => void

  // Computed values
  hasActiveCourse: () => boolean
  isWorkflowRunning: () => boolean
}

export const useAppStore = create<AppStore>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    currentCourse: null,
    selectedNode: null,
    canvasViewport: { x: 0, y: 0, zoom: 1 },
    sidebarOpen: true,
    chatOpen: false,
    currentWorkflow: null,
    editorInstance: null,

    // Actions
    setCurrentCourse: (course) => set({ currentCourse: course }),
    setSelectedNode: (nodeId) => set({ selectedNode: nodeId }),
    setCanvasViewport: (viewport) => set({ canvasViewport: viewport }),
    setSidebarOpen: (open) => set({ sidebarOpen: open }),
    setChatOpen: (open) => set({ chatOpen: open }),
    setCurrentWorkflow: (workflow) => set({ currentWorkflow: workflow }),
    setEditorInstance: (editor) => set({ editorInstance: editor }),

    // Computed values
    hasActiveCourse: () => get().currentCourse !== null,
    isWorkflowRunning: () => {
      const workflow = get().currentWorkflow
      return workflow?.some(step => step.status === 'running') ?? false
    },
  }))
)

// Persistence subscription for important state
useAppStore.subscribe(
  (state) => state.canvasViewport,
  (viewport) => {
    localStorage.setItem('canvas-viewport', JSON.stringify(viewport))
  }
)

// Load persisted viewport on initialization
const persistedViewport = localStorage.getItem('canvas-viewport')
if (persistedViewport) {
  try {
    const viewport = JSON.parse(persistedViewport)
    useAppStore.getState().setCanvasViewport(viewport)
  } catch (error) {
    console.warn('Failed to load persisted canvas viewport:', error)
  }
}