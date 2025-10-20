/**
 * ContentPanel - 内容展示面板
 * 展示UbD三阶段的结构化内容（Stage One/Two/Three）
 */

import React from 'react';
import { Card, Space, Typography, List, Tag, Collapse, Button, Alert, Tooltip, Progress } from 'antd';
import { EditOutlined, EyeOutlined, CheckCircleOutlined, WarningOutlined, InfoCircleOutlined } from '@ant-design/icons';
import type { StageOneData, StageTwoData, StageThreeData } from '../types/course';
import { UbdTooltip } from './UbdTooltip';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

export interface ContentPanelProps {
  /** 当前步骤 (1-3) */
  currentStep: number;

  /** Stage One数据 */
  stageOneData?: StageOneData;

  /** Stage Two数据 */
  stageTwoData?: StageTwoData;

  /** Stage Three数据 */
  stageThreeData?: StageThreeData;

  /** 是否为编辑模式 */
  isEditMode?: boolean;

  /** 切换编辑模式 */
  onToggleEdit?: () => void;

  /** 自定义样式 */
  style?: React.CSSProperties;
}

/**
 * ContentPanel组件
 *
 * 根据当前步骤展示对应的Stage数据
 *
 * @example
 * ```tsx
 * <ContentPanel
 *   currentStep={1}
 *   stageOneData={stageOne}
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
  style,
}) => {
  /**
   * 渲染Stage One内容 (G/U/Q/K/S)
   */
  const renderStageOne = () => {
    if (!stageOneData) {
      return <Text type="secondary">暂无数据，请先生成或输入课程信息</Text>;
    }

    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* G: 迁移目标 */}
        <div>
          <Title level={4}>G: 迁移目标 (Transfer Goals)</Title>
          <List
            dataSource={stageOneData.goals || []}
            renderItem={(goal, idx) => (
              <List.Item>
                <Text>{idx + 1}. {goal.text}</Text>
              </List.Item>
            )}
          />
        </div>

        {/* U: 持续理解 */}
        <div>
          <Title level={4}>
            U: 持续理解 (Understandings)
            <UbdTooltip element="U" mode="popover" trigger="click" />
          </Title>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {(stageOneData.understandings || []).map((u, idx) => {
              const score = u.validation_score !== undefined ? u.validation_score : null;
              const isExcellent = score !== null && score >= 0.85;
              const needsImprovement = score !== null && score < 0.7;

              return (
                <Card
                  key={idx}
                  size="small"
                  bordered={true}
                  style={{
                    backgroundColor: isExcellent ? '#f6ffed' : needsImprovement ? '#fff7e6' : '#f5f5f5',
                    borderColor: isExcellent ? '#52c41a' : needsImprovement ? '#fa8c16' : '#d9d9d9',
                  }}
                >
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text strong>U{idx + 1}: </Text>
                      <Text>{u.text}</Text>
                    </div>

                    <div>
                      <Text type="secondary" italic>理由: {u.rationale}</Text>
                    </div>

                    {score !== null && (
                      <div>
                        <Space align="center">
                          {isExcellent && (
                            <Tooltip title="这是一个优秀的持续理解陈述">
                              <CheckCircleOutlined style={{ color: '#52c41a' }} />
                            </Tooltip>
                          )}
                          {needsImprovement && (
                            <Tooltip title="这个理解陈述可能过于具体，建议修改为更抽象的big idea">
                              <WarningOutlined style={{ color: '#fa8c16' }} />
                            </Tooltip>
                          )}
                          <Text
                            type={isExcellent ? 'success' : needsImprovement ? 'warning' : undefined}
                            strong
                          >
                            语义质量: {(score * 100).toFixed(0)}%
                          </Text>
                          <Progress
                            percent={score * 100}
                            size="small"
                            strokeColor={isExcellent ? '#52c41a' : needsImprovement ? '#fa8c16' : '#1890ff'}
                            showInfo={false}
                            style={{ width: 100 }}
                          />
                        </Space>
                      </div>
                    )}

                    {isExcellent && (
                      <Alert
                        message="为什么这是一个好的U？"
                        description="这个理解陈述是抽象的、可迁移的核心观念，学生在多年后仍会记住这个深刻洞察。"
                        type="success"
                        showIcon
                        icon={<InfoCircleOutlined />}
                        closable
                      />
                    )}

                    {needsImprovement && (
                      <Alert
                        message="改进建议"
                        description={
                          <ul style={{ paddingLeft: 20, marginBottom: 0 }}>
                            <li>检查是否包含了具体的工具名称或技术细节（这些应该属于K）</li>
                            <li>尝试将具体知识点提升为更普遍的原理或观念</li>
                            <li>思考：学生在5年后还会记住这个吗？</li>
                            <li>参考右侧帮助文档中U的定义和示例</li>
                          </ul>
                        }
                        type="warning"
                        showIcon
                        closable
                      />
                    )}
                  </Space>
                </Card>
              );
            })}
          </Space>
        </div>

        {/* Q: 基本问题 */}
        <div>
          <Title level={4}>Q: 基本问题 (Essential Questions)</Title>
          <List
            dataSource={stageOneData.questions || []}
            renderItem={(q, idx) => (
              <List.Item>
                <Text>{idx + 1}. {q.text}</Text>
              </List.Item>
            )}
          />
        </div>

        {/* K: 知识 */}
        <div>
          <Title level={4}>K: 应掌握的知识 (Knowledge)</Title>
          <List
            dataSource={stageOneData.knowledge || []}
            renderItem={(k) => (
              <List.Item>
                <Text>• {k.text}</Text>
              </List.Item>
            )}
          />
        </div>

        {/* S: 技能 */}
        <div>
          <Title level={4}>S: 应形成的技能 (Skills)</Title>
          <List
            dataSource={stageOneData.skills || []}
            renderItem={(s) => (
              <List.Item>
                <Text>• {s.text}</Text>
              </List.Item>
            )}
          />
        </div>
      </Space>
    );
  };

  /**
   * 渲染Stage Two内容 (驱动性问题 + 表现性任务)
   */
  const renderStageTwo = () => {
    if (!stageTwoData) {
      return <Text type="secondary">暂无数据，请先完成Stage One</Text>;
    }

    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 驱动性问题 */}
        <div>
          <Title level={4}>驱动性问题 (Driving Question)</Title>
          <Card bordered={false} style={{ backgroundColor: '#e6f7ff' }}>
            <Title level={5}>{stageTwoData.driving_question}</Title>
            <Paragraph type="secondary">{stageTwoData.driving_question_context}</Paragraph>
          </Card>
        </div>

        {/* 表现性任务 */}
        <div>
          <Title level={4}>表现性任务 (Performance Tasks)</Title>
          <Collapse>
            {(stageTwoData.performance_tasks || []).map((task, idx) => (
              <Panel
                key={idx}
                header={
                  <Space>
                    <Text strong>任务{idx + 1}: {task.title}</Text>
                    <Tag>第{task.milestone_week}周</Tag>
                  </Space>
                }
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text strong>任务描述: </Text>
                    <Paragraph>{task.description}</Paragraph>
                  </div>
                  <div>
                    <Text strong>真实情境: </Text>
                    <Text>{task.context}</Text>
                  </div>
                  <div>
                    <Text strong>学生角色: </Text>
                    <Text>{task.student_role}</Text>
                  </div>
                  <div>
                    <Text strong>最终产出物: </Text>
                    <Text>{task.deliverable}</Text>
                  </div>
                  <div>
                    <Text strong>关联UbD元素: </Text>
                    <Space wrap>
                      {task.linked_ubd_elements.u?.map((i) => <Tag key={`u${i}`} color="blue">U{i+1}</Tag>)}
                      {task.linked_ubd_elements.s?.map((i) => <Tag key={`s${i}`} color="green">S{i+1}</Tag>)}
                      {task.linked_ubd_elements.k?.map((i) => <Tag key={`k${i}`} color="orange">K{i+1}</Tag>)}
                    </Space>
                  </div>
                </Space>
              </Panel>
            ))}
          </Collapse>
        </div>

        {/* 其他评估证据 */}
        {stageTwoData.other_evidence && stageTwoData.other_evidence.length > 0 && (
          <div>
            <Title level={4}>其他评估证据</Title>
            <List
              dataSource={stageTwoData.other_evidence}
              renderItem={(evidence) => (
                <List.Item>
                  <Text strong>{evidence.type}: </Text>
                  <Text>{evidence.description}</Text>
                </List.Item>
              )}
            />
          </div>
        )}
      </Space>
    );
  };

  /**
   * 渲染Stage Three内容 (PBL学习蓝图)
   */
  const renderStageThree = () => {
    if (!stageThreeData) {
      return <Text type="secondary">暂无数据，请先完成Stage Two</Text>;
    }

    const phaseTypeMap: Record<string, string> = {
      launch: '项目启动',
      build: '知识与技能构建',
      develop: '开发与迭代',
      present: '成果展示与反思',
    };

    // WHERETO原则说明映射
    const wheretoMap: Record<string, { name: string; description: string }> = {
      W: { name: 'Where & Why', description: '帮助学生了解学习目标和意义' },
      H: { name: 'Hook', description: '激发兴趣和参与' },
      E: {
        name: 'Equip & Experience',
        description: '提供学习所需的知识、技能和体验',
      },
      R: { name: 'Rethink & Revise', description: '引导反思和改进' },
      E2: { name: 'Explore & Enable', description: '鼓励探究和自主学习' },
      T: { name: 'Tailor', description: '个性化和差异化教学' },
      O: { name: 'Organize & Optimize', description: '优化学习流程和资源' },
    };

    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Title level={4}>PBL学习蓝图</Title>
        <Collapse>
          {(stageThreeData.pbl_phases || []).map((phase, phaseIdx) => (
            <Panel
              key={phaseIdx}
              header={
                <Space>
                  <Text strong>{phase.phase_name}</Text>
                  <Tag color="purple">{phaseTypeMap[phase.phase_type]}</Tag>
                  <Tag>{phase.duration_weeks}周</Tag>
                </Space>
              }
            >
              <List
                dataSource={phase.activities || []}
                renderItem={(activity) => (
                  <List.Item>
                    <Card size="small" style={{ width: '100%' }}>
                      <Title level={5}>Week {activity.week}: {activity.title}</Title>
                      <Paragraph>{activity.description}</Paragraph>
                      <Space wrap>
                        <Text strong>时长: </Text>
                        <Tag>{activity.duration_hours}小时</Tag>
                        <Text strong>WHERETO原则: </Text>
                        {activity.whereto_labels.map((label) => {
                          const key = label === 'E' ? (activity.whereto_labels.filter((l) => l === 'E').length > 1 ? 'E2' : 'E') : label;
                          const tooltip = wheretoMap[key] || { name: label, description: '' };
                          return (
                            <Tooltip
                              key={label + activity.week}
                              title={
                                <div>
                                  <Text strong style={{ color: '#fff' }}>
                                    {tooltip.name}
                                  </Text>
                                  <br />
                                  <Text style={{ color: '#fff' }}>{tooltip.description}</Text>
                                </div>
                              }
                            >
                              <Tag color="cyan">{label}</Tag>
                            </Tooltip>
                          );
                        })}
                      </Space>
                      <br />
                      {activity.linked_ubd_elements && (
                        <>
                          <Space wrap style={{ marginTop: 8 }}>
                            <Text strong>关联UbD元素: </Text>
                            {activity.linked_ubd_elements.u?.map((i) => (
                              <Tag key={`u${i}`} color="blue">
                                U{i + 1}
                              </Tag>
                            ))}
                            {activity.linked_ubd_elements.s?.map((i) => (
                              <Tag key={`s${i}`} color="green">
                                S{i + 1}
                              </Tag>
                            ))}
                            {activity.linked_ubd_elements.k?.map((i) => (
                              <Tag key={`k${i}`} color="orange">
                                K{i + 1}
                              </Tag>
                            ))}
                          </Space>
                          <br />
                        </>
                      )}
                      <Text type="secondary" italic>
                        教学提示: {activity.notes}
                      </Text>
                    </Card>
                  </List.Item>
                )}
              />
            </Panel>
          ))}
        </Collapse>
      </Space>
    );
  };

  /**
   * 根据当前步骤选择渲染内容
   */
  const renderContent = () => {
    switch (currentStep) {
      case 1:
        return renderStageOne();
      case 2:
        return renderStageTwo();
      case 3:
        return renderStageThree();
      default:
        return <Text type="secondary">未知步骤</Text>;
    }
  };

  return (
    <Card
      title={`Stage ${currentStep} - UbD ${['确定预期学习结果', '确定可接受的证据', '规划学习体验'][currentStep - 1]}`}
      extra={
        onToggleEdit && (
          <Button
            type="text"
            icon={isEditMode ? <EyeOutlined /> : <EditOutlined />}
            onClick={onToggleEdit}
          >
            {isEditMode ? '查看模式' : '编辑模式'}
          </Button>
        )
      }
      style={{ height: '100%', ...style }}
      styles={{ body: { overflowY: 'auto', padding: '24px' } }}
    >
      {renderContent()}
    </Card>
  );
};

export default ContentPanel;
