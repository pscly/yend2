<template>
  <view class="page-container">
    <header-bar title="消息中心"></header-bar>
    
    <view class="push-container">
      <view class="filter-section">
        <view class="filter-header">
          <text class="filter-title">消息筛选</text>
          <text class="reset-btn" @click="resetFilter">重置</text>
        </view>
        
        <view class="filter-options">
          <view class="filter-item">
            <text class="filter-label">来源：</text>
            <picker 
              :range="sourceOptions" 
              range-key="name"
              :value="selectedSourceIndex"
              @change="onSourceChange"
            >
              <view class="picker-value">
                {{ selectedSourceName || '全部来源' }}
              </view>
            </picker>
          </view>
          
          <view class="filter-item">
            <text class="filter-label">状态：</text>
            <picker 
              :range="statusOptions" 
              range-key="name"
              :value="selectedStatusIndex"
              @change="onStatusChange"
            >
              <view class="picker-value">
                {{ selectedStatusName || '全部状态' }}
              </view>
            </picker>
          </view>
          
          <view class="filter-item checkbox">
            <checkbox 
              :checked="pushStore.currentFilter.unreadOnly" 
              @click="toggleUnreadOnly"
              color="#007aff"
            />
            <text class="checkbox-label">仅显示未读</text>
          </view>
        </view>
      </view>
      
      <view class="message-list">
        <view class="list-header">
          <text class="list-title">消息列表</text>
          <text class="mark-all-btn" @click="markAllAsRead">全部标为已读</text>
        </view>
        
        <view v-if="pushStore.loading" class="loading">
          <text>加载中...</text>
        </view>
        
        <view v-else-if="pushStore.filteredMessages.length === 0" class="empty-list">
          <text>暂无消息</text>
        </view>
        
        <view v-else class="messages">
          <view 
            v-for="message in pushStore.filteredMessages" 
            :key="message.id"
            class="message-item"
            :class="{ unread: message.status === 'unread' }"
            @click="viewMessageDetail(message)"
          >
            <view class="message-header">
              <text class="message-title">{{ message.title }}</text>
              <text class="message-time">{{ formatTime(message.created_at) }}</text>
            </view>
            
            <view class="message-content">
              <text class="message-text">{{ truncateContent(message.content) }}</text>
            </view>
            
            <view class="message-footer">
              <text class="message-source">来源: {{ message.source_name }}</text>
              <view class="message-actions">
                <text 
                  v-if="message.status === 'unread'"
                  class="action-btn read-btn"
                  @click.stop="markAsRead(message.id)"
                >
                  标为已读
                </text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { usePushStore, type PushMessage } from '@/store/modules/push';
import { useUserStore } from '@/store/modules/user';
import { showSuccess } from '@/utils/message';
import HeaderBar from '@/components/common/HeaderBar.vue';

const pushStore = usePushStore();
const userStore = useUserStore();

// 来源选项
const sourceOptions = computed(() => {
  return [
    { id: null, name: '全部来源' },
    ...pushStore.sources
  ];
});

// 状态选项
const statusOptions = [
  { value: null, name: '全部状态' },
  { value: 'unread', name: '未读' },
  { value: 'read', name: '已读' }
];

// 选中的来源索引
const selectedSourceIndex = computed(() => {
  const index = sourceOptions.value.findIndex(
    source => source.id === pushStore.currentFilter.sourceId
  );
  return index >= 0 ? index : 0;
});

// 选中的来源名称
const selectedSourceName = computed(() => {
  const source = sourceOptions.value.find(
    source => source.id === pushStore.currentFilter.sourceId
  );
  return source ? source.name : null;
});

// 选中的状态索引
const selectedStatusIndex = computed(() => {
  const index = statusOptions.findIndex(
    status => status.value === pushStore.currentFilter.status
  );
  return index >= 0 ? index : 0;
});

// 选中的状态名称
const selectedStatusName = computed(() => {
  const status = statusOptions.find(
    status => status.value === pushStore.currentFilter.status
  );
  return status ? status.name : null;
});

// 来源变更
const onSourceChange = (e: any) => {
  const index = e.detail.value;
  const sourceId = sourceOptions.value[index].id;
  pushStore.setFilter({ sourceId });
};

// 状态变更
const onStatusChange = (e: any) => {
  const index = e.detail.value;
  const status = statusOptions[index].value;
  pushStore.setFilter({ status });
};

// 切换仅显示未读
const toggleUnreadOnly = () => {
  pushStore.setFilter({ unreadOnly: !pushStore.currentFilter.unreadOnly });
};

// 重置筛选
const resetFilter = () => {
  pushStore.resetFilter();
};

// 标记为已读
const markAsRead = (messageId: number) => {
  pushStore.markAsRead(messageId);
  showSuccess('已标记为已读');
};

// 全部标为已读
const markAllAsRead = () => {
  pushStore.markAllAsRead(pushStore.currentFilter.sourceId || undefined);
  showSuccess('已全部标记为已读');
};

// 查看消息详情
const viewMessageDetail = (message: PushMessage) => {
  // 如果是未读消息，标记为已读
  if (message.status === 'unread') {
    pushStore.markAsRead(message.id);
  }
  
  // 跳转到详情页
  uni.navigateTo({
    url: `/pages/push/detail?id=${message.id}`
  });
};

// 格式化时间
const formatTime = (timeStr: string) => {
  const date = new Date(timeStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 截断内容
const truncateContent = (content: string, maxLength = 50) => {
  if (content.length <= maxLength) return content;
  return content.substring(0, maxLength) + '...';
};

onMounted(() => {
  // 如果用户已登录，获取推送来源和消息
  if (userStore.isLoggedIn) {
    pushStore.fetchSources();
    pushStore.fetchMessages();
  }
});

onShow(() => {
  // 页面显示时，如果用户已登录，刷新消息列表
  if (userStore.isLoggedIn) {
    pushStore.fetchMessages();
  }
});
</script>

<style lang="scss">
.push-container {
  padding: 30rpx;
}

.filter-section {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.filter-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.reset-btn {
  font-size: 28rpx;
  color: #007aff;
}

.filter-options {
  display: flex;
  flex-direction: column;
}

.filter-item {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.filter-label {
  width: 120rpx;
  font-size: 28rpx;
  color: #666;
}

.picker-value {
  flex: 1;
  height: 70rpx;
  line-height: 70rpx;
  padding: 0 20rpx;
  background-color: #f5f7fa;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #333;
}

.checkbox {
  display: flex;
  align-items: center;
}

.checkbox-label {
  margin-left: 10rpx;
  font-size: 28rpx;
  color: #666;
}

.message-list {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.list-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.mark-all-btn {
  font-size: 28rpx;
  color: #007aff;
}

.loading, .empty-list {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200rpx;
  color: #999;
  font-size: 28rpx;
}

.message-item {
  padding: 30rpx;
  border-bottom: 1px solid #eee;
  position: relative;
}

.message-item.unread::before {
  content: '';
  position: absolute;
  top: 30rpx;
  left: 10rpx;
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  background-color: #f56c6c;
}

.message-item:last-child {
  border-bottom: none;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.message-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.message-time {
  font-size: 24rpx;
  color: #999;
}

.message-content {
  margin-bottom: 20rpx;
}

.message-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-source {
  font-size: 24rpx;
  color: #999;
}

.message-actions {
  display: flex;
}

.action-btn {
  font-size: 24rpx;
  color: #007aff;
  margin-left: 20rpx;
}

.page-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>












