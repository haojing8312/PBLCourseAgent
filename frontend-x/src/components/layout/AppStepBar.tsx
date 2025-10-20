/**
 * AppStepBar - 步骤导航栏容器
 *
 * 为StepNavigator提供统一的容器样式
 * 遵循"Good taste"原则：步骤栏在所有使用它的页面保持一致
 *
 * @example
 * ```tsx
 * <AppStepBar>
 *   <StepNavigator
 *     allowStepChange={true}
 *     onGenerateStage={handleGenerateStage}
 *   />
 * </AppStepBar>
 * ```
 */

import React from 'react';
import { SPACING, COLORS } from '@/constants/layout';

export interface AppStepBarProps {
  /**
   * 子元素（通常是StepNavigator）
   */
  children: React.ReactNode;

  /**
   * 自定义样式
   */
  style?: React.CSSProperties;

  /**
   * 自定义className
   */
  className?: string;
}

/**
 * AppStepBar组件
 *
 * 负责：
 * 1. 统一步骤栏的背景和边框
 * 2. 统一步骤栏的内边距
 * 3. 保持与Header的视觉一致性
 */
export const AppStepBar: React.FC<AppStepBarProps> = ({
  children,
  style,
  className = '',
}) => {
  const containerStyle: React.CSSProperties = {
    background: COLORS.BG_CONTAINER,
    padding: `${SPACING.SM}px ${SPACING.MD}px`,
    borderBottom: `1px solid ${COLORS.BORDER}`,
    ...style,
  };

  return (
    <div className={`app-step-bar ${className}`} style={containerStyle}>
      {children}
    </div>
  );
};

export default AppStepBar;
