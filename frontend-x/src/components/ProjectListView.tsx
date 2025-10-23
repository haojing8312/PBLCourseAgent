/**
 * ProjectListView - 项目列表视图
 * 显示所有课程项目，支持搜索、过滤、删除、复制
 */

import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Input, Space, Tag, Popconfirm, message, Typography, Tooltip } from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  DeleteOutlined,
  CopyOutlined,
  FolderOpenOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { CourseProject } from '../types/course';
import { API_BASE_URL } from '@/config/api';

const { Search } = Input;
const { Text } = Typography;

export interface ProjectListViewProps {
  /** 打开项目回调 */
  onOpenProject: (project: CourseProject) => void;

  /** 创建新项目回调 */
  onCreateProject: () => void;
}

/**
 * ProjectListView组件
 *
 * 项目管理界面，显示所有课程项目列表
 *
 * @example
 * ```tsx
 * <ProjectListView
 *   onOpenProject={(project) => navigate(`/course/${project.id}`)}
 *   onCreateProject={() => setCreateModalOpen(true)}
 * />
 * ```
 */
export const ProjectListView: React.FC<ProjectListViewProps> = ({
  onOpenProject,
  onCreateProject,
}) => {
  const [projects, setProjects] = useState<CourseProject[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');

  /**
   * 加载项目列表
   */
  const loadProjects = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/courses`);
      if (response.ok) {
        const data = await response.json();
        setProjects(data);
      }
    } catch (error) {
      message.error('加载项目列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  /**
   * 删除项目
   */
  const handleDelete = async (id: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/courses/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        message.success('项目已删除');
        loadProjects();
      } else {
        message.error('删除失败');
      }
    } catch (error) {
      message.error('删除失败');
    }
  };

  /**
   * 复制项目
   */
  const handleCopy = async (id: number) => {
    try {
      const response = await fetch(`${API_BASE_URL}/courses/${id}/copy`, {
        method: 'POST',
      });

      if (response.ok) {
        message.success('项目已复制');
        loadProjects();
      } else {
        message.error('复制失败');
      }
    } catch (error) {
      message.error('复制失败');
    }
  };

  /**
   * 表格列定义
   */
  const columns: ColumnsType<CourseProject> = [
    {
      title: '课程名称',
      dataIndex: 'title',
      key: 'title',
      width: 300,
      render: (text, record) => (
        <Space direction="vertical" size={0}>
          <Button type="link" onClick={() => onOpenProject(record)}>
            {text}
          </Button>
          {record.description && (
            record.description.length > 50 ? (
              <Tooltip title={record.description} placement="topLeft">
                <Text type="secondary" style={{ fontSize: '12px', cursor: 'help' }}>
                  {`${record.description.substring(0, 50)}...`}
                </Text>
              </Tooltip>
            ) : (
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {record.description}
              </Text>
            )
          )}
        </Space>
      ),
    },
    {
      title: '学科',
      dataIndex: 'subject',
      key: 'subject',
      width: 150,
      render: (text) => text || '-',
    },
    {
      title: '年级',
      dataIndex: 'grade_level',
      key: 'grade_level',
      width: 100,
      render: (text) => text || '-',
    },
    {
      title: '时长',
      key: 'duration',
      width: 250,
      render: (_, record) => {
        if (!record.total_class_hours && !record.schedule_description) {
          return '-';
        }

        return (
          <Space direction="vertical" size={0}>
            {record.total_class_hours && (
              <Text strong>{record.total_class_hours}课时</Text>
            )}
            {record.schedule_description && (
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {record.schedule_description}
              </Text>
            )}
          </Space>
        );
      },
    },
    {
      title: '进度',
      key: 'progress',
      width: 200,
      render: (_, record) => {
        const hasStageOne = !!record.stage_one_data;
        const hasStageTwo = !!record.stage_two_data;
        const hasStageThree = !!record.stage_three_data;

        return (
          <Space wrap>
            <Tag color={hasStageOne ? 'success' : 'default'}>Stage 1</Tag>
            <Tag color={hasStageTwo ? 'success' : 'default'}>Stage 2</Tag>
            <Tag color={hasStageThree ? 'success' : 'default'}>Stage 3</Tag>
          </Space>
        );
      },
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (date) => (date ? new Date(date).toLocaleString('zh-CN') : '-'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<FolderOpenOutlined />}
            onClick={() => onOpenProject(record)}
          >
            打开
          </Button>
          <Button type="text" icon={<CopyOutlined />} onClick={() => handleCopy(record.id!)}>
            复制
          </Button>
          <Popconfirm
            title="确定删除此项目？"
            description="删除后无法恢复。"
            onConfirm={() => handleDelete(record.id!)}
            okText="删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button type="text" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  /**
   * 过滤项目
   */
  const filteredProjects = projects.filter(
    (project) =>
      !searchText ||
      project.title.toLowerCase().includes(searchText.toLowerCase()) ||
      (project.subject && project.subject.toLowerCase().includes(searchText.toLowerCase()))
  );

  return (
    <Card
      title="我的课程项目"
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={onCreateProject}>
          新建课程
        </Button>
      }
    >
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Search
          placeholder="搜索课程名称或学科..."
          allowClear
          enterButton={<SearchOutlined />}
          size="large"
          onSearch={(value) => setSearchText(value)}
          onChange={(e) => setSearchText(e.target.value)}
          style={{ width: 400 }}
        />

        <Table
          columns={columns}
          dataSource={filteredProjects}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个项目`,
          }}
          scroll={{ x: 1200 }}
        />
      </Space>
    </Card>
  );
};

export default ProjectListView;
