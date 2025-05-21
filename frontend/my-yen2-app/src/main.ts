import { createSSRApp } from "vue";
import App from "./App.vue";
import { createPinia } from 'pinia';

export function createApp() {
  const app = createSSRApp(App);
  
  // 添加状态管理
  const pinia = createPinia();
  app.use(pinia);
  
  // 调试信息
  console.log('App created successfully');
  
  return {
    app,
  };
}
