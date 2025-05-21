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
        console.log('开始登录请求:', username);
        const response = await loginRequest(username, password);
        console.log('登录响应:', response);
        
        if (response && response.access_token) {
          // 保存token (可能服务器返回的是access_token而不是token)
          const token = response.access_token;
          this.token = token;
          setToken(token);
          
          // 登录成功后立即获取用户信息
          try {
            await this.getUserInfo();
          } catch (error) {
            console.error('获取用户信息失败:', error);
          }
          
          return response;
        } else {
          throw new Error('登录响应中没有找到token');
        }
      } catch (error) {
        console.error('登录失败:', error);
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
