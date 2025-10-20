/**
 * AppHeader - 统一的应用顶部导航
 *
 * 提供一致的Header布局和交互
 * 遵循"Good taste"原则：Header在所有页面保持一致
 *
 * @example
 * ```tsx
 * // 基础用法
 * <AppHeader
 *   title="UbD-PBL 课程架构师"
 *   onHelpClick={() => setHelpOpen(true)}
 * />
 *
 * // 自定义标题和操作区
 * <AppHeader
 *   title={
 *     <Space>
 *       <span>应用名称</span>
 *       <Text type="secondary">当前项目</Text>
 *     </Space>
 *   }
 *   extra={
 *     <>
 *       <Button>操作1</Button>
 *       <Button type="primary">操作2</Button>
 *     </>
 *   }
 *   onHelpClick={() => setHelpOpen(true)}
 * />
 * ```
 */

import React from 'react';
import { Layout, Row, Col, Space, Button } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';
import { SPACING, COLORS, COMPONENT_HEIGHT } from '@/constants/layout';

const { Header } = Layout;

export interface AppHeaderProps {
  /**
   * 页面标题（左侧）
   * 可以是字符串或自定义React节点
   */
  title?: React.ReactNode;

  /**
   * 中间区域内容
   * 用于显示步骤导航等
   */
  center?: React.ReactNode;

  /**
   * 右侧操作区
   * 通常放置按钮、下拉菜单等
   */
  extra?: React.ReactNode;

  /**
   * 帮助按钮点击回调
   * 如果提供，会在右侧显示帮助按钮
   */
  onHelpClick?: () => void;

  /**
   * 是否显示帮助按钮
   * @default true（当onHelpClick存在时）
   */
  showHelp?: boolean;

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
 * AppHeader组件
 *
 * 负责：
 * 1. 统一Header高度和样式
 * 2. 统一左右布局结构
 * 3. 统一交互元素（帮助按钮等）
 */
export const AppHeader: React.FC<AppHeaderProps> = ({
  title = 'UbD-PBL 课程架构师',
  center,
  extra,
  onHelpClick,
  showHelp = true,
  style,
  className = '',
}) => {
  const headerStyle: React.CSSProperties = {
    background: COLORS.BG_CONTAINER,
    padding: `0 ${SPACING.MD}px`,
    borderBottom: `1px solid ${COLORS.BORDER}`,
    height: COMPONENT_HEIGHT.HEADER,
    lineHeight: `${COMPONENT_HEIGHT.HEADER}px`,
    ...style,
  };

  return (
    <Header className={`app-header ${className}`} style={headerStyle}>
      <Row justify="space-between" align="middle" style={{ height: '100%' }}>
        {/* 左侧：标题区域 */}
        <Col flex="0 0 auto">
          <Space size="large">
            {typeof title === 'string' ? (
              <h2 style={{ margin: 0, color: COLORS.PRIMARY, fontSize: 20, fontWeight: 600 }}>
                {title}
              </h2>
            ) : (
              title
            )}
          </Space>
        </Col>

        {/* 中间：步骤导航等 */}
        {center && (
          <Col flex="1 1 auto" style={{ display: 'flex', justifyContent: 'center' }}>
            {center}
          </Col>
        )}

        {/* 右侧：操作区域 */}
        <Col flex="0 0 auto">
          <Space>
            {/* 帮助按钮 */}
            {showHelp && onHelpClick && (
              <Button icon={<QuestionCircleOutlined />} onClick={onHelpClick}>
                帮助
              </Button>
            )}

            {/* 自定义操作区 */}
            {extra}
          </Space>
        </Col>
      </Row>
    </Header>
  );
};

export default AppHeader;
