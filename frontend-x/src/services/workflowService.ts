/**
 * Workflow Service - SSE流式生成服务
 * 处理UbD三阶段的流式生成，使用Server-Sent Events
 */

import type { WorkflowRequest, SSEEvent, StageOneData, StageTwoData, StageThreeData } from '../types/course';
import { API_BASE_URL } from '@/config/api';

export interface WorkflowEventHandlers {
  onStart?: (data: SSEEvent['data']) => void;
  onProgress?: (data: SSEEvent['data']) => void;
  onStageComplete?: (data: SSEEvent['data']) => void;
  onError?: (data: SSEEvent['data']) => void;
  onComplete?: (data: SSEEvent['data']) => void;
}

export interface WorkflowStreamResult {
  abort: () => void;
}

/**
 * 流式生成完整工作流
 *
 * 使用fetch with ReadableStream处理SSE（而不是EventSource，因为需要POST）
 *
 * @param request - 工作流请求参数
 * @param handlers - 事件处理器
 * @returns 包含abort方法的对象，用于取消流式生成
 */
export async function streamWorkflow(
  request: WorkflowRequest,
  handlers: WorkflowEventHandlers
): Promise<WorkflowStreamResult> {
  const abortController = new AbortController();

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/workflow/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
      signal: abortController.signal,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    if (!response.body) {
      throw new Error('Response body is null');
    }

    // 处理流式响应
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    // 异步读取流
    const processStream = async () => {
      try {
        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          // 解码chunk
          buffer += decoder.decode(value, { stream: true });

          // 按行分割（SSE格式：data: {...}\n\n）
          const lines = buffer.split('\n\n');

          // 保留最后一个不完整的行
          buffer = lines.pop() || '';

          // 处理每个完整的事件
          for (const line of lines) {
            if (line.trim().startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6); // 移除 "data: " 前缀
                const event: SSEEvent = JSON.parse(jsonStr);

                // 根据事件类型调用对应的handler
                switch (event.event) {
                  case 'start':
                    handlers.onStart?.(event.data);
                    break;
                  case 'progress':
                    handlers.onProgress?.(event.data);
                    break;
                  case 'stage_complete':
                    handlers.onStageComplete?.(event.data);
                    break;
                  case 'error':
                    handlers.onError?.(event.data);
                    break;
                  case 'complete':
                    handlers.onComplete?.(event.data);
                    break;
                  default:
                    console.warn('[WorkflowService] Unknown event type:', event.event);
                }
              } catch (parseError) {
                console.error('[WorkflowService] Failed to parse SSE event:', line, parseError);
              }
            }
          }
        }
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          console.log('[WorkflowService] Stream aborted by user');
        } else {
          console.error('[WorkflowService] Stream processing error:', error);
          handlers.onError?.({ message: error instanceof Error ? error.message : String(error) });
        }
      }
    };

    // 启动流处理（不等待）
    processStream();

  } catch (error) {
    console.error('[WorkflowService] Failed to start stream:', error);
    handlers.onError?.({
      message: error instanceof Error ? error.message : String(error)
    });
  }

  return {
    abort: () => {
      abortController.abort();
      console.log('[WorkflowService] Workflow stream aborted');
    },
  };
}

/**
 * 辅助函数：从SSE event data中提取stage结果
 */
export function extractStageResult(
  event: SSEEvent
): StageOneData | StageTwoData | StageThreeData | null {
  if (event.event !== 'stage_complete') {
    return null;
  }

  return event.data.result || null;
}

/**
 * 辅助函数：检查是否所有阶段都已完成
 */
export function isWorkflowComplete(event: SSEEvent): boolean {
  return event.event === 'complete';
}

/**
 * 辅助函数：格式化进度百分比
 */
export function formatProgress(event: SSEEvent): string {
  if (event.event === 'progress' && event.data.progress !== undefined) {
    return `${Math.round(event.data.progress * 100)}%`;
  }
  return '';
}
