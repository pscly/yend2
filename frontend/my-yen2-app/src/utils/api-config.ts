import { OpenAPI } from '@/api';
import { getToken } from '@/utils/auth';
import axios from 'axios';

// 配置API基础URL和请求拦截器
export function setupAPI() {
  // 设置基础URL
  // #ifdef H5
  OpenAPI.BASE = import.meta.env.VITE_API_BASE_URL || '';
  // #endif
  
  // #ifdef MP-WEIXIN
  OpenAPI.BASE = 'https://api.example.com';
  // #endif
  
  // #ifdef APP-PLUS
  OpenAPI.BASE = 'https://api.example.com';
  // #endif
  
  // 配置认证token获取方法
  OpenAPI.TOKEN = async () => getToken();
  
  // 配置凭证策略
  OpenAPI.WITH_CREDENTIALS = true;
  
  // 配置请求头
  OpenAPI.HEADERS = async () => {
    return {
      'Accept-Language': uni.getStorageSync('language') || 'zh-CN',
      'X-Client-Platform': process.env.UNI_PLATFORM || 'unknown'
    };
  };
  
  // 添加全局请求拦截器，处理表单数据
  axios.interceptors.request.use(config => {
    // 检查是否是表单数据请求
    if (config.headers['Content-Type'] === 'application/x-www-form-urlencoded' && 
        typeof config.data === 'object' && 
        !(config.data instanceof URLSearchParams)) {
      
      // 将对象转换为URLSearchParams
      const params = new URLSearchParams();
      Object.entries(config.data).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
      config.data = params;
    }
    return config;
  });
}
