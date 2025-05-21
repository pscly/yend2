<template>
  <view class="page-container">
    <header-bar title="首页"></header-bar>
    
    <view class="index-container">
      <view class="welcome-section">
        <text class="title">Yen2 个人导航</text>
      </view>
      
      <!-- 添加登录入口 -->
      <view class="login-section" v-if="!userStore.isLoggedIn">
        <button class="login-btn" @click="goToLogin">登录/注册</button>
      </view>
      
      <!-- 内容区域将根据用户登录状态显示不同内容 -->
      <view class="content-section">
        <view v-if="userStore.isLoggedIn" class="logged-in-content">
          <text class="welcome-text">欢迎回来，{{ userStore.userInfo?.username || '用户' }}</text>
          <view class="quick-links">
            <view class="link-item" @click="navigateTo('/pages/push/index')">
              <text class="link-text">消息中心</text>
            </view>
            <view class="link-item" @click="navigateTo('/pages/user/index')">
              <text class="link-text">个人中心</text>
            </view>
          </view>
        </view>
        <view v-else class="guest-content">
          <text class="guest-text">请登录后查看更多内容</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onLoad, onShow } from '@dcloudio/uni-app';
import { useUserStore } from '@/store/modules/user';
import HeaderBar from '@/components/common/HeaderBar.vue';

const userStore = useUserStore();

onLoad(() => {
  console.log('首页加载完成');
});

onShow(() => {
  console.log('首页显示');
});

// 跳转到登录页面
const goToLogin = () => {
  uni.navigateTo({
    url: '/pages/login/index'
  });
};

// 导航到指定页面
const navigateTo = (url: string) => {
  // 由于删除了 tabBar，所有页面都使用 navigateTo
  uni.navigateTo({ url });
};
</script>

<style lang="scss">
.page-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.index-container {
  flex: 1;
  padding: 40rpx;
}

.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 40rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.login-section {
  display: flex;
  justify-content: center;
  margin-bottom: 40rpx;
}

.login-btn {
  width: 300rpx;
  height: 80rpx;
  line-height: 80rpx;
  background-color: #409EFF;
  color: #fff;
  font-size: 30rpx;
  border-radius: 40rpx;
}

.content-section {
  background-color: #fff;
  padding: 30rpx;
  border-radius: 12rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
  min-height: 300rpx;
}

.logged-in-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.welcome-text {
  font-size: 32rpx;
  color: #333;
  margin-bottom: 30rpx;
}

.quick-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;
}

.link-item {
  width: 200rpx;
  height: 100rpx;
  background-color: #f5f7fa;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20rpx;
}

.link-text {
  font-size: 28rpx;
  color: #333;
}

.guest-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200rpx;
}

.guest-text {
  font-size: 30rpx;
  color: #909399;
}
</style>
