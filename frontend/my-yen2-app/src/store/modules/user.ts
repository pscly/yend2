import { defineStore } from 'pinia';
import { getToken, setToken, removeToken } from '@/utils/auth';
import { loginRequest } from '@/utils/api-helpers';

interface UserInfo {
  id: number;
  username: string;
  email: string;
  avatar?: string;
  role?: string;
}

interface UserState {
  token: string;
  userInfo: UserInfo | null;
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: getToken(),
    userInfo: null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token
  },
  
  actions: {
    // 登录
    async login(username: string, password: string) {
      try {
        const response = await loginRequest(username, password);
        const { token } = response;
        
        // 保存token
        this.token = token;
        setToken(token);
        
        return response;
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },
    
    // 获取用户信息
    async getUserInfo() {
      try {
        // 这里应该调用获取用户信息的API
        // 暂时使用模拟数据
        this.userInfo = {
          id: 1,
          username: '测试用户',
          email: 'test@example.com',
          avatar: '/static/images/default-avatar.png',
          role: 'user'
        };
        
        return this.userInfo;
      } catch (error) {
        console.error('Get user info failed:', error);
        throw error;
      }
    },
    
    // 登出
    logout() {
      this.token = '';
      this.userInfo = null;
      removeToken();
    }
  }
});
