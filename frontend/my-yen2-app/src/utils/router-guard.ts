import { isLoggedIn } from './auth';

// 需要登录才能访问的页面路径
const authPages = [
  '/pages/user/index',
  '/pages/settings/index',
  '/pages/push/index', // 添加消息中心页面
  // 添加其他需要登录的页面
];

// 登录页路径
const loginPage = '/pages/login/index';

// 路由守卫
export function setupRouterGuard() {
  // 页面跳转前拦截
  uni.addInterceptor('navigateTo', {
    invoke(params) {
      return checkAuth(params.url);
    }
  });
  
  uni.addInterceptor('redirectTo', {
    invoke(params) {
      return checkAuth(params.url);
    }
  });
  
  // 虽然我们删除了 tabBar，但保留这个拦截器以防万一
  uni.addInterceptor('switchTab', {
    invoke(params) {
      return checkAuth(params.url);
    }
  });
  
  uni.addInterceptor('reLaunch', {
    invoke(params) {
      return checkAuth(params.url);
    }
  });
}

// 检查是否需要登录
function checkAuth(url: string): boolean {
  // 提取页面路径
  const pagePath = url.split('?')[0];
  
  // 如果是需要登录的页面，检查是否已登录
  if (authPages.some(page => pagePath.includes(page))) {
    if (!isLoggedIn()) {
      // 未登录，跳转到登录页
      uni.navigateTo({
        url: `${loginPage}?redirect=${encodeURIComponent(url)}`
      });
      return false;
    }
  }
  
  return true;
}
