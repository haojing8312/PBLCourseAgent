/**
 * useStepWorkflow Hook
 * 管理UbD三阶段导航和工作流生成
 */

import {  useCallback, useRef } from 'react';
import { useCourseStore } from '../stores/courseStore';
import { streamWorkflow, WorkflowStreamResult } from '../services/workflowService';
import type { WorkflowRequest } from '../types/course';

export interface UseStepWorkflowReturn {
  // 状态
  currentStep: number;
  stepStatus: Record<number, 'pending' | 'in_progress' | 'completed' | 'error'>;
  isGenerating: boolean;
  generationProgress: number;
  generationError: string | null;

  // 导航
  goToStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  canGoNext: boolean;
  canGoPrev: boolean;

  // 工作流生成
  startWorkflow: (request: WorkflowRequest) => Promise<void>;
  abortWorkflow: () => void;
}

/**
 * useStepWorkflow Hook
 *
 * 提供步骤导航和工作流生成的完整功能
 *
 * @example
 * ```tsx
 * const { currentStep, goToStep, startWorkflow, isGenerating } = useStepWorkflow();
 *
 * // 导航
 * <Steps current={currentStep} onChange={goToStep} />
 *
 * // 开始生成
 * await startWorkflow({
 *   title: "AI编程课程",
 *   duration_weeks: 12,
 *   stages_to_generate: [1, 2, 3]
 * });
 * ```
 */
export function useStepWorkflow(): UseStepWorkflowReturn {
  const {
    currentStep,
    setCurrentStep,
    stepStatus,
    setStepStatus,
    isGenerating,
    setGenerating,
    generationProgress,
    setGenerationProgress,
    generationError,
    setGenerationError,
    setStageOneData,
    setStageTwoData,
    setStageThreeData,
    updateStageVersion,
  } = useCourseStore();

  // 工作流控制器引用
  const workflowControllerRef = useRef<WorkflowStreamResult | null>(null);

  /**
   * 导航到指定步骤
   */
  const goToStep = useCallback((step: number) => {
    if (step < 1 || step > 3) {
      console.warn('[useStepWorkflow] Invalid step:', step);
      return;
    }
    setCurrentStep(step);
  }, [setCurrentStep]);

  /**
   * 下一步
   */
  const nextStep = useCallback(() => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  }, [currentStep, setCurrentStep]);

  /**
   * 上一步
   */
  const prevStep = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  }, [currentStep, setCurrentStep]);

  /**
   * 能否前进
   */
  const canGoNext = currentStep < 3;

  /**
   * 能否后退
   */
  const canGoPrev = currentStep > 1;

  /**
   * 开始工作流生成
   */
  const startWorkflow = useCallback(async (request: WorkflowRequest) => {
    try {
      // 重置状态
      setGenerating(true);
      setGenerationProgress(0);
      setGenerationError(null);

      // 标记要生成的阶段为in_progress
      request.stages_to_generate.forEach((stage) => {
        setStepStatus(stage, 'in_progress');
      });

      // 启动SSE流
      const controller = await streamWorkflow(request, {
        onStart: (data) => {
          console.log('[useStepWorkflow] Workflow started:', data);
        },

        onProgress: (data) => {
          console.log('[useStepWorkflow] Progress:', data);
          if (data.progress !== undefined) {
            setGenerationProgress(data.progress * 100);
          }
          if (data.stage) {
            setStepStatus(data.stage, 'in_progress');
          }
        },

        onStageComplete: (data) => {
          console.log('[useStepWorkflow] Stage complete:', data);

          const stage = data.stage;
          const result = data.result;

          if (!stage || !result) {
            console.warn('[useStepWorkflow] Missing stage or result in event:', data);
            return;
          }

          // 更新对应阶段的数据
          switch (stage) {
            case 1:
              setStageOneData(result);
              updateStageVersion(1);
              break;
            case 2:
              setStageTwoData(result);
              updateStageVersion(2);
              break;
            case 3:
              setStageThreeData(result);
              updateStageVersion(3);
              break;
            default:
              console.warn('[useStepWorkflow] Unknown stage:', stage);
          }

          // 标记为完成
          setStepStatus(stage, 'completed');

          // 显示验证结果（如果有）
          if (data.validation) {
            const { overall_valid, avg_score, warnings } = data.validation;
            console.log(`[useStepWorkflow] Stage ${stage} validation:`, {
              valid: overall_valid,
              score: avg_score,
              warnings,
            });
          }
        },

        onError: (data) => {
          console.error('[useStepWorkflow] Error:', data);
          const errorMessage = data.message || 'Unknown error occurred';
          setGenerationError(errorMessage);

          // 标记当前步骤为错误
          if (data.stage) {
            setStepStatus(data.stage, 'error');
          }
        },

        onComplete: (data) => {
          console.log('[useStepWorkflow] Workflow complete:', data);
          setGenerating(false);
          setGenerationProgress(100);

          // 打印总结
          if (data.summary) {
            console.log('[useStepWorkflow] Summary:', data.summary);
          }
          if (data.total_time) {
            console.log(`[useStepWorkflow] Total time: ${data.total_time}s`);
          }
        },
      });

      // 保存控制器引用
      workflowControllerRef.current = controller;

    } catch (error) {
      console.error('[useStepWorkflow] Failed to start workflow:', error);
      setGenerationError(error instanceof Error ? error.message : String(error));
      setGenerating(false);
    }
  }, [
    setGenerating,
    setGenerationProgress,
    setGenerationError,
    setStepStatus,
    setStageOneData,
    setStageTwoData,
    setStageThreeData,
    updateStageVersion,
  ]);

  /**
   * 中止工作流生成
   */
  const abortWorkflow = useCallback(() => {
    if (workflowControllerRef.current) {
      workflowControllerRef.current.abort();
      workflowControllerRef.current = null;
      setGenerating(false);
      setGenerationError('Generation aborted by user');
      console.log('[useStepWorkflow] Workflow aborted');
    }
  }, [setGenerating, setGenerationError]);

  return {
    // 状态
    currentStep,
    stepStatus,
    isGenerating,
    generationProgress,
    generationError,

    // 导航
    goToStep,
    nextStep,
    prevStep,
    canGoNext,
    canGoPrev,

    // 工作流
    startWorkflow,
    abortWorkflow,
  };
}
