/**
 * Course Service - 课程CRUD操作
 * 处理课程项目的创建、读取、更新、删除
 */

import type { CourseProject } from '../types/course';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface CreateCourseRequest {
  title: string;
  subject?: string;
  grade_level?: string;
  duration_weeks?: number;
  description?: string;
}

export interface UpdateCourseRequest {
  title?: string;
  subject?: string;
  grade_level?: string;
  duration_weeks?: number;
  description?: string;
}

/**
 * 创建新课程
 */
export async function createCourse(request: CreateCourseRequest): Promise<CourseProject> {
  const response = await fetch(`${API_BASE_URL}/api/v1/courses`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to create course: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * 获取课程详情
 */
export async function getCourse(courseId: number): Promise<CourseProject> {
  const response = await fetch(`${API_BASE_URL}/api/v1/courses/${courseId}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to get course: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * 获取课程列表
 */
export async function listCourses(skip = 0, limit = 100): Promise<CourseProject[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/courses?skip=${skip}&limit=${limit}`);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to list courses: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * 更新课程基本信息
 */
export async function updateCourse(
  courseId: number,
  request: UpdateCourseRequest
): Promise<CourseProject> {
  const response = await fetch(`${API_BASE_URL}/api/v1/courses/${courseId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to update course: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * 删除课程
 */
export async function deleteCourse(courseId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/courses/${courseId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to delete course: ${response.status} ${errorText}`);
  }
}

/**
 * 更新Stage One数据 (Markdown)
 */
export async function updateStageOne(
  courseId: number,
  markdown: string
): Promise<CourseProject> {
  const response = await fetch(`${API_BASE_URL}/api/v1/courses/${courseId}/stage-one`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ markdown }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to update stage one: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * 更新Stage Two数据 (Markdown)
 */
export async function updateStageTwo(
  courseId: number,
  markdown: string
): Promise<CourseProject> {
  const response = await fetch(`${API_BASE_URL}/api/v1/courses/${courseId}/stage-two`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ markdown }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to update stage two: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * 更新Stage Three数据 (Markdown)
 */
export async function updateStageThree(
  courseId: number,
  markdown: string
): Promise<CourseProject> {
  const response = await fetch(`${API_BASE_URL}/api/v1/courses/${courseId}/stage-three`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ markdown }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to update stage three: ${response.status} ${errorText}`);
  }

  return response.json();
}
