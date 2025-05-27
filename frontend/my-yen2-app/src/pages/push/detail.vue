<template>
  <view class="page-container">
    <header-bar title="消息详情"></header-bar>
    
    <view class="detail-container">
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      
      <view v-else-if="!message" class="error-message">
        <text>消息不存在或已被删除</text>
        <button class="back-btn" @click="goBack">返回列表</button>
      </view>
      
      <view v-else class="message-detail">
        <view class="message-header">
          <text class="message-title">{{ message.title || '无标题' }}</text>
          <text class="message-time">{{ formatTime(message.created_at) }}</text>
        </view>
        
        <view class="message-meta">
          <text class="message-source">来源: {{ message.source?.name || '未知来源' }}</text>
          <text class="message-status" :class="message.status">{{ statusText }}</text>
        </view>
        
        <view class="message-content">
          <text class="content-text">{{ message.content }}</text>
        </view>
        
        <view class="message-actions">
          <button class="action-btn" @click="goBack">返回列表</button>
          <button v-if="message.status === 'unread'" class="action-btn mark-read" @click="markAsRead">标为已读</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { usePushStore } from '@/store/modules/push';
import { PushNotificationsService } from '@/api/services/PushNotificationsService';
import { showSuccess, showError } from '@/utils/message';
import HeaderBar from '@/components/common/HeaderBar.vue';

const pushStore = usePushStore();
const loading = ref(true);
const message = ref(null);
const messageId = ref(null);

// 获取消息ID
onMounted(() => {
  const query = uni.getLaunchOptionsSync().query || {};
  const id = Number(query.id);
  
  if (id) {
    messageId.value = id;
    fetchMessageDetail(id);
  } else {
    loading.value = false;
    showError('消息ID无效');
  }
});

// 页面显示时刷新数据
onShow(() => {
  if (messageId.value) {
    fetchMessageDetail(messageId.value);
  }
});

// 获取消息详情
const fetchMessageDetail = async (id) => {
  loading.value = true;
  try {
    // 先从store中查找消息
    const cachedMessage = pushStore.messages.find(msg => msg.id === id);
    if (cachedMessage) {
      message.value = cachedMessage;
    } else {
      // 如果store中没有，则从API获取
      const response = await PushNotificationsService.readUserPushMessageApiV1PushMessagesMessageIdGet(id);
      message.value = response;
    }
    
    // 如果消息是未读状态，自动标记为已读
    if (message.value && message.value.status === 'unread') {
      await markAsRead();
    }
  } catch (error) {
    console.error('获取消息详情失败:', error);
    showError('获取消息详情失败');
    message.value = null;
  } finally {
    loading.value = false;
  }
};

// 标记消息为已读
const markAsRead = async () => {
  if (!message.value || message.value.status !== 'unread') return;
  
  try {
    await PushNotificationsService.updateUserPushMessageApiV1PushMessagesMessageIdPut(
      message.value.id,
      { status: 'read' }
    );
    message.value.status = 'read';
    pushStore.updateMessageStatus(message.value.id, 'read');
    showSuccess('已标记为已读');
  } catch (error) {
    console.error('标记已读失败:', error);
  }
};

// 返回列表页
const goBack = () => {
  uni.navigateBack();
};

// 格式化时间
const formatTime = (timeStr) => {
  const date = new Date(timeStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

// 状态文本
const statusText = computed(() => {
  if (!message.value) return '';
  
  switch (message.value.status) {
    case 'read': return '已读';
    case 'unread': return '未读';
    default: return message.value.status;
  }
});
</script>

<style lang="scss">
.detail-container {
  padding: 30rpx;
  margin-top: 100rpx;
}

.loading, .error-message {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 400rpx;
  color: #999;
  font-size: 28rpx;
}

.back-btn {
  margin-top: 30rpx;
  width: 200rpx;
  height: 70rpx;
  line-height: 70rpx;
  background-color: #409EFF;
  color: #fff;
  font-size: 28rpx;
  border-radius: 35rpx;
}

.message-detail {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 30rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.1);
}

.message-header {
  margin-bottom: 20rpx;
}

.message-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 10rpx;
}

.message-time {
  font-size: 24rpx;
  color: #999;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 1px solid #eee;
}

.message-source {
  font-size: 26rpx;
  color: #666;
}

.message-status {
  font-size: 24rpx;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
}

.message-status.read {
  background-color: #f0f0f0;
  color: #999;
}

.message-status.unread {
  background-color: #ecf5ff;
  color: #409EFF;
}

.message-content {
  padding: 20rpx 0;
  min-height: 200rpx;
}

.content-text {
  font-size: 30rpx;
  color: #333;
  line-height: 1.6;
}

.message-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 40rpx;
}

.action-btn {
  margin-left: 20rpx;
  width: 180rpx;
  height: 70rpx;
  line-height: 70rpx;
  font-size: 28rpx;
  border-radius: 35rpx;
  background-color: #f0f0f0;
  color: #666;
}

.mark-read {
  background-color: #409EFF;
  color: #fff;
}
</style>