/**
 * ContentPanel - 内容展示面板
 * 展示UbD三阶段的Markdown内容
 *
 * V2: 简化为Markdown展示（移除JSON解析逻辑）
 */

import React from 'react';
import { Card, Space, Button, Tooltip, Empty } from 'antd';
import { EditOutlined, EyeOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { MarkdownPreview } from './MarkdownPreview';

export interface ContentPanelProps {
  /** 当前步骤 (1-3) */
  currentStep: number;

  /** Stage One数据 (Markdown字符串) */
  stageOneData?: string;

  /** Stage Two数据 (Markdown字符串) */
  stageTwoData?: string;

  /** Stage Three数据 (Markdown字符串) */
  stageThreeData?: string;

  /** 是否为编辑模式 */
  isEditMode?: boolean;

  /** 切换编辑模式 */
  onToggleEdit?: () => void;

  /** 生成下一阶段的回调 */
  onGenerateNextStage?: () => void;

  /** 是否正在生成 */
  isGenerating?: boolean;

  /** 自定义样式 */
  style?: React.CSSProperties;
}

/**
 * ContentPanel组件
 *
 * 根据当前步骤展示对应的Stage Markdown内容
 *
 * @example
 * ```tsx
 * <ContentPanel
 *   currentStep={1}
 *   stageOneData={markdownString}
 *   isEditMode={false}
 *   onToggleEdit={() => setEditMode(!editMode)}
 * />
 * ```
 */
export const ContentPanel: React.FC<ContentPanelProps> = ({
  currentStep,
  stageOneData,
  stageTwoData,
  stageThreeData,
  isEditMode = false,
  onToggleEdit,
  onGenerateNextStage,
  isGenerating = false,
  style,
}) => {
  /**
   * 获取当前阶段的数据（用于判断是否已生成）
   */
  const getCurrentStageData = (): string | undefined => {
    switch (currentStep) {
      case 1:
        return stageOneData;
      case 2:
        return stageTwoData;
      case 3:
        return stageThreeData;
      default:
        return undefined;
    }
  };

  /**
   * 渲染内容
   */
  const renderContent = () => {
    const currentData = getCurrentStageData();

    if (!currentData) {
      return (
        <Empty
          description={
            <span>
              {currentStep === 1
                ? '暂无数据，请先生成或输入课程信息'
                : `暂无数据，请先完成 Stage ${currentStep - 1}`}
            </span>
          }
        />
      );
    }

    return <MarkdownPreview content={currentData} />;
  };

  /**
   * 获取阶段标题
   */
  const getStageTitle = (step: number): string => {
    const titles = [
      '确定预期学习结果',
      '确定可接受的证据',
      '规划学习体验'
    ];
    return `Stage ${step} - UbD ${titles[step - 1]}`;
  };

  return (
    <Card
      title={getStageTitle(currentStep)}
      extra={
        <Space>
          {onToggleEdit && (
            <Button
              type="text"
              icon={isEditMode ? <EyeOutlined /> : <EditOutlined />}
              onClick={onToggleEdit}
            >
              {isEditMode ? '查看模式' : '编辑模式'}
            </Button>
          )}
          {/* 开始下一阶段按钮 */}
          {onGenerateNextStage && currentStep < 3 && getCurrentStageData() && (
            <Tooltip title={`当前阶段已完成，点击生成${['阶段二', '阶段三'][currentStep - 1]}`}>
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                onClick={onGenerateNextStage}
                loading={isGenerating}
                disabled={isGenerating}
              >
                开始{['阶段二', '阶段三'][currentStep - 1]}
              </Button>
            </Tooltip>
          )}
        </Space>
      }
      style={{ height: '100%', ...style }}
      styles={{ body: { overflowY: 'auto', padding: '24px' } }}
    >
      {renderContent()}
    </Card>
  );
};

export default ContentPanel;
