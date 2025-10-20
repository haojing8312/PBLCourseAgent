/**
 * useChatConversation Hook
 * 集成Ant Design X的对话功能，管理步骤级别的对话历史
 */

import { useMemo, useCallback } from 'react';
import { useCourseStore } from '../stores/courseStore';
import type { ConversationMessage } from '../types/course';
import {
  addConversationMessages,
  createUserMessage,
  createAssistantMessage,
} from '../services/conversationService';

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
}

export interface UseChatConversationReturn {
  /** 当前步骤的对话消息 */
  messages: ChatMessage[];

  /** 发送用户消息 */
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
  const { currentStep, autoSync = false, courseId } = options;

  const {
    conversationHistory,
    addMessage: addMessageToStore,
    clearConversation,
  } = useCourseStore();

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
   * 发送用户消息
   */
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) {
        console.warn('[useChatConversation] Empty message ignored');
        return;
      }

      // 添加到本地Store
      addMessageToStore({
        role: 'user',
        content,
        step: currentStep,
      });

      // 同步到后端
      if (autoSync && courseId) {
        try {
          await addConversationMessages(courseId, [
            createUserMessage(content, currentStep),
          ]);
          console.log('[useChatConversation] Message synced to backend');
        } catch (error) {
          console.error('[useChatConversation] Failed to sync message:', error);
          // 不阻塞用户操作，只记录错误
        }
      }
    },
    [currentStep, autoSync, courseId, addMessageToStore]
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
