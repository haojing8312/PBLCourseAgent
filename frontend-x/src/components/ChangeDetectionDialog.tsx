/**
 * ChangeDetectionDialog - 变更检测对话框
 * 检测到Stage数据变更时，提示用户是否重新生成下游阶段
 */

import React from 'react';
import { Modal, Space, Typography, List, Alert, Button } from 'antd';
import { ExclamationCircleOutlined, SyncOutlined } from '@ant-design/icons';

const { Text, Paragraph } = Typography;

export interface ChangeDetectionDialogProps {
  /** 是否显示对话框 */
  open: boolean;

  /** 变更的阶段 */
  changedStage: number;

  /** 受影响的阶段列表 */
  affectedStages: number[];

  /** 确认重新生成回调 */
  onRegenerate: (stages: number[]) => void;

  /** 取消回调 */
  onCancel: () => void;

  /** 跳过检测回调 */
  onSkip: () => void;

  /** 是否正在重新生成 */
  loading?: boolean;
}

/**
 * ChangeDetectionDialog组件
 *
 * 当检测到Stage数据变更时，提示用户是否重新生成下游阶段
 *
 * @example
 * ```tsx
 * <ChangeDetectionDialog
 *   open={showChangeDialog}
 *   changedStage={1}
 *   affectedStages={[2, 3]}
 *   onRegenerate={(stages) => {
 *     // 重新生成stages [2, 3]
 *   }}
 *   onCancel={() => setShowChangeDialog(false)}
 *   onSkip={() => {
 *     // 跳过这次检测
 *     setShowChangeDialog(false);
 *   }}
 * />
 * ```
 */
export const ChangeDetectionDialog: React.FC<ChangeDetectionDialogProps> = ({
  open,
  changedStage,
  affectedStages,
  onRegenerate,
  onCancel,
  onSkip,
  loading = false,
}) => {
  const stageNames = ['确定预期学习结果', '确定可接受的证据', '规划学习体验'];

  return (
    <Modal
      title={
        <Space>
          <ExclamationCircleOutlined style={{ color: '#fa8c16' }} />
          <span>检测到内容变更</span>
        </Space>
      }
      open={open}
      onCancel={onCancel}
      footer={
        <Space>
          <Button onClick={onSkip}>跳过检测</Button>
          <Button onClick={onCancel}>暂不重生成</Button>
          <Button
            type="primary"
            icon={<SyncOutlined />}
            onClick={() => onRegenerate(affectedStages)}
            loading={loading}
          >
            重新生成
          </Button>
        </Space>
      }
      width={600}
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Alert
          message="内容一致性提醒"
          description={
            <div>
              <Paragraph>
                您修改了
                <Text strong> Stage {changedStage} ({stageNames[changedStage - 1]})</Text>
                的内容，这可能影响后续阶段的设计。
              </Paragraph>
              <Paragraph>
                为了保持UbD框架的逻辑一致性，建议重新生成受影响的阶段。
              </Paragraph>
            </div>
          }
          type="warning"
          showIcon
        />

        <div>
          <Text strong>受影响的阶段：</Text>
          <List
            size="small"
            bordered
            dataSource={affectedStages}
            renderItem={(stage) => (
              <List.Item>
                <Text>
                  Stage {stage}: {stageNames[stage - 1]}
                </Text>
              </List.Item>
            )}
          />
        </div>

        <div>
          <Text strong>重新生成说明：</Text>
          <ul style={{ paddingLeft: 20, marginTop: 8 }}>
            <li>
              <Text>AI将基于您修改后的内容重新生成后续阶段</Text>
            </li>
            <li>
              <Text>原有内容将被覆盖，请确保已保存重要修改</Text>
            </li>
            <li>
              <Text>重新生成可能需要1-2分钟</Text>
            </li>
          </ul>
        </div>

        <Alert
          message="提示"
          description="选择'跳过检测'将在本次会话中不再显示此提示。您随时可以手动触发重新生成。"
          type="info"
          showIcon
          closable
        />
      </Space>
    </Modal>
  );
};

export default ChangeDetectionDialog;
