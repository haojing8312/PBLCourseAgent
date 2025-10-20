/**
 * 课程项目状态管理 - Zustand Store
 * 管理当前课程的完整状态和工作流进度
 */
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

/**
 * 对话消息
 */
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  step?: number; // 消息属于哪个步骤（1-3）
}

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
  durationWeeks?: number;
  description?: string;
}

/**
 * Stage One 数据（G/U/Q/K/S）
 */
export interface StageOneData {
  goals?: any[];
  understandings?: any[];
  questions?: any[];
  knowledge?: any[];
  skills?: any[];
}

/**
 * Stage Two 数据（驱动性问题 + 表现性任务）
 */
export interface StageTwoData {
  drivingQuestion?: string;
  drivingQuestionContext?: string;
  performanceTasks?: any[];
  otherEvidence?: any[];
}

/**
 * Stage Three 数据（PBL学习蓝图）
 */
export interface StageThreeData {
  pblPhases?: any[];
}

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

  // === 三阶段数据 ===
  stageOneData: StageOneData | null;
  setStageOneData: (data: StageOneData) => void;

  stageTwoData: StageTwoData | null;
  setStageTwoData: (data: StageTwoData) => void;

  stageThreeData: StageThreeData | null;
  setStageThreeData: (data: StageThreeData) => void;

  // === Markdown内容（用于编辑预览） ===
  stageMarkdowns: Record<number, string>; // 每个阶段的Markdown内容
  setStageMarkdown: (step: number, markdown: string) => void;

  // === 编辑模式 ===
  isEditMode: boolean;
  setEditMode: (mode: boolean) => void;

  // === 对话历史 ===
  conversationHistory: Message[];
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
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
        stageMarkdowns: {},
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

        setStageOneData: (data) =>
          set({
            stageOneData: data,
            stepStatus: { ...get().stepStatus, 1: 'completed' },
          }),

        setStageTwoData: (data) =>
          set({
            stageTwoData: data,
            stepStatus: { ...get().stepStatus, 2: 'completed' },
          }),

        setStageThreeData: (data) =>
          set({
            stageThreeData: data,
            stepStatus: { ...get().stepStatus, 3: 'completed' },
          }),

        setStageMarkdown: (step, markdown) =>
          set((state) => ({
            stageMarkdowns: { ...state.stageMarkdowns, [step]: markdown },
          })),

        setEditMode: (mode) => set({ isEditMode: mode }),

        addMessage: (message) =>
          set((state) => ({
            conversationHistory: [
              ...state.conversationHistory,
              {
                ...message,
                id: generateId(),
                timestamp: new Date(),
              },
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
