/**
 * 认证状态管理 - Zustand Store
 *
 * 管理用户登录状态、token 存储和认证操作
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  // 状态
  token: string | null;
  username: string | null;
  isAuthenticated: boolean;

  // 操作
  login: (token: string, username: string) => void;
  logout: () => void;
  getToken: () => string | null;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      token: null,
      username: null,
      isAuthenticated: false,

      // 登录
      login: (token: string, username: string) => {
        set({
          token,
          username,
          isAuthenticated: true,
        });
        console.log('[AuthStore] User logged in:', username);
      },

      // 登出
      logout: () => {
        set({
          token: null,
          username: null,
          isAuthenticated: false,
        });
        console.log('[AuthStore] User logged out');
      },

      // 获取 token（供 API 调用使用）
      getToken: () => {
        return get().token;
      },
    }),
    {
      name: 'auth-storage', // localStorage key
      partialize: (state) => ({
        token: state.token,
        username: state.username,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
