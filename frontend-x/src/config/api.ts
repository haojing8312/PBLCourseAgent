/**
 * API配置中心 - Single Source of Truth
 *
 * 开发环境：
 *   - 使用相对路径 '/api'
 *   - Vite proxy自动转发到 http://localhost:8000
 *   - 零配置，开箱即用
 *
 * 生产环境：
 *   - 设置环境变量 VITE_API_BASE_URL
 *   - 或在部署层配置反向代理（推荐）
 *
 * 示例：
 *   import { API_BASE_URL } from '@/config/api';
 *   fetch(`${API_BASE_URL}/v1/courses`);
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
