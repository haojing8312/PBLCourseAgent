/**
 * MarkdownPreview - Markdown预览组件
 * 使用react-markdown和remark-gfm渲染GitHub风格的Markdown
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Typography } from 'antd';
import './MarkdownPreview.css';

const { Title, Paragraph, Text } = Typography;

export interface MarkdownPreviewProps {
  /** Markdown内容 */
  content: string;

  /** 自定义样式 */
  style?: React.CSSProperties;

  /** 自定义CSS类名 */
  className?: string;

  /** 是否显示为紧凑模式 */
  compact?: boolean;
}

/**
 * MarkdownPreview组件
 *
 * 渲染Markdown内容，支持GFM（GitHub Flavored Markdown）
 *
 * @example
 * ```tsx
 * <MarkdownPreview
 *   content={markdownText}
 *   className="custom-preview"
 * />
 * ```
 */
export const MarkdownPreview: React.FC<MarkdownPreviewProps> = ({
  content,
  style,
  className,
  compact = false,
}) => {
  return (
    <div
      className={`markdown-preview ${compact ? 'compact' : ''} ${className || ''}`}
      style={style}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // 自定义标题渲染
          h1: ({ children }) => <Title level={1}>{children}</Title>,
          h2: ({ children }) => <Title level={2}>{children}</Title>,
          h3: ({ children }) => <Title level={3}>{children}</Title>,
          h4: ({ children }) => <Title level={4}>{children}</Title>,
          h5: ({ children }) => <Title level={5}>{children}</Title>,

          // 自定义段落渲染
          p: ({ children }) => <Paragraph>{children}</Paragraph>,

          // 自定义代码块渲染
          code: ({ inline, className, children, ...props }) => {
            if (inline) {
              return <Text code>{children}</Text>;
            }
            return (
              <pre className={className} {...props}>
                <code>{children}</code>
              </pre>
            );
          },

          // 自定义表格渲染
          table: ({ children }) => (
            <div style={{ overflowX: 'auto', marginBottom: '16px' }}>
              <table className="markdown-table">{children}</table>
            </div>
          ),

          // 自定义列表渲染
          ul: ({ children }) => (
            <ul className="markdown-list">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="markdown-list">{children}</ol>
          ),

          // 自定义链接渲染
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className="markdown-link">
              {children}
            </a>
          ),

          // 自定义引用块渲染
          blockquote: ({ children }) => (
            <blockquote className="markdown-blockquote">{children}</blockquote>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownPreview;
