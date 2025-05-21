import { formDataRequest } from '@/utils/api-helpers';

export class CustomAuthService {
  // 用户注册
  static async register(userData: {
    username: string;
    email: string;
    password: string;
  }) {
    return formDataRequest('/api/v1/auth/register', userData);
  }
  
  // 重置密码请求
  static async requestPasswordReset(email: string) {
    return formDataRequest('/api/v1/auth/password-reset/request', { email });
  }
  
  // 确认重置密码
  static async confirmPasswordReset(token: string, newPassword: string) {
    return formDataRequest('/api/v1/auth/password-reset/confirm', {
      token,
      new_password: newPassword
    });
  }
  
  // 更新用户信息
  static async updateUserProfile(userData: Record<string, any>) {
    return formDataRequest('/api/v1/users/me', userData, 'PATCH');
  }
  
  // 更改密码
  static async changePassword(currentPassword: string, newPassword: string) {
    return formDataRequest('/api/v1/users/me/password', {
      current_password: currentPassword,
      new_password: newPassword
    });
  }
}