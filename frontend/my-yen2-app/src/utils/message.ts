/**
 * 消息提示工具
 * 封装uni-app的提示API，提供更友好的接口
 */

// 成功提示
export function showSuccess(message: string, duration = 2000) {
  uni.showToast({
    title: message,
    icon: 'success',
    duration
  });
}

// 错误提示
export function showError(message: string, duration = 3000) {
  uni.showToast({
    title: message,
    icon: 'none',
    duration
  });
}

// 警告提示
export function showWarning(message: string, duration = 2500) {
  uni.showToast({
    title: message,
    icon: 'none',
    duration
  });
}

// 加载提示
export function showLoading(message = '加载中...') {
  uni.showLoading({
    title: message,
    mask: true
  });
}

// 隐藏加载提示
export function hideLoading() {
  uni.hideLoading();
}

// 模态确认框
export function showConfirm(content: string, title = '提示', options = {}): Promise<boolean> {
  return new Promise((resolve) => {
    uni.showModal({
      title,
      content,
      ...options,
      success: (res) => {
        resolve(res.confirm);
      }
    });
  });
}



