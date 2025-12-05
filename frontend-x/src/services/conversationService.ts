/**
 * Conversation Service - 对话历史API服务
 * 处理课程项目的对话记录CRUD操作
 */

import type { ConversationMessage } from '../types/course';
import { authFetch } from './api';

export interface AddConversationRequest {
  messages: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
    step?: number;
  }>;
}

export interface ConversationHistoryResponse {
  course_id: number;
  messages: ConversationMessage[];
}

/**
 * 添加对话消息到历史记录
 *
 * @param courseId - 课程ID
 * @param messages - 消息列表
 * @returns 更新后的课程对象
 */
export async function addConversationMessages(
  courseId: number,
  messages: AddConversationRequest['messages']
): Promise<any> {
  const response = await authFetch(`/courses/${courseId}/conversation`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ messages }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to add messages: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * 获取对话历史
 *
 * @param courseId - 课程ID
 * @param step - 可选，过滤特定步骤的对话 (1-3)
 * @returns 对话历史
 */
export async function getConversationHistory(
  courseId: number,
  step?: number
): Promise<ConversationHistoryResponse> {
  let endpoint = `/courses/${courseId}/conversation`;
  if (step !== undefined) {
    endpoint += `?step=${step}`;
  }

  const response = await authFetch(endpoint, {
    method: 'GET',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to get conversation: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * 清除对话历史
 *
 * @param courseId - 课程ID
 * @param step - 可选，只清除特定步骤的对话
 */
export async function clearConversationHistory(
  courseId: number,
  step?: number
): Promise<void> {
  let endpoint = `/courses/${courseId}/conversation`;
  if (step !== undefined) {
    endpoint += `?step=${step}`;
  }

  const response = await authFetch(endpoint, {
    method: 'DELETE',
  });

  if (!response.ok && response.status !== 204) {
    const errorText = await response.text();
    throw new Error(`Failed to clear conversation: ${response.status} ${errorText}`);
  }
}

/**
 * 辅助函数：创建用户消息
 */
export function createUserMessage(content: string, step?: number): AddConversationRequest['messages'][0] {
  return {
    role: 'user',
    content,
    step,
  };
}

/**
 * 辅助函数：创建助手消息
 */
export function createAssistantMessage(content: string, step?: number): AddConversationRequest['messages'][0] {
  return {
    role: 'assistant',
    content,
    step,
  };
}

/**
 * 辅助函数：创建系统消息
 */
export function createSystemMessage(content: string, step?: number): AddConversationRequest['messages'][0] {
  return {
    role: 'system',
    content,
    step,
  };
}
