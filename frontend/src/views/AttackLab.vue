<template>
  <div class="attack-lab fade-in-up">
    <!-- 页面头部 -->
    <div class="page-header glass-effect">
      <div class="header-content">
        <div class="header-icon">⚔️</div>
        <div class="header-text">
          <h1 class="page-title">异构攻击实验室</h1>
          <p class="page-subtitle">ATTACK SIMULATION LABORATORY</p>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-box">
          <div class="stat-value">{{ attackCount }}</div>
          <div class="stat-label">攻击测试</div>
        </div>
      </div>
    </div>

    <el-row :gutter="24" class="main-content">
        <!-- 左侧：控制面板 -->
        <el-col :span="10">
        <div class="control-panel glass-effect hover-card">
          <div class="panel-header">
            <div class="panel-title">⚙️ 攻击配置</div>
            <div class="panel-indicator"></div>
          </div>

          <!-- 标签页 - 提高对比度 -->
          <el-tabs v-model="activeTab" class="tech-tabs">
              <!-- AIGC 破坏模拟 -->
              <el-tab-pane label="AIGC 破坏模拟" name="aigc">
                <div class="attack-config">
                <div class="config-header">
                  <div class="config-icon">🎨</div>
                  <div class="config-info">
                    <h3>AIGC 对抗攻击</h3>
                    <p class="description">针对 AI 生成模型的主流攻击（论文常用测试）</p>
                  </div>
                </div>
                  
                <el-form label-position="top" class="attack-form">
                  <!-- Stable Diffusion 重绘（最重要） -->
                  <el-form-item label="🖼️ Stable Diffusion 重绘（核心）">
                    <div class="attack-info-box">
                      <span class="info-tag">论文必测</span>
                      <span class="info-desc">模拟 SD img2img 重绘攻击</span>
                    </div>
                      <el-slider
                      v-model="sdIntensity"
                        :min="0.1"
                        :max="1.0"
                        :step="0.1"
                        show-stops
                    />
                    <div class="slider-labels">
                      <span>轻微重绘 (denoising 0.1)</span>
                      <span class="intensity-value">{{ (sdIntensity * 100).toFixed(0) }}%</span>
                      <span>完全重绘 (denoising 1.0)</span>
                    </div>
                    <el-button
                      type="danger"
                      size="large"
                      :loading="attacking"
                      :disabled="!sourceImage"
                      @click="handleAttack('sd_repaint', sdIntensity)"
                      class="attack-button danger"
                    >
                      <el-icon v-if="!attacking"><Lightning /></el-icon>
                      <span>{{ attacking ? '处理中...' : '执行 SD 重绘攻击' }}</span>
                    </el-button>
                  </el-form-item>

                  <!-- 图像修复（Inpainting） -->
                  <el-form-item label="🩹 图像修复攻击">
                    <div class="attack-info-box">
                      <span class="info-tag">常用测试</span>
                      <span class="info-desc">模拟 Inpainting 局部重绘</span>
                    </div>
                    <el-slider
                      v-model="inpaintRatio"
                      :min="0.1"
                      :max="0.5"
                      :step="0.05"
                      show-stops
                      />
                      <div class="slider-labels">
                      <span>10% 区域</span>
                      <span class="intensity-value">{{ (inpaintRatio * 100).toFixed(0) }}%</span>
                      <span>50% 区域</span>
                      </div>
                    <el-button
                      type="danger"
                      size="large"
                      :loading="attacking"
                      :disabled="!sourceImage"
                      @click="handleAttack('inpaint', inpaintRatio)"
                      class="attack-button danger"
                    >
                      执行修复攻击
                    </el-button>
                    </el-form-item>

                  <!-- 超分辨率 -->
                  <el-form-item label="🔬 超分辨率重建">
                    <div class="attack-info-box">
                      <span class="info-tag">鲁棒性测试</span>
                      <span class="info-desc">测试超分后水印存活率</span>
                    </div>
                    <el-slider
                      v-model="superResScale"
                      :min="2"
                      :max="4"
                      :step="1"
                      show-stops
                    />
                    <div class="slider-labels">
                      <span>2x Real-ESRGAN</span>
                      <span class="intensity-value">{{ superResScale }}x</span>
                      <span>4x Real-ESRGAN</span>
                    </div>
                      <el-button
                        type="danger"
                        size="large"
                        :loading="attacking"
                        :disabled="!sourceImage"
                      @click="handleAttack('super_resolution', superResScale)"
                      class="attack-button danger"
                      >
                      执行超分攻击
                      </el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </el-tab-pane>

              <!-- 常规几何攻击 -->
              <el-tab-pane label="常规几何攻击" name="geometric">
                <div class="attack-config">
                <div class="config-header">
                  <div class="config-icon">📐</div>
                  <div class="config-info">
                    <h3>传统图像攻击</h3>
                    <p class="description">经典的图像处理攻击（论文基准测试）</p>
                  </div>
                </div>
                
                <el-form label-position="top" class="attack-form">
                  <!-- JPEG 压缩（最常见） -->
                  <el-form-item label="📦 JPEG 压缩（基准）">
                    <div class="attack-info-box">
                      <span class="info-tag">论文必测</span>
                      <span class="info-desc">最常见的有损压缩攻击</span>
                    </div>
                    <el-slider
                      v-model="jpegQuality"
                      :min="10"
                      :max="95"
                      :step="5"
                      show-stops
                    />
                    <div class="slider-labels">
                      <span>低质量 Q=10</span>
                      <span class="intensity-value">质量 {{ jpegQuality }}</span>
                      <span>高质量 Q=95</span>
                    </div>
                    <el-button
                      type="warning"
                      size="large"
                      :loading="attacking"
                      :disabled="!sourceImage"
                      @click="handleAttack('jpeg', jpegQuality)"
                      class="attack-button warning"
                    >
                      执行 JPEG 压缩
                    </el-button>
                  </el-form-item>

                    <!-- 裁剪攻击 -->
                  <el-form-item label="✂️ 裁剪攻击">
                    <div class="attack-info-box">
                      <span class="info-tag">空间鲁棒性</span>
                      <span class="info-desc">测试边缘裁剪抵抗能力</span>
                    </div>
                      <el-slider
                        v-model="cropIntensity"
                        :min="0.1"
                      :max="0.5"
                      :step="0.05"
                        show-stops
                      />
                    <div class="slider-labels">
                      <span>轻度 10%</span>
                      <span class="intensity-value">{{ (cropIntensity * 100).toFixed(0) }}%</span>
                      <span>重度 50%</span>
                    </div>
                      <el-button
                        type="warning"
                      size="large"
                        :loading="attacking"
                        :disabled="!sourceImage"
                        @click="handleAttack('crop', cropIntensity)"
                      class="attack-button warning"
                      >
                        执行裁剪攻击
                      </el-button>
                    </el-form-item>

                  <!-- 高斯噪声 -->
                  <el-form-item label="🌫️ 高斯噪声">
                    <div class="attack-info-box">
                      <span class="info-tag">噪声抵抗</span>
                      <span class="info-desc">测试加性噪声鲁棒性</span>
                    </div>
                      <el-slider
                      v-model="noiseLevel"
                      :min="5"
                      :max="50"
                      :step="5"
                        show-stops
                      />
                    <div class="slider-labels">
                      <span>σ=5</span>
                      <span class="intensity-value">σ={{ noiseLevel }}</span>
                      <span>σ=50</span>
                    </div>
                      <el-button
                        type="warning"
                      size="large"
                        :loading="attacking"
                        :disabled="!sourceImage"
                      @click="handleAttack('noise', noiseLevel)"
                      class="attack-button warning"
                      >
                      添加高斯噪声
                      </el-button>
                    </el-form-item>

                  <!-- 高斯模糊 -->
                  <el-form-item label="💫 高斯模糊">
                    <div class="attack-info-box">
                      <span class="info-tag">模糊抵抗</span>
                      <span class="info-desc">测试低通滤波影响</span>
                    </div>
                      <el-slider
                      v-model="blurRadius"
                      :min="1"
                      :max="10"
                      :step="1"
                        show-stops
                      />
                    <div class="slider-labels">
                      <span>kernel=1</span>
                      <span class="intensity-value">kernel={{ blurRadius }}</span>
                      <span>kernel=10</span>
                    </div>
                      <el-button
                        type="warning"
                      size="large"
                        :loading="attacking"
                        :disabled="!sourceImage"
                      @click="handleAttack('blur', blurRadius)"
                      class="attack-button warning"
                      >
                      执行高斯模糊
                      </el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </el-tab-pane>
            </el-tabs>
        </div>
        </el-col>

        <!-- 右侧：预览区 -->
        <el-col :span="14">
        <div class="preview-panel glass-effect hover-card">
          <div class="panel-header">
            <div class="panel-title">🖼️ 攻击效果预览</div>
            <div class="panel-indicator"></div>
            </div>

          <!-- 显示原始图片（如果有） -->
          <div v-if="sourceImage && !attackedImage" class="single-image-container">
            <div class="image-card glass-effect">
              <div class="image-label">原始水印图（等待攻击）</div>
              <img :src="sourceImage" alt="原图" class="preview-image" />
            </div>
            <div class="hint-box">
              <el-icon><Lightning /></el-icon>
              <span>选择左侧攻击类型开始测试</span>
            </div>
          </div>

          <!-- 显示对比结果 -->
          <div v-else-if="sourceImage && attackedImage" class="compare-container">
            <el-row :gutter="16">
              <el-col :span="12">
                <div class="image-card glass-effect">
                  <div class="image-label">原始水印图</div>
                  <img :src="sourceImage" alt="原图" class="preview-image" />
                </div>
              </el-col>
              <el-col :span="12">
                <div class="image-card glass-effect">
                  <div class="image-label glow">攻击后图像</div>
                  <img :src="attackedImage" alt="攻击后" class="preview-image" />
                </div>
              </el-col>
            </el-row>

            <!-- 攻击信息 -->
            <div v-if="attackInfo" class="attack-info glass-effect">
              <div class="info-header">
                <el-icon><InfoFilled /></el-icon>
                <span>攻击结果</span>
              </div>
              <div class="info-content">
                <div class="info-item">
                  <span class="info-label">攻击类型</span>
                  <span class="info-value">{{ attackInfo.type }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">强度/参数</span>
                  <span class="info-value">{{ attackInfo.intensity }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">处理时间</span>
                  <span class="info-value">{{ attackInfo.time }}ms</span>
                </div>
            </div>

              <!-- 操作按钮 -->
              <div class="attack-actions">
              <el-button
                type="primary"
                size="large"
                  @click="sendToTracing"
                  class="send-tracing-button"
                >
                  <el-icon><Right /></el-icon>
                  <span>发送到溯源中心</span>
                </el-button>
                <el-button
                  type="info"
                  size="large"
                  @click="resetAttack"
                  class="reset-button"
                >
                  <el-icon><Refresh /></el-icon>
                  <span>重置攻击</span>
                </el-button>
              </div>
            </div>
          </div>

          <!-- 占位符 + 上传选项 -->
          <div v-else class="placeholder">
            <el-icon class="placeholder-icon"><Picture /></el-icon>
            <div class="placeholder-text">暂无水印图片</div>
            <div class="placeholder-hint">
              <p>💡 方式1：在 <router-link to="/embedding" class="link">嵌入工作台</router-link> 嵌入水印后自动加载</p>
              <p>💡 方式2：手动上传带水印的图片</p>
            </div>
            
            <!-- 手动上传 -->
            <el-upload
              ref="uploadRef"
              class="manual-upload"
              :auto-upload="false"
              :on-change="handleManualUpload"
              :limit="1"
              accept="image/*"
              :show-file-list="false"
              >
              <el-button type="primary" size="large">
                <el-icon><UploadFilled /></el-icon>
                手动上传图片
              </el-button>
            </el-upload>
          </div>
            </div>
        </el-col>
      </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Lightning, Picture, InfoFilled, UploadFilled, Right, Refresh } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const activeTab = ref('aigc')
const attacking = ref(false)
const attackCount = ref(0)
const sourceImage = ref('')
const attackedImage = ref('')
const attackInfo = ref(null)

// 手动上传图片
const handleManualUpload = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    sourceImage.value = e.target.result
    ElMessage.success('图片上传成功，可以开始攻击测试')
  }
  reader.readAsDataURL(file.raw)
}

// 页面加载时自动加载保存的水印图片
onMounted(() => {
  // 优先从 sessionStorage 读取（更大容量，关闭标签页才清除）
  let savedImage = sessionStorage.getItem('watermarkedImage')
  let savedText = sessionStorage.getItem('watermarkText')
  let savedTimestamp = sessionStorage.getItem('watermarkTimestamp')
  
  // 如果 sessionStorage 没有，尝试 localStorage（向后兼容）
  if (!savedImage) {
    savedImage = localStorage.getItem('watermarkedImage')
    savedText = localStorage.getItem('watermarkText')
    savedTimestamp = localStorage.getItem('watermarkTimestamp')
  }
  
  if (savedImage && savedTimestamp) {
    // 检查图片是否是最近保存的（1小时内）
    const timestamp = parseInt(savedTimestamp)
    const now = Date.now()
    const oneHour = 60 * 60 * 1000
    
    if (now - timestamp < oneHour) {
    sourceImage.value = savedImage
      if (savedText) {
        ElMessage.success(`✅ 已自动加载水印图片（水印：${savedText}）`)
      } else {
        ElMessage.success('✅ 已自动加载水印图片')
      }
      console.log('✅ 图片加载成功，大小:', savedImage.length, '字符')
    } else {
      console.log('保存的水印图片已过期（超过1小时）')
    }
  } else {
    console.log('未找到保存的水印图片，请在嵌入工作台嵌入或手动上传')
  }
})

// AIGC 攻击参数（论文核心测试）
const sdIntensity = ref(0.5)          // Stable Diffusion 重绘强度
const inpaintRatio = ref(0.2)         // 图像修复区域比例
const superResScale = ref(2)          // 超分辨率倍数

// 传统攻击参数（论文基准测试）
const jpegQuality = ref(50)           // JPEG 压缩质量
const cropIntensity = ref(0.3)        // 裁剪比例
const noiseLevel = ref(15)            // 高斯噪声标准差 σ
const blurRadius = ref(3)             // 高斯模糊核大小

const router = useRouter()

// 保存原始图片（用于重置）
const originalImage = ref('')

const handleAttack = async (attackType, intensity) => {
  if (!sourceImage.value) {
    ElMessage.warning('请先在嵌入工作台生成带水印的图片')
    return
  }

  attacking.value = true
  const startTime = Date.now()

  try {
    // 确保每次攻击都基于原始图片（不会叠加）
    // 如果 originalImage 为空，说明是第一次攻击，保存原始图片
    if (!originalImage.value) {
      originalImage.value = sourceImage.value
    }
    
    // 将 base64 转换为 Blob（始终使用原始图片）
    const base64Data = originalImage.value.split(',')[1]
    const blob = base64ToBlob(base64Data, 'image/png')

    const formData = new FormData()
    formData.append('image', blob, 'watermarked.png')
    formData.append('attack_type', attackType)
    formData.append('intensity', String(intensity))

    const response = await request({
      url: '/attack/attack',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    attackedImage.value = `data:image/png;base64,${response.image_base64}`
    
    const endTime = Date.now()
    attackInfo.value = {
      type: response.attack_type || getAttackTypeName(attackType),
      intensity: formatIntensity(attackType, intensity),
      time: endTime - startTime
    }

    attackCount.value++
    ElMessage.success(`✅ ${response.attack_type || '攻击'}完成！每次攻击都基于原始图片，不会叠加`)
  } catch (error) {
    console.error('攻击失败:', error)
    ElMessage.error('攻击失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    attacking.value = false
  }
}

// 重置攻击（清除攻击结果，恢复原始图片显示）
const resetAttack = () => {
  attackedImage.value = ''
  attackInfo.value = null
  originalImage.value = ''  // 清除保存的原始图片，下次攻击会重新保存
  ElMessage.info('已重置，下次攻击将基于原始图片')
}

// 发送到溯源中心
const sendToTracing = () => {
  if (!attackedImage.value) {
    ElMessage.warning('请先执行攻击')
    return
}

  try {
    // 保存攻击后的图片到 sessionStorage
    sessionStorage.setItem('attackedImage', attackedImage.value)
    sessionStorage.setItem('attackType', attackInfo.value?.type || '未知攻击')
    sessionStorage.setItem('attackIntensity', attackInfo.value?.intensity || '')
    sessionStorage.setItem('attackTimestamp', Date.now().toString())
    
    // 同时保存原始水印信息（如果有）
    const watermarkText = sessionStorage.getItem('watermarkText')
    if (watermarkText) {
      sessionStorage.setItem('originalWatermarkText', watermarkText)
    }
    
    console.log('✅ 已保存攻击后图片到 sessionStorage')
    ElMessage.success('✅ 已发送到溯源中心！')
    
    // 跳转到溯源中心
    setTimeout(() => {
      router.push('/tracing')
    }, 800)
  } catch (error) {
    console.error('保存失败:', error)
    if (error.name === 'QuotaExceededError') {
      ElMessage.error('图片过大，无法保存。请尝试使用更小的图片。')
    } else {
      ElMessage.error('保存失败: ' + error.message)
    }
  }
}

const base64ToBlob = (base64, mimeType) => {
  const byteCharacters = atob(base64)
  const byteNumbers = new Array(byteCharacters.length)
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i)
  }
  const byteArray = new Uint8Array(byteNumbers)
  return new Blob([byteArray], { type: mimeType })
}

const getAttackTypeName = (type) => {
  const names = {
    // AIGC 攻击（论文核心）
    'sd_repaint': 'Stable Diffusion 重绘',
    'inpaint': 'AI 图像修复 (Inpainting)',
    'super_resolution': 'AI 超分辨率',
    // 传统攻击（论文基准）
    'jpeg': 'JPEG 有损压缩',
    'crop': '边缘裁剪',
    'noise': '加性高斯噪声 (AWGN)',
    'blur': '高斯模糊滤波'
  }
  return names[type] || type
}

const formatIntensity = (type, value) => {
  const formats = {
    // AIGC 攻击参数
    'sd_repaint': `denoising=${(value * 100).toFixed(0)}%`,
    'inpaint': `mask_ratio=${(value * 100).toFixed(0)}%`,
    'super_resolution': `scale=${value}x`,
    // 传统攻击参数
    'jpeg': `Q=${value}`,
    'crop': `ratio=${(value * 100).toFixed(0)}%`,
    'noise': `σ=${value}`,
    'blur': `kernel=${value}`
  }
  return formats[type] || value
}

const loadWatermarkedImage = () => {
  const savedImage = localStorage.getItem('watermarkedImage')
  if (savedImage) {
    sourceImage.value = savedImage
  }
}

onMounted(() => {
  loadWatermarkedImage()
})
</script>

<style scoped>
.attack-lab {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  margin-bottom: 24px;
  border-radius: 16px;
  border: 1px solid rgba(0, 162, 255, 0.2);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  font-size: 48px;
  filter: drop-shadow(0 0 20px rgba(0, 162, 255, 0.5));
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 11px;
  color: rgba(0, 162, 255, 0.6);
  letter-spacing: 2px;
  font-weight: 600;
  margin: 0;
}

.header-stats {
  display: flex;
  align-items: center;
}

.stat-box {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: 'SF Mono', monospace;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

/* 主内容 */
.main-content {
  margin-top: 24px;
}

/* 面板样式 */
.control-panel,
.preview-panel {
  padding: 28px;
  border-radius: 16px;
  border: 1px solid rgba(0, 162, 255, 0.2);
  min-height: 600px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(0, 162, 255, 0.1);
}

.panel-title {
  font-size: 18px;
  font-weight: 600;
  color: #00d4ff;
}

.panel-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00ff88;
  box-shadow: 0 0 12px rgba(0, 255, 136, 0.6);
  animation: breathe 2s ease-in-out infinite;
}

/* 标签页样式 - 提高对比度 */
.tech-tabs {
  margin-top: 20px;
}

.tech-tabs :deep(.el-tabs__header) {
  margin: 0 0 24px 0;
}

.tech-tabs :deep(.el-tabs__nav-wrap::after) {
  background: linear-gradient(90deg, transparent, rgba(0, 162, 255, 0.3), transparent);
  height: 1px;
}

.tech-tabs :deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.9) !important;
  font-size: 15px;
  font-weight: 600;
  padding: 0 24px;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s;
  background: rgba(0, 18, 51, 0.3);
  border: 1px solid rgba(0, 162, 255, 0.15);
  border-radius: 8px 8px 0 0;
  margin-right: 8px;
}

.tech-tabs :deep(.el-tabs__item:hover) {
  color: #00d4ff !important;
  background: rgba(0, 102, 255, 0.15);
  border-color: rgba(0, 162, 255, 0.3);
}

.tech-tabs :deep(.el-tabs__item.is-active) {
  color: #00d4ff !important;
  background: rgba(0, 102, 255, 0.25);
  border: 1px solid rgba(0, 162, 255, 0.5);
  border-bottom: none;
  box-shadow: 0 0 20px rgba(0, 162, 255, 0.2);
}

.tech-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #0066ff, #00d4ff);
  height: 3px;
  border-radius: 3px 3px 0 0;
}

/* 攻击配置 */
.attack-config {
  padding: 20px 0;
}

.config-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 28px;
  padding: 20px;
  background: rgba(0, 18, 51, 0.3);
  border: 1px solid rgba(0, 162, 255, 0.15);
  border-radius: 12px;
}

.config-icon {
  font-size: 40px;
  filter: drop-shadow(0 0 15px rgba(0, 162, 255, 0.4));
}

.config-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #00d4ff;
  margin: 0 0 8px 0;
}

.description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  line-height: 1.6;
}

/* 攻击信息提示框 */
.attack-info-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(0, 102, 255, 0.08);
  border: 1px solid rgba(0, 162, 255, 0.2);
  border-radius: 8px;
  margin-bottom: 16px;
}

.info-tag {
  padding: 4px 12px;
  background: linear-gradient(135deg, #0066ff, #00a2ff);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.info-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
}

/* 表单样式 */
.attack-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.attack-form :deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 12px;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.intensity-value {
  font-weight: 700;
  color: #00d4ff;
  font-family: 'SF Mono', monospace;
}

/* 按钮样式 */
.attack-button {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  transition: all 0.3s;
  margin-top: 16px;
}

.attack-button.danger {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff4757 100%);
  box-shadow: 0 8px 24px rgba(255, 107, 107, 0.3);
}

.attack-button.danger:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(255, 107, 107, 0.4);
}

.attack-button.warning {
  background: linear-gradient(135deg, #ffa500 0%, #ff8c00 100%);
  box-shadow: 0 8px 24px rgba(255, 165, 0, 0.3);
}

.attack-button.warning:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(255, 165, 0, 0.4);
}

/* 预览区域 */
.compare-container {
  padding: 20px 0;
}

.image-card {
  position: relative;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(0, 162, 255, 0.2);
  overflow: hidden;
}

.image-label {
  position: absolute;
  top: 24px;
  left: 24px;
  padding: 6px 16px;
  background: rgba(0, 18, 51, 0.9);
  border: 1px solid rgba(0, 162, 255, 0.3);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  z-index: 10;
  backdrop-filter: blur(10px);
}

.image-label.glow {
  border-color: #ff6b6b;
  box-shadow: 0 0 20px rgba(255, 107, 107, 0.4);
  color: #ff6b6b;
}

.preview-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  display: block;
}

/* 攻击信息 */
.attack-info {
  margin-top: 24px;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid rgba(0, 162, 255, 0.2);
}

.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 162, 255, 0.1);
  font-size: 15px;
  font-weight: 600;
  color: #00d4ff;
}

.attack-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 162, 255, 0.1);
}

.send-tracing-button {
  flex: 1;
  height: 45px;
  background: linear-gradient(135deg, #00b894 0%, #00ff88 100%);
  border: none;
  box-shadow: 0 4px 16px rgba(0, 255, 136, 0.3);
  transition: all 0.3s;
}

.send-tracing-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 255, 136, 0.4);
}

.reset-button {
  flex: 1;
  height: 45px;
  background: rgba(0, 162, 255, 0.2);
  border: 1px solid rgba(0, 162, 255, 0.4);
  color: #00d4ff;
  transition: all 0.3s;
}

.reset-button:hover {
  background: rgba(0, 162, 255, 0.3);
  border-color: rgba(0, 162, 255, 0.6);
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.info-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #00d4ff;
  font-family: 'SF Mono', monospace;
}

/* 占位符 */
.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 500px;
  color: rgba(255, 255, 255, 0.3);
}

.placeholder-icon {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.3;
}

.placeholder-text {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
}

.placeholder-hint {
  margin: 20px 0;
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.8;
}

.placeholder-hint p {
  margin: 8px 0;
}

.placeholder-hint .link {
  color: #00d4ff;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s;
}

.placeholder-hint .link:hover {
  color: #00ff88;
  text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.manual-upload {
  margin-top: 20px;
}

.single-image-container {
  padding: 20px;
}

.single-image-container .image-card {
  margin-bottom: 20px;
}

.hint-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 162, 255, 0.1);
  border: 1px solid rgba(0, 162, 255, 0.3);
  border-radius: 12px;
  color: #00d4ff;
  font-size: 14px;
  margin-top: 16px;
}

.hint-box .el-icon {
  font-size: 20px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

@keyframes breathe {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}
</style>
