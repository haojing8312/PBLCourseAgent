/**
 * ChatPanel - AI对话面板
 * 使用Ant Design X的Conversations组件提供ChatGPT式对话界面
 */

import React, { useMemo } from 'react';
import { Conversations, Bubble, Sender } from '@ant-design/x';
import { Card, Space, Button, Tooltip, Badge } from 'antd';
import { DeleteOutlined, DownloadOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useChatConversation } from '../hooks/useChatConversation';
// import type { ConversationMessage } from '../types/course';

export interface ChatPanelProps {
  /** 当前步骤 (1-3) */
  currentStep: number;

  /** 课程ID */
  courseId?: number;

  /** 是否自动同步到后端 */
  autoSync?: boolean;

  /** 面板标题 */
  title?: string;

  /** 是否显示清除按钮 */
  showClearButton?: boolean;

  /** 是否显示导出按钮 */
  showExportButton?: boolean;

  /** 自定义样式 */
  style?: React.CSSProperties;

  /** 自定义CSS类名 */
  className?: string;
}

/**
 * ChatPanel组件
 *
 * 提供ChatGPT式的对话界面，用于与AI Agent进行交互
 *
 * @example
 * ```tsx
 * <ChatPanel
 *   currentStep={1}
 *   courseId={123}
 *   autoSync={true}
 *   title="Stage One: 项目基础定义"
 *   showClearButton={true}
 * />
 * ```
 */
export const ChatPanel: React.FC<ChatPanelProps> = ({
  currentStep,
  courseId,
  autoSync = false,
  title,
  showClearButton = true,
  showExportButton = false,
  style,
  className,
}) => {
  const {
    messages,
    sendMessage,
    clearMessages,
    hasMessages,
  } = useChatConversation({
    currentStep,
    courseId,
    autoSync,
  });

  /**
   * 转换为Ant Design X的消息格式
   */
  const conversationItems = useMemo(() => {
    return messages.map((msg) => ({
      id: msg.id,
      role: msg.role,
      content: msg.content,
      createAt: typeof msg.timestamp === 'string' ? new Date(msg.timestamp) : msg.timestamp,
    }));
  }, [messages]);

  /**
   * 处理发送消息
   */
  const handleSend = async (content: string) => {
    await sendMessage(content);
  };

  /**
   * 处理清除对话
   */
  const handleClear = () => {
    if (window.confirm('确定要清除当前对话吗？此操作不可撤销。')) {
      clearMessages();
    }
  };

  /**
   * 导出对话为文本
   */
  const handleExport = () => {
    const text = messages
      .map((msg) => {
        const timestamp = typeof msg.timestamp === 'string'
          ? msg.timestamp
          : msg.timestamp.toISOString();
        return `[${msg.role.toUpperCase()}] ${timestamp}\n${msg.content}\n`;
      })
      .join('\n---\n\n');

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `conversation-step-${currentStep}-${Date.now()}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Card
      title={
        <Space>
          {title || `Step ${currentStep} 对话`}
          {hasMessages && (
            <Badge count={messages.length} showZero={false} />
          )}
        </Space>
      }
      extra={
        <Space>
          {showExportButton && hasMessages && (
            <Tooltip title="导出对话">
              <Button
                type="text"
                icon={<DownloadOutlined />}
                onClick={handleExport}
                size="small"
              />
            </Tooltip>
          )}
          {showClearButton && hasMessages && (
            <Tooltip title="清除对话">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={handleClear}
                size="small"
              />
            </Tooltip>
          )}
          <Tooltip title="与AI进行对话，完善课程方案">
            <InfoCircleOutlined style={{ cursor: 'help' }} />
          </Tooltip>
        </Space>
      }
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        ...style,
      }}
      bodyStyle={{
        flex: 1,
        overflow: 'hidden',
        padding: 0,
        display: 'flex',
        flexDirection: 'column',
      }}
      className={className}
    >
      <Conversations
        items={conversationItems}
        renderMessages={(messages) => (
          <div style={{ padding: '16px', overflowY: 'auto', flex: 1 }}>
            {messages.map((msg) => (
              <Bubble
                key={msg.id}
                placement={msg.role === 'user' ? 'end' : 'start'}
                avatar={
                  msg.role === 'user'
                    ? undefined
                    : { src: '/ai-avatar.png', fallback: '🤖' }
                }
                content={msg.content}
                variant={msg.role === 'system' ? 'borderless' : undefined}
                styles={{
                  content: {
                    backgroundColor: msg.role === 'system' ? '#f0f0f0' : undefined,
                  },
                }}
              />
            ))}
          </div>
        )}
        renderInputArea={(_, onSubmit) => (
          <div style={{ padding: '16px', borderTop: '1px solid #f0f0f0' }}>
            <Sender
              placeholder="输入消息..."
              onSubmit={(message) => {
                handleSend(message);
                onSubmit?.(message);
              }}
              loading={false}
            />
          </div>
        )}
      />
    </Card>
  );
};

export default ChatPanel;
