<template>
  <el-config-provider :locale="locale">
    <div class="app-container">
      <div class="tech-bg"></div>
      <div class="grid-overlay"></div>
      <router-view />
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref } from 'vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const locale = ref(zhCn)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #000;
  color: #e5e5eb;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
  position: relative;
}

.app-container {
  min-height: 100vh;
  position: relative;
}

/* 科技感背景 */
.tech-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(ellipse at top, rgba(13, 47, 93, 0.4) 0%, transparent 50%),
    radial-gradient(ellipse at bottom, rgba(6, 24, 68, 0.4) 0%, transparent 50%),
    linear-gradient(180deg, #000814 0%, #001233 50%, #000814 100%);
  z-index: -2;
}

/* 网格叠加层 */
.grid-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(0, 162, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 162, 255, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  z-index: -1;
  animation: gridMove 20s linear infinite;
}

@keyframes gridMove {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 18, 51, 0.5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #0066ff 0%, #00a2ff 100%);
  border-radius: 4px;
  transition: all 0.3s;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #0080ff 0%, #00b8ff 100%);
}

/* 玻璃态效果通用类 */
.glass-effect {
  background: rgba(13, 27, 62, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 162, 255, 0.2);
  box-shadow: 
    0 8px 32px 0 rgba(0, 102, 255, 0.15),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
}

/* 发光效果 */
.glow-effect {
  box-shadow: 
    0 0 20px rgba(0, 162, 255, 0.3),
    0 0 40px rgba(0, 162, 255, 0.2),
    inset 0 0 20px rgba(0, 162, 255, 0.1);
}

/* 悬浮卡片效果 */
.hover-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.hover-card:hover {
  transform: translateY(-4px);
  box-shadow: 
    0 12px 48px 0 rgba(0, 102, 255, 0.25),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.08);
  border-color: rgba(0, 162, 255, 0.4);
}

/* Element Plus 组件样式覆盖 */
.el-card {
  background: rgba(13, 27, 62, 0.6) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 162, 255, 0.2) !important;
  transition: all 0.3s;
}

.el-card:hover {
  border-color: rgba(0, 162, 255, 0.4) !important;
  box-shadow: 0 8px 32px 0 rgba(0, 102, 255, 0.2) !important;
}

.el-button--primary {
  background: linear-gradient(135deg, #0066ff 0%, #00a2ff 100%) !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3) !important;
  transition: all 0.3s !important;
}

.el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 162, 255, 0.4) !important;
}

.el-input__wrapper {
  background: rgba(0, 18, 51, 0.5) !important;
  border: 1px solid rgba(0, 162, 255, 0.2) !important;
  backdrop-filter: blur(10px);
  box-shadow: none !important;
  transition: all 0.3s !important;
}

.el-input__wrapper:hover {
  border-color: rgba(0, 162, 255, 0.4) !important;
}

.el-input__wrapper.is-focus {
  border-color: #00a2ff !important;
  box-shadow: 0 0 15px rgba(0, 162, 255, 0.3) !important;
}

/* 数据面板标题样式 */
.panel-title {
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #00a2ff 0%, #0066ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(0, 162, 255, 0.5);
}

/* 数据统计数字样式 */
.stat-number {
  font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

/* 动画关键帧 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in-up {
  animation: fadeInUp 0.6s ease-out;
}
</style>

