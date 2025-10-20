/**
 * 步骤导航器组件
 * 使用Ant Design Steps显示UbD三阶段工作流进度
 */
import React from 'react';
import { Steps } from 'antd';
import type { StepProps } from 'antd';
import {
  CheckCircleFilled,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { useCourseStore, type StepStatus } from '@/stores/courseStore';

const { Step } = Steps;

/**
 * UbD三阶段定义
 */
const UBD_STEPS: Array<{
  title: string;
  shortTitle: string;
  description?: string;
}> = [
  {
    title: '阶段一：确定预期学习结果',
    shortTitle: '阶段1',
    description: '确定预期学习结果',
  },
  {
    title: '阶段二：确定恰当的评估方法',
    shortTitle: '阶段2',
    description: '确定可接受的证据',
  },
  {
    title: '阶段三：规划相关教学过程',
    shortTitle: '阶段3',
    description: '规划学习体验',
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
   * 是否为紧凑模式（用于Header中）
   */
  compact?: boolean;

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
  compact = false,
  onGenerateStage,
}) => {
  const {
    currentStep,
    setCurrentStep,
    stepStatus,
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
   * 获取步骤图标
   */
  const getStepIcon = (stepNumber: number) => {
    const status = stepStatus[stepNumber] || 'pending';

    if (status === 'completed') {
      return <CheckCircleFilled style={{ fontSize: '20px' }} />;
    }

    return <CheckCircleOutlined style={{ fontSize: '20px' }} />;
  };

  // 紧凑模式：显示完整阶段名称，不显示描述
  if (compact) {
    return (
      <Steps
        current={currentStep - 1}
        onChange={handleStepChange}
        direction="horizontal"
        size="small"
        className={className}
        style={{ margin: 0 }}
      >
        {UBD_STEPS.map((step, index) => {
          const stepNumber = index + 1;
          const status = stepStatus[stepNumber] || 'pending';

          return (
            <Step
              key={stepNumber}
              title={step.title}
              icon={getStepIcon(stepNumber)}
              status={mapStepStatus(status)}
              style={{
                cursor: allowStepChange ? 'pointer' : 'default',
              }}
            />
          );
        })}
      </Steps>
    );
  }

  // 完整模式：保留原有功能（暂时不使用）
  return (
    <div className={`step-navigator ${className}`}>
      <Steps
        current={currentStep - 1}
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
              icon={getStepIcon(stepNumber)}
              status={mapStepStatus(status)}
              style={{
                cursor: allowStepChange ? 'pointer' : 'default',
              }}
            />
          );
        })}
      </Steps>
    </div>
  );
};

export default StepNavigator;
