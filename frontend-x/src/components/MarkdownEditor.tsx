/**
 * MarkdownEditor - Markdown编辑器组件
 * 提供Markdown编辑和实时预览功能
 */

import React, { useRef, useEffect } from 'react';
import { Card, Space, Button, Badge } from 'antd';
import { EyeOutlined, SaveOutlined, UndoOutlined } from '@ant-design/icons';
import { useMarkdownSync, getSaveStatus, getSaveStatusColor } from '../hooks/useMarkdownSync';
import './MarkdownEditor.css';

export interface MarkdownEditorProps {
  /** 当前步骤 (1-3) */
  step: number;

  /** 初始内容 */
  _initialContent?: string;

  /** 自动保存延迟（毫秒） */
  debounceMs?: number;

  /** 启用自动保存 */
  autoSave?: boolean;

  /** 保存回调 */
  onSave?: (step: number, markdown: string) => Promise<void>;

  /** 切换编辑模式回调（退出编辑模式） */
  onToggleEdit?: () => void;

  /** 自定义样式 */
  style?: React.CSSProperties;

  /** 高度（已废弃，现在使用flex布局自适应） */
  height?: string | number;
}

/**
 * MarkdownEditor组件
 *
 * 提供编辑和预览两个模式，支持自动保存
 *
 * @example
 * ```tsx
 * <MarkdownEditor
 *   step={1}
 *   autoSave={true}
 *   onSave={async (step, content) => {
 *     await updateMarkdown(courseId, step, content);
 *   }}
 * />
 * ```
 */
export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  step,
  _initialContent = '',
  debounceMs = 1000,
  autoSave = false,
  onSave,
  onToggleEdit,
  style,
  height: _deprecatedHeight,
}) => {
  // Textarea ref 用于恢复光标位置
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // 保存光标位置
  const cursorPositionRef = useRef<{ start: number; end: number } | null>(null);

  const {
    markdown,
    setMarkdown,
    isDirty,
    isSaving,
    save,
    reset,
  } = useMarkdownSync({
    step,
    debounceMs,
    autoSave,
    onSave,
  });

  /**
   * 恢复光标位置
   */
  useEffect(() => {
    if (textareaRef.current && cursorPositionRef.current) {
      const { start, end } = cursorPositionRef.current;
      textareaRef.current.setSelectionRange(start, end);
    }
  }, [markdown]);

  /**
   * 处理文本变化（保存光标位置）
   */
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = e.target;

    // 保存光标位置
    cursorPositionRef.current = {
      start: textarea.selectionStart,
      end: textarea.selectionEnd,
    };

    // 更新内容
    setMarkdown(textarea.value);
  };

  /**
   * 手动保存
   */
  const handleManualSave = async () => {
    try {
      await save();
    } catch (error) {
      console.error('[MarkdownEditor] Manual save failed:', error);
    }
  };

  /**
   * 重置内容
   */
  const handleReset = () => {
    if (window.confirm('确定要重置内容吗？未保存的更改将丢失。')) {
      reset();
    }
  };

  const saveStatusText = getSaveStatus(isDirty, isSaving);
  const saveStatusColor = getSaveStatusColor(isDirty, isSaving);

  return (
    <Card
      title={
        <Space>
          <span>Markdown编辑器</span>
          <Badge
            status={saveStatusColor}
            text={saveStatusText}
          />
        </Space>
      }
      extra={
        <Space>
          {onToggleEdit && (
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={onToggleEdit}
            >
              查看模式
            </Button>
          )}
          {isDirty && !autoSave && (
            <Button
              type="primary"
              size="small"
              icon={<SaveOutlined />}
              onClick={handleManualSave}
              loading={isSaving}
            >
              保存
            </Button>
          )}
          {isDirty && (
            <Button
              size="small"
              icon={<UndoOutlined />}
              onClick={handleReset}
            >
              重置
            </Button>
          )}
        </Space>
      }
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        ...style
      }}
      styles={{
        body: {
          padding: 0,
          flex: 1,
          minHeight: 0,
          overflow: 'hidden',
        }
      }}
    >
      <textarea
        ref={textareaRef}
        className="markdown-editor-textarea"
        value={markdown}
        onChange={handleChange}
        placeholder="在此输入Markdown内容..."
        style={{
          width: '100%',
          height: '100%',
          resize: 'none',
          boxSizing: 'border-box',
          border: 'none',
          outline: 'none',
          padding: '16px',
        }}
      />
    </Card>
  );
};

export default MarkdownEditor;
