import { useState } from 'react'
import { apiService } from '@/services/api'

export function ApiTestPanel() {
  const [healthStatus, setHealthStatus] = useState<string>('未测试')
  const [isLoading, setIsLoading] = useState(false)
  const [lastResponse, setLastResponse] = useState<string>('')

  const testHealthCheck = async () => {
    setIsLoading(true)
    try {
      const response = await apiService.healthCheck()
      if (response.success) {
        setHealthStatus('✅ 健康')
        setLastResponse(JSON.stringify(response, null, 2))
      } else {
        setHealthStatus('❌ 异常')
        setLastResponse(`错误: ${response.error || response.message}`)
      }
    } catch (error) {
      setHealthStatus('❌ 连接失败')
      setLastResponse(`连接错误: ${error}`)
    } finally {
      setIsLoading(false)
    }
  }

  const testStatusCheck = async () => {
    setIsLoading(true)
    try {
      const response = await apiService.getStatus()
      if (response.success) {
        setLastResponse(JSON.stringify(response, null, 2))
      } else {
        setLastResponse(`错误: ${response.error || response.message}`)
      }
    } catch (error) {
      setLastResponse(`连接错误: ${error}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="p-4 border border-border rounded-lg bg-card">
      <h3 className="text-lg font-semibold mb-4">API连接测试</h3>

      <div className="space-y-4">
        <div className="flex items-center space-x-4">
          <span className="text-sm">后端状态:</span>
          <span className="text-sm font-mono">{healthStatus}</span>
          <button
            onClick={testHealthCheck}
            disabled={isLoading}
            className="px-3 py-1 bg-primary text-primary-foreground text-sm rounded hover:bg-primary/90 disabled:opacity-50"
          >
            {isLoading ? '测试中...' : '健康检查'}
          </button>
          <button
            onClick={testStatusCheck}
            disabled={isLoading}
            className="px-3 py-1 bg-secondary text-secondary-foreground text-sm rounded hover:bg-secondary/90 disabled:opacity-50"
          >
            {isLoading ? '测试中...' : '状态检查'}
          </button>
        </div>

        {lastResponse && (
          <div className="mt-4">
            <div className="text-sm font-medium mb-2">最新响应:</div>
            <pre className="text-xs bg-muted p-3 rounded overflow-auto max-h-40 whitespace-pre-wrap">
              {lastResponse}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}