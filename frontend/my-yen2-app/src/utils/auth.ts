// 从存储中获取token
export function getToken(): string {
  return uni.getStorageSync('token') || '';
}

// 保存token到存储
export function setToken(token: string): void {
  uni.setStorageSync('token', token);
}

// 清除token
export function removeToken(): void {
  uni.removeStorageSync('token');
}

// 检查是否已登录
export function isLoggedIn(): boolean {
  return !!getToken();
}

// 检查token是否过期
export function isTokenExpired(token: string): boolean {
  if (!token) return true;
  
  try {
    // JWT token由三部分组成，用.分隔
    const payload = token.split('.')[1];
    // Base64解码
    const decoded = JSON.parse(atob(payload));
    // 检查exp字段
    return decoded.exp * 1000 < Date.now();
  } catch (e) {
    console.error('Token解析失败:', e);
    return true;
  }
}