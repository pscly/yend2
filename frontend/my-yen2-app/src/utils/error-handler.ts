import { showError } from './message';

// 全局错误处理
export function setupErrorHandler() {
  try {
    // 捕获Promise中未处理的rejection
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled rejection:', event.reason);
      
      // 显示友好的错误提示
      const errorMessage = getErrorMessage(event.reason);
      showError(errorMessage);
      
      // 阻止默认处理
      event.preventDefault();
    });
    
    // 捕获全局JavaScript错误
    window.addEventListener('error', (event) => {
      console.error('Global error:', event.error);
      
      // 显示友好的错误提示
      const errorMessage = getErrorMessage(event.error);
      showError(errorMessage);
      
      // 阻止默认处理
      event.preventDefault();
      return true;
    }, true);
  } catch (e) {
    console.error('Error setting up error handler:', e);
  }
}

// 从错误对象中提取友好的错误信息
function getErrorMessage(error: any): string {
  if (!error) return '发生未知错误';
  
  // 如果是API错误
  if (error.status && error.message) {
    return error.message;
  }
  
  // 如果是标准Error对象
  if (error.message) {
    // 过滤掉技术细节，只显示用户友好的信息
    const message = error.message;
    
    // 网络错误
    if (message.includes('Network Error')) {
      return '网络连接失败，请检查您的网络';
    }
    
    // 超时错误
    if (message.includes('timeout')) {
      return '请求超时，请稍后重试';
    }
    
    return message;
  }
  
  // 默认错误信息
  return '应用发生错误，请稍后重试';
}


