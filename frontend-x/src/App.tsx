/**
 * App.tsx - UbD-PBL课程架构师主应用
 * 集成所有组件，提供完整的课程设计工作流
 */

import React, { useState, useEffect } from 'react';
import { Layout, Row, Col, Space, Button, Input, Form, Modal, message, Spin } from 'antd';
import { PlusOutlined, SaveOutlined } from '@ant-design/icons';
import { StepNavigator } from './components/StepNavigator';
import { ChatPanel } from './components/ChatPanel';
import { ContentPanel } from './components/ContentPanel';
import { MarkdownEditor } from './components/MarkdownEditor';
import { DownloadButton } from './components/DownloadButton';
import { useStepWorkflow } from './hooks/useStepWorkflow';
import { useCourseStore } from './stores/courseStore';
import type { WorkflowRequest } from './types/course';
import './App.css';

const { Header, Content } = Layout;

function App() {
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
    stepStatus,
    generationProgress,
    generationError,
    startWorkflow,
    abortWorkflow,
  } = useStepWorkflow();

  // 新建课程对话框
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [createForm] = Form.useForm();

  /**
   * 如果没有课程信息，显示创建对话框
   */
  useEffect(() => {
    if (!courseInfo) {
      setCreateModalVisible(true);
    }
  }, [courseInfo]);

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

    // 构建工作流请求
    const workflowRequest: WorkflowRequest = {
      title: values.title,
      subject: values.subject,
      grade_level: values.gradeLevel,
      duration_weeks: values.durationWeeks,
      description: values.description,
      stages_to_generate: [1, 2, 3], // 生成所有三个阶段
    };

    // 关闭对话框
    setCreateModalVisible(false);

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
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 顶部导航栏 */}
      <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
        <Row justify="space-between" align="middle" style={{ height: '100%' }}>
          <Col>
            <Space size="large">
              <h2 style={{ margin: 0, color: '#1890ff' }}>UbD-PBL 课程架构师</h2>
              {courseInfo && <span style={{ color: '#666' }}>{courseInfo.title}</span>}
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
              >
                新建课程
              </Button>
              <DownloadButton
                courseId={courseInfo?.id}
                dropdown={true}
                disabled={!stageOneData}
              />
            </Space>
          </Col>
        </Row>
      </Header>

      {/* 步骤导航器 */}
      <div style={{ background: '#fff', padding: '16px 24px', borderBottom: '1px solid #f0f0f0' }}>
        <StepNavigator
          current={currentStep - 1}
          stepStatus={stepStatus}
          onChange={(step) => {
            // 通过useStepWorkflow的goToStep处理
          }}
        />
      </div>

      {/* 主内容区 */}
      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        {isGenerating && (
          <div style={{ textAlign: 'center', padding: '24px', background: '#fff', marginBottom: '16px', borderRadius: '8px' }}>
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
          <div style={{ padding: '16px', background: '#fff', marginBottom: '16px', borderRadius: '8px', border: '1px solid #ff4d4f' }}>
            <p style={{ color: '#ff4d4f', margin: 0 }}>错误: {generationError}</p>
          </div>
        )}

        <Row gutter={[16, 16]} style={{ height: 'calc(100vh - 240px)' }}>
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
              <MarkdownEditor
                step={currentStep}
                autoSave={true}
                debounceMs={1000}
                onSave={handleSaveMarkdown}
                height="100%"
              />
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
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              {courseInfo && (
                <Button onClick={() => setCreateModalVisible(false)}>
                  取消
                </Button>
              )}
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
                创建并生成
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  );
}

export default App;
