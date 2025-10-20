/**
 * HelpDialog - UbD理论帮助对话框
 * 提供详细的UbD框架说明和示例
 */

import React from 'react';
import { Modal, Tabs, Typography, Collapse, Space, Tag, Divider } from 'antd';
import { InfoCircleOutlined, BookOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import {
  UBD_FRAMEWORK_OVERVIEW,
  UBD_STAGE_ONE_ELEMENTS,
  UBD_STAGE_TWO_GUIDE,
  UBD_STAGE_THREE_GUIDE,
  UBD_ELEMENT_COLORS,
} from '../constants/ubdDefinitions';

const { Title, Paragraph, Text } = Typography;
const { Panel } = Collapse;

export interface HelpDialogProps {
  /** 是否显示对话框 */
  open: boolean;

  /** 关闭回调 */
  onClose: () => void;

  /** 默认激活的标签页 */
  defaultActiveKey?: string;
}

/**
 * HelpDialog组件
 *
 * 提供UbD框架的完整理论说明和示例
 *
 * @example
 * ```tsx
 * const [helpOpen, setHelpOpen] = useState(false);
 *
 * <Button onClick={() => setHelpOpen(true)}>帮助</Button>
 * <HelpDialog
 *   open={helpOpen}
 *   onClose={() => setHelpOpen(false)}
 *   defaultActiveKey="stage-one"
 * />
 * ```
 */
export const HelpDialog: React.FC<HelpDialogProps> = ({
  open,
  onClose,
  defaultActiveKey = 'overview',
}) => {
  /**
   * 渲染UbD框架总览
   */
  const renderOverview = () => (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div>
        <Title level={3}>
          <InfoCircleOutlined /> {UBD_FRAMEWORK_OVERVIEW.title}
        </Title>
        <Text type="secondary">{UBD_FRAMEWORK_OVERVIEW.subtitle}</Text>
        <Paragraph style={{ marginTop: 16 }}>
          {UBD_FRAMEWORK_OVERVIEW.description}
        </Paragraph>
      </div>

      <Divider />

      <div>
        <Title level={4}>UbD三阶段</Title>
        <Collapse>
          {UBD_FRAMEWORK_OVERVIEW.stages.map((stage) => (
            <Panel
              key={stage.stage}
              header={
                <Space>
                  <Tag color="blue">阶段{stage.stage}</Tag>
                  <Text strong>{stage.name}</Text>
                </Space>
              }
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong>核心问题: </Text>
                  <Text>{stage.question}</Text>
                </div>
                <div>
                  <Text strong>产出物: </Text>
                  <Text>{stage.output}</Text>
                </div>
              </Space>
            </Panel>
          ))}
        </Collapse>
      </div>

      <Divider />

      <div>
        <Title level={4}>核心哲学</Title>
        <Paragraph italic style={{ backgroundColor: '#e6f7ff', padding: 16, borderRadius: 8 }}>
          {UBD_FRAMEWORK_OVERVIEW.corePhilosophy}
        </Paragraph>
      </div>
    </Space>
  );

  /**
   * 渲染Stage One说明
   */
  const renderStageOne = () => (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      <Title level={4}>阶段一：确定预期学习结果 (G/U/Q/K/S)</Title>

      <Collapse accordion>
        {Object.values(UBD_STAGE_ONE_ELEMENTS).map((element) => (
          <Panel
            key={element.symbol}
            header={
              <Space>
                <Tag color={UBD_ELEMENT_COLORS[element.symbol as keyof typeof UBD_ELEMENT_COLORS]}>
                  {element.symbol}
                </Tag>
                <Text strong>{element.name}</Text>
              </Space>
            }
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>简短说明：</Text>
                <Paragraph>{element.shortDescription}</Paragraph>
              </div>

              <div>
                <Text strong>详细说明：</Text>
                <Paragraph>{element.fullDescription}</Paragraph>
              </div>

              {element.examples && element.examples.length > 0 && (
                <div>
                  <Text strong>示例：</Text>
                  <ul>
                    {element.examples.map((example, idx) => (
                      <li key={idx}>
                        <Text>{example}</Text>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {element.commonMistakes && element.commonMistakes.length > 0 && (
                <div>
                  <Text strong type="warning">
                    常见错误：
                  </Text>
                  <ul>
                    {element.commonMistakes.map((mistake, idx) => (
                      <li key={idx}>
                        <Text type="warning">{mistake}</Text>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Space>
          </Panel>
        ))}
      </Collapse>
    </Space>
  );

  /**
   * 渲染Stage Two说明
   */
  const renderStageTwo = () => (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      <Title level={4}>阶段二：确定可接受的证据</Title>

      <Collapse accordion defaultActiveKey={['driving-question']}>
        <Panel
          key="driving-question"
          header={<Text strong>{UBD_STAGE_TWO_GUIDE.drivingQuestion.title}</Text>}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <Paragraph>{UBD_STAGE_TWO_GUIDE.drivingQuestion.description}</Paragraph>

            <div>
              <Text strong>设计标准：</Text>
              <ul>
                {UBD_STAGE_TWO_GUIDE.drivingQuestion.criteria.map((criterion, idx) => (
                  <li key={idx}>
                    <Text>{criterion}</Text>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <Text strong type="success">
                ✅ 好例子：
              </Text>
              <Paragraph style={{ backgroundColor: '#f6ffed', padding: 12, borderRadius: 4 }}>
                {UBD_STAGE_TWO_GUIDE.drivingQuestion.goodExample}
              </Paragraph>
            </div>

            <div>
              <Text strong type="danger">
                ❌ 坏例子：
              </Text>
              <Paragraph style={{ backgroundColor: '#fff2e8', padding: 12, borderRadius: 4 }}>
                {UBD_STAGE_TWO_GUIDE.drivingQuestion.badExample}
              </Paragraph>
            </div>
          </Space>
        </Panel>

        <Panel
          key="performance-tasks"
          header={<Text strong>{UBD_STAGE_TWO_GUIDE.performanceTasks.title}</Text>}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <Paragraph>{UBD_STAGE_TWO_GUIDE.performanceTasks.description}</Paragraph>

            <div>
              <Text strong>设计原则：</Text>
              <ul>
                {UBD_STAGE_TWO_GUIDE.performanceTasks.principles.map((principle, idx) => (
                  <li key={idx}>
                    <Text>{principle}</Text>
                  </li>
                ))}
              </ul>
            </div>
          </Space>
        </Panel>

        <Panel key="rubric" header={<Text strong>{UBD_STAGE_TWO_GUIDE.rubric.title}</Text>}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Paragraph>{UBD_STAGE_TWO_GUIDE.rubric.description}</Paragraph>

            <div>
              <Text strong>等级标准：</Text>
              <Space wrap>
                {UBD_STAGE_TWO_GUIDE.rubric.levels.map((level) => (
                  <Tag key={level} color="blue">
                    {level}
                  </Tag>
                ))}
              </Space>
            </div>

            <div>
              <Text strong>常见维度：</Text>
              <ul>
                {UBD_STAGE_TWO_GUIDE.rubric.commonDimensions.map((dimension, idx) => (
                  <li key={idx}>
                    <Text>{dimension}</Text>
                  </li>
                ))}
              </ul>
            </div>
          </Space>
        </Panel>
      </Collapse>
    </Space>
  );

  /**
   * 渲染Stage Three说明
   */
  const renderStageThree = () => (
    <Space direction="vertical" size="middle" style={{ width: '100%' }}>
      <Title level={4}>阶段三：规划学习体验</Title>

      <Collapse accordion defaultActiveKey={['pbl-phases']}>
        <Panel
          key="pbl-phases"
          header={<Text strong>{UBD_STAGE_THREE_GUIDE.pblPhases.title}</Text>}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <Paragraph>{UBD_STAGE_THREE_GUIDE.pblPhases.description}</Paragraph>

            {UBD_STAGE_THREE_GUIDE.pblPhases.phases.map((phase, idx) => (
              <div key={idx} style={{ marginBottom: 16 }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Tag color="purple">{phase.name}</Tag>
                  </div>
                  <div>
                    <Text strong>目的: </Text>
                    <Text>{phase.purpose}</Text>
                  </div>
                  <div>
                    <Text strong>时长: </Text>
                    <Text>{phase.duration}</Text>
                  </div>
                  <div>
                    <Text strong>关键词: </Text>
                    <Space wrap>
                      {phase.keywords.map((keyword) => (
                        <Tag key={keyword}>{keyword}</Tag>
                      ))}
                    </Space>
                  </div>
                </Space>
                {idx < UBD_STAGE_THREE_GUIDE.pblPhases.phases.length - 1 && <Divider />}
              </div>
            ))}
          </Space>
        </Panel>

        <Panel
          key="whereto"
          header={<Text strong>{UBD_STAGE_THREE_GUIDE.wheretoPrinciples.title}</Text>}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <Paragraph>{UBD_STAGE_THREE_GUIDE.wheretoPrinciples.description}</Paragraph>

            {UBD_STAGE_THREE_GUIDE.wheretoPrinciples.principles.map((principle) => (
              <div key={principle.code} style={{ marginBottom: 12 }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Tag color="cyan">{principle.code}</Tag>
                    <Text strong>{principle.name}</Text>
                  </div>
                  <div>
                    <Text>{principle.description}</Text>
                  </div>
                  <div>
                    <Text type="secondary" italic>
                      例如: {principle.example}
                    </Text>
                  </div>
                </Space>
              </div>
            ))}
          </Space>
        </Panel>
      </Collapse>
    </Space>
  );

  return (
    <Modal
      title={
        <Space>
          <BookOutlined />
          <span>UbD框架帮助</span>
        </Space>
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={800}
      style={{ top: 20 }}
      bodyStyle={{ maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' }}
    >
      <Tabs defaultActiveKey={defaultActiveKey}>
        <Tabs.TabPane
          tab={
            <span>
              <InfoCircleOutlined /> 框架总览
            </span>
          }
          key="overview"
        >
          {renderOverview()}
        </Tabs.TabPane>

        <Tabs.TabPane
          tab={
            <span>
              <QuestionCircleOutlined /> 阶段一 (G/U/Q/K/S)
            </span>
          }
          key="stage-one"
        >
          {renderStageOne()}
        </Tabs.TabPane>

        <Tabs.TabPane tab="阶段二 (评估证据)" key="stage-two">
          {renderStageTwo()}
        </Tabs.TabPane>

        <Tabs.TabPane tab="阶段三 (学习体验)" key="stage-three">
          {renderStageThree()}
        </Tabs.TabPane>
      </Tabs>
    </Modal>
  );
};

export default HelpDialog;
