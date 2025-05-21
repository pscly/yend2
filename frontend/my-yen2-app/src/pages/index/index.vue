<template>
  <view class="index-container">
    <view class="welcome-section">
      <text class="title">欢迎使用 Yen2 应用</text>
      <text class="subtitle">这是一个简单的测试页面</text>
    </view>
    
    <view class="content-section">
      <text>如果您能看到这个内容，说明应用已经正常运行了！</text>
    </view>
    
    <button class="test-button" type="primary" @click="showTestMessage">
      测试按钮
    </button>
  </view>
</template>

<script setup lang="ts">
import { onLoad, onShow } from '@dcloudio/uni-app';
import { showSuccess } from '@/utils/message';

onLoad(() => {
  console.log('首页加载完成');
});

onShow(() => {
  console.log('首页显示');
});

const showTestMessage = () => {
  showSuccess('按钮点击成功！');
};
</script>

<style lang="scss">
.index-container {
  padding: 40rpx;
}

.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
}

.content-section {
  background-color: #fff;
  padding: 30rpx;
  border-radius: 12rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.test-button {
  width: 100%;
  margin-top: 30rpx;
}
</style>
