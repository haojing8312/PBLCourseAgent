import { useAppStore } from '@/stores/appStore'
import { InfiniteCanvas } from '@/components/canvas/InfiniteCanvas'
import { CanvasToolbar } from '@/components/toolbar/CanvasToolbar'
import { ChatSidebar } from '@/components/chat/ChatSidebar'
import { Toolbar } from '@/components/ui/Toolbar'
import { StatusBar } from '@/components/ui/StatusBar'
import { ApiTestPanel } from '@/components/ui/ApiTestPanel'
import { cn } from '@/utils/cn'

export function AppLayout() {
  const { chatOpen } = useAppStore()

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top toolbar */}
      <div className="flex-none border-b border-border">
        <Toolbar />
      </div>

      {/* Main content area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Canvas area */}
        <div
          className={cn(
            "flex-1 relative transition-all duration-300",
            chatOpen && "mr-96"
          )}
        >
          <div className="h-full flex flex-col">
            {/* API Test Panel - temporary for Phase 2.1 validation */}
            <div className="flex-none p-4">
              <ApiTestPanel />
            </div>

            {/* Canvas */}
            <div className="flex-1 relative">
              <InfiniteCanvas />
              <CanvasToolbar />
            </div>
          </div>
        </div>

        {/* Chat sidebar */}
        <div
          className={cn(
            "fixed right-0 top-16 bottom-8 w-96 bg-card border-l border-border transition-transform duration-300 z-50",
            chatOpen ? "translate-x-0" : "translate-x-full"
          )}
        >
          <ChatSidebar />
        </div>
      </div>

      {/* Bottom status bar */}
      <div className="flex-none border-t border-border">
        <StatusBar />
      </div>
    </div>
  )
}