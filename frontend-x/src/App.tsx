/**
 * App.tsx - UbD-PBL课程架构师主应用
 * 集成所有组件，提供完整的课程设计工作流
 *
 * 架构原则：
 * - 使用统一的Layout组件系统
 * - 消除所有内联样式和magic number
 * - 保持布局一致性
 */

import React, { useState, lazy, Suspense } from 'react';
import { Layout, Row, Col, Space, Button, Input, Form, Modal, message, Spin, Typography } from 'antd';
import { PlusOutlined, SaveOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { StepNavigator } from './components/StepNavigator';
import { ChatPanel } from './components/ChatPanel';
import { ContentPanel } from './components/ContentPanel';
import { DownloadButton } from './components/DownloadButton';
import { AppHeader, PageContainer } from './components/layout';
import { COLORS, SPACING } from './constants/layout';
import { useStepWorkflow } from './hooks/useStepWorkflow';
import { useCourseStore } from './stores/courseStore';
import type { WorkflowRequest, CourseProject } from './types/course';
import './App.css';

const { Content } = Layout;
const { Text } = Typography;

type ViewMode = 'list' | 'course';

// 懒加载组件 - 减少初始包大小，提升加载性能
const MarkdownEditor = lazy(() => import('./components/MarkdownEditor').then(m => ({ default: m.MarkdownEditor })));
const HelpDialog = lazy(() => import('./components/HelpDialog').then(m => ({ default: m.HelpDialog })));
const OnboardingOverlay = lazy(() => import('./components/OnboardingOverlay').then(m => ({ default: m.OnboardingOverlay })));
const ProjectListView = lazy(() => import('./components/ProjectListView').then(m => ({ default: m.ProjectListView })));
const ChangeDetectionDialog = lazy(() => import('./components/ChangeDetectionDialog').then(m => ({ default: m.ChangeDetectionDialog })));

/**
 * 加载占位组件
 */
const LoadingFallback: React.FC = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '50px' }}>
    <Spin size="large" />
  </div>
);

function App() {
  // 视图模式 ('list' | 'course')
  const [viewMode, setViewMode] = useState<ViewMode>('list');

  // 课程Store状态
  const {
    courseInfo,
    setCourseInfo,
    currentStep,
    stageOneData,
    stageTwoData,
    stageThreeData,
    isEditMode,
    setEditMode,
    isGenerating,
  } = useCourseStore();

  // 步骤工作流Hook
  const {
    generationProgress,
    generationError,
    startWorkflow,
    abortWorkflow,
  } = useStepWorkflow();

  // 新建课程对话框
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [createForm] = Form.useForm();

  // 帮助对话框和引导页
  const [helpDialogOpen, setHelpDialogOpen] = useState(false);
  const [onboardingOpen, setOnboardingOpen] = useState(
    !localStorage.getItem('onboarding-completed')
  );

  // 变更检测对话框
  const [changeDetectionOpen, setChangeDetectionOpen] = useState(false);
  const [changedStage, setChangedStage] = useState<number>(1);
  const [affectedStages, setAffectedStages] = useState<number[]>([]);
  const [skipChangeDetection, setSkipChangeDetection] = useState(false); // 跳过变更检测标志

  /**
   * 打开项目（从列表进入课程设计视图）
   */
  const handleOpenProject = async (project: CourseProject) => {
    // 加载项目数据到Store
    setCourseInfo({
      id: project.id,
      title: project.title,
      subject: project.subject,
      gradeLevel: project.grade_level,
      durationWeeks: project.duration_weeks,
      description: project.description,
    });

    // TODO: 从后端加载stage数据到Store
    // await loadProjectData(project.id);

    // 切换到课程设计视图
    setViewMode('course');
  };

  /**
   * 返回项目列表
   */
  const handleBackToList = () => {
    setViewMode('list');
  };

  /**
   * 创建新课程并启动工作流
   */
  const handleCreateCourse = async (values: any) => {
    const courseData = {
      title: values.title,
      subject: values.subject,
      grade_level: values.gradeLevel,
      duration_weeks: values.durationWeeks,
      description: values.description,
    };

    // 保存到Store
    setCourseInfo(courseData);

    // 构建工作流请求 - 只生成Stage 1，用户确认后再生成后续阶段
    const workflowRequest: WorkflowRequest = {
      title: values.title,
      subject: values.subject,
      grade_level: values.gradeLevel,
      duration_weeks: values.durationWeeks,
      description: values.description,
      stages_to_generate: [1], // 只生成Stage 1，符合UbD逆向设计的理念
    };

    // 关闭对话框
    setCreateModalVisible(false);

    // 切换到课程视图
    setViewMode('course');

    // 启动工作流
    try {
      await startWorkflow(workflowRequest);
      message.success('课程生成已完成！');
    } catch (error) {
      message.error('课程生成失败，请重试');
    }
  };

  /**
   * 切换编辑模式
   */
  const handleToggleEdit = () => {
    setEditMode(!isEditMode);
  };

  /**
   * 手动保存Markdown
   */
  const handleSaveMarkdown = async (step: number, markdown: string) => {
    // 这里可以调用后端API保存
    console.log(`[App] Saving markdown for step ${step}:`, markdown);
    // await updateStageMarkdown(courseInfo?.id, step, markdown);

    // 触发变更检测
    handleStageChange(step);
  };

  /**
   * 处理Stage数据变更
   * 检测是否需要重新生成下游阶段
   */
  const handleStageChange = (step: number) => {
    // 如果用户已选择跳过检测，直接返回
    if (skipChangeDetection) {
      return;
    }

    // 更新Stage版本
    useCourseStore.getState().updateStageVersion(step);

    // 确定受影响的下游阶段
    const downstream: number[] = [];
    if (step === 1) {
      // Stage 1变更影响Stage 2和3
      if (stageTwoData) downstream.push(2);
      if (stageThreeData) downstream.push(3);
    } else if (step === 2) {
      // Stage 2变更影响Stage 3
      if (stageThreeData) downstream.push(3);
    }
    // Stage 3没有下游阶段

    // 如果有受影响的阶段，显示变更检测对话框
    if (downstream.length > 0) {
      setChangedStage(step);
      setAffectedStages(downstream);
      setChangeDetectionOpen(true);
    }
  };

  /**
   * 级联重新生成受影响的阶段
   */
  const handleCascadeRegenerate = async (stages: number[]) => {
    setChangeDetectionOpen(false);

    // 构建工作流请求
    const workflowRequest: WorkflowRequest = {
      title: courseInfo?.title || '',
      subject: courseInfo?.subject,
      grade_level: courseInfo?.gradeLevel,
      duration_weeks: courseInfo?.durationWeeks || 12,
      description: courseInfo?.description,
      stages_to_generate: stages,
    };

    try {
      message.info(`正在重新生成 Stage ${stages.join(', ')}...`);
      await startWorkflow(workflowRequest);
      message.success('重新生成完成！');
    } catch (error) {
      message.error('重新生成失败，请重试');
    }
  };

  /**
   * 生成指定阶段
   */
  const handleGenerateStage = async (stage: number) => {
    if (!courseInfo) {
      message.error('课程信息不完整');
      return;
    }

    // 构建工作流请求
    const workflowRequest: WorkflowRequest = {
      title: courseInfo.title,
      subject: courseInfo.subject,
      grade_level: courseInfo.gradeLevel,
      duration_weeks: courseInfo.durationWeeks || 12,
      description: courseInfo.description,
      stages_to_generate: [stage], // 只生成当前阶段
      // 如果生成Stage 2或3，需要提供前置阶段的数据
      stage_one_data: stage >= 2 ? stageOneData || undefined : undefined,
      stage_two_data: stage >= 3 ? stageTwoData || undefined : undefined,
    };

    try {
      message.info(`开始生成 Stage ${stage}...`);
      await startWorkflow(workflowRequest);
      message.success(`Stage ${stage} 生成完成！`);
    } catch (error) {
      message.error(`Stage ${stage} 生成失败，请重试`);
    }
  };

  /**
   * 渲染Header中间区域（步骤导航）
   */
  const renderHeaderCenter = () => {
    if (viewMode === 'course') {
      return (
        <div style={{ flex: 1, maxWidth: '600px', margin: '0 auto' }}>
          <StepNavigator compact={true} allowStepChange={true} />
        </div>
      );
    }
    return null;
  };

  /**
   * 渲染Header右侧操作区
   */
  const renderHeaderActions = () => {
    if (viewMode === 'course') {
      return (
        <>
          <Button icon={<ArrowLeftOutlined />} onClick={handleBackToList}>
            返回
          </Button>
          <DownloadButton
            courseId={courseInfo?.id}
            dropdown={true}
            disabled={!stageOneData}
          />
        </>
      );
    }

    return (
      <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalVisible(true)}>
        新建课程
      </Button>
    );
  };

  /**
   * 渲染课程设计视图
   */
  const renderCourseView = () => (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 加载和错误提示 */}
      {isGenerating && (
        <div style={{
          textAlign: 'center',
          padding: SPACING.MD,
          background: COLORS.BG_CONTAINER,
          marginBottom: SPACING.SM,
          borderRadius: '8px'
        }}>
          <Space direction="vertical" size="large">
            <Spin size="large" />
            <div>
              <p>正在生成课程方案...</p>
              <p>进度: {Math.round(generationProgress)}%</p>
            </div>
            <Button danger onClick={abortWorkflow}>
              中止生成
            </Button>
          </Space>
        </div>
      )}

      {generationError && (
        <div style={{
          padding: SPACING.SM,
          background: COLORS.BG_CONTAINER,
          marginBottom: SPACING.SM,
          borderRadius: '8px',
          border: '1px solid #ff4d4f'
        }}>
          <p style={{ color: '#ff4d4f', margin: 0 }}>错误: {generationError}</p>
        </div>
      )}

      {/* 对话和预览区域 - 全屏宽度 */}
      <Row gutter={[SPACING.SM, SPACING.SM]} style={{ flex: 1, minHeight: 0 }}>
        {/* 左侧：对话面板 */}
        <Col xs={24} lg={10} style={{ height: '100%' }}>
          <ChatPanel
            currentStep={currentStep}
            courseId={courseInfo?.id}
            autoSync={false}
            title={`Stage ${currentStep} 对话`}
            showClearButton={true}
            showExportButton={true}
            style={{ height: '100%' }}
          />
        </Col>

        {/* 右侧：内容/编辑面板 */}
        <Col xs={24} lg={14} style={{ height: '100%' }}>
          {isEditMode ? (
            <Suspense fallback={<LoadingFallback />}>
              <MarkdownEditor
                step={currentStep}
                autoSave={true}
                debounceMs={1000}
                onSave={handleSaveMarkdown}
                height="100%"
              />
            </Suspense>
          ) : (
            <ContentPanel
              currentStep={currentStep}
              stageOneData={stageOneData || undefined}
              stageTwoData={stageTwoData || undefined}
              stageThreeData={stageThreeData || undefined}
              isEditMode={isEditMode}
              onToggleEdit={handleToggleEdit}
              style={{ height: '100%' }}
            />
          )}
        </Col>
      </Row>
    </div>
  );

  return (
    <Layout style={{ minHeight: '100vh', background: COLORS.BG_PAGE }}>
      {/* 顶部导航栏 */}
      <AppHeader
        title={
          <Space size="large">
            <span>UbD-PBL 课程架构师</span>
            {viewMode === 'course' && courseInfo && (
              <Text type="secondary">{courseInfo.title}</Text>
            )}
          </Space>
        }
        center={renderHeaderCenter()}
        extra={renderHeaderActions()}
        onHelpClick={() => setHelpDialogOpen(true)}
      />

      {/* 主内容区 */}
      <Content style={{ padding: 0 }}>
        {viewMode === 'list' ? (
          <PageContainer maxWidth="normal" padding="MD">
            <Suspense fallback={<LoadingFallback />}>
              <ProjectListView
                onOpenProject={handleOpenProject}
                onCreateProject={() => setCreateModalVisible(true)}
              />
            </Suspense>
          </PageContainer>
        ) : (
          <div style={{
            width: '100%',
            height: 'calc(100vh - 64px)',
            padding: SPACING.MD,
            boxSizing: 'border-box'
          }}>
            {renderCourseView()}
          </div>
        )}
      </Content>

      {/* 创建课程对话框 */}
      <Modal
        title="创建新课程"
        open={createModalVisible}
        onCancel={() => {
          if (courseInfo) {
            setCreateModalVisible(false);
          } else {
            message.warning('请先创建课程项目');
          }
        }}
        footer={null}
        closable={!!courseInfo}
        maskClosable={false}
      >
        <Form
          form={createForm}
          layout="vertical"
          onFinish={handleCreateCourse}
          initialValues={{
            durationWeeks: 12,
          }}
        >
          <Form.Item
            name="title"
            label="课程名称"
            rules={[{ required: true, message: '请输入课程名称' }]}
          >
            <Input placeholder="例如：0基础AI编程课程" />
          </Form.Item>

          <Form.Item name="subject" label="学科领域">
            <Input placeholder="例如：计算机科学、人工智能" />
          </Form.Item>

          <Form.Item name="gradeLevel" label="年级水平">
            <Input placeholder="例如：大学、高中" />
          </Form.Item>

          <Form.Item
            name="durationWeeks"
            label="课程时长（周）"
            rules={[{ required: true, message: '请输入课程时长' }]}
          >
            <Input type="number" min={1} max={52} />
          </Form.Item>

          <Form.Item name="description" label="课程简介">
            <Input.TextArea
              rows={4}
              placeholder="简要描述课程目标和内容..."
            />
          </Form.Item>

          <Form.Item>
            <Row justify="end">
              <Space>
                {courseInfo && (
                  <Button onClick={() => setCreateModalVisible(false)}>
                    取消
                  </Button>
                )}
                <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
                  创建并生成
                </Button>
              </Space>
            </Row>
          </Form.Item>
        </Form>
      </Modal>

      {/* 帮助对话框 */}
      <Suspense fallback={null}>
        <HelpDialog
          open={helpDialogOpen}
          onClose={() => setHelpDialogOpen(false)}
          defaultActiveKey={currentStep === 1 ? 'stage-one' : currentStep === 2 ? 'stage-two' : 'stage-three'}
        />
      </Suspense>

      {/* 新手引导 */}
      <Suspense fallback={null}>
        <OnboardingOverlay
          open={onboardingOpen}
          onFinish={() => {
            localStorage.setItem('onboarding-completed', 'true');
            setOnboardingOpen(false);
          }}
        />
      </Suspense>

      {/* 变更检测对话框 */}
      <Suspense fallback={null}>
        <ChangeDetectionDialog
          open={changeDetectionOpen}
          changedStage={changedStage}
          affectedStages={affectedStages}
          onRegenerate={handleCascadeRegenerate}
          onCancel={() => setChangeDetectionOpen(false)}
          onSkip={() => {
            setSkipChangeDetection(true);
            setChangeDetectionOpen(false);
            message.info('已跳过变更检测，本次会话将不再提示');
          }}
          loading={isGenerating}
        />
      </Suspense>
    </Layout>
  );
}

export default App;
