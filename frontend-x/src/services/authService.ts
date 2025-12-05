/**
 * 认证服务 - 登录 API 调用
 */
import { API_BASE_URL } from '@/config/api';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface UserResponse {
  username: string;
}

/**
 * 登录获取 token
 */
export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '登录失败' }));
    throw new Error(error.detail || '登录失败');
  }

  return response.json();
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(token: string): Promise<UserResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('获取用户信息失败');
  }

  return response.json();
}

/**
 * 验证 token 是否有效
 */
export async function verifyToken(token: string): Promise<boolean> {
  try {
    await getCurrentUser(token);
    return true;
  } catch {
    return false;
  }
}
