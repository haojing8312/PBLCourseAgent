/**
 * 步骤导航器组件
 * 使用Ant Design Steps显示UbD三阶段工作流进度
 */
import React from 'react';
import { Steps, Button, Space, Alert } from 'antd';
import type { StepProps } from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  ProjectOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';
import { useCourseStore, type StepStatus } from '@/stores/courseStore';

const { Step } = Steps;

/**
 * UbD三阶段定义
 */
const UBD_STEPS: Array<{
  title: string;
  description: string;
  icon: React.ReactNode;
}> = [
  {
    title: '阶段1: 确定预期学习结果',
    description: '定义G/U/Q/K/S框架',
    icon: <FileTextOutlined />,
  },
  {
    title: '阶段2: 确定可接受的证据',
    description: '设计驱动性问题和表现性任务',
    icon: <CheckCircleOutlined />,
  },
  {
    title: '阶段3: 规划学习体验',
    description: 'PBL四阶段学习蓝图',
    icon: <ProjectOutlined />,
  },
];

/**
 * 将StepStatus映射到Ant Design Steps的status
 */
function mapStepStatus(status: StepStatus): StepProps['status'] {
  switch (status) {
    case 'completed':
      return 'finish';
    case 'in_progress':
      return 'process';
    case 'error':
      return 'error';
    case 'pending':
    default:
      return 'wait';
  }
}

interface StepNavigatorProps {
  /**
   * 是否允许点击切换步骤
   */
  allowStepChange?: boolean;

  /**
   * 自定义className
   */
  className?: string;

  /**
   * 生成指定阶段的回调函数
   */
  onGenerateStage?: (stage: number) => void;
}

/**
 * 步骤导航器组件
 */
export const StepNavigator: React.FC<StepNavigatorProps> = ({
  allowStepChange = true,
  className = '',
  onGenerateStage,
}) => {
  const {
    currentStep,
    setCurrentStep,
    stepStatus,
    stageOneData,
    stageTwoData,
    stageThreeData,
    isGenerating,
  } = useCourseStore();

  /**
   * 处理步骤点击
   */
  const handleStepChange = (newStep: number) => {
    if (!allowStepChange) {
      return;
    }

    // 步骤从0开始，但我们使用1-based索引
    const stepNumber = newStep + 1;

    // 检查是否可以跳转（只能跳转到已完成的步骤或下一个步骤）
    const canNavigate = stepNumber <= currentStep || stepStatus[stepNumber] === 'completed';

    if (canNavigate) {
      setCurrentStep(stepNumber);
    }
  };

  /**
   * 检查当前阶段是否已生成
   */
  const isCurrentStageGenerated = (): boolean => {
    switch (currentStep) {
      case 1:
        return stageOneData !== null;
      case 2:
        return stageTwoData !== null;
      case 3:
        return stageThreeData !== null;
      default:
        return false;
    }
  };

  /**
   * 获取生成按钮文本
   */
  const getGenerateButtonText = (): string => {
    if (isGenerating) {
      return '生成中...';
    }
    return `生成 Stage ${currentStep}`;
  };

  /**
   * 检查是否可以生成当前阶段
   * Stage 2需要Stage 1完成，Stage 3需要Stage 2完成
   */
  const canGenerateCurrentStage = (): boolean => {
    if (currentStep === 1) {
      return true; // Stage 1总是可以生成
    }
    if (currentStep === 2) {
      return stageOneData !== null; // Stage 2需要Stage 1完成
    }
    if (currentStep === 3) {
      return stageTwoData !== null; // Stage 3需要Stage 2完成
    }
    return false;
  };

  return (
    <div className={`step-navigator ${className}`}>
      <Steps
        current={currentStep - 1} // Steps组件使用0-based索引
        onChange={handleStepChange}
        direction="horizontal"
        size="small"
        style={{ padding: '24px 0' }}
      >
        {UBD_STEPS.map((step, index) => {
          const stepNumber = index + 1;
          const status = stepStatus[stepNumber] || 'pending';

          return (
            <Step
              key={stepNumber}
              title={step.title}
              description={step.description}
              icon={step.icon}
              status={mapStepStatus(status)}
              style={{
                cursor: allowStepChange ? 'pointer' : 'default',
              }}
            />
          );
        })}
      </Steps>

      {/* 可选：显示当前步骤的详细信息和生成按钮 */}
      <div
        style={{
          padding: '16px',
          background: '#f0f2f5',
          borderRadius: '4px',
          marginTop: '16px',
        }}
      >
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div>
            <h4 style={{ margin: 0, marginBottom: '8px' }}>
              {UBD_STEPS[currentStep - 1]?.title}
            </h4>
            <p style={{ margin: 0, color: '#666' }}>
              {UBD_STEPS[currentStep - 1]?.description}
            </p>
          </div>

          {/* 如果当前阶段未生成，显示生成按钮 */}
          {!isCurrentStageGenerated() && onGenerateStage && (
            <>
              {!canGenerateCurrentStage() && (
                <Alert
                  type="warning"
                  message={`请先完成 Stage ${currentStep - 1}`}
                  description={`Stage ${currentStep} 需要在前一阶段完成后才能生成。`}
                  showIcon
                  banner
                />
              )}
              <Button
                type="primary"
                size="large"
                icon={<PlayCircleOutlined />}
                onClick={() => onGenerateStage(currentStep)}
                loading={isGenerating}
                disabled={!canGenerateCurrentStage() || isGenerating}
                block
              >
                {getGenerateButtonText()}
              </Button>
            </>
          )}

          {/* 如果阶段已生成，显示完成提示 */}
          {isCurrentStageGenerated() && (
            <Alert
              type="success"
              message={`Stage ${currentStep} 已完成`}
              description="您可以切换到下一阶段，或继续编辑当前阶段。"
              showIcon
              banner
            />
          )}
        </Space>
      </div>
    </div>
  );
};

export default StepNavigator;
