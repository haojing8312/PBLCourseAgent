/**
 * Course相关类型定义
 * 对应后端的UbD Stage数据模型
 */

// ========== Stage One: 确定预期学习结果 (G/U/Q/K/S) ==========

export interface GoalItem {
  text: string;
  order: number;
}

export interface UnderstandingItem {
  text: string;
  order: number;
  rationale: string;
  validation_score?: number; // 0-1, 语义验证分数
}

export interface QuestionItem {
  text: string;
  order: number;
}

export interface KnowledgeItem {
  text: string;
  order: number;
}

export interface SkillItem {
  text: string;
  order: number;
}

export interface StageOneData {
  goals: GoalItem[];
  understandings: UnderstandingItem[];
  questions: QuestionItem[];
  knowledge: KnowledgeItem[];
  skills: SkillItem[];
}

// ========== Stage Two: 确定可接受的证据 ==========

export interface RubricLevel {
  level: number; // 1-4
  label: string; // 卓越/熟练/发展中/初步
  description: string;
}

export interface RubricDimension {
  name: string;
  weight: number; // 0-1
  levels: RubricLevel[];
}

export interface Rubric {
  name: string;
  dimensions: RubricDimension[];
}

export interface PerformanceTask {
  title: string;
  description: string;
  context: string;
  student_role: string;
  deliverable: string;
  milestone_week: number;
  order: number;
  linked_ubd_elements: {
    u: number[];
    s: number[];
    k: number[];
  };
  rubric: Rubric;
}

export interface OtherEvidence {
  type: string;
  description: string;
}

export interface StageTwoData {
  driving_question: string;
  driving_question_context: string;
  performance_tasks: PerformanceTask[];
  other_evidence: OtherEvidence[];
}

// ========== Stage Three: 规划学习体验 ==========

export interface Activity {
  week: number;
  title: string;
  description: string;
  duration_hours: number;
  whereto_labels: string[]; // W/H/E/R/E/T/O
  linked_ubd_elements: {
    u: number[];
    s: number[];
    k: number[];
  };
  notes: string;
}

export interface PBLPhase {
  phase_type: 'launch' | 'build' | 'develop' | 'present';
  phase_name: string;
  duration_weeks: number;
  order: number;
  activities: Activity[];
}

export interface StageThreeData {
  pbl_phases: PBLPhase[];
}

// ========== Course Project ==========

export interface CourseProject {
  id?: number;
  title: string;
  subject?: string;
  grade_level?: string;

  // 课程时长 - 灵活方案
  total_class_hours?: number;  // 总课时数（按45分钟标准课时）
  schedule_description?: string;  // 上课周期描述

  description?: string;

  // UbD三阶段数据 - Markdown版本
  stage_one_data?: string;  // Markdown文本
  stage_two_data?: string;  // Markdown文本
  stage_three_data?: string;  // Markdown文本

  // 对话历史
  conversation_history?: ConversationMessage[];

  // 版本控制
  stage_one_version?: string;
  stage_two_version?: string;
  stage_three_version?: string;

  // 元数据
  created_at?: string;
  updated_at?: string;
}

// ========== Workflow相关 ==========

export interface WorkflowRequest {
  title: string;
  subject?: string;
  grade_level?: string;

  // 课程时长 - 灵活方案
  total_class_hours?: number;
  schedule_description?: string;

  description?: string;
  stages_to_generate?: number[]; // [1, 2, 3]
  stage_one_data?: string; // Stage One Markdown（修改后重新生成时提供）
  stage_two_data?: string; // Stage Two Markdown（修改后重新生成时提供）

  // 🎯 新增：AI对话中的编辑指令
  edit_instructions?: string; // AI对话中提出的修改指令
}

export interface SSEEvent {
  event: 'start' | 'progress' | 'stage_complete' | 'error' | 'complete';
  data: {
    stage?: number;
    progress?: number;
    message?: string;
    markdown?: string;  // Markdown文本（替代result）
    generation_time?: number;
    total_time?: number;
    summary?: {
      stage_one?: { markdown_length: number };
      stage_two?: { markdown_length: number };
      stage_three?: { markdown_length: number };
    };
  };
}

// ========== Conversation Message (从courseStore移到这里) ==========

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date | string;
  step?: number; // 所属步骤（1-3）
}
