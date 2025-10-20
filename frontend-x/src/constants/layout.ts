/**
 * 布局常量 - 统一的设计系统
 *
 * 遵循"Good taste"原则：
 * - 所有布局相关的magic number都在这里定义
 * - 使用8px网格系统，确保视觉一致性
 * - 提供响应式断点支持
 */

/**
 * 容器最大宽度
 *
 * FULL: 100% - 适用于需要全屏的场景（如画布）
 * WIDE: 1600px - 适用于多列布局（如课程设计页）
 * NORMAL: 1200px - 适用于标准内容页（如列表页）
 * NARROW: 960px - 适用于表单页（如创建课程）
 */
export const LAYOUT_MAX_WIDTH = {
  FULL: '100%',
  WIDE: 1600,
  NORMAL: 1200,
  NARROW: 960,
} as const;

/**
 * 间距系统（基于8px网格）
 *
 * XS: 8px - 最小间距
 * SM: 16px - 小间距
 * MD: 24px - 标准间距（最常用）
 * LG: 32px - 大间距
 * XL: 48px - 超大间距
 */
export const SPACING = {
  XS: 8,
  SM: 16,
  MD: 24,
  LG: 32,
  XL: 48,
} as const;

/**
 * 组件高度常量
 */
export const COMPONENT_HEIGHT = {
  HEADER: 64,      // 顶部导航栏高度
  STEP_BAR: 140,   // 步骤导航栏高度（包含padding）
  FOOTER: 64,      // 页脚高度（预留）
} as const;

/**
 * 颜色系统
 *
 * 保持与Ant Design默认主题一致
 */
export const COLORS = {
  BG_PAGE: '#f0f2f5',       // 页面背景色
  BG_CONTAINER: '#fff',      // 容器背景色
  BORDER: '#f0f0f0',         // 边框颜色
  PRIMARY: '#1890ff',        // 主题色
  TEXT_PRIMARY: '#000000d9', // 主文本色
  TEXT_SECONDARY: '#00000073', // 次要文本色
} as const;

/**
 * 响应式断点（与Ant Design Grid一致）
 */
export const BREAKPOINTS = {
  XS: 480,   // 手机
  SM: 576,   // 平板竖屏
  MD: 768,   // 平板横屏
  LG: 992,   // 笔记本
  XL: 1200,  // 桌面显示器
  XXL: 1600, // 大屏显示器
} as const;

/**
 * Z-index层级系统
 */
export const Z_INDEX = {
  DROPDOWN: 1000,
  MODAL: 1000,
  NOTIFICATION: 1010,
  TOOLTIP: 1030,
  HEADER: 100,
} as const;

/**
 * 动画时长（毫秒）
 */
export const ANIMATION_DURATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
} as const;

/**
 * 工具函数：计算内容区域高度
 *
 * @param hasStepBar - 是否有步骤导航栏
 * @returns CSS calc表达式
 */
export function getContentHeight(hasStepBar: boolean = false): string {
  const offset = hasStepBar
    ? COMPONENT_HEIGHT.HEADER + COMPONENT_HEIGHT.STEP_BAR
    : COMPONENT_HEIGHT.HEADER;

  return `calc(100vh - ${offset}px)`;
}

/**
 * 工具函数：获取响应式padding
 *
 * @param size - 间距大小
 * @returns 响应式padding字符串
 */
export function getResponsivePadding(size: keyof typeof SPACING = 'MD'): string {
  const value = SPACING[size];
  // 移动端使用较小的padding
  return `max(${SPACING.SM}px, ${value}px)`;
}
