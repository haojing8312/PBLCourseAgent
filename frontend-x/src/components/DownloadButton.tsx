/**
 * DownloadButton - 下载按钮组件
 * 导出课程方案为Markdown文件
 */

import React, { useState } from 'react';
import { Button, Dropdown, message, Space } from 'antd';
import type { MenuProps } from 'antd';
import { DownloadOutlined, CopyOutlined, EyeOutlined } from '@ant-design/icons';
import {
  exportCourseAsMarkdown,
  copyMarkdownToClipboard,
  previewMarkdown,
} from '../services/exportService';

export interface DownloadButtonProps {
  /** 课程ID */
  courseId?: number;

  /** 按钮文本 */
  text?: string;

  /** 按钮类型 */
  type?: 'primary' | 'default' | 'dashed' | 'text' | 'link';

  /** 按钮大小 */
  size?: 'small' | 'middle' | 'large';

  /** 是否显示下拉菜单 */
  dropdown?: boolean;

  /** 禁用状态 */
  disabled?: boolean;

  /** 自定义样式 */
  style?: React.CSSProperties;

  /** 预览回调（打开模态框展示Markdown） */
  onPreview?: (markdown: string) => void;
}

/**
 * DownloadButton组件
 *
 * 提供课程方案导出功能，支持下载、复制、预览
 *
 * @example
 * ```tsx
 * // 简单模式
 * <DownloadButton courseId={123} text="下载教案" />
 *
 * // 下拉菜单模式
 * <DownloadButton
 *   courseId={123}
 *   dropdown={true}
 *   onPreview={(markdown) => setPreviewContent(markdown)}
 * />
 * ```
 */
export const DownloadButton: React.FC<DownloadButtonProps> = ({
  courseId,
  text = '导出课程',
  type = 'primary',
  size = 'middle',
  dropdown = false,
  disabled = false,
  style,
  onPreview,
}) => {
  const [loading, setLoading] = useState(false);

  /**
   * 下载为Markdown文件
   */
  const handleDownload = async () => {
    if (!courseId) {
      message.error('请先创建或选择课程项目');
      return;
    }

    setLoading(true);
    try {
      await exportCourseAsMarkdown(courseId);
      message.success('课程方案已下载');
    } catch (error) {
      console.error('[DownloadButton] Download failed:', error);
      message.error(`下载失败: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 复制Markdown到剪贴板
   */
  const handleCopy = async () => {
    if (!courseId) {
      message.error('请先创建或选择课程项目');
      return;
    }

    setLoading(true);
    try {
      await copyMarkdownToClipboard(courseId);
      message.success('Markdown内容已复制到剪贴板');
    } catch (error) {
      console.error('[DownloadButton] Copy failed:', error);
      message.error(`复制失败: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 预览Markdown内容
   */
  const handlePreview = async () => {
    if (!courseId) {
      message.error('请先创建或选择课程项目');
      return;
    }

    setLoading(true);
    try {
      const markdown = await previewMarkdown(courseId);
      onPreview?.(markdown);
      message.info('Markdown预览已加载');
    } catch (error) {
      console.error('[DownloadButton] Preview failed:', error);
      message.error(`预览失败: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  // 下拉菜单项
  const menuItems: MenuProps['items'] = [
    {
      key: 'download',
      label: '下载为Markdown',
      icon: <DownloadOutlined />,
      onClick: handleDownload,
    },
    {
      key: 'copy',
      label: '复制到剪贴板',
      icon: <CopyOutlined />,
      onClick: handleCopy,
    },
  ];

  // 如果提供了预览回调，添加预览选项
  if (onPreview) {
    menuItems.push({
      key: 'preview',
      label: '预览Markdown',
      icon: <EyeOutlined />,
      onClick: handlePreview,
    });
  }

  // 如果启用下拉菜单
  if (dropdown) {
    return (
      <Dropdown menu={{ items: menuItems }} trigger={['click']} disabled={disabled || !courseId}>
        <Button
          type={type}
          size={size}
          loading={loading}
          icon={<DownloadOutlined />}
          disabled={disabled || !courseId}
          style={style}
        >
          <Space>
            {text}
          </Space>
        </Button>
      </Dropdown>
    );
  }

  // 简单模式：直接下载按钮
  return (
    <Button
      type={type}
      size={size}
      loading={loading}
      icon={<DownloadOutlined />}
      onClick={handleDownload}
      disabled={disabled || !courseId}
      style={style}
    >
      {text}
    </Button>
  );
};

export default DownloadButton;
