<template>
  <view class="container">
    <!-- 应用内容将由路由自动加载 -->
  </view>
</template>

<script setup lang="ts">
import { onLaunch, onShow, onHide } from "@dcloudio/uni-app";
import { setupAPI } from '@/utils/api-config';
import { useUserStore } from '@/store/modules/user';
import { showError } from '@/utils/message';
import { setupRouterGuard } from '@/utils/router-guard';

// 初始化API配置
setupAPI();

// 初始化路由守卫
setupRouterGuard();

// 获取用户状态管理
const userStore = useUserStore();

onLaunch(() => {
  console.log("App Launch");
  
  // 如果已登录，获取用户信息
  if (userStore.isLoggedIn) {
    userStore.getUserInfo().catch(error => {
      console.error('获取用户信息失败:', error);
      showError('登录状态已过期，请重新登录');
      // 如果获取用户信息失败，可能是token过期，清除登录状态
      userStore.logout();
    });
  }
});

onShow(() => {
  console.log("App Show");
});

onHide(() => {
  console.log("App Hide");
});
</script>

<style>
/* 全局样式 */
page {
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica,
    Segoe UI, Arial, Roboto, 'PingFang SC', 'miui', 'Hiragino Sans GB', 'Microsoft Yahei',
    sans-serif;
  font-size: 28rpx;
  line-height: 1.5;
  color: #333;
  background-color: #f5f7fa;
}

.container {
  min-height: 100vh;
}
</style>
