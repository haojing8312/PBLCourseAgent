/**
 * Chat Service - AI对话服务
 *
 * 提供ChatGPT式的流式对话体验
 */

import type { ConversationMessage } from '../types/course';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ChatRequest {
  course_id: number;
  message: string;
  current_step: number;
  conversation_history: Array<{
    role: string;
    content: string;
  }>;
}

export interface ChatStreamEvent {
  type: 'start' | 'chunk' | 'done' | 'error';
  content?: string;
  message?: string;
}

export interface ChatStreamHandlers {
  onStart?: () => void;
  onChunk?: (content: string) => void;
  onDone?: () => void;
  onError?: (error: string) => void;
}

export interface ChatStreamResult {
  abort: () => void;
}

/**
 * 流式AI对话
 *
 * 对标ChatGPT的流式响应体验
 *
 * @example
 * ```tsx
 * const controller = await streamChat({
 *   course_id: 123,
 *   message: "如何改进这个课程?",
 *   current_step: 1,
 *   conversation_history: []
 * }, {
 *   onStart: () => console.log('AI开始回复'),
 *   onChunk: (text) => appendToMessage(text),
 *   onDone: () => console.log('AI回复完成'),
 *   onError: (error) => showError(error)
 * });
 *
 * // 中止生成
 * controller.abort();
 * ```
 */
export async function streamChat(
  request: ChatRequest,
  handlers: ChatStreamHandlers
): Promise<ChatStreamResult> {
  const abortController = new AbortController();

  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
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
                const event: ChatStreamEvent = JSON.parse(jsonStr);

                // 根据事件类型调用对应的handler
                switch (event.type) {
                  case 'start':
                    handlers.onStart?.();
                    break;
                  case 'chunk':
                    if (event.content) {
                      handlers.onChunk?.(event.content);
                    }
                    break;
                  case 'done':
                    handlers.onDone?.();
                    break;
                  case 'error':
                    handlers.onError?.(event.message || 'Unknown error');
                    break;
                  default:
                    console.warn('[ChatService] Unknown event type:', event.type);
                }
              } catch (parseError) {
                console.error('[ChatService] Failed to parse SSE event:', line, parseError);
              }
            }
          }
        }
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          console.log('[ChatService] Stream aborted by user');
        } else {
          console.error('[ChatService] Stream processing error:', error);
          handlers.onError?.(error instanceof Error ? error.message : String(error));
        }
      }
    };

    // 启动流处理（不等待）
    processStream();

  } catch (error) {
    console.error('[ChatService] Failed to start stream:', error);
    handlers.onError?.(error instanceof Error ? error.message : String(error));
  }

  return {
    abort: () => {
      abortController.abort();
      console.log('[ChatService] Chat stream aborted');
    },
  };
}

/**
 * 非流式AI对话
 *
 * 一次性返回完整回复（不推荐，体验不如流式）
 */
export async function chat(request: ChatRequest): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    return data.message;
  } catch (error) {
    console.error('[ChatService] Chat error:', error);
    throw error;
  }
}

/**
 * 辅助函数：将ConversationMessage转换为API格式
 */
export function toApiMessages(messages: ConversationMessage[]): Array<{ role: string; content: string }> {
  return messages.map(msg => ({
    role: msg.role,
    content: msg.content
  }));
}
