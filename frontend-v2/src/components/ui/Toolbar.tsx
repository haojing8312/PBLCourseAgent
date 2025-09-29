import {
  Menu,
  MessageSquare,
  Save,
  Download,
  Upload,
  Settings,
  Lightbulb
} from 'lucide-react'
import { useAppStore } from '@/stores/appStore'

export function Toolbar() {
  const {
    sidebarOpen,
    chatOpen,
    setSidebarOpen,
    setChatOpen,
    currentCourse,
    isWorkflowRunning
  } = useAppStore()

  return (
    <div className="h-16 flex items-center justify-between px-4 bg-background border-b border-border">
      {/* Left section */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors"
          title="切换侧边栏"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="text-lg font-semibold text-foreground">
          PBLCourseAgent
        </div>

        {currentCourse && (
          <div className="text-sm text-muted-foreground">
            {currentCourse.title}
          </div>
        )}
      </div>

      {/* Center section */}
      <div className="flex items-center space-x-2">
        <button
          className="flex items-center space-x-2 px-3 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
          disabled={isWorkflowRunning()}
          title="开始AI课程生成"
        >
          <Lightbulb className="h-4 w-4" />
          <span>{isWorkflowRunning() ? '生成中...' : '开始生成'}</span>
        </button>
      </div>

      {/* Right section */}
      <div className="flex items-center space-x-2">
        <button
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors"
          title="导入课程"
        >
          <Upload className="h-4 w-4" />
        </button>

        <button
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors"
          title="保存课程"
          disabled={!currentCourse}
        >
          <Save className="h-4 w-4" />
        </button>

        <button
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors"
          title="导出课程"
          disabled={!currentCourse}
        >
          <Download className="h-4 w-4" />
        </button>

        <div className="w-px h-6 bg-border" />

        <button
          onClick={() => setChatOpen(!chatOpen)}
          className={`p-2 rounded-md transition-colors ${
            chatOpen
              ? 'bg-primary text-primary-foreground'
              : 'hover:bg-accent hover:text-accent-foreground'
          }`}
          title="AI助手"
        >
          <MessageSquare className="h-4 w-4" />
        </button>

        <button
          className="p-2 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors"
          title="设置"
        >
          <Settings className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}