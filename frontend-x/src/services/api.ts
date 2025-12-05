/**
 * API 封装 - 统一添加认证 header
 *
 * 所有需要认证的 API 调用都应使用 authFetch
 */
import { useAuthStore } from '@/stores/authStore';
import { API_BASE_URL } from '@/config/api';

/**
 * 带认证的 fetch 封装
 *
 * 自动添加 Authorization header
 * 401 响应时自动登出
 */
export async function authFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = useAuthStore.getState().token;

  const headers: HeadersInit = {
    ...options.headers,
  };

  // 添加认证头
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // 401 时自动登出
  if (response.status === 401) {
    console.warn('[API] Unauthorized, logging out...');
    useAuthStore.getState().logout();
    // 可以选择重定向到登录页
    // window.location.reload();
  }

  return response;
}

/**
 * 带认证的 JSON POST 请求
 */
export async function authPost<T>(endpoint: string, data: unknown): Promise<T> {
  const response = await authFetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(error.detail || '请求失败');
  }

  return response.json();
}

/**
 * 带认证的 JSON PUT 请求
 */
export async function authPut<T>(endpoint: string, data: unknown): Promise<T> {
  const response = await authFetch(endpoint, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(error.detail || '请求失败');
  }

  return response.json();
}

/**
 * 带认证的 DELETE 请求
 */
export async function authDelete(endpoint: string): Promise<void> {
  const response = await authFetch(endpoint, {
    method: 'DELETE',
  });

  if (!response.ok && response.status !== 204) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(error.detail || '请求失败');
  }
}

/**
 * 带认证的 GET 请求
 */
export async function authGet<T>(endpoint: string): Promise<T> {
  const response = await authFetch(endpoint, {
    method: 'GET',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(error.detail || '请求失败');
  }

  return response.json();
}
