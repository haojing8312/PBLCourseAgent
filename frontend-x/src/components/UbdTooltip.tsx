/**
 * UbdTooltip - UbD理论提示气泡
 * 展示UbD框架的核心概念定义和说明
 */

import React from 'react';
import { Tooltip, Popover, Space, Typography, Tag, Divider } from 'antd';
import { QuestionCircleOutlined, InfoCircleOutlined } from '@ant-design/icons';
import {
  UBD_STAGE_ONE_ELEMENTS,
  UBD_ELEMENT_COLORS,
  type UbdElement,
} from '../constants/ubdDefinitions';

const { Title, Text, Paragraph } = Typography;

export interface UbdTooltipProps {
  /** UbD元素符号 (G/U/Q/K/S) */
  element: 'G' | 'U' | 'Q' | 'K' | 'S';

  /** 展示模式 */
  mode?: 'tooltip' | 'popover';

  /** 子元素（如果不提供，则显示默认图标） */
  children?: React.ReactNode;

  /** 触发方式 */
  trigger?: 'hover' | 'click';

  /** 自定义样式 */
  style?: React.CSSProperties;
}

/**
 * UbdTooltip组件
 *
 * 为UbD元素提供理论说明的工具提示
 *
 * @example
 * ```tsx
 * // 简单模式：图标+tooltip
 * <UbdTooltip element="U" mode="tooltip" />
 *
 * // 完整模式：包裹文本+popover
 * <UbdTooltip element="G" mode="popover">
 *   <Text strong>迁移目标</Text>
 * </UbdTooltip>
 * ```
 */
export const UbdTooltip: React.FC<UbdTooltipProps> = ({
  element,
  mode = 'tooltip',
  children,
  trigger = 'hover',
  style,
}) => {
  const definition = UBD_STAGE_ONE_ELEMENTS[element];

  if (!definition) {
    console.warn(`[UbdTooltip] Unknown element: ${element}`);
    return <>{children || null}</>;
  }

  const color = UBD_ELEMENT_COLORS[element];

  /**
   * 渲染简单的Tooltip内容
   */
  const renderTooltipContent = () => {
    return (
      <div style={{ maxWidth: '300px' }}>
        <div>
          <Tag color={color}>{definition.symbol}</Tag>
          <Text strong style={{ color: '#fff' }}>
            {definition.name}
          </Text>
        </div>
        <Divider style={{ margin: '8px 0', borderColor: 'rgba(255,255,255,0.3)' }} />
        <Paragraph style={{ color: '#fff', marginBottom: 0 }}>
          {definition.shortDescription}
        </Paragraph>
      </div>
    );
  };

  /**
   * 渲染完整的Popover内容
   */
  const renderPopoverContent = () => {
    return (
      <div style={{ maxWidth: '400px' }}>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          {/* 标题 */}
          <div>
            <Tag color={color}>{definition.symbol}</Tag>
            <Text strong>{definition.name}</Text>
          </div>

          {/* 简短描述 */}
          <Paragraph>{definition.shortDescription}</Paragraph>

          {/* 完整描述 */}
          <div>
            <Text strong>详细说明：</Text>
            <Paragraph>{definition.fullDescription}</Paragraph>
          </div>

          {/* 示例 */}
          {definition.examples && definition.examples.length > 0 && (
            <div>
              <Text strong>示例：</Text>
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                {definition.examples.map((example, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>
                    <Text>{example}</Text>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* 常见错误 */}
          {definition.commonMistakes && definition.commonMistakes.length > 0 && (
            <div>
              <Text strong type="warning">
                常见错误：
              </Text>
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                {definition.commonMistakes.map((mistake, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>
                    <Text type="warning">{mistake}</Text>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Space>
      </div>
    );
  };

  /**
   * 默认的触发元素
   */
  const defaultTrigger = (
    <QuestionCircleOutlined
      style={{
        color,
        cursor: 'help',
        marginLeft: '4px',
        ...style,
      }}
    />
  );

  const triggerElement = children || defaultTrigger;

  // 根据模式选择Tooltip或Popover
  if (mode === 'tooltip') {
    return (
      <Tooltip
        title={renderTooltipContent()}
        trigger={trigger}
        overlayInnerStyle={{ backgroundColor: 'rgba(0, 0, 0, 0.85)' }}
      >
        {triggerElement}
      </Tooltip>
    );
  } else {
    return (
      <Popover
        content={renderPopoverContent()}
        title={
          <Space>
            <InfoCircleOutlined style={{ color }} />
            <Text strong>UbD框架说明</Text>
          </Space>
        }
        trigger={trigger}
        overlayStyle={{ maxWidth: '450px' }}
      >
        {triggerElement}
      </Popover>
    );
  }
};

/**
 * 批量渲染UbD元素标签（带提示）
 *
 * @example
 * ```tsx
 * <UbdElementTags elements={['U1', 'S2', 'K3']} mode="popover" />
 * ```
 */
export const UbdElementTags: React.FC<{
  elements: string[];
  mode?: 'tooltip' | 'popover';
}> = ({ elements, mode = 'tooltip' }) => {
  return (
    <Space wrap>
      {elements.map((el) => {
        // 提取字母和数字 (e.g., "U1" -> element="U", index=1)
        const match = el.match(/^([GUQKS])(\d*)$/);
        if (!match) return <Tag key={el}>{el}</Tag>;

        const element = match[1] as 'G' | 'U' | 'Q' | 'K' | 'S';
        const color = UBD_ELEMENT_COLORS[element];

        return (
          <UbdTooltip key={el} element={element} mode={mode} trigger="hover">
            <Tag color={color} style={{ cursor: 'help' }}>
              {el}
            </Tag>
          </UbdTooltip>
        );
      })}
    </Space>
  );
};

export default UbdTooltip;
