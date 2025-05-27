<template>
  <view class="page-container">
    <header-bar title="消息中心"></header-bar>
    
    <view class="push-container">
      <!-- 导航标签 -->
      <view class="nav-tabs">
        <view class="tab-item" :class="{ active: activeTab === 'messages' }" @click="activeTab = 'messages'">
          <text>消息列表</text>
        </view>
        <view class="tab-item" :class="{ active: activeTab === 'sources' }" @click="activeTab = 'sources'">
          <text>消息来源</text>
        </view>
        <view class="tab-item" :class="{ active: activeTab === 'subscriptions' }" @click="activeTab = 'subscriptions'">
          <text>我的订阅</text>
        </view>
      </view>
      
      <!-- 消息列表 -->
      <view v-if="activeTab === 'messages'" class="tab-content">
        <!-- 筛选区域 -->
        <view class="filter-section">
          <view class="filter-buttons">
            <view class="filter-button" :class="{ active: filter.status === 'all' }" @click="setStatusFilter('all')">全部</view>
            <view class="filter-button" :class="{ active: filter.status === 'unread' }" @click="setStatusFilter('unread')">未读</view>
            <view class="filter-button" :class="{ active: filter.status === 'read' }" @click="setStatusFilter('read')">已读</view>
          </view>
          <picker class="source-picker" :range="sourceOptions" range-key="name" :value="sourceIndex" @change="onSourceChange">
            <view class="picker-value">{{ sourceOptions[sourceIndex].name }}</view>
          </picker>
          <text class="reset-btn" @click="resetFilter">重置</text>
        </view>
        
        <!-- 消息列表 -->
        <view class="message-list">
          <view v-if="loading" class="loading">加载中...</view>
          <view v-else-if="filteredMessages.length === 0" class="empty-list">暂无消息</view>
          <view v-else v-for="message in filteredMessages" :key="message.id" class="message-item" 
                :class="{ unread: message.status === 'unread' }" @click="viewMessageDetail(message)">
            <view class="message-header">
              <text class="message-title">{{ message.title || '无标题' }}</text>
              <text class="message-time">{{ formatTime(message.created_at) }}</text>
            </view>
            <view class="message-content">
              <text class="message-preview">{{ message.content.substring(0, 100) }}{{ message.content.length > 100 ? '...' : '' }}</text>
            </view>
            <view class="message-footer">
              <text class="message-source">{{ message.source?.name || '未知来源' }}</text>
              <text v-if="message.status === 'unread'" class="action-btn" @click.stop="markAsRead(message.id)">标为已读</text>
            </view>
          </view>
        </view>
        
        <!-- 操作栏 -->
        <view class="action-bar">
          <button class="refresh-btn" @click="fetchMessages">刷新</button>
          <button v-if="hasUnreadMessages" class="mark-all-btn" @click="markAllAsRead">全部标为已读</button>
        </view>
      </view>
      
      <!-- 消息来源 -->
      <view v-else-if="activeTab === 'sources'" class="tab-content">
        <view class="sources-header">
          <text class="section-title">消息来源管理</text>
          <button class="add-btn" @click="addSource">添加来源</button>
        </view>
        
        <view v-if="loadingSources" class="loading">加载中...</view>
        <view v-else-if="sources.length === 0" class="empty-list">暂无消息来源</view>
        <view v-else class="sources-list">
          <view v-for="source in sources" :key="source.id" class="source-item" :class="{ inactive: !source.is_active }">
            <view class="source-header">
              <text class="source-name">{{ source.name }}</text>
              <view class="source-actions">
                <text class="action-btn edit" @click="editSource(source)">编辑</text>
                <text class="action-btn delete" @click="confirmDeleteSource(source.id)">删除</text>
              </view>
            </view>
            <view class="source-info">
              <text class="source-type">类型: {{ source.source_type }}</text>
              <text class="source-status" :class="{ active: source.is_active }">{{ source.is_active ? '已启用' : '已禁用' }}</text>
            </view>
          </view>
        </view>
      </view>
      
      <!-- 我的订阅 -->
      <view v-else-if="activeTab === 'subscriptions'" class="tab-content">
        <view class="section-header">
          <text class="section-title">我的订阅</text>
        </view>
        
        <view v-if="loadingSubscriptions" class="loading">加载中...</view>
        <view v-else-if="subscriptions.length === 0" class="empty-list">暂无订阅</view>
        <view v-else class="subscriptions-list">
          <view v-for="subscription in subscriptions" :key="subscription.id" class="subscription-item">
            <view class="subscription-header">
              <text class="subscription-name">{{ subscription.source?.name || '未知来源' }}</text>
              <switch :checked="subscription.is_active" @change="toggleSubscription(subscription.id, $event)" color="#409EFF" />
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 弹窗 -->
    <uni-popup ref="sourcePopup" type="center">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">{{ editingSource ? '编辑来源' : '添加来源' }}</text>
          <text class="close-btn" @click="closeSourceModal">×</text>
        </view>
        <view class="form-item">
          <text class="form-label">名称</text>
          <input class="form-input" v-model="sourceForm.name" placeholder="请输入来源名称" />
        </view>
        <view class="form-item">
          <text class="form-label">类型</text>
          <picker class="form-picker" :range="sourceTypes" :value="sourceTypeIndex" @change="onSourceTypeChange">
            <view class="picker-value">{{ sourceTypes[sourceTypeIndex] }}</view>
          </picker>
        </view>
        <view class="form-item">
          <text class="form-label">描述</text>
          <textarea class="form-textarea" v-model="sourceForm.description" placeholder="请输入来源描述" />
        </view>
        <view class="form-item">
          <text class="form-label">状态</text>
          <switch :checked="sourceForm.is_active" @change="e => sourceForm.is_active = e.detail.value" color="#409EFF" />
        </view>
        <view class="form-actions">
          <button class="cancel-btn" @click="closeSourceModal">取消</button>
          <button class="submit-btn" @click="saveSource">保存</button>
        </view>
      </view>
    </uni-popup>
    
    <uni-popup ref="deletePopup" type="dialog">
      <uni-popup-dialog type="warning" title="确认删除" content="确定要删除这个消息来源吗？此操作不可撤销。" :before-close="true" @confirm="deleteSource" @close="closeDeletePopup"></uni-popup-dialog>
    </uni-popup>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { usePushStore } from '@/store/modules/push';
import { PushNotificationsService } from '@/api';
import { showSuccess, showError } from '@/utils/message';
import HeaderBar from '@/components/common/HeaderBar.vue';

const pushStore = usePushStore();
const loading = ref(true);
const loadingSources = ref(true);
const loadingSubscriptions = ref(true);
const activeTab = ref('messages');
const sourcePopup = ref(null);
const deletePopup = ref(null);
const deletingSourceId = ref(null);

// 消息筛选
const filter = ref({ status: 'all', sourceId: null });

// 消息来源
const sources = ref([]);
const editingSource = ref(null);
const sourceForm = reactive({
  name: '',
  source_type: 'webhook',
  description: '',
  is_active: true
});

// 来源类型选项
const sourceTypes = ['webhook', 'dingtalk', 'email', 'sms', 'wechat'];
const sourceTypeIndex = ref(0);

// 订阅
const subscriptions = ref([]);

// 来源选择器
const sourceOptions = computed(() => {
  return [{ id: null, name: '全部来源' }, ...sources.value];
});
const sourceIndex = ref(0);

// 初始化数据
onMounted(() => {
  fetchMessages();
  fetchSources();
  fetchSubscriptions();
});

// 页面显示时刷新数据
onShow(() => {
  if (activeTab.value === 'messages') {
    fetchMessages();
  } else if (activeTab.value === 'sources') {
    fetchSources();
  } else if (activeTab.value === 'subscriptions') {
    fetchSubscriptions();
  }
});

// 获取消息列表
const fetchMessages = async () => {
  loading.value = true;
  try {
    await pushStore.fetchMessages();
  } catch (error) {
    console.error('获取消息列表失败:', error);
    showError('获取消息列表失败');
  } finally {
    loading.value = false;
  }
};

// 获取消息来源
const fetchSources = async () => {
  loadingSources.value = true;
  try {
    const response = await PushNotificationsService.readPushSourcesApiV1PushSourcesGet(0, 100, false);
    sources.value = response;
  } catch (error) {
    console.error('获取消息来源失败:', error);
    showError('获取消息来源失败');
  } finally {
    loadingSources.value = false;
  }
};

// 获取订阅列表
const fetchSubscriptions = async () => {
  loadingSubscriptions.value = true;
  try {
    const response = await PushNotificationsService.readUserSubscriptionsApiV1PushSubscriptionsGet(0, 100);
    subscriptions.value = response;
  } catch (error) {
    console.error('获取订阅列表失败:', error);
    showError('获取订阅列表失败');
  } finally {
    loadingSubscriptions.value = false;
  }
};

// 过滤后的消息列表
const filteredMessages = computed(() => {
  let result = [...pushStore.messages];
  if (filter.value.status !== 'all') {
    result = result.filter(msg => msg.status === filter.value.status);
  }
  if (filter.value.sourceId) {
    result = result.filter(msg => msg.source_id === filter.value.sourceId);
  }
  return result;
});

// 是否有未读消息
const hasUnreadMessages = computed(() => {
  return pushStore.messages.some(msg => msg.status === 'unread');
});

// 设置状态过滤器
const setStatusFilter = (status) => {
  filter.value.status = status;
};

// 来源选择变更
const onSourceChange = (e) => {
  sourceIndex.value = e.detail.value;
  filter.value.sourceId = sourceOptions.value[sourceIndex.value].id;
};

// 来源类型变更
const onSourceTypeChange = (e) => {
  sourceTypeIndex.value = e.detail.value;
  sourceForm.source_type = sourceTypes[sourceTypeIndex.value];
};

// 重置过滤器
const resetFilter = () => {
  filter.value.status = 'all';
  filter.value.sourceId = null;
  sourceIndex.value = 0;
};

// 标记消息为已读
const markAsRead = async (messageId) => {
  try {
    await PushNotificationsService.updateUserMessageStatusApiV1PushMessagesMessageIdStatusPut(
      messageId,
      { status: 'read' }
    );
    pushStore.updateMessageStatus(messageId, 'read');
    showSuccess('已标记为已读');
  } catch (error) {
    console.error('标记已读失败:', error);
    showError('标记已读失败');
  }
};

// 标记所有消息为已读
const markAllAsRead = async () => {
  try {
    await PushNotificationsService.markAllUserMessagesAsReadApiV1PushMessagesMarkAllReadPost();
    
    // 更新本地状态
    pushStore.messages.forEach(msg => {
      if (msg.status === 'unread') {
        pushStore.updateMessageStatus(msg.id, 'read');
      }
    });
    
    showSuccess('已将所有消息标记为已读');
  } catch (error) {
    console.error('标记全部已读失败:', error);
    showError('标记全部已读失败');
  }
};

// 查看消息详情
const viewMessageDetail = (message) => {
  uni.navigateTo({
    url: `/pages/push/detail?id=${message.id}`
  });
};

// 切换订阅状态
const toggleSubscription = async (subscriptionId, event) => {
  const isActive = event.detail.value;
  try {
    await PushNotificationsService.updateUserSubscriptionApiV1PushSubscriptionsSubscriptionIdPut(
      subscriptionId,
      { is_active: isActive }
    );
    
    // 更新本地状态
    const subscription = subscriptions.value.find(sub => sub.id === subscriptionId);
    if (subscription) {
      subscription.is_active = isActive;
    }
    
    showSuccess(isActive ? '已开启订阅' : '已关闭订阅');
  } catch (error) {
    console.error('更新订阅状态失败:', error);
    showError('更新订阅状态失败');
    
    // 恢复原状态
    fetchSubscriptions();
  }
};

// 编辑来源
const editSource = (source) => {
  editingSource.value = source;
  sourceForm.name = source.name;
  sourceForm.source_type = source.source_type;
  sourceForm.description = source.description || '';
  sourceForm.is_active = source.is_active;
  
  // 设置来源类型索引
  const typeIndex = sourceTypes.findIndex(type => type === source.source_type);
  sourceTypeIndex.value = typeIndex >= 0 ? typeIndex : 0;
  
  sourcePopup.value.open();
};

// 添加来源
const addSource = () => {
  editingSource.value = null;
  sourceForm.name = '';
  sourceForm.source_type = sourceTypes[0];
  sourceForm.description = '';
  sourceForm.is_active = true;
  sourceTypeIndex.value = 0;
  
  sourcePopup.value.open();
};

// 保存来源
const saveSource = async () => {
  try {
    if (editingSource.value) {
      // 更新来源
      const updateData = {
        name: sourceForm.name,
        source_type: sourceForm.source_type,
        description: sourceForm.description,
        is_active: sourceForm.is_active
      };
      
      await PushNotificationsService.updatePushSourceApiV1PushSourcesSourceIdPut(
        editingSource.value.id,
        updateData
      );
      
      showSuccess('更新来源成功');
    } else {
      // 创建来源
      await PushNotificationsService.createPushSourceApiV1PushSourcesPost(sourceForm);
      showSuccess('创建来源成功');
    }
    
    // 刷新来源列表
    fetchSources();
    closeSourceModal();
  } catch (error) {
    console.error('保存来源失败:', error);
    showError('保存来源失败');
  }
};

// 确认删除来源
const confirmDeleteSource = (sourceId) => {
  deletingSourceId.value = sourceId;
  deletePopup.value.open();
};

// 删除来源
const deleteSource = async () => {
  if (!deletingSourceId.value) return;
  
  try {
    await PushNotificationsService.deletePushSourceApiV1PushSourcesSourceIdDelete(
      deletingSourceId.value
    );
    
    showSuccess('删除来源成功');
    fetchSources();
  } catch (error) {
    console.error('删除来源失败:', error);
    showError('删除来源失败');
  } finally {
    closeDeletePopup();
  }
};

// 关闭来源弹窗
const closeSourceModal = () => {
  sourcePopup.value.close();
};

// 关闭删除确认弹窗
const closeDeletePopup = () => {
  deletePopup.value.close();
  deletingSourceId.value = null;
};

// 格式化时间
const formatTime = (timeStr) => {
  const date = new Date(timeStr);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
};








</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
}

.push-container {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}

/* 导航标签样式 */
.nav-tabs {
  display: flex;
  background-color: #fff;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 14px;
  color: #606266;
  position: relative;
}

.tab-item.active {
  color: #409EFF;
  font-weight: 500;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background-color: #409EFF;
  border-radius: 3px;
}

/* 筛选区域样式 */
.filter-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  background-color: #fff;
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-buttons {
  display: flex;
}

.filter-button {
  padding: 6px 12px;
  margin-right: 8px;
  font-size: 12px;
  color: #606266;
  background-color: #f0f2f5;
  border-radius: 4px;
}

.filter-button.active {
  color: #fff;
  background-color: #409EFF;
}

.source-picker {
  flex: 1;
  max-width: 120px;
  font-size: 12px;
  color: #606266;
}

.picker-value {
  padding: 6px 12px;
  background-color: #f0f2f5;
  border-radius: 4px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reset-btn {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}

/* 消息列表样式 */
.message-list {
  margin-bottom: 15px;
}

.message-item {
  background-color: #fff;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.message-item.unread {
  border-left: 3px solid #409EFF;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.message-content {
  margin-bottom: 10px;
}

.message-preview {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-source {
  font-size: 12px;
  color: #909399;
  background-color: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.action-btn {
  font-size: 12px;
  color: #409EFF;
}

/* 操作栏样式 */
.action-bar {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}

.refresh-btn, .mark-all-btn {
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 4px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  color: #606266;
}

.mark-all-btn {
  color: #409EFF;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

/* 来源管理样式 */
.sources-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.add-btn {
  padding: 6px 12px;
  font-size: 14px;
  color: #fff;
  background-color: #409EFF;
  border-radius: 4px;
  border: none;
}

.source-item {
  background-color: #fff;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.source-item.inactive {
  opacity: 0.7;
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.source-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.source-actions {
  display: flex;
}

.source-actions .action-btn {
  margin-left: 10px;
}

.action-btn.edit {
  color: #409EFF;
}

.action-btn.delete {
  color: #F56C6C;
}

.source-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.source-type {
  font-size: 12px;
  color: #909399;
  background-color: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.source-status {
  font-size: 12px;
  color: #909399;
}

.source-status.active {
  color: #67C23A;
}

/* 订阅列表样式 */
.section-header {
  margin-bottom: 15px;
}

.subscription-item {
  background-color: #fff;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.subscription-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subscription-name {
  font-size: 16px;
  color: #303133;
}

/* 弹窗样式 */
.popup-content {
  width: 300px;
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.popup-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.close-btn {
  font-size: 20px;
  color: #909399;
}

.form-item {
  margin-bottom: 15px;
}

.form-label {
  display: block;
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.form-input, .form-textarea, .form-picker {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  background-color: #fff;
}

.form-textarea {
  height: 80px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.cancel-btn, .submit-btn {
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 4px;
  margin-left: 10px;
}

.cancel-btn {
  background-color: #fff;
  border: 1px solid #dcdfe6;
  color: #606266;
}

.submit-btn {
  background-color: #409EFF;
  border: none;
  color: #fff;
}

/* 加载和空状态 */
.loading, .empty-list {
  text-align: center;
  padding: 30px 0;
  color: #909399;
  font-size: 14px;
}
</style>

