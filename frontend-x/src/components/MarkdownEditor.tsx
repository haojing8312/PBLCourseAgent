/**
 * MarkdownEditor - Markdown编辑器组件
 * 提供Markdown编辑和实时预览功能
 */

import React, { useState } from 'react';
import { Card, Tabs, Space, Button, Badge } from 'antd';
import { EyeOutlined, EditOutlined, SaveOutlined, UndoOutlined } from '@ant-design/icons';
import { MarkdownPreview } from './MarkdownPreview';
import { useMarkdownSync, getSaveStatus, getSaveStatusColor } from '../hooks/useMarkdownSync';
import './MarkdownEditor.css';

const { TabPane } = Tabs;

export interface MarkdownEditorProps {
  /** 当前步骤 (1-3) */
  step: number;

  /** 初始内容 */
  initialContent?: string;

  /** 自动保存延迟（毫秒） */
  debounceMs?: number;

  /** 启用自动保存 */
  autoSave?: boolean;

  /** 保存回调 */
  onSave?: (step: number, markdown: string) => Promise<void>;

  /** 自定义样式 */
  style?: React.CSSProperties;

  /** 高度 */
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
 *   height="600px"
 * />
 * ```
 */
export const MarkdownEditor: React.FC<MarkdownEditorProps> = ({
  step,
  initialContent = '',
  debounceMs = 1000,
  autoSave = false,
  onSave,
  style,
  height = '600px',
}) => {
  const [activeTab, setActiveTab] = useState<'edit' | 'preview'>('edit');

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
      style={{ height: '100%', ...style }}
      bodyStyle={{
        padding: 0,
        height: `calc(100% - 57px)`,
        overflow: 'hidden',
      }}
    >
      <Tabs
        activeKey={activeTab}
        onChange={(key) => setActiveTab(key as 'edit' | 'preview')}
        style={{ height: '100%' }}
        tabBarStyle={{ paddingLeft: '16px', paddingRight: '16px', marginBottom: 0 }}
      >
        <TabPane
          tab={
            <span>
              <EditOutlined /> 编辑
            </span>
          }
          key="edit"
        >
          <textarea
            className="markdown-editor-textarea"
            value={markdown}
            onChange={(e) => setMarkdown(e.target.value)}
            placeholder="在此输入Markdown内容..."
            style={{
              width: '100%',
              height: typeof height === 'number' ? `${height}px` : height,
              resize: 'none',
            }}
          />
        </TabPane>

        <TabPane
          tab={
            <span>
              <EyeOutlined /> 预览
            </span>
          }
          key="preview"
        >
          <div
            style={{
              height: typeof height === 'number' ? `${height}px` : height,
              overflowY: 'auto',
            }}
          >
            <MarkdownPreview content={markdown} />
          </div>
        </TabPane>
      </Tabs>
    </Card>
  );
};

export default MarkdownEditor;
