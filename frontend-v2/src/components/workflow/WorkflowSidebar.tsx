import { Play, Edit2, CheckCircle, AlertCircle, Download, X } from 'lucide-react'

interface StageInfo {
  number: 1 | 2 | 3
  name: string
  status: 'pending' | 'generating' | 'completed' | 'editing' | 'error'
  content: string
  onStart: () => void
  onEdit: () => void
  onConfirm: () => void
  onContentChange: (content: string) => void
  errorMessage?: string
}

interface WorkflowSidebarProps {
  stages: [StageInfo, StageInfo, StageInfo]
  currentStage: 1 | 2 | 3 | 'complete'
  onClose?: () => void
  onExport?: () => void
  courseTitle: string
}

export function WorkflowSidebar({ stages, currentStage, onClose, onExport, courseTitle }: WorkflowSidebarProps) {
  const currentStageInfo = currentStage === 'complete' ? null : stages[currentStage - 1]

  return (
    <div className="w-96 h-full bg-white border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <h3 className="text-sm font-semibold text-gray-800">🤖 AI 助手</h3>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/50 rounded transition-colors"
            >
              <X className="w-4 h-4 text-gray-600" />
            </button>
          )}
        </div>
        <p className="text-xs text-gray-600 mt-1">{courseTitle}</p>
      </div>

      {/* Stage Progress */}
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
        <div className="space-y-2">
          {stages.map((stage, index) => (
            <div
              key={stage.number}
              className={`flex items-center space-x-3 p-2 rounded-lg transition-colors ${
                currentStage === stage.number
                  ? 'bg-indigo-100 border border-indigo-200'
                  : 'bg-white'
              }`}
            >
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                stage.status === 'completed' ? 'bg-green-100 text-green-800' :
                stage.status === 'generating' || stage.status === 'editing' ? 'bg-indigo-100 text-indigo-800' :
                stage.status === 'error' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-500'
              }`}>
                {stage.status === 'completed' ? (
                  <CheckCircle className="w-4 h-4" />
                ) : stage.status === 'error' ? (
                  <AlertCircle className="w-4 h-4" />
                ) : (
                  stage.number
                )}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800">{stage.name}</p>
                <p className="text-xs text-gray-500">
                  {stage.status === 'generating' ? '生成中...' :
                   stage.status === 'editing' ? '编辑中' :
                   stage.status === 'completed' ? '已完成' :
                   stage.status === 'error' ? '生成失败' :
                   '等待开始'}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {currentStage === 'complete' ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h4 className="text-lg font-semibold text-gray-800 mb-2">课程设计完成!</h4>
            <p className="text-sm text-gray-600 mb-4">所有阶段已完成，您可以导出课程方案了。</p>
            {onExport && (
              <button
                onClick={onExport}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2 mx-auto"
              >
                <Download className="w-4 h-4" />
                <span>导出课程</span>
              </button>
            )}
          </div>
        ) : currentStageInfo ? (
          <div className="space-y-4">
            {/* Stage Assistant Message */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-gray-700">
                {currentStageInfo.status === 'pending' && (
                  <>
                    <span className="font-medium">准备开始阶段 {currentStageInfo.number}：{currentStageInfo.name}</span>
                    <br />
                    点击下方按钮开始生成。
                  </>
                )}
                {currentStageInfo.status === 'generating' && (
                  <>
                    <span className="font-medium">正在生成 {currentStageInfo.name}...</span>
                    <br />
                    请稍候，AI正在处理您的请求。
                  </>
                )}
                {currentStageInfo.status === 'completed' && (
                  <>
                    <span className="font-medium">阶段 {currentStageInfo.number} 完成!</span>
                    <br />
                    您可以查看并编辑内容，确认后继续下一阶段。
                  </>
                )}
                {currentStageInfo.status === 'editing' && (
                  <>
                    <span className="font-medium">正在编辑内容</span>
                    <br />
                    修改完成后请保存。
                  </>
                )}
                {currentStageInfo.status === 'error' && (
                  <>
                    <span className="font-medium text-red-700">生成失败</span>
                    <br />
                    {currentStageInfo.errorMessage || '请重试或联系支持。'}
                  </>
                )}
              </p>
            </div>

            {/* Content Display (when completed/editing) */}
            {(currentStageInfo.status === 'completed' || currentStageInfo.status === 'editing') && currentStageInfo.content && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                {currentStageInfo.status === 'editing' ? (
                  <textarea
                    value={currentStageInfo.content}
                    onChange={(e) => currentStageInfo.onContentChange(e.target.value)}
                    className="w-full h-64 p-2 border border-gray-300 rounded-lg text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="编辑内容..."
                  />
                ) : (
                  <div className="text-xs text-gray-600 font-mono whitespace-pre-wrap max-h-64 overflow-y-auto">
                    {currentStageInfo.content.slice(0, 500)}
                    {currentStageInfo.content.length > 500 && '...\n\n[在画布节点中查看完整内容]'}
                  </div>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-2">
              {currentStageInfo.status === 'pending' && (
                <button
                  onClick={currentStageInfo.onStart}
                  className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center space-x-2"
                >
                  <Play className="w-4 h-4" />
                  <span>开始生成阶段 {currentStageInfo.number}</span>
                </button>
              )}

              {currentStageInfo.status === 'completed' && (
                <>
                  <button
                    onClick={currentStageInfo.onEdit}
                    className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center space-x-2"
                  >
                    <Edit2 className="w-4 h-4" />
                    <span>编辑内容</span>
                  </button>
                  <button
                    onClick={currentStageInfo.onConfirm}
                    className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center space-x-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>确认并继续下一阶段</span>
                  </button>
                </>
              )}

              {currentStageInfo.status === 'editing' && (
                <button
                  onClick={currentStageInfo.onConfirm}
                  className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center space-x-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>保存并确认</span>
                </button>
              )}

              {currentStageInfo.status === 'error' && (
                <button
                  onClick={currentStageInfo.onStart}
                  className="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  重试
                </button>
              )}
            </div>
          </div>
        ) : null}
      </div>

      {/* Footer Tips */}
      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
        <p className="text-xs text-gray-500">
          💡 提示：双击画布上的节点可以查看完整内容
        </p>
      </div>
    </div>
  )
}