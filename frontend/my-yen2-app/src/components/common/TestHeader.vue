<template>
  <view class="test-header">
    <text class="test-title">测试导航栏</text>
  </view>
</template>

<script setup>
// 简单的测试组件
</script>

<style>
.test-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100rpx;
  background-color: #ff0000;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.test-title {
  color: white;
  font-size: 36rpx;
  font-weight: bold;
}
</style>