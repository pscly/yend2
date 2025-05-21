<template>
  <view class="header-bar">
    <view class="header-left">
      <text class="page-title">{{ title }}</text>
    </view>
    
    <!-- 导航菜单 -->
    <view class="nav-menu">
      <view 
        v-for="(item, index) in navItems" 
        :key="index" 
        class="nav-item"
        :class="{ active: currentPath === item.path }"
        @click="navigateTo(item.path)"
      >
        <text class="nav-text">{{ item.text }}</text>
      </view>
    </view>
    
    <view class="header-right" v-if="userStore.isLoggedIn">
      <view class="user-info" @click="toggleDropdown">
        <text class="username">{{ userStore.userInfo?.username || '用户' }}</text>
        <view class="avatar-wrapper">
          <image class="avatar" :src="userStore.userInfo?.avatar || '/static/images/default-avatar.png'" />
        </view>
      </view>
      
      <!-- 下拉菜单 -->
      <view class="dropdown-menu" v-if="showDropdown">
        <view class="dropdown-item" @click="navigateTo('/pages/user/index')">
          <text class="dropdown-text">个人主页</text>
        </view>
        <view class="dropdown-item" @click="navigateTo('/pages/settings/index')">
          <text class="dropdown-text">设置</text>
        </view>
        <view class="dropdown-item logout" @click="handleLogout">
          <text class="dropdown-text">注销</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useUserStore } from '@/store/modules/user';
import { showSuccess, showConfirm } from '@/utils/message';

const props = defineProps({
  title: {
    type: String,
    default: '首页'
  }
});

const userStore = useUserStore();
const showDropdown = ref(false);
const currentPath = ref('');

// 根据登录状态显示不同的导航项
const navItems = computed(() => {
  const baseItems = [
    { text: '首页', path: '/pages/index/index' }
  ];
  
  if (userStore.isLoggedIn) {
    return [
      ...baseItems,
      { text: '消息中心', path: '/pages/push/index' },
      // 可以添加更多需要登录的页面
    ];
  }
  
  return baseItems;
});

// 获取当前页面路径
onMounted(() => {
  const pages = getCurrentPages();
  if (pages.length > 0) {
    const currentPage = pages[pages.length - 1];
    currentPath.value = `/${currentPage.route}`;
  }
});

// 切换下拉菜单显示状态
const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

// 导航到指定页面
const navigateTo = (url: string) => {
  showDropdown.value = false;
  
  // 判断是否是 tabBar 页面
  const tabBarPages = ['/pages/index/index', '/pages/user/index'];
  if (tabBarPages.includes(url)) {
    uni.switchTab({ url });
  } else {
    uni.navigateTo({ url });
  }
};

// 处理登出操作
const handleLogout = async () => {
  const confirmed = await showConfirm('确定要退出登录吗？');
  if (confirmed) {
    userStore.logout();
    showSuccess('已退出登录');
    
    // 返回登录页面
    uni.reLaunch({
      url: '/pages/login/index'
    });
  }
  showDropdown.value = false;
};

// 点击页面其他区域关闭下拉菜单
uni.onTouchStart(() => {
  if (showDropdown.value) {
    showDropdown.value = false;
  }
});
</script>

<style lang="scss">
.header-bar {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100rpx;
  padding: 0 30rpx;
  background-color: #fff;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.nav-menu {
  display: flex;
  align-items: center;
  height: 100%;
}

.nav-item {
  padding: 0 20rpx;
  height: 100%;
  display: flex;
  align-items: center;
  position: relative;
  cursor: pointer;
}

.nav-item.active {
  color: #409EFF;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20rpx;
  right: 20rpx;
  height: 4rpx;
  background-color: #409EFF;
}

.nav-text {
  font-size: 28rpx;
}

.header-right {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-right: 20rpx;
  font-size: 28rpx;
  color: #333;
}

.avatar-wrapper {
  width: 70rpx;
  height: 70rpx;
  border-radius: 50%;
  overflow: hidden;
  background-color: #f0f0f0;
}

.avatar {
  width: 100%;
  height: 100%;
}

.dropdown-menu {
  position: absolute;
  top: 100rpx;
  right: 0;
  width: 240rpx;
  background-color: #fff;
  border-radius: 8rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.15);
  z-index: 101;
}

.dropdown-item {
  padding: 24rpx 30rpx;
  border-bottom: 1px solid #f0f0f0;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-text {
  font-size: 28rpx;
  color: #333;
}

.logout .dropdown-text {
  color: #f56c6c;
}
</style>
