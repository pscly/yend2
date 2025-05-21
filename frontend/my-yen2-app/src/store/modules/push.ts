import { defineStore } from 'pinia';
import { PushNotificationsService } from '@/api';
import { showError } from '@/utils/message';

// 推送消息类型定义
export interface PushMessage {
  id: number;
  title: string;
  content: string;
  source_id: number;
  source_name: string;
  created_at: string;
  status: 'read' | 'unread';
}

// 推送来源类型定义
export interface PushSource {
  id: number;
  name: string;
  description: string;
  active: boolean;
}

interface PushState {
  messages: PushMessage[];
  sources: PushSource[];
  loading: boolean;
  currentFilter: {
    sourceId: number | null;
    status: string | null;
    unreadOnly: boolean;
  };
}

export const usePushStore = defineStore('push', {
  state: (): PushState => ({
    messages: [],
    sources: [],
    loading: false,
    currentFilter: {
      sourceId: null,
      status: null,
      unreadOnly: false
    }
  }),
  
  getters: {
    unreadCount: (state) => state.messages.filter(msg => msg.status === 'unread').length,
    
    filteredMessages: (state) => {
      return state.messages.filter(msg => {
        // 按来源筛选
        if (state.currentFilter.sourceId !== null && msg.source_id !== state.currentFilter.sourceId) {
          return false;
        }
        
        // 按状态筛选
        if (state.currentFilter.status !== null && msg.status !== state.currentFilter.status) {
          return false;
        }
        
        // 仅显示未读
        if (state.currentFilter.unreadOnly && msg.status !== 'unread') {
          return false;
        }
        
        return true;
      });
    }
  },
  
  actions: {
    // 获取推送消息列表
    async fetchMessages() {
      this.loading = true;
      try {
        const { sourceId, status, unreadOnly } = this.currentFilter;
        const messages = await PushNotificationsService.readUserPushMessagesApiV1PushMessagesGet(
          0, 50, sourceId, status, unreadOnly
        );
        this.messages = messages;
      } catch (error) {
        console.error('获取推送消息失败:', error);
        showError('获取推送消息失败');
      } finally {
        this.loading = false;
      }
    },
    
    // 获取推送来源列表
    async fetchSources() {
      try {
        const sources = await PushNotificationsService.readPushSourcesApiV1PushSourcesGet(0, 100, true);
        this.sources = sources;
      } catch (error) {
        console.error('获取推送来源失败:', error);
        showError('获取推送来源失败');
      }
    },
    
    // 标记消息为已读
    async markAsRead(messageId: number) {
      try {
        await PushNotificationsService.updateUserMessageStatusApiV1PushMessagesMessageIdStatusPut(
          messageId,
          { status: 'read' }
        );
        
        // 更新本地状态
        const message = this.messages.find(msg => msg.id === messageId);
        if (message) {
          message.status = 'read';
        }
      } catch (error) {
        console.error('标记消息已读失败:', error);
        showError('标记消息已读失败');
      }
    },
    
    // 标记所有消息为已读
    async markAllAsRead(sourceId?: number) {
      try {
        await PushNotificationsService.markAllUserMessagesAsReadApiV1PushMessagesMarkAllReadPost(sourceId || null);
        
        // 更新本地状态
        if (sourceId) {
          this.messages.forEach(msg => {
            if (msg.source_id === sourceId) {
              msg.status = 'read';
            }
          });
        } else {
          this.messages.forEach(msg => {
            msg.status = 'read';
          });
        }
      } catch (error) {
        console.error('标记全部已读失败:', error);
        showError('标记全部已读失败');
      }
    },
    
    // 设置筛选条件
    setFilter(filter: Partial<PushState['currentFilter']>) {
      this.currentFilter = { ...this.currentFilter, ...filter };
      this.fetchMessages();
    },
    
    // 重置筛选条件
    resetFilter() {
      this.currentFilter = {
        sourceId: null,
        status: null,
        unreadOnly: false
      };
      this.fetchMessages();
    }
  }
});