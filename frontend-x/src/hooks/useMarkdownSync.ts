/**
 * useMarkdownSync Hook
 * 提供Markdown内容的防抖自动保存功能
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useCourseStore } from '../stores/courseStore';

export interface UseMarkdownSyncOptions {
  /** 当前步骤 (1-3) */
  step: number;
  /** 防抖延迟（毫秒），默认1000ms */
  debounceMs?: number;
  /** 自动保存回调（可用于后端同步） */
  onSave?: (step: number, markdown: string) => Promise<void>;
  /** 启用自动保存 */
  autoSave?: boolean;
}

export interface UseMarkdownSyncReturn {
  /** 当前Markdown内容 */
  markdown: string;

  /** 更新Markdown内容 */
  setMarkdown: (value: string) => void;

  /** 是否有未保存的更改 */
  isDirty: boolean;

  /** 是否正在保存 */
  isSaving: boolean;

  /** 手动保存 */
  save: () => Promise<void>;

  /** 重置为Store中的值 */
  reset: () => void;
}

/**
 * useMarkdownSync Hook
 *
 * 为Markdown编辑器提供防抖自动保存和脏检查
 *
 * @example
 * ```tsx
 * const { markdown, setMarkdown, isDirty, isSaving } = useMarkdownSync({
 *   step: 1,
 *   debounceMs: 1000,
 *   autoSave: true,
 *   onSave: async (step, content) => {
 *     await updateStageMarkdown(courseId, step, content);
 *   }
 * });
 *
 * <CodeMirror
 *   value={markdown}
 *   onChange={setMarkdown}
 * />
 * {isDirty && <Badge>未保存</Badge>}
 * {isSaving && <Spin />}
 * ```
 */
export function useMarkdownSync(
  options: UseMarkdownSyncOptions
): UseMarkdownSyncReturn {
  const {
    step,
    debounceMs = 1000,
    onSave,
    autoSave = false,
  } = options;

  const { stageMarkdowns, setStageMarkdown } = useCourseStore();

  // 从Store获取初始值
  const storeValue = stageMarkdowns[step] || '';

  // 本地编辑状态
  const [markdown, setMarkdownLocal] = useState(storeValue);
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // 防抖定时器
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // 保存函数
  const save = useCallback(async () => {
    if (!isDirty) return;

    setIsSaving(true);

    try {
      // 保存到Store
      setStageMarkdown(step, markdown);

      // 调用自定义保存回调（后端同步）
      if (onSave) {
        await onSave(step, markdown);
      }

      setIsDirty(false);
      console.log(`[useMarkdownSync] Saved markdown for step ${step}`);
    } catch (error) {
      console.error(`[useMarkdownSync] Failed to save markdown for step ${step}:`, error);
      throw error;
    } finally {
      setIsSaving(false);
    }
  }, [step, markdown, isDirty, onSave, setStageMarkdown]);

  // 更新Markdown
  const setMarkdown = useCallback((value: string) => {
    setMarkdownLocal(value);
    setIsDirty(value !== storeValue);

    // 清除旧的定时器
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // 如果启用自动保存，设置新的定时器
    if (autoSave) {
      debounceTimerRef.current = setTimeout(() => {
        save();
      }, debounceMs);
    }
  }, [storeValue, autoSave, debounceMs, save]);

  // 重置为Store中的值
  const reset = useCallback(() => {
    setMarkdownLocal(storeValue);
    setIsDirty(false);
  }, [storeValue]);

  // 当step或storeValue变化时，重置本地状态
  useEffect(() => {
    setMarkdownLocal(storeValue);
    setIsDirty(false);
  }, [step, storeValue]);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  // 在组件卸载前保存未保存的内容
  useEffect(() => {
    return () => {
      if (isDirty && autoSave) {
        // 立即保存（不等待异步完成）
        setStageMarkdown(step, markdown);
        onSave?.(step, markdown).catch((error) => {
          console.error('[useMarkdownSync] Failed to save on unmount:', error);
        });
      }
    };
  }, [isDirty, autoSave, step, markdown, setStageMarkdown, onSave]);

  return {
    markdown,
    setMarkdown,
    isDirty,
    isSaving,
    save,
    reset,
  };
}

/**
 * 辅助函数：创建保存指示器文本
 */
export function getSaveStatus(
  isDirty: boolean,
  isSaving: boolean
): string {
  if (isSaving) return '保存中...';
  if (isDirty) return '未保存';
  return '已保存';
}

/**
 * 辅助函数：获取保存状态对应的颜色
 */
export function getSaveStatusColor(
  isDirty: boolean,
  isSaving: boolean
): 'success' | 'warning' | 'processing' {
  if (isSaving) return 'processing';
  if (isDirty) return 'warning';
  return 'success';
}
