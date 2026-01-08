<template>
  <div class="login-container">
    <!-- 装饰性粒子背景 -->
    <div class="particles"></div>
    <div class="glow-orb orb-1"></div>
    <div class="glow-orb orb-2"></div>
    
    <div class="login-card glass-effect">
      <div class="card-header">
        <div class="logo-section">
          <div class="logo-icon">🛡️</div>
          <h1 class="system-title">AIGC 水印溯源系统</h1>
          <div class="system-subtitle">STEGASTAMP INTELLIGENCE PLATFORM</div>
          <div class="version-badge">V2.0 QUANTUM</div>
        </div>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
      >
        <el-form-item prop="username" class="form-item">
          <div class="input-label">
            <el-icon><User /></el-icon>
            <span>用户名</span>
          </div>
          <el-input
            v-model="loginForm.username"
            placeholder="Enter username"
            size="large"
            class="custom-input"
          >
            <template #prefix>
              <el-icon class="input-icon"><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password" class="form-item">
          <div class="input-label">
            <el-icon><Lock /></el-icon>
            <span>密码</span>
          </div>
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Enter password"
            size="large"
            class="custom-input"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon class="input-icon"><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item class="form-item">
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            <span v-if="!loading">访问系统</span>
            <span v-else>验证中...</span>
          </el-button>
        </el-form-item>

        <div class="divider">
          <span class="divider-text">OR</span>
        </div>

        <el-form-item class="form-item">
          <el-button
            size="large"
            @click="showRegister = true"
            class="register-button"
          >
            创建新账户
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 状态指示器 -->
      <div class="status-bar">
        <div class="status-item">
          <div class="status-dot"></div>
          <span>系统在线</span>
        </div>
        <div class="status-divider">|</div>
        <div class="status-item">
          <el-icon><Lock /></el-icon>
          <span>安全连接</span>
        </div>
      </div>
    </div>

    <!-- 注册对话框 -->
    <el-dialog
      v-model="showRegister"
      title="创建新账户"
      width="450px"
      class="register-dialog"
    >
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            size="large"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱（可选）"
            size="large"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegister = false" size="large">取消</el-button>
        <el-button
          type="primary"
          :loading="registerLoading"
          @click="handleRegister"
          size="large"
        >
          注册
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { setToken } from '@/utils/auth'
import request from '@/utils/request'

const router = useRouter()

const loginFormRef = ref(null)
const registerFormRef = ref(null)
const loading = ref(false)
const registerLoading = ref(false)
const showRegister = ref(false)

const loginForm = reactive({
  username: 'admin',
  password: 'admin123'
})

const registerForm = reactive({
  username: '',
  password: '',
  email: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const formData = new FormData()
        formData.append('username', loginForm.username)
        formData.append('password', loginForm.password)
        
        console.log('开始登录...')
        const response = await request({
          url: '/login',
          method: 'post',
          data: formData,
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        console.log('登录响应:', response)
        
        if (response.access_token) {
          setToken(response.access_token)
          localStorage.setItem('username', loginForm.username)
          ElMessage.success('登录成功')
          console.log('准备跳转到主页...')
          
          // 使用 setTimeout 确保 token 已保存
          setTimeout(() => {
            router.push('/').then(() => {
              console.log('跳转成功')
            }).catch(err => {
              console.error('路由跳转失败:', err)
            })
          }, 100)
        } else {
          ElMessage.error('登录响应格式错误')
          console.error('响应缺少 access_token:', response)
        }
      } catch (error) {
        console.error('登录失败:', error)
        ElMessage.error('登录失败: ' + (error.message || '未知错误'))
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      registerLoading.value = true
      try {
        await request.post('/register', registerForm)
        ElMessage.success('注册成功，请登录')
        showRegister.value = false
        registerForm.username = ''
        registerForm.password = ''
        registerForm.email = ''
      } catch (error) {
        console.error('注册失败:', error)
      } finally {
        registerLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  padding: 20px;
}

/* 粒子背景效果 */
.particles {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(2px 2px at 20% 30%, rgba(0, 162, 255, 0.3), transparent),
    radial-gradient(2px 2px at 60% 70%, rgba(0, 212, 255, 0.3), transparent),
    radial-gradient(2px 2px at 50% 50%, rgba(0, 102, 255, 0.3), transparent),
    radial-gradient(2px 2px at 80% 10%, rgba(0, 162, 255, 0.3), transparent),
    radial-gradient(2px 2px at 10% 80%, rgba(0, 212, 255, 0.3), transparent);
  background-size: 200% 200%;
  animation: particlesMove 20s ease infinite;
}

@keyframes particlesMove {
  0%, 100% {
    background-position: 0% 0%, 100% 100%, 50% 50%, 100% 0%, 0% 100%;
  }
  50% {
    background-position: 100% 100%, 0% 0%, 25% 75%, 0% 100%, 100% 0%;
  }
}

/* 发光球体装饰 */
.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: float 8s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(0, 102, 255, 0.6) 0%, transparent 70%);
  top: -100px;
  left: -100px;
}

.orb-2 {
  width: 350px;
  height: 350px;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.5) 0%, transparent 70%);
  bottom: -100px;
  right: -100px;
  animation-delay: -4s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

/* 登录卡片 */
.login-card {
  width: 480px;
  max-width: 100%;
  padding: 48px 40px;
  border-radius: 24px;
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.6s ease-out;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 100px rgba(0, 162, 255, 0.1);
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00a2ff, transparent);
}

/* Logo 区域 */
.card-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 64px;
  margin-bottom: 8px;
  filter: drop-shadow(0 0 30px rgba(0, 162, 255, 0.6));
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.system-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
  margin: 0;
  text-shadow: 0 0 50px rgba(0, 162, 255, 0.3);
}

.system-subtitle {
  font-size: 11px;
  color: rgba(0, 162, 255, 0.7);
  letter-spacing: 3px;
  font-weight: 600;
  text-transform: uppercase;
  margin-top: 4px;
}

.version-badge {
  display: inline-block;
  padding: 4px 16px;
  background: linear-gradient(135deg, rgba(0, 102, 255, 0.2) 0%, rgba(0, 162, 255, 0.2) 100%);
  border: 1px solid rgba(0, 162, 255, 0.3);
  border-radius: 20px;
  font-size: 10px;
  color: #00d4ff;
  letter-spacing: 2px;
  font-weight: 600;
  text-transform: uppercase;
  margin-top: 12px;
  box-shadow: 0 0 20px rgba(0, 162, 255, 0.2);
}

/* 表单样式 */
.login-form {
  margin-top: 32px;
}

.form-item {
  margin-bottom: 24px;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input-label .el-icon {
  color: #00a2ff;
}

.custom-input {
  height: 50px;
}

.custom-input :deep(.el-input__wrapper) {
  height: 50px;
  border-radius: 12px;
  background: rgba(0, 18, 51, 0.6);
  border: 1px solid rgba(0, 162, 255, 0.2);
  padding: 0 16px;
  transition: all 0.3s;
}

.custom-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(0, 162, 255, 0.4);
  background: rgba(0, 18, 51, 0.7);
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: #00a2ff;
  background: rgba(0, 18, 51, 0.8);
  box-shadow: 0 0 20px rgba(0, 162, 255, 0.2);
}

.custom-input :deep(.el-input__inner) {
  color: #fff;
  font-size: 15px;
}

.custom-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.3);
}

.input-icon {
  color: #00a2ff;
  font-size: 18px;
}

/* 按钮样式 */
.login-button,
.register-button {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  transition: all 0.3s;
  border: none;
}

.login-button {
  background: linear-gradient(135deg, #0066ff 0%, #00a2ff 100%);
  box-shadow: 0 8px 24px rgba(0, 102, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.login-button:hover::before {
  left: 100%;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 162, 255, 0.4);
}

.register-button {
  background: rgba(0, 18, 51, 0.5);
  border: 1px solid rgba(0, 162, 255, 0.3);
  color: #00a2ff;
}

.register-button:hover {
  background: rgba(0, 102, 255, 0.2);
  border-color: rgba(0, 162, 255, 0.5);
  color: #00d4ff;
  transform: translateY(-2px);
}

/* 分隔线 */
.divider {
  position: relative;
  text-align: center;
  margin: 32px 0;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 162, 255, 0.3), transparent);
}

.divider-text {
  position: relative;
  display: inline-block;
  padding: 0 16px;
  background: rgba(13, 27, 62, 0.8);
  color: rgba(0, 162, 255, 0.5);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 2px;
}

/* 状态栏 */
.status-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 162, 255, 0.1);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00ff88;
  box-shadow: 0 0 12px rgba(0, 255, 136, 0.6);
  animation: breathe 2s ease-in-out infinite;
}

.status-divider {
  color: rgba(0, 162, 255, 0.3);
}

/* 对话框样式 */
.register-dialog :deep(.el-dialog) {
  background: rgba(13, 27, 62, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 162, 255, 0.2);
  border-radius: 16px;
}

.register-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(0, 162, 255, 0.1);
}

.register-dialog :deep(.el-dialog__title) {
  color: #00d4ff;
  font-weight: 600;
}
</style>

