/**
 * Export Service - 课程导出服务
 * 处理课程方案导出为Markdown文件
 */

import { API_BASE_URL } from '@/config/api';

/**
 * 导出课程为Markdown文件并触发浏览器下载
 *
 * @param courseId - 课程ID
 * @throws Error if export fails
 */
export async function exportCourseAsMarkdown(courseId: number): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/courses/${courseId}/export/markdown`, {
      method: 'GET',
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Export failed: ${response.status} ${errorText}`);
    }

    // 获取文件名（从Content-Disposition header）
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = '课程方案.md';

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    }

    // 获取文件内容
    const blob = await response.blob();

    // 触发浏览器下载
    downloadBlob(blob, filename);

    console.log(`[ExportService] Successfully exported: ${filename}`);
  } catch (error) {
    console.error('[ExportService] Export failed:', error);
    throw error;
  }
}

/**
 * 辅助函数：触发浏览器下载Blob
 *
 * @param blob - 文件Blob对象
 * @param filename - 下载的文件名
 */
function downloadBlob(blob: Blob, filename: string): void {
  // 创建临时URL
  const url = window.URL.createObjectURL(blob);

  // 创建临时<a>标签并触发点击
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();

  // 清理
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * 辅助函数：预览Markdown内容（不下载）
 *
 * @param courseId - 课程ID
 * @returns Markdown文本内容
 */
export async function previewMarkdown(courseId: number): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/courses/${courseId}/export/markdown`, {
    method: 'GET',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Preview failed: ${response.status} ${errorText}`);
  }

  return response.text();
}

/**
 * 辅助函数：复制Markdown到剪贴板
 *
 * @param courseId - 课程ID
 */
export async function copyMarkdownToClipboard(courseId: number): Promise<void> {
  const markdown = await previewMarkdown(courseId);

  if (navigator.clipboard && navigator.clipboard.writeText) {
    await navigator.clipboard.writeText(markdown);
    console.log('[ExportService] Markdown copied to clipboard');
  } else {
    // Fallback for older browsers
    const textarea = document.createElement('textarea');
    textarea.value = markdown;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    console.log('[ExportService] Markdown copied to clipboard (fallback)');
  }
}
