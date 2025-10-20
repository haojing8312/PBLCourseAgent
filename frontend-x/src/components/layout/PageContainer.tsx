/**
 * PageContainer - 统一的页面容器
 *
 * 提供一致的宽度、间距和响应式支持
 * 遵循"Good taste"原则：所有页面使用相同的容器，无特殊情况
 *
 * @example
 * ```tsx
 * // 标准列表页
 * <PageContainer maxWidth="normal">
 *   <ProjectListView />
 * </PageContainer>
 *
 * // 宽屏课程设计页
 * <PageContainer maxWidth="wide">
 *   <CourseDesignView />
 * </PageContainer>
 *
 * // 窄屏表单页
 * <PageContainer maxWidth="narrow" background>
 *   <CreateCourseForm />
 * </PageContainer>
 * ```
 */

import React from 'react';
import { LAYOUT_MAX_WIDTH, SPACING, COLORS } from '@/constants/layout';

export interface PageContainerProps {
  /**
   * 容器最大宽度
   * - full: 100% 全屏（如画布）
   * - wide: 1600px 宽屏（如课程设计页）
   * - normal: 1200px 标准（如列表页）
   * - narrow: 960px 窄屏（如表单页）
   */
  maxWidth?: 'full' | 'wide' | 'normal' | 'narrow';

  /**
   * 内边距大小
   * - XS: 8px
   * - SM: 16px
   * - MD: 24px（默认）
   * - LG: 32px
   * - XL: 48px
   */
  padding?: keyof typeof SPACING;

  /**
   * 是否显示白色背景
   * @default false
   */
  background?: boolean;

  /**
   * 子元素
   */
  children: React.ReactNode;

  /**
   * 自定义样式（会覆盖默认样式）
   */
  style?: React.CSSProperties;

  /**
   * 自定义CSS类名
   */
  className?: string;
}

/**
 * PageContainer组件
 *
 * 负责：
 * 1. 统一容器宽度
 * 2. 统一内边距
 * 3. 响应式支持
 * 4. 水平居中
 */
export const PageContainer: React.FC<PageContainerProps> = ({
  maxWidth = 'wide',
  padding = 'MD',
  background = false,
  children,
  style,
  className = '',
}) => {
  // 获取最大宽度值
  const getMaxWidth = () => {
    const key = maxWidth.toUpperCase() as keyof typeof LAYOUT_MAX_WIDTH;
    const value = LAYOUT_MAX_WIDTH[key];
    return typeof value === 'number' ? `${value}px` : value;
  };

  const containerStyle: React.CSSProperties = {
    width: '100%',
    maxWidth: getMaxWidth(),
    margin: '0 auto',
    padding: SPACING[padding],
    background: background ? COLORS.BG_CONTAINER : 'transparent',
    ...style,
  };

  return (
    <div className={`page-container ${className}`} style={containerStyle}>
      {children}
    </div>
  );
};

export default PageContainer;
