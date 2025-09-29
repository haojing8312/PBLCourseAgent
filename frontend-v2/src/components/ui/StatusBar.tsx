import { useAppStore } from '@/stores/appStore'

export function StatusBar() {
  const { canvasViewport, currentWorkflow, hasActiveCourse } = useAppStore()

  const formatZoom = (zoom: number) => `${Math.round(zoom * 100)}%`

  const getWorkflowStatus = () => {
    if (!currentWorkflow) return '就绪'

    const runningSteps = currentWorkflow.filter(step => step.status === 'running')
    const completedSteps = currentWorkflow.filter(step => step.status === 'completed')

    if (runningSteps.length > 0) {
      return `执行中: ${runningSteps[0].name}`
    }

    return `已完成 ${completedSteps.length}/${currentWorkflow.length} 步骤`
  }

  return (
    <div className="h-8 flex items-center justify-between px-4 bg-muted text-muted-foreground text-xs">
      {/* Left section */}
      <div className="flex items-center space-x-4">
        <span>状态: {getWorkflowStatus()}</span>
        {hasActiveCourse() && (
          <span>课程: 已加载</span>
        )}
      </div>

      {/* Right section */}
      <div className="flex items-center space-x-4">
        <span>
          位置: {Math.round(canvasViewport.x)}, {Math.round(canvasViewport.y)}
        </span>
        <span>缩放: {formatZoom(canvasViewport.zoom)}</span>
        <span>前端 v2.0.0</span>
      </div>
    </div>
  )
}