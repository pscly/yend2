<template>
  <view class="login-container">
    <header-bar title="用户登录"></header-bar>
    
    <view class="login-form-container">
      <view class="login-header">
        <image class="logo" src="/static/logo.png" />
        <text class="title">用户登录</text>
      </view>
      
      <view class="login-form">
        <view class="form-item">
          <text class="label">用户名</text>
          <input 
            class="input" 
            type="text" 
            v-model="form.username" 
            placeholder="请输入用户名" 
          />
        </view>
        
        <view class="form-item">
          <text class="label">密码</text>
          <input 
            class="input" 
            type="password" 
            v-model="form.password" 
            placeholder="请输入密码" 
            password 
          />
        </view>
        
        <button 
          class="login-button" 
          type="primary" 
          :loading="loading" 
          @click="handleLogin"
        >
          登录
        </button>
        
        <view class="form-actions">
          <text class="action-link" @click="navigateTo('/pages/register/index')">注册账号</text>
          <text class="action-link" @click="navigateTo('/pages/forgot-password/index')">忘记密码</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useUserStore } from '@/store/modules/user';
import { showError, showSuccess, showLoading, hideLoading } from '@/utils/message';
import HeaderBar from '@/components/common/HeaderBar.vue';

const userStore = useUserStore();
const loading = ref(false);

const form = reactive({
  username: '',
  password: ''
});

const handleLogin = async () => {
  if (!form.username || !form.password) {
    showError('请输入用户名和密码');
    return;
  }
  
  loading.value = true;
  showLoading('登录中...');
  
  try {
    const response = await userStore.login(form.username, form.password);
    hideLoading();
    showSuccess('登录成功');
    
    console.log('登录成功，用户信息:', userStore.userInfo);
    console.log('登录状态:', userStore.isLoggedIn);
    
    // 登录成功后跳转到首页
    setTimeout(() => {
      uni.reLaunch({
        url: '/pages/index/index'
      });
    }, 1500);
  } catch (error: any) {
    hideLoading();
    console.error('登录错误详情:', error);
    
    // 处理不同类型的错误
    if (error.response) {
      if (error.response.status === 401) {
        showError('用户名或密码错误');
      } else if (error.response.status === 403) {
        showError('账号已被禁用');
      } else {
        showError(error.response.data?.detail || '登录失败，请稍后重试');
      }
    } else {
      showError(error.message || '登录失败，请稍后重试');
    }
  } finally {
    loading.value = false;
  }
};

const navigateTo = (url: string) => {
  uni.navigateTo({ url });
};
</script>

<style lang="scss">
.login-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 60rpx;
  margin-top: 60rpx;
}

.logo {
  width: 160rpx;
  height: 160rpx;
  margin-bottom: 30rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.login-form {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.form-item {
  margin-bottom: 30rpx;
}

.label {
  display: block;
  margin-bottom: 10rpx;
  font-size: 28rpx;
  color: #333;
}

.input {
  width: 100%;
  height: 80rpx;
  border: 1px solid #ddd;
  border-radius: 8rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  background-color: #f8f8f8;
}

.login-button {
  margin-top: 40rpx;
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background-color: #007aff;
  color: #fff;
  border-radius: 8rpx;
  font-size: 32rpx;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 30rpx;
}

.action-link {
  font-size: 26rpx;
  color: #007aff;
}

.login-form-container {
  padding: 40rpx;
  flex: 1;
}
</style>
