<template>
  <el-container class="main-container">
    <!-- 左侧导航栏 - 玻璃态 -->
    <el-aside width="280px" class="sidebar glass-effect">
      <div class="logo">
        <div class="logo-icon">🛡️</div>
        <h2 class="logo-text">AIGC 水印溯源</h2>
        <div class="logo-subtitle">StegaStamp V2.0</div>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
        background-color="transparent"
        text-color="rgba(255, 255, 255, 0.7)"
        active-text-color="#00d4ff"
      >
        <el-menu-item index="/embedding" class="menu-item">
          <el-icon class="menu-icon"><Document /></el-icon>
          <span class="menu-text">嵌入工作台</span>
          <div class="menu-indicator"></div>
        </el-menu-item>
        <el-menu-item index="/attack" class="menu-item">
          <el-icon class="menu-icon"><Warning /></el-icon>
          <span class="menu-text">攻击实验室</span>
          <div class="menu-indicator"></div>
        </el-menu-item>
        <el-menu-item index="/tracing" class="menu-item">
          <el-icon class="menu-icon"><Search /></el-icon>
          <span class="menu-text">智能溯源</span>
          <div class="menu-indicator"></div>
        </el-menu-item>
        <el-menu-item index="/dashboard" class="menu-item">
          <el-icon class="menu-icon"><DataAnalysis /></el-icon>
          <span class="menu-text">效能看板</span>
          <div class="menu-indicator"></div>
        </el-menu-item>
        <el-menu-item index="/history" class="menu-item">
          <el-icon class="menu-icon"><DocumentCopy /></el-icon>
          <span class="menu-text">历史记录</span>
          <div class="menu-indicator"></div>
        </el-menu-item>
      </el-menu>

      <!-- 状态指示器 -->
      <div class="status-card glass-effect">
        <div class="status-item">
          <div class="status-dot"></div>
          <span>系统运行正常</span>
        </div>
        <div class="status-divider"></div>
        <div class="status-stats">
          <div class="stat-item">
            <span class="stat-label">在线时间</span>
            <span class="stat-value">{{ formatUptime() }}</span>
          </div>
        </div>
      </div>
      
      <div class="user-info glass-effect">
        <el-dropdown @command="handleCommand" class="user-dropdown-wrapper">
          <div class="user-card">
            <div class="user-avatar">
            <el-icon><User /></el-icon>
            </div>
            <div class="user-details">
              <div class="user-name">{{ username }}</div>
              <div class="user-role">管理员</div>
            </div>
            <el-icon class="dropdown-icon"><arrow-down /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu class="glass-effect">
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-aside>

    <!-- 右侧内容区 -->
    <el-main class="main-content">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { removeToken } from '@/utils/auth'
import { Document, Warning, Search, DataAnalysis, DocumentCopy, User, ArrowDown, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const startTime = ref(Date.now())

const activeMenu = computed(() => route.path)
const username = computed(() => {
  return localStorage.getItem('username') || 'Admin'
})

const formatUptime = () => {
  const now = Date.now()
  const diff = Math.floor((now - startTime.value) / 1000)
  const hours = Math.floor(diff / 3600)
  const minutes = Math.floor((diff % 3600) / 60)
  return `${hours}h ${minutes}m`
}

const handleCommand = (command) => {
  if (command === 'logout') {
    removeToken()
    localStorage.removeItem('username')
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}

onMounted(() => {
  // 每分钟更新一次在线时间
  setInterval(() => {
    startTime.value = startTime.value
  }, 60000)
})
</script>

<style scoped>
.main-container {
  height: 100vh;
  background: transparent;
  position: relative;
}

.sidebar {
  border-right: 1px solid rgba(0, 162, 255, 0.1);
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  overflow: hidden;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, rgba(0, 102, 255, 0.05) 0%, transparent 100%);
  pointer-events: none;
}

/* Logo 区域 */
.logo {
  padding: 20px;
  text-align: center;
  margin-bottom: 30px;
  position: relative;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 12px;
  filter: drop-shadow(0 0 20px rgba(0, 162, 255, 0.5));
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 4px;
  letter-spacing: 1px;
}

.logo-subtitle {
  font-size: 11px;
  color: rgba(0, 162, 255, 0.6);
  letter-spacing: 2px;
  font-weight: 500;
  text-transform: uppercase;
}

/* 菜单样式 */
.sidebar-menu {
  border: none;
  flex: 1;
  background: transparent !important;
}

.menu-item {
  height: 52px !important;
  line-height: 52px !important;
  margin: 8px 12px !important;
  border-radius: 12px !important;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  overflow: hidden;
  background: transparent !important;
}

.menu-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.1) 0%, rgba(0, 162, 255, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.menu-item:hover::before {
  opacity: 1;
}

.menu-item:hover {
  background: rgba(0, 102, 255, 0.15) !important;
  border-left: 3px solid rgba(0, 162, 255, 0.5);
  transform: translateX(4px);
}

.menu-item.is-active {
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.25) 0%, rgba(0, 162, 255, 0.25) 100%) !important;
  border-left: 3px solid #00a2ff;
  box-shadow: 
    0 8px 24px rgba(0, 162, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.menu-icon {
  font-size: 20px;
  margin-right: 12px;
  transition: all 0.3s;
}

.menu-item:hover .menu-icon {
  transform: scale(1.1);
  color: #00d4ff;
}

.menu-item.is-active .menu-icon {
  color: #00d4ff;
  filter: drop-shadow(0 0 8px rgba(0, 212, 255, 0.6));
}

.menu-text {
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.menu-indicator {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00d4ff;
  opacity: 0;
  transition: opacity 0.3s;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.8);
}

.menu-item.is-active .menu-indicator {
  opacity: 1;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: translateY(-50%) scale(1);
  }
  50% {
    opacity: 0.6;
    transform: translateY(-50%) scale(1.2);
  }
}

/* 状态卡片 */
.status-card {
  margin: 20px 12px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(0, 162, 255, 0.2);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00ff88;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.6);
  animation: breathe 2s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

.status-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 162, 255, 0.3), transparent);
  margin: 12px 0;
}

.status-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.stat-value {
  font-size: 13px;
  font-weight: 600;
  color: #00d4ff;
  font-family: 'SF Mono', monospace;
}

/* 用户信息 */
.user-info {
  margin: 12px;
  padding: 4px;
  border-radius: 12px;
  border: 1px solid rgba(0, 162, 255, 0.2);
  margin-top: auto;
}

.user-dropdown-wrapper {
  width: 100%;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.3s;
}

.user-card:hover {
  background: rgba(0, 102, 255, 0.1);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #0066ff 0%, #00a2ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
}

.user-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.user-role {
  font-size: 11px;
  color: rgba(0, 162, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.dropdown-icon {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  transition: transform 0.3s;
}

.user-card:hover .dropdown-icon {
  transform: translateY(2px);
}

/* 主内容区 */
.main-content {
  background: transparent;
  padding: 0;
  overflow-y: auto;
  position: relative;
}

.content-wrapper {
  padding: 24px;
  min-height: 100%;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

