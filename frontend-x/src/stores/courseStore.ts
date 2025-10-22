/**
 * 课程项目状态管理 - Zustand Store (Markdown版本)
 * 管理当前课程的完整状态和工作流进度
 * 直接存储markdown字符串而非JSON对象
 */
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type {
  ConversationMessage,
} from '../types/course';

/**
 * 对话消息 (使用 types/course.ts 中的定义)
 */
export type Message = ConversationMessage;

/**
 * 步骤状态
 */
export type StepStatus = 'pending' | 'in_progress' | 'completed' | 'error';

/**
 * 课程项目基本信息
 */
export interface CourseInfo {
  id?: number;
  title: string;
  subject?: string;
  gradeLevel?: string;

  // 课程时长 - 灵活方案
  totalClassHours?: number;  // 总课时数（按45分钟标准课时）
  scheduleDescription?: string;  // 上课周期描述

  description?: string;
}

// StageOneData, StageTwoData, StageThreeData 现在从 types/course.ts 导入

/**
 * 课程Store状态
 */
interface CourseState {
  // === 课程基本信息 ===
  courseInfo: CourseInfo | null;
  setCourseInfo: (info: CourseInfo) => void;

  // === 工作流状态 ===
  currentStep: number; // 当前步骤 (1-3)
  setCurrentStep: (step: number) => void;

  stepStatus: Record<number, StepStatus>; // 每个步骤的状态
  setStepStatus: (step: number, status: StepStatus) => void;

  // === 三阶段数据 (Markdown格式) ===
  stageOneData: string | null;
  setStageOneData: (markdown: string) => void;

  stageTwoData: string | null;
  setStageTwoData: (markdown: string) => void;

  stageThreeData: string | null;
  setStageThreeData: (markdown: string) => void;

  // === 兼容性接口：数组访问方式 ===
  stageMarkdowns: Record<number, string>; // {1: stageOneData, 2: stageTwoData, 3: stageThreeData}
  setStageMarkdown: (step: number, markdown: string) => void;

  // === 编辑模式 ===
  isEditMode: boolean;
  setEditMode: (mode: boolean) => void;

  // === 对话历史 ===
  conversationHistory: Message[];
  addMessage: (message: Partial<Message> & Pick<Message, 'role' | 'content'>) => void;
  clearConversation: (step?: number) => void; // 清除特定步骤或所有对话

  // === SSE生成状态 ===
  isGenerating: boolean;
  setGenerating: (generating: boolean) => void;

  generationProgress: number; // 0-100
  setGenerationProgress: (progress: number) => void;

  generationError: string | null;
  setGenerationError: (error: string | null) => void;

  // === 版本控制（用于变更检测） ===
  stageVersions: Record<number, Date>;
  updateStageVersion: (step: number) => void;

  // === 重置 ===
  resetCourse: () => void;
}

/**
 * 生成唯一ID
 */
const generateId = () => `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

/**
 * 课程Store
 */
export const useCourseStore = create<CourseState>()(
  devtools(
    persist(
      (set, get) => ({
        // === 初始状态 ===
        courseInfo: null,
        currentStep: 1,
        stepStatus: {
          1: 'pending',
          2: 'pending',
          3: 'pending',
        },
        stageOneData: null,
        stageTwoData: null,
        stageThreeData: null,
        stageMarkdowns: {}, // 兼容性接口
        isEditMode: false,
        conversationHistory: [],
        isGenerating: false,
        generationProgress: 0,
        generationError: null,
        stageVersions: {},

        // === Actions ===
        setCourseInfo: (info) => set({ courseInfo: info }),

        setCurrentStep: (step) => set({ currentStep: step }),

        setStepStatus: (step, status) =>
          set((state) => ({
            stepStatus: { ...state.stepStatus, [step]: status },
          })),

        setStageOneData: (markdown) =>
          set((state) => ({
            stageOneData: markdown,
            stageMarkdowns: { ...state.stageMarkdowns, 1: markdown },
            stepStatus: { ...state.stepStatus, 1: 'completed' },
          })),

        setStageTwoData: (markdown) =>
          set((state) => ({
            stageTwoData: markdown,
            stageMarkdowns: { ...state.stageMarkdowns, 2: markdown },
            stepStatus: { ...state.stepStatus, 2: 'completed' },
          })),

        setStageThreeData: (markdown) =>
          set((state) => ({
            stageThreeData: markdown,
            stageMarkdowns: { ...state.stageMarkdowns, 3: markdown },
            stepStatus: { ...state.stepStatus, 3: 'completed' },
          })),

        setStageMarkdown: (step, markdown) => {
          const state = get();
          switch (step) {
            case 1:
              state.setStageOneData(markdown);
              break;
            case 2:
              state.setStageTwoData(markdown);
              break;
            case 3:
              state.setStageThreeData(markdown);
              break;
            default:
              console.warn(`[courseStore] Invalid step: ${step}`);
          }
        },

        setEditMode: (mode) => set({ isEditMode: mode }),

        addMessage: (message) =>
          set((state) => ({
            conversationHistory: [
              ...state.conversationHistory,
              {
                ...message,
                id: message.id || generateId(),
                timestamp: message.timestamp || new Date(),
              } as Message,
            ],
          })),

        clearConversation: (step) =>
          set((state) => ({
            conversationHistory: step
              ? state.conversationHistory.filter((msg) => msg.step !== step)
              : [],
          })),

        setGenerating: (generating) => set({ isGenerating: generating }),

        setGenerationProgress: (progress) =>
          set({ generationProgress: progress }),

        setGenerationError: (error) => set({ generationError: error }),

        updateStageVersion: (step) =>
          set((state) => ({
            stageVersions: { ...state.stageVersions, [step]: new Date() },
          })),

        resetCourse: () =>
          set({
            courseInfo: null,
            currentStep: 1,
            stepStatus: {
              1: 'pending',
              2: 'pending',
              3: 'pending',
            },
            stageOneData: null,
            stageTwoData: null,
            stageThreeData: null,
            stageMarkdowns: {},
            isEditMode: false,
            conversationHistory: [],
            isGenerating: false,
            generationProgress: 0,
            generationError: null,
            stageVersions: {},
          }),
      }),
      {
        name: 'course-store', // localStorage key
        // 仅持久化关键数据，不持久化临时状态
        partialize: (state) => ({
          courseInfo: state.courseInfo,
          currentStep: state.currentStep,
          stepStatus: state.stepStatus,
          stageOneData: state.stageOneData,
          stageTwoData: state.stageTwoData,
          stageThreeData: state.stageThreeData,
          stageMarkdowns: state.stageMarkdowns,
          conversationHistory: state.conversationHistory,
          stageVersions: state.stageVersions,
        }),
      }
    ),
    {
      name: 'CourseStore', // DevTools name
    }
  )
);
