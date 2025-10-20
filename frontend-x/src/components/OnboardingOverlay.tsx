/**
 * OnboardingOverlay - 新手引导遮罩层
 * 首次使用时介绍UbD核心概念和使用流程
 */

import React, { useState } from 'react';
import { Modal, Steps, Button, Space, Typography, Card, Tag } from 'antd';
import {
  RightOutlined,
  LeftOutlined,
  CheckCircleOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { UBD_ELEMENT_COLORS } from '../constants/ubdDefinitions';

const { Title, Paragraph, Text } = Typography;
const { Step } = Steps;

export interface OnboardingOverlayProps {
  /** 是否显示引导 */
  open: boolean;

  /** 完成引导回调 */
  onFinish: () => void;
}

/** 引导步骤定义 */
const ONBOARDING_STEPS = [
  {
    title: '欢迎使用UbD-PBL课程架构师',
    content: (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={3}>欢迎！</Title>
          <Paragraph>
            这个工具将帮助您设计一份专业的、基于<Text strong>理解by Design (UbD)</Text>框架的项目式学习(PBL)课程方案。
          </Paragraph>
          <Paragraph>
            在接下来的几个步骤中，我们将简要介绍UbD框架的核心思想，帮助您更好地使用本工具。
          </Paragraph>
        </div>

        <Card style={{ backgroundColor: '#e6f7ff', borderColor: '#1890ff' }}>
          <Space direction="vertical">
            <Text strong>UbD的核心理念：以终为始</Text>
            <Text>先确定学生应该"理解什么"，再设计"如何评估理解"，最后规划"如何教学"。</Text>
          </Space>
        </Card>
      </Space>
    ),
  },
  {
    title: '阶段一：确定预期学习结果',
    content: (
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Title level={4}>G/U/Q/K/S框架</Title>

        <Paragraph>
          在第一个阶段，您将明确学习的最终目标，包括5个核心要素：
        </Paragraph>

        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <Card size="small" style={{ borderLeft: `4px solid ${UBD_ELEMENT_COLORS.G}` }}>
            <Text strong>
              <Tag color={UBD_ELEMENT_COLORS.G}>G</Tag>
              迁移目标 (Goals)
            </Text>
            <br />
            <Text type="secondary">学生将能够自主地将所学应用到新情境</Text>
          </Card>

          <Card size="small" style={{ borderLeft: `4px solid ${UBD_ELEMENT_COLORS.U}` }}>
            <Text strong>
              <Tag color={UBD_ELEMENT_COLORS.U}>U</Tag>
              持续理解 (Understandings)
            </Text>
            <br />
            <Text type="secondary">学生在5年后仍会记住的核心思想</Text>
          </Card>

          <Card size="small" style={{ borderLeft: `4px solid ${UBD_ELEMENT_COLORS.Q}` }}>
            <Text strong>
              <Tag color={UBD_ELEMENT_COLORS.Q}>Q</Tag>
              基本问题 (Questions)
            </Text>
            <br />
            <Text type="secondary">开放性问题，激发探究和思考</Text>
          </Card>

          <Card size="small" style={{ borderLeft: `4px solid ${UBD_ELEMENT_COLORS.K}` }}>
            <Text strong>
              <Tag color={UBD_ELEMENT_COLORS.K}>K</Tag>
              知识 (Knowledge)
            </Text>
            <br />
            <Text type="secondary">学生需要知道的事实、概念、原理</Text>
          </Card>

          <Card size="small" style={{ borderLeft: `4px solid ${UBD_ELEMENT_COLORS.S}` }}>
            <Text strong>
              <Tag color={UBD_ELEMENT_COLORS.S}>S</Tag>
              技能 (Skills)
            </Text>
            <br />
            <Text type="secondary">学生需要能够做到的具体技能</Text>
          </Card>
        </Space>

        <Card style={{ backgroundColor: '#fff7e6', borderColor: '#fa8c16' }}>
          <Text strong type="warning">
            关键区别
          </Text>
          <br />
          <Text>
            <Text strong>U (持续理解)</Text>是抽象的big idea，而<Text strong>K (知识)</Text>是具体的事实。
            例如："AI技术是双刃剑"是U，"Python语法规则"是K。
          </Text>
        </Card>
      </Space>
    ),
  },
  {
    title: '阶段二：确定可接受的证据',
    content: (
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Title level={4}>如何知道学生真正理解了？</Title>

        <Paragraph>
          在第二个阶段，您将设计评估方法来检验学生是否达成了理解目标：
        </Paragraph>

        <Card title="驱动性问题 (Driving Question)" style={{ marginBottom: 16 }}>
          <Paragraph>
            一个贯穿整个项目的核心挑战问题，基于真实情境，激发学生解决真实问题的动力。
          </Paragraph>
          <Text type="secondary" italic>
            例如："我们如何利用AI技术为社区创造一个解决实际问题的工具？"
          </Text>
        </Card>

        <Card title="表现性任务 (Performance Tasks)">
          <Paragraph>
            学生通过完成真实的、情境化的任务来展示他们的理解。每个任务都有明确的角色、情境和产出物。
          </Paragraph>
          <Space wrap>
            <Tag>任务1: 探索</Tag>
            <Tag>任务2: 设计</Tag>
            <Tag>任务3: 开发</Tag>
            <Tag>任务4: 展示</Tag>
          </Space>
        </Card>
      </Space>
    ),
  },
  {
    title: '阶段三：规划学习体验',
    content: (
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Title level={4}>如何帮助学生达成理解？</Title>

        <Paragraph>
          在第三个阶段，您将规划具体的教学活动，遵循PBL四阶段结构：
        </Paragraph>

        <Steps direction="vertical" current={-1}>
          <Step
            title="项目启动 (Launch)"
            description="激发兴趣，建立需求，介绍驱动性问题"
          />
          <Step
            title="知识与技能构建 (Build)"
            description="系统学习完成项目所需的知识和技能"
          />
          <Step
            title="开发与迭代 (Develop)"
            description="学生应用所学创造产出物，持续改进"
          />
          <Step
            title="成果展示与反思 (Present)"
            description="展示学习成果，反思学习过程"
          />
        </Steps>

        <Card style={{ backgroundColor: '#f6ffed', borderColor: '#52c41a', marginTop: 16 }}>
          <Text strong>WHERETO原则</Text>
          <br />
          <Text>
            每个学习活动都应该服务于至少一个WHERETO原则，确保活动有明确的教学设计依据。
          </Text>
        </Card>
      </Space>
    ),
  },
  {
    title: '开始使用',
    content: (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div>
          <Title level={3}>
            <CheckCircleOutlined style={{ color: '#52c41a' }} /> 准备好了！
          </Title>
          <Paragraph>
            现在您已经了解了UbD框架的基本概念，可以开始创建您的课程了。
          </Paragraph>
        </div>

        <Card>
          <Title level={5}>使用流程：</Title>
          <ol>
            <li>输入课程基本信息（名称、学科、时长等）</li>
            <li>AI将自动生成三个阶段的初始方案</li>
            <li>在左侧对话框与AI交流，完善方案</li>
            <li>在右侧查看结构化内容，或切换到编辑模式修改</li>
            <li>完成后导出Markdown格式的完整教案</li>
          </ol>
        </Card>

        <Card style={{ backgroundColor: '#e6f7ff', borderColor: '#1890ff' }}>
          <Space>
            <BookOutlined />
            <Text>
              在使用过程中，点击右上角的<Text strong>"帮助"</Text>按钮可以随时查看详细的UbD理论说明。
            </Text>
          </Space>
        </Card>
      </Space>
    ),
  },
];

/**
 * OnboardingOverlay组件
 *
 * 为首次使用的用户提供UbD框架的引导式介绍
 *
 * @example
 * ```tsx
 * const [showOnboarding, setShowOnboarding] = useState(!localStorage.getItem('onboarding-completed'));
 *
 * <OnboardingOverlay
 *   open={showOnboarding}
 *   onFinish={() => {
 *     localStorage.setItem('onboarding-completed', 'true');
 *     setShowOnboarding(false);
 *   }}
 * />
 * ```
 */
export const OnboardingOverlay: React.FC<OnboardingOverlayProps> = ({ open, onFinish }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const handleNext = () => {
    if (currentStep < ONBOARDING_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onFinish();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    onFinish();
  };

  return (
    <Modal
      title={
        <Steps current={currentStep} size="small">
          {ONBOARDING_STEPS.map((step, index) => (
            <Step key={index} />
          ))}
        </Steps>
      }
      open={open}
      closable={false}
      footer={
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Button onClick={handleSkip}>跳过引导</Button>
          <Space>
            <Button onClick={handlePrev} disabled={currentStep === 0} icon={<LeftOutlined />}>
              上一步
            </Button>
            <Button type="primary" onClick={handleNext} icon={<RightOutlined />}>
              {currentStep === ONBOARDING_STEPS.length - 1 ? '开始使用' : '下一步'}
            </Button>
          </Space>
        </Space>
      }
      width={700}
      centered
      maskClosable={false}
    >
      <div style={{ minHeight: '400px', padding: '24px 0' }}>
        {ONBOARDING_STEPS[currentStep].content}
      </div>
    </Modal>
  );
};

export default OnboardingOverlay;
