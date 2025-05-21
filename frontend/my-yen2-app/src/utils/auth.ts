// 从存储中获取token
export function getToken(): string {
  return uni.getStorageSync('token') || '';
}

// 保存token到存储
export function setToken(token: string): void {
  uni.setStorageSync('token', token);
  console.log('Token已保存:', token); // 添加日志以便调试
}

// 清除token
export function removeToken(): void {
  uni.removeStorageSync('token');
  console.log('Token已清除');
}

// 检查是否已登录
export function isLoggedIn(): boolean {
  const token = getToken();
  console.log('检查登录状态, token存在:', !!token);
  return !!token;
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
    const isExpired = decoded.exp * 1000 < Date.now();
    console.log('Token过期状态:', isExpired);
    return isExpired;
  } catch (e) {
    console.error('Token解析失败:', e);
    return true;
  }
}
