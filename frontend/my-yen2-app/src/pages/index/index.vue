<template>
  <view class="page-container">
    <header-bar title="首页"></header-bar>
    
    <view class="index-container">
      <view class="welcome-section">
        <text class="title">Yen2 个人导航</text>
      </view>
      
      <!-- 内容区域将根据用户登录状态显示不同内容 -->
      <view class="content-section">
        <!-- 内容将在后续实现 -->
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

.content-section {
  background-color: #fff;
  padding: 30rpx;
  border-radius: 12rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
  min-height: 300rpx;
}
</style>
