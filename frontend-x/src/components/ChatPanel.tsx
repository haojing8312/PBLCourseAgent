/**
 * ChatPanel - AI对话面板 (对标ChatGPT)
 *
 * 功能：
 * - 流式AI回复（打字机效果）
 * - Markdown渲染
 * - 代码高亮
 * - 停止生成
 * - 复制内容
 */

import React, { useMemo, useEffect, useRef } from 'react';
import { Card, Space, Button, Tooltip, Badge, Spin } from 'antd';
import {
  DeleteOutlined,
  DownloadOutlined,
  InfoCircleOutlined,
  StopOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import { useChatConversation } from '../hooks/useChatConversation';
import 'highlight.js/styles/github-dark.css'; // 代码高亮样式

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
 * 单个消息气泡组件
 */
const MessageBubble: React.FC<{
  role: 'user' | 'assistant' | 'system';
  content: string;
  isStreaming?: boolean;
}> = ({ role, content, isStreaming }) => {
  const isUser = role === 'user';
  const isSystem = role === 'system';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '16px',
      }}
    >
      <div
        style={{
          maxWidth: '80%',
          padding: '12px 16px',
          borderRadius: '12px',
          background: isUser
            ? '#1677ff'
            : isSystem
            ? '#f0f0f0'
            : '#ffffff',
          color: isUser ? '#ffffff' : isSystem ? '#666666' : '#000000',
          border: !isUser && !isSystem ? '1px solid #e8e8e8' : 'none',
          boxShadow: !isUser && !isSystem ? '0 1px 2px rgba(0,0,0,0.05)' : 'none',
        }}
        data-ai-streaming={isStreaming ? 'true' : undefined}
      >
        {/* AI回复使用Markdown渲染 */}
        {role === 'assistant' ? (
          <ReactMarkdown
            rehypePlugins={[rehypeHighlight]}
            components={{
              // 自定义代码块样式
              code({node, inline, className, children, ...props}) {
                return inline ? (
                  <code
                    style={{
                      background: '#f6f8fa',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      fontSize: '0.9em',
                    }}
                    {...props}
                  >
                    {children}
                  </code>
                ) : (
                  <code className={className} style={{ display: 'block' }} {...props}>
                    {children}
                  </code>
                );
              },
              // 自定义链接样式
              a({node, children, ...props}) {
                return (
                  <a
                    {...props}
                    style={{ color: '#1677ff', textDecoration: 'underline' }}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {children}
                  </a>
                );
              },
            }}
          >
            {content}
          </ReactMarkdown>
        ) : (
          // 用户和系统消息直接显示
          <div style={{ whiteSpace: 'pre-wrap' }}>{content}</div>
        )}

        {/* 流式生成动画 */}
        {isStreaming && (
          <span
            style={{
              display: 'inline-block',
              width: '8px',
              height: '16px',
              marginLeft: '4px',
              background: '#666',
              animation: 'blink 1s infinite',
            }}
          />
        )}
      </div>
    </div>
  );
};

/**
 * ChatPanel组件
 *
 * 提供ChatGPT式的对话界面
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
    isAIResponding,
    streamingMessage,
    abortAIResponse,
  } = useChatConversation({
    currentStep,
    courseId,
    autoSync,
  });

  // 输入框引用
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // 消息列表引用（用于自动滚动）
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  /**
   * 处理发送消息
   */
  const handleSend = async () => {
    const input = inputRef.current;
    if (!input || !input.value.trim()) return;

    const message = input.value.trim();
    input.value = '';

    // 发送消息（自动触发AI回复）
    await sendMessage(message);
  };

  /**
   * 处理Enter键发送
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
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
        const timestamp =
          typeof msg.timestamp === 'string'
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

  // 无课程ID时禁用
  const disabled = !courseId;

  return (
    <>
      {/* 添加打字机动画CSS */}
      <style>
        {`
          @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
          }
        `}
      </style>

      <Card
        title={
          <Space>
            {title || `Step ${currentStep} 对话`}
            {hasMessages && <Badge count={messages.length} showZero={false} />}
          </Space>
        }
        extra={
          <Space>
            {isAIResponding && (
              <Tooltip title="停止生成">
                <Button
                  type="text"
                  danger
                  icon={<StopOutlined />}
                  onClick={abortAIResponse}
                  size="small"
                />
              </Tooltip>
            )}
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
            <Tooltip title="与AI讨论和完善课程方案">
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
        styles={{
          body: {
            flex: 1,
            overflow: 'hidden',
            padding: 0,
            display: 'flex',
            flexDirection: 'column',
          },
        }}
        className={className}
      >
        {/* 消息列表 */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '16px',
            background: '#fafafa',
          }}
        >
          {disabled ? (
            <div
              style={{
                textAlign: 'center',
                padding: '40px 20px',
                color: '#999',
              }}
            >
              <InfoCircleOutlined style={{ fontSize: '32px', marginBottom: '12px' }} />
              <p>请先创建课程才能开始对话</p>
            </div>
          ) : messages.length === 0 && !isAIResponding ? (
            <div
              style={{
                textAlign: 'center',
                padding: '40px 20px',
                color: '#999',
              }}
            >
              <InfoCircleOutlined style={{ fontSize: '32px', marginBottom: '12px' }} />
              <p>开始与AI对话，讨论和完善你的课程设计</p>
              <p style={{ fontSize: '12px', marginTop: '8px' }}>
                提示：你可以询问设计建议、修改意见、理论依据等
              </p>
            </div>
          ) : (
            <>
              {/* 历史消息 */}
              {messages.map((msg) => (
                <MessageBubble
                  key={msg.id}
                  role={msg.role}
                  content={msg.content}
                />
              ))}

              {/* 流式生成中的消息 */}
              {isAIResponding && streamingMessage && (
                <MessageBubble
                  role="assistant"
                  content={streamingMessage}
                  isStreaming={true}
                />
              )}

              {/* AI思考中（没有内容时） */}
              {isAIResponding && !streamingMessage && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Spin size="small" />
                  <span style={{ color: '#999' }}>AI正在思考...</span>
                </div>
              )}

              {/* 自动滚动锚点 */}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* 输入区域 */}
        <div
          style={{
            padding: '16px',
            borderTop: '1px solid #f0f0f0',
            background: '#ffffff',
          }}
        >
          <div style={{ display: 'flex', gap: '8px' }}>
            <textarea
              ref={inputRef}
              placeholder={disabled ? '请先创建课程...' : '输入消息... (Shift+Enter换行)'}
              disabled={disabled || isAIResponding}
              onKeyDown={handleKeyDown}
              style={{
                flex: 1,
                padding: '8px 12px',
                border: '1px solid #d9d9d9',
                borderRadius: '8px',
                resize: 'none',
                minHeight: '40px',
                maxHeight: '120px',
                fontFamily: 'inherit',
                fontSize: '14px',
              }}
              rows={2}
            />
            <Button
              type="primary"
              onClick={handleSend}
              disabled={disabled || isAIResponding}
              style={{ alignSelf: 'flex-end' }}
            >
              发送
            </Button>
          </div>
        </div>
      </Card>
    </>
  );
};

export default ChatPanel;
