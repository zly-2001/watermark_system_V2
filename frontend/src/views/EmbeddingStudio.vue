<template>
  <div class="embedding-studio fade-in-up">
    <!-- 页面头部 -->
    <div class="page-header glass-effect">
      <div class="header-content">
        <div class="header-icon">📝</div>
        <div class="header-text">
          <h1 class="page-title">水印嵌入工作台</h1>
          <p class="page-subtitle">WATERMARK EMBEDDING STUDIO</p>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-box">
          <div class="stat-value">{{ embedCount }}</div>
          <div class="stat-label">已处理</div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-box">
          <div class="stat-value">100%</div>
          <div class="stat-label">成功率</div>
        </div>
      </div>
    </div>

    <el-row :gutter="24" class="main-content">
        <!-- 左侧：上传和配置区 -->
        <el-col :span="10">
        <div class="control-panel glass-effect hover-card">
          <div class="panel-header">
            <div class="panel-title">⚙️ 配置参数</div>
            <div class="panel-indicator"></div>
          </div>
            
          <!-- 文件上传区域 -->
          <div class="upload-section">
            <el-upload
              ref="uploadRef"
              class="tech-upload"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept="image/*"
            >
              <div class="upload-content">
                <el-icon class="upload-icon"><upload-filled /></el-icon>
                <div class="upload-text">
                  <div class="upload-title">拖拽或点击上传图片</div>
                  <div class="upload-hint">支持 JPG、PNG、BMP、TIFF、WEBP 等 | 推荐 512-2048px</div>
                </div>
              </div>
            </el-upload>
          </div>

          <!-- 参数配置表单 -->
          <el-form :model="form" class="config-form" label-position="top">
            <el-form-item label="水印模型" class="form-group">
              <el-select 
                v-model="form.modelType" 
                placeholder="选择水印模型" 
                size="large"
                style="width: 100%"
              >
                <el-option 
                  label="DWT-DCT (传统频域)" 
                  value="dwtdct"
                >
                  <div class="model-option">
                    <span class="model-name">DWT-DCT (传统频域)</span>
                    <el-tag size="small" type="info">传统攻击 ⭐⭐⭐⭐</el-tag>
                  </div>
                </el-option>
                <el-option 
                  label="Stable Signature (Meta 开源)" 
                  value="stablesig"
                >
                  <div class="model-option">
                    <span class="model-name">Stable Signature (Meta)</span>
                    <el-tag size="small" type="success">AIGC 抵抗 ⭐⭐⭐⭐⭐</el-tag>
                  </div>
                </el-option>
                <el-option 
                  label="StegaStamp (深度学习)" 
                  value="stegastamp"
                >
                  <div class="model-option">
                    <span class="model-name">StegaStamp (深度学习)</span>
                    <el-tag size="small" type="warning">AIGC 抵抗 ⭐⭐⭐⭐</el-tag>
                  </div>
                </el-option>
                <el-option 
                  label="Tree-Ring (扩散模型专用)" 
                  value="treering"
                >
                  <div class="model-option">
                    <span class="model-name">Tree-Ring (扩散模型专用)</span>
                    <el-tag size="small" type="success">AIGC 抵抗 ⭐⭐⭐⭐⭐</el-tag>
                  </div>
                </el-option>
              </el-select>
              <div class="model-hint">
                {{ getModelHint() }}
              </div>
            </el-form-item>

            <el-form-item label="水印文本" class="form-group">
                <el-input
                  v-model="form.text"
                  placeholder="例如: Thesis-2024"
                size="large"
                  clearable
                />
              </el-form-item>

            <el-form-item label="隐蔽性 ↔ 鲁棒性平衡" class="form-group">
                <el-slider
                  v-model="form.balance"
                :min="0"
                :max="1"
                  :step="0.1"
                :show-tooltip="true"
                />
                <div class="slider-labels">
                <span>🔒 更隐蔽</span>
                <span class="balance-value">{{ (form.balance * 100).toFixed(0) }}%</span>
                <span>💪 更鲁棒</span>
                </div>
              </el-form-item>

                <el-button
                  type="primary"
                  size="large"
                  :loading="processing"
                  :disabled="!selectedFile"
                  @click="handleEmbed"
              class="embed-button"
                >
              <el-icon v-if="!processing"><MagicStick /></el-icon>
              <span>{{ processing ? '嵌入处理中...' : '开始嵌入水印' }}</span>
            </el-button>

            <!-- 发送到攻击实验室按钮 -->
            <el-button
              v-if="watermarkedImage"
              type="success"
              size="large"
              @click="sendToAttackLab"
              class="send-button"
            >
              <el-icon><Right /></el-icon>
              <span>发送到攻击实验室</span>
                </el-button>
            </el-form>
        </div>
        </el-col>

      <!-- 右侧：预览区 -->
        <el-col :span="14">
        <div class="preview-panel glass-effect hover-card">
          <div class="panel-header">
            <div class="panel-title">🖼️ 对比预览</div>
            <div class="panel-indicator"></div>
          </div>

            <div v-if="originalImage && watermarkedImage" class="compare-container">
            <el-row :gutter="16">
              <el-col :span="12">
                <div class="image-card glass-effect">
                  <div class="image-label">原始图片</div>
                  <img :src="originalImage" alt="原图" class="preview-image" />
                </div>
              </el-col>
              <el-col :span="12">
                <div class="image-card glass-effect">
                  <div class="image-label glow">水印图片</div>
                  <img :src="watermarkedImage" alt="水印图" class="preview-image" />
                </div>
              </el-col>
            </el-row>

            <!-- 质量指标 -->
            <div v-if="metrics.psnr" class="metrics-panel glass-effect">
              <div class="metric-item">
                <div class="metric-label">PSNR</div>
                <div class="metric-value">{{ metrics.psnr }} dB</div>
              </div>
              <div class="metric-divider"></div>
              <div class="metric-item">
                <div class="metric-label">SSIM</div>
                <div class="metric-value">{{ metrics.ssim }}</div>
              </div>
            </div>
            </div>

            <div v-else class="placeholder">
              <el-icon class="placeholder-icon"><Picture /></el-icon>
            <div class="placeholder-text">上传图片后将显示对比预览</div>
            </div>
            </div>
        </el-col>
      </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, MagicStick, Picture, Right } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const uploadRef = ref(null)
const selectedFile = ref(null)
const originalImage = ref('')
const watermarkedImage = ref('')
const processing = ref(false)
const embedCount = ref(0)

const form = reactive({
  text: 'Thesis-2024',
  balance: 0.5,
  modelType: 'dwtdct'  // 默认使用 DWT-DCT
})

const metrics = reactive({
  psnr: '',
  ssim: ''
})

const handleFileChange = (file) => {
  // 验证文件大小（建议不超过 10MB）
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.raw.size > maxSize) {
    ElMessage.warning(`⚠️ 图片过大 (${(file.raw.size / 1024 / 1024).toFixed(2)}MB)，建议小于 10MB`)
    // 仍然允许上传，但给出警告
  }
  
  selectedFile.value = file.raw
  const reader = new FileReader()
  reader.onload = (e) => {
    originalImage.value = e.target.result
    
    // 验证图片尺寸
    const img = new Image()
    img.onload = () => {
      const width = img.width
      const height = img.height
      
      // 给出尺寸建议
      if (width < 256 || height < 256) {
        ElMessage.warning(`⚠️ 图片尺寸较小 (${width}×${height})，建议至少 256×256 像素`)
      } else if (width > 4096 || height > 4096) {
        ElMessage.warning(`⚠️ 图片尺寸较大 (${width}×${height})，处理可能较慢`)
      }
    }
    img.src = e.target.result
    
    watermarkedImage.value = ''
    metrics.psnr = ''
    metrics.ssim = ''
  }
  reader.readAsDataURL(file.raw)
}

const handleEmbed = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先上传图片')
    return
  }

  if (!form.text.trim()) {
    ElMessage.warning('请输入水印文字')
    return
  }

  processing.value = true

  try {
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    formData.append('text', form.text)
    formData.append('balance', form.balance)
    formData.append('model_type', form.modelType)

    const response = await request({
      url: '/watermark/embed',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    watermarkedImage.value = `data:image/png;base64,${response.image_base64}`
    metrics.psnr = response.psnr?.toFixed(2) || 'N/A'
    metrics.ssim = response.ssim?.toFixed(4) || 'N/A'
    embedCount.value++

    // 保存水印信息到 sessionStorage，供攻击模块使用
    // 使用 sessionStorage 而不是 localStorage，避免配额问题
    try {
      console.log('嵌入成功，保存数据到 sessionStorage')
      
      // 先清理旧数据
      sessionStorage.removeItem('watermarkedImage')
      sessionStorage.removeItem('watermarkText')
      sessionStorage.removeItem('watermarkModel')
      sessionStorage.removeItem('watermarkTimestamp')
      sessionStorage.removeItem('watermarkLength')
      
      // 保存新数据
      sessionStorage.setItem('watermarkText', form.text)
      sessionStorage.setItem('watermarkModel', form.modelType)
      sessionStorage.setItem('watermarkedImage', watermarkedImage.value)
      sessionStorage.setItem('watermarkTimestamp', Date.now().toString())
      // 保存文本长度（用于提取时匹配）
      sessionStorage.setItem('watermarkLength', new TextEncoder().encode(form.text).length.toString())
      
      // 验证保存是否成功
      const saved = sessionStorage.getItem('watermarkedImage')
      console.log('验证保存:', saved ? `✅ 成功 (长度: ${saved.length})` : '❌ 失败')

      ElMessage.success('✅ 水印嵌入成功！可点击下方按钮发送到攻击实验室')
    } catch (error) {
      console.error('保存失败:', error)
      if (error.name === 'QuotaExceededError') {
        ElMessage.warning('⚠️ 图片较大，建议使用更小的图片。仍可点击按钮发送。')
      }
    }
  } catch (error) {
    console.error('嵌入失败:', error)
  } finally {
    processing.value = false
  }
}

const getModelHint = () => {
  const hints = {
    'dwtdct': '💡 适合抵抗 JPEG 压缩、噪声、模糊等传统攻击',
    'stablesig': '💡 Meta 开源，自动下载预训练模型，最强 AIGC 抵抗力！',
    'stegastamp': '💡 深度学习水印，对 AIGC 攻击有较强抵抗力',
    'treering': '💡 最新方法，专门抵抗 Stable Diffusion 等 AIGC 攻击'
  }
  return hints[form.modelType] || ''
}

const router = useRouter()

const sendToAttackLab = () => {
  // 确保水印图片已保存
  if (watermarkedImage.value) {
    try {
      console.log('正在保存水印图片...')
      
      // 先清理旧数据，避免超出配额
      const oldKeys = ['watermarkedImage', 'watermarkText', 'watermarkModel', 'watermarkTimestamp']
      oldKeys.forEach(key => {
        try {
          localStorage.removeItem(key)
        } catch (e) {
          console.warn('清理失败:', key)
        }
      })
      
      // 保存新数据（使用 sessionStorage 而不是 localStorage，容量更大）
      sessionStorage.setItem('watermarkedImage', watermarkedImage.value)
      sessionStorage.setItem('watermarkText', form.text)
      sessionStorage.setItem('watermarkModel', form.modelType)
      sessionStorage.setItem('watermarkTimestamp', Date.now().toString())
      
      console.log('✅ 保存成功，准备跳转...')
      ElMessage.success('✅ 已发送到攻击实验室！')
      
      // 跳转到攻击实验室
      setTimeout(() => {
        console.log('跳转到 /attack')
        router.push('/attack')
      }, 800)
    } catch (error) {
      console.error('保存失败:', error)
      if (error.name === 'QuotaExceededError') {
        ElMessage.error('图片过大，无法保存。请尝试上传更小的图片或在攻击实验室手动上传。')
      } else {
        ElMessage.error('保存失败: ' + error.message)
      }
    }
  } else {
    console.error('watermarkedImage 为空')
    ElMessage.error('请先嵌入水印')
  }
}
</script>

<style scoped>
.embedding-studio {
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
  gap: 24px;
}

.stat-box {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
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

.stat-divider {
  width: 1px;
  height: 40px;
  background: linear-gradient(180deg, transparent, rgba(0, 162, 255, 0.3), transparent);
}

/* 主内容区 */
.main-content {
  margin-top: 24px;
}

/* 面板通用样式 */
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

/* 上传区域 */
.upload-section {
  margin-bottom: 32px;
}

.tech-upload {
  width: 100%;
}

.tech-upload :deep(.el-upload-dragger) {
  border: 2px dashed rgba(0, 162, 255, 0.3);
  border-radius: 12px;
  background: rgba(0, 18, 51, 0.3);
  transition: all 0.3s;
  padding: 40px 20px;
}

.tech-upload :deep(.el-upload-dragger:hover) {
  border-color: rgba(0, 162, 255, 0.6);
  background: rgba(0, 102, 255, 0.1);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon {
  font-size: 64px;
  color: #00a2ff;
  filter: drop-shadow(0 0 20px rgba(0, 162, 255, 0.4));
}

.upload-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.upload-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* 表单样式 */
.config-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group :deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 12px;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.balance-value {
  font-weight: 700;
  color: #00d4ff;
  font-family: 'SF Mono', monospace;
}

.embed-button {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #0066ff 0%, #00a2ff 100%);
  border: none;
  box-shadow: 0 8px 24px rgba(0, 102, 255, 0.3);
  transition: all 0.3s;
  margin-top: 12px;
}

.embed-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 162, 255, 0.4);
}

/* 发送按钮 */
.send-button {
  width: 100%;
  height: 50px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #00b894 0%, #00ff88 100%);
  border: none;
  box-shadow: 0 8px 24px rgba(0, 255, 136, 0.3);
  transition: all 0.3s;
  margin-top: 12px;
}

.send-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 255, 136, 0.4);
  background: linear-gradient(135deg, #00cca3 0%, #00ff99 100%);
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
  border-color: #00a2ff;
  box-shadow: 0 0 20px rgba(0, 162, 255, 0.4);
  color: #00d4ff;
}

.preview-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  display: block;
}

/* 指标面板 */
.metrics-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  margin-top: 24px;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid rgba(0, 162, 255, 0.2);
}

.metric-item {
  text-align: center;
}

.metric-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: 'SF Mono', monospace;
}

.metric-divider {
  width: 1px;
  height: 40px;
  background: linear-gradient(180deg, transparent, rgba(0, 162, 255, 0.3), transparent);
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
  font-size: 16px;
}

@keyframes breathe {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

/* 模型选择器样式 */
.model-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.model-name {
  font-size: 14px;
  font-weight: 500;
}

.model-hint {
  margin-top: 8px;
  font-size: 12px;
  color: rgba(0, 212, 255, 0.7);
  padding: 8px 12px;
  background: rgba(0, 162, 255, 0.1);
  border-radius: 6px;
  border-left: 3px solid rgba(0, 212, 255, 0.5);
}

:deep(.el-select-dropdown__item) {
  padding: 12px 16px;
}
</style>
