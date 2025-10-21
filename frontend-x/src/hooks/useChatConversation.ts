/**
 * useChatConversation Hook
 * 集成Ant Design X的对话功能，管理步骤级别的对话历史
 * 支持ChatGPT式的流式AI回复
 */

import { useMemo, useCallback, useRef, useState } from 'react';
import { useCourseStore } from '../stores/courseStore';
// import type { ConversationMessage } from '../types/course';
import {
  addConversationMessages,
  createUserMessage,
  createAssistantMessage,
} from '../services/conversationService';
import { streamChat, toApiMessages } from '../services/chatService';
import type { ChatStreamResult } from '../services/chatService';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date | string;
}

export interface UseChatConversationOptions {
  /** 当前步骤 (1-3) */
  currentStep?: number;
  /** 是否自动同步到后端 */
  autoSync?: boolean;
  /** 课程ID（用于后端同步） */
  courseId?: number;
  /** 当AI请求重新生成课程方案时的回调 */
  onRegenerateRequest?: (stage: number, instructions: string) => void;
}

export interface UseChatConversationReturn {
  /** 当前步骤的对话消息 */
  messages: ChatMessage[];

  /** 发送用户消息（自动触发AI回复） */
  sendMessage: (content: string) => Promise<void>;

  /** 添加助手消息 */
  addAssistantMessage: (content: string) => void;

  /** 添加系统消息 */
  addSystemMessage: (content: string) => void;

  /** 清除当前步骤的对话 */
  clearMessages: () => void;

  /** 清除所有对话 */
  clearAllMessages: () => void;

  /** 是否有消息 */
  hasMessages: boolean;

  /** AI是否正在回复 */
  isAIResponding: boolean;

  /** 当前AI正在生成的消息（流式） */
  streamingMessage: string;

  /** 中止AI回复 */
  abortAIResponse: () => void;
}

/**
 * useChatConversation Hook
 *
 * 为ChatGPT式对话界面提供消息管理
 *
 * @example
 * ```tsx
 * const { messages, sendMessage, clearMessages } = useChatConversation({
 *   currentStep: 1,
 *   autoSync: true,
 *   courseId: 123
 * });
 *
 * // 使用Ant Design X Conversations组件
 * <Conversations
 *   items={messages}
 *   onSend={sendMessage}
 * />
 * ```
 */
export function useChatConversation(
  options: UseChatConversationOptions = {}
): UseChatConversationReturn {
  const { currentStep, autoSync = false, courseId, onRegenerateRequest } = options;

  const {
    conversationHistory,
    addMessage: addMessageToStore,
    clearConversation,
  } = useCourseStore();

  // 流式回复状态
  const [isAIResponding, setIsAIResponding] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const streamControllerRef = useRef<ChatStreamResult | null>(null);

  /**
   * 过滤当前步骤的消息
   */
  const messages = useMemo(() => {
    if (currentStep === undefined) {
      return conversationHistory;
    }
    return conversationHistory.filter((msg) => msg.step === currentStep);
  }, [conversationHistory, currentStep]);

  /**
   * 发送用户消息并触发AI回复
   */
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) {
        console.warn('[useChatConversation] Empty message ignored');
        return;
      }

      if (!courseId) {
        console.warn('[useChatConversation] No courseId, cannot send message');
        return;
      }

      // 1. 添加用户消息到Store
      addMessageToStore({
        role: 'user',
        content,
        step: currentStep,
      });

      // 2. 同步用户消息到后端
      if (autoSync) {
        try {
          await addConversationMessages(courseId, [
            createUserMessage(content, currentStep),
          ]);
          console.log('[useChatConversation] User message synced to backend');
        } catch (error) {
          console.error('[useChatConversation] Failed to sync user message:', error);
        }
      }

      // 3. 触发AI流式回复
      try {
        setIsAIResponding(true);
        setStreamingMessage('');

        // 准备对话历史（不包含当前用户消息，因为会在API中添加）
        const history = conversationHistory
          .filter((msg) => !currentStep || msg.step === currentStep)
          .slice(-20); // 最多保留最近20条

        // 调用流式Chat API
        const controller = await streamChat(
          {
            course_id: courseId,
            message: content,
            current_step: currentStep || 1,
            conversation_history: toApiMessages(history),
          },
          {
            onStart: () => {
              console.log('[useChatConversation] AI started responding');
            },
            onChunk: (chunk) => {
              // 累积AI回复内容
              setStreamingMessage((prev) => prev + chunk);
            },
            onDone: () => {
              console.log('[useChatConversation] AI response complete');

              // 将完整的AI回复添加到Store
              const finalMessage = streamingMessage + ''; // 确保获取最新值

              // 使用setTimeout确保获取到最新的streamingMessage
              setTimeout(() => {
                const fullMessage = document.querySelector('[data-ai-streaming]')?.textContent || streamingMessage;

                addMessageToStore({
                  role: 'assistant',
                  content: fullMessage,
                  step: currentStep,
                });

                // 同步到后端
                if (autoSync) {
                  addConversationMessages(courseId, [
                    createAssistantMessage(fullMessage, currentStep),
                  ]).catch((error) => {
                    console.error('[useChatConversation] Failed to sync AI message:', error);
                  });
                }

                // 清理状态
                setIsAIResponding(false);
                setStreamingMessage('');
              }, 100);
            },
            onError: (error) => {
              console.error('[useChatConversation] AI response error:', error);

              // 添加错误消息
              addMessageToStore({
                role: 'system',
                content: `❌ AI回复失败: ${error}`,
                step: currentStep,
              });

              // 清理状态
              setIsAIResponding(false);
              setStreamingMessage('');
            },
            onArtifact: (artifact) => {
              console.log('[useChatConversation] Received artifact event:', artifact);

              // 调用上层提供的regenerate回调
              if (artifact.action === 'regenerate' && onRegenerateRequest) {
                onRegenerateRequest(artifact.stage, artifact.instructions);
              }
            },
          }
        );

        streamControllerRef.current = controller;
      } catch (error) {
        console.error('[useChatConversation] Failed to start AI response:', error);
        setIsAIResponding(false);
        setStreamingMessage('');
      }
    },
    [currentStep, autoSync, courseId, addMessageToStore, conversationHistory, streamingMessage, onRegenerateRequest]
  );

  /**
   * 添加助手消息
   */
  const addAssistantMessage = useCallback(
    (content: string) => {
      addMessageToStore({
        role: 'assistant',
        content,
        step: currentStep,
      });

      // 同步到后端
      if (autoSync && courseId) {
        addConversationMessages(courseId, [
          createAssistantMessage(content, currentStep),
        ]).catch((error) => {
          console.error('[useChatConversation] Failed to sync assistant message:', error);
        });
      }
    },
    [currentStep, autoSync, courseId, addMessageToStore]
  );

  /**
   * 添加系统消息
   */
  const addSystemMessage = useCallback(
    (content: string) => {
      addMessageToStore({
        role: 'system',
        content,
        step: currentStep,
      });
    },
    [currentStep, addMessageToStore]
  );

  /**
   * 清除当前步骤的对话
   */
  const clearMessages = useCallback(() => {
    clearConversation(currentStep);
  }, [currentStep, clearConversation]);

  /**
   * 清除所有对话
   */
  const clearAllMessages = useCallback(() => {
    clearConversation();
  }, [clearConversation]);

  /**
   * 中止AI回复
   */
  const abortAIResponse = useCallback(() => {
    if (streamControllerRef.current) {
      streamControllerRef.current.abort();
      streamControllerRef.current = null;
      setIsAIResponding(false);
      setStreamingMessage('');
      console.log('[useChatConversation] AI response aborted');
    }
  }, []);

  /**
   * 是否有消息
   */
  const hasMessages = messages.length > 0;

  return {
    messages,
    sendMessage,
    addAssistantMessage,
    addSystemMessage,
    clearMessages,
    clearAllMessages,
    hasMessages,
    isAIResponding,
    streamingMessage,
    abortAIResponse,
  };
}

/**
 * 辅助函数：转换为Ant Design X的消息格式
 *
 * Ant Design X期望的消息格式与我们的ConversationMessage略有不同
 */
export function toAntdXMessages(messages: ChatMessage[]) {
  return messages.map((msg) => ({
    id: msg.id,
    role: msg.role,
    content: msg.content,
    createAt: typeof msg.timestamp === 'string' ? new Date(msg.timestamp) : msg.timestamp,
  }));
}

/**
 * 辅助函数：从Ant Design X格式转换回我们的格式
 */
export function fromAntdXMessage(msg: any): Omit<ChatMessage, 'id' | 'timestamp'> {
  return {
    role: msg.role,
    content: msg.content,
  };
}
