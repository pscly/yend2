import axios from 'axios';
import { OpenAPI } from '@/api';
import { getToken } from '@/utils/auth';

// 登录请求函数 - 使用正确的表单格式
export async function loginRequest(username: string, password: string) {
  try {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    const response = await axios.post(`${OpenAPI.BASE}/api/v1/auth/login`, params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Login request failed:', error);
    throw error;
  }
}

// 通用的表单提交函数 - 用于其他需要表单数据的API
export async function formDataRequest(url: string, data: Record<string, any>, method = 'POST') {
  try {
    const params = new URLSearchParams();
    
    // 将数据转换为URLSearchParams格式
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });
    
    const token = getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/x-www-form-urlencoded'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await axios({
      method,
      url: `${OpenAPI.BASE}${url}`,
      data: params,
      headers
    });
    
    return response.data;
  } catch (error) {
    console.error(`API request failed: ${url}`, error);
    throw error;
  }
}
