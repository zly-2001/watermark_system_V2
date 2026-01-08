<template>
  <div class="tracing-center">
    <el-card shadow="hover" class="main-card">
      <template #header>
        <div class="card-header">
          <h2>🔍 智能溯源与报告</h2>
          <p>提取水印并生成法证分析报告</p>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧：图片上传 -->
        <el-col :span="12">
          <el-card shadow="never" class="upload-card">
            <h3>上传待溯源图片</h3>
            
            <!-- 从攻击实验室加载 -->
            <el-button
              type="info"
              :icon="Refresh"
              @click="loadAttackedImage"
              style="width: 100%; margin-bottom: 20px"
            >
              从攻击实验室加载图片
            </el-button>

            <!-- 手动上传 -->
            <el-upload
              ref="uploadRef"
              class="upload-demo"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept="image/*"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将图片拖到此处，或<em>点击上传</em>
              </div>
            </el-upload>

            <!-- 图片预览 -->
            <div v-if="sourceImage" class="image-preview">
              <img :src="sourceImage" alt="待溯源图片" />
            </div>

            <!-- 提取按钮 -->
            <el-button
              type="primary"
              size="large"
              :loading="extracting"
              :disabled="!sourceImage"
              @click="handleExtract"
              style="width: 100%; margin-top: 20px"
            >
              <el-icon><Search /></el-icon>
              开始提取水印
            </el-button>
          </el-card>
        </el-col>

        <!-- 右侧：提取结果 -->
        <el-col :span="12">
          <el-card shadow="never" class="result-card">
            <h3>提取结果</h3>

            <!-- 加载动画 -->
            <div v-if="extracting" class="loading-container">
              <el-icon class="loading-icon is-loading"><Loading /></el-icon>
              <p>正在提取水印，模拟神经网络推理中...</p>
            </div>

            <!-- 提取成功 -->
            <div v-else-if="extractResult && extractResult.status === 'Success'" class="result-success">
              <div class="success-icon">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <h2>提取成功！</h2>
              
              <div class="result-content">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="提取内容">
                    <el-tag type="success" size="large">{{ extractResult.extracted_text }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="提取状态">
                    <el-tag type="success">{{ extractResult.status }}</el-tag>
                  </el-descriptions-item>
                </el-descriptions>

                <!-- BER 仪表盘 -->
                <div class="ber-dashboard">
                  <h4>误码率 (BER)</h4>
                  <el-progress
                    type="dashboard"
                    :percentage="berPercentage"
                    :color="berColor"
                    :width="200"
                  >
                    <template #default="{ percentage }">
                      <span class="percentage-value">{{ extractResult.ber.toFixed(4) }}</span>
                      <span class="percentage-label">{{ (extractResult.ber * 100).toFixed(2) }}%</span>
                    </template>
                  </el-progress>
                </div>
              </div>

              <!-- 下载报告按钮 -->
              <el-button
                type="success"
                size="large"
                :icon="Download"
                @click="downloadReport"
                style="width: 100%; margin-top: 20px"
              >
                📥 下载法证分析报告 (PDF)
              </el-button>
            </div>

            <!-- 提取失败 -->
            <div v-else-if="extractResult && extractResult.status === 'Fail'" class="result-fail">
              <div class="fail-icon">
                <el-icon><CircleClose /></el-icon>
              </div>
              <h2>提取失败</h2>
              <p>误码率过高，无法正确提取水印</p>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="误码率">
                  <el-tag type="danger">{{ (extractResult.ber * 100).toFixed(2) }}%</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 初始状态 -->
            <div v-else class="placeholder">
              <el-icon class="placeholder-icon"><Document /></el-icon>
              <p>请上传图片并点击提取</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  UploadFilled,
  Search,
  Loading,
  CircleCheck,
  CircleClose,
  Download,
  Document
} from '@element-plus/icons-vue'
import request from '@/utils/request'

const uploadRef = ref(null)
const sourceImage = ref('')
const extracting = ref(false)
const extractResult = ref(null)

// 从攻击实验室加载图片
const loadAttackedImage = () => {
  // 优先从 sessionStorage 读取
  let attackedImage = sessionStorage.getItem('attackedImage')
  let attackType = sessionStorage.getItem('attackType')
  let attackTimestamp = sessionStorage.getItem('attackTimestamp')
  
  // 如果 sessionStorage 没有，尝试 localStorage（向后兼容）
  if (!attackedImage) {
    attackedImage = localStorage.getItem('attackedImage')
    attackType = localStorage.getItem('attackType')
    attackTimestamp = localStorage.getItem('attackTimestamp')
  }
  
  if (attackedImage && attackTimestamp) {
    // 检查是否在1小时内
    const timestamp = parseInt(attackTimestamp)
    const now = Date.now()
    const oneHour = 60 * 60 * 1000
    
    if (now - timestamp < oneHour) {
      sourceImage.value = attackedImage
      extractResult.value = null
      if (attackType) {
        ElMessage.success(`✅ 已加载攻击后的图片（${attackType}）`)
      } else {
        ElMessage.success('✅ 已加载攻击后的图片')
      }
    } else {
      ElMessage.warning('攻击后的图片已过期（超过1小时），请重新执行攻击')
    }
  } else {
    ElMessage.warning('未找到攻击后的图片，请先在攻击实验室执行攻击')
  }
}

const handleFileChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    sourceImage.value = e.target.result
    extractResult.value = null
  }
  reader.readAsDataURL(file.raw)
}

const handleExtract = async () => {
  if (!sourceImage.value) {
    ElMessage.warning('请先上传图片')
    return
  }

  extracting.value = true
  extractResult.value = null

  try {
    // 模拟 2 秒的加载动画（模拟神经网络推理）
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 将 Base64 图片转换为 File 对象
    const base64Data = sourceImage.value.split(',')[1]
    const byteCharacters = atob(base64Data)
    const byteNumbers = new Array(byteCharacters.length)
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    const byteArray = new Uint8Array(byteNumbers)
    const blob = new Blob([byteArray], { type: 'image/png' })

    // 获取原始水印文本和模型类型（如果有）
    const originalText = sessionStorage.getItem('originalWatermarkText') || sessionStorage.getItem('watermarkText') || ''
    const modelType = sessionStorage.getItem('watermarkModel') || 'dwtdct'
    const watermarkLength = sessionStorage.getItem('watermarkLength') || ''

    const formData = new FormData()
    formData.append('image', blob, 'attacked_image.png')
    formData.append('model_type', modelType)
    if (originalText) {
      formData.append('original_text', originalText)
    }
    if (watermarkLength) {
      formData.append('watermark_length', watermarkLength)
    }

    const response = await request({
      url: '/watermark/extract',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    extractResult.value = {
      extracted_text: response.extracted_text || response.text || '',
      ber: response.ber || 0,
      status: response.status || (response.ber < 0.1 ? 'Success' : 'Fail')
    }
    
    console.log('提取结果:', extractResult.value)
    
    if (extractResult.value.status === 'Success') {
      ElMessage.success(`✅ 水印提取成功！文本: ${extractResult.value.extracted_text}, BER: ${(extractResult.value.ber * 100).toFixed(2)}%`)
    } else {
      const berPercent = (extractResult.value.ber * 100).toFixed(2)
      if (extractResult.value.extracted_text && extractResult.value.extracted_text !== '提取失败') {
        ElMessage.warning(`⚠️ 水印提取部分成功，文本: ${extractResult.value.extracted_text}, BER: ${berPercent}%`)
      } else {
        ElMessage.error(`❌ 水印提取失败，BER: ${berPercent}%。可能原因：攻击太强或图片未包含水印`)
      }
    }
  } catch (error) {
    console.error('提取失败:', error)
    ElMessage.error('提取失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    extracting.value = false
  }
}

const berPercentage = computed(() => {
  if (!extractResult.value) return 0
  // BER 转换为百分比显示（0-10% 范围）
  return Math.min(extractResult.value.ber * 1000, 100)
})

const berColor = computed(() => {
  if (!extractResult.value) return '#409eff'
  const ber = extractResult.value.ber
  if (ber < 0.02) return '#67c23a'  // 绿色：优秀
  if (ber < 0.05) return '#e6a23c'  // 橙色：良好
  return '#f56c6c'  // 红色：较差
})

const downloadReport = async () => {
  if (!extractResult.value || !sourceImage.value) {
    ElMessage.warning('请先完成水印提取')
    return
  }

  try {
    const formData = new FormData()
    formData.append('extracted_text', extractResult.value.extracted_text)
    formData.append('ber', extractResult.value.ber.toString())
    formData.append('status', extractResult.value.status)
    formData.append('image_base64', sourceImage.value)

    const response = await request({
      url: '/watermark/report',
      method: 'post',
      data: formData,
      responseType: 'blob',
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    // 对于 blob 响应，response 是完整的 axios response 对象
    // response.data 才是 blob 数据
    const blob = response.data instanceof Blob ? response.data : new Blob([response.data])
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `watermark_report_${Date.now()}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    ElMessage.success('报告下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('报告下载失败: ' + (error.message || '未知错误'))
  }
}

// 组件挂载时尝试加载图片
onMounted(() => {
  // 页面加载时自动加载攻击后的图片
  const attackedImage = sessionStorage.getItem('attackedImage')
  const attackTimestamp = sessionStorage.getItem('attackTimestamp')
  
  if (attackedImage && attackTimestamp) {
    const timestamp = parseInt(attackTimestamp)
    const now = Date.now()
    const oneHour = 60 * 60 * 1000
    
    if (now - timestamp < oneHour) {
      sourceImage.value = attackedImage
      const attackType = sessionStorage.getItem('attackType')
      if (attackType) {
        ElMessage.success(`✅ 已自动加载攻击后的图片（${attackType}）`)
      } else {
        ElMessage.success('✅ 已自动加载攻击后的图片')
      }
    }
  }
})
</script>

<style scoped>
.tracing-center {
  max-width: 1400px;
  margin: 0 auto;
}

.main-card {
  background: #1a1d3a;
  border: 1px solid #2d2f45;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  color: #409eff;
  margin-bottom: 10px;
}

.card-header p {
  color: #909399;
  font-size: 14px;
}

.upload-card,
.result-card {
  background: #252849;
  border: 1px solid #2d2f45;
  min-height: 600px;
}

.upload-card h3,
.result-card h3 {
  color: #e4e7ed;
  margin-bottom: 20px;
  font-size: 18px;
}

.upload-demo {
  width: 100%;
}

.image-preview {
  margin-top: 20px;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #409eff;
}

.loading-icon {
  font-size: 64px;
  margin-bottom: 20px;
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.result-success,
.result-fail {
  text-align: center;
  padding: 20px;
}

.success-icon,
.fail-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.success-icon {
  color: #67c23a;
}

.fail-icon {
  color: #f56c6c;
}

.result-success h2,
.result-fail h2 {
  color: #e4e7ed;
  margin-bottom: 20px;
}

.result-content {
  margin-top: 30px;
  text-align: left;
}

.ber-dashboard {
  margin-top: 30px;
  text-align: center;
}

.ber-dashboard h4 {
  color: #e4e7ed;
  margin-bottom: 20px;
}

.percentage-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.percentage-label {
  display: block;
  font-size: 14px;
  color: #909399;
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #909399;
}

.placeholder-icon {
  font-size: 64px;
  margin-bottom: 20px;
}
</style>

