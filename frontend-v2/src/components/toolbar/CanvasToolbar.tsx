import { PlusSquare, MousePointer, Move, Square, Play, Workflow } from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import { createShapeId } from 'tldraw'
import { workflowService } from '@/services/workflowService'

export function CanvasToolbar() {
  const { editorInstance } = useAppStore()

  // Initialize workflow service with editor when available
  if (editorInstance) {
    workflowService.setEditor(editorInstance)
  }

  const handleCreateTaskNode = () => {
    if (editorInstance) {
      // Get the current viewport center
      const viewport = (editorInstance as any).getViewportPageBounds?.() || { x: 0, y: 0, w: 800, h: 600 }
      const centerX = viewport.x + viewport.w / 2
      const centerY = viewport.y + viewport.h / 2

      // Create a rectangle shape for the task node
      const taskNodeId = createShapeId()

      try {
        (editorInstance as any).createShape?.({
          id: taskNodeId,
          type: 'geo',
          x: centerX - 100,
          y: centerY - 60,
          props: {
            geo: 'rectangle',
            w: 200,
            h: 120,
            fill: 'solid',
            color: 'blue',
            text: 'New Task\n\nClick to edit...',
          },
        })

        // Select the newly created shape
        (editorInstance as any).select?.(taskNodeId)
      } catch (error) {
        console.warn('Failed to create task node:', error)
      }
    }
  }

  const handleSelectTool = () => {
    if (editorInstance) {
      try {
        (editorInstance as any).setCurrentTool?.('select')
      } catch (error) {
        console.warn('Failed to set select tool:', error)
      }
    }
  }

  const handleHandTool = () => {
    if (editorInstance) {
      try {
        (editorInstance as any).setCurrentTool?.('hand')
      } catch (error) {
        console.warn('Failed to set hand tool:', error)
      }
    }
  }

  const handleRectangleTool = () => {
    if (editorInstance) {
      try {
        (editorInstance as any).setCurrentTool?.('geo')
      } catch (error) {
        console.warn('Failed to set geo tool:', error)
      }
    }
  }

  const handleInitializeWorkflow = async () => {
    try {
      await workflowService.initializePBLWorkflow()
      console.log('PBL workflow initialized successfully')
    } catch (error) {
      console.error('Failed to initialize workflow:', error)
    }
  }

  const handleExecuteWorkflow = async () => {
    try {
      // Sample course input for demonstration
      const sampleInput = {
        course_topic: "环保与可持续发展",
        course_overview: "通过项目式学习探索环保主题，培养学生的环保意识和实践能力",
        age_group: "初中 (12-15岁)",
        duration: "4周",
        ai_tools: "AI数据分析工具、环境监测AI、创意设计AI"
      }

      await workflowService.executePBLWorkflow(sampleInput)
      console.log('PBL workflow executed successfully')
    } catch (error) {
      console.error('Failed to execute workflow:', error)
    }
  }

  return (
    <div className="absolute top-4 left-4 z-10 bg-card border border-border rounded-lg shadow-lg p-2">
      <div className="flex flex-col space-y-2">
        {/* Select Tool */}
        <button
          onClick={handleSelectTool}
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors group"
          title="选择工具"
        >
          <MousePointer className="h-4 w-4" />
        </button>

        {/* Hand Tool */}
        <button
          onClick={handleHandTool}
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors group"
          title="手型工具（拖拽画布）"
        >
          <Move className="h-4 w-4" />
        </button>

        {/* Divider */}
        <div className="h-px bg-border my-1" />

        {/* Task Node Tool */}
        <button
          onClick={handleCreateTaskNode}
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors group bg-primary text-primary-foreground"
          title="创建任务节点"
        >
          <PlusSquare className="h-4 w-4" />
        </button>

        {/* Rectangle Tool */}
        <button
          onClick={handleRectangleTool}
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors group"
          title="矩形工具"
        >
          <Square className="h-4 w-4" />
        </button>

        {/* Divider */}
        <div className="h-px bg-border my-1" />

        {/* Workflow Tools */}
        <button
          onClick={handleInitializeWorkflow}
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors group bg-green-600 text-white"
          title="初始化PBL工作流"
        >
          <Workflow className="h-4 w-4" />
        </button>

        <button
          onClick={handleExecuteWorkflow}
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors group bg-amber-600 text-white"
          title="执行工作流"
        >
          <Play className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}