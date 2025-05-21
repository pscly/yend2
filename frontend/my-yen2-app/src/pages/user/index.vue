<template>
  <view class="user-container">
    <view v-if="userStore.isLoggedIn" class="user-info">
      <view class="avatar-wrapper">
        <image class="avatar" src="/static/images/default-avatar.png" />
      </view>
      <view class="info-content">
        <text class="username">{{ userStore.userInfo?.username || '用户名' }}</text>
        <text class="email">{{ userStore.userInfo?.email || 'email@example.com' }}</text>
      </view>
    </view>
    
    <view v-else class="not-logged-in">
      <text class="tip">您尚未登录</text>
      <button class="login-btn" @click="goToLogin">去登录</button>
    </view>
    
    <view class="menu-list">
      <view class="menu-item" @click="navigateTo('/pages/settings/index')">
        <text class="menu-text">设置</text>
        <text class="arrow">></text>
      </view>
      
      <view class="menu-item" @click="navigateTo('/pages/about/index')">
        <text class="menu-text">关于我们</text>
        <text class="arrow">></text>
      </view>
      
      <view v-if="userStore.isLoggedIn" class="menu-item logout" @click="handleLogout">
        <text class="menu-text">退出登录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app';
import { useUserStore } from '@/store/modules/user';
import { showError, showSuccess, showConfirm, showLoading, hideLoading } from '@/utils/message';

const userStore = useUserStore();

onShow(() => {
  // 页面显示时，如果已登录但没有用户信息，则获取用户信息
  if (userStore.isLoggedIn && !userStore.userInfo) {
    getUserInfo();
  }
});

const getUserInfo = async () => {
  showLoading('加载中...');
  try {
    await userStore.getUserInfo();
    hideLoading();
  } catch (error: any) {
    hideLoading();
    showError(error.message || '获取用户信息失败');
  }
};

const goToLogin = () => {
  uni.navigateTo({
    url: '/pages/login/index'
  });
};

const navigateTo = (url: string) => {
  uni.navigateTo({ url });
};

const handleLogout = async () => {
  const confirmed = await showConfirm('确定要退出登录吗？');
  if (confirmed) {
    userStore.logout();
    showSuccess('已退出登录');
  }
};
</script>

<style lang="scss">
.user-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 40rpx;
  background-color: #fff;
  margin-bottom: 20rpx;
}

.avatar-wrapper {
  margin-right: 30rpx;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 60rpx;
}

.info-content {
  display: flex;
  flex-direction: column;
}

.username {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.email {
  font-size: 24rpx;
  color: #909399;
}

.not-logged-in {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60rpx 40rpx;
  background-color: #fff;
  margin-bottom: 20rpx;
}

.tip {
  font-size: 30rpx;
  color: #909399;
  margin-bottom: 30rpx;
}

.login-btn {
  width: 200rpx;
  height: 70rpx;
  line-height: 70rpx;
  background-color: #409eff;
  color: #fff;
  font-size: 28rpx;
  border-radius: 35rpx;
}

.menu-list {
  background-color: #fff;
  margin-top: 20rpx;
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 40rpx;
  border-bottom: 1px solid #ebeef5;
}

.menu-text {
  font-size: 28rpx;
  color: #303133;
}

.arrow {
  font-size: 28rpx;
  color: #c0c4cc;
}

.logout {
  margin-top: 30rpx;
  border-top: 10rpx solid #f5f7fa;
}

.logout .menu-text {
  color: #f56c6c;
}
</style>
