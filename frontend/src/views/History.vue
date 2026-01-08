<template>
  <div class="history-page fade-in-up">
    <!-- 页面头部 -->
    <div class="page-header glass-effect">
      <div class="header-content">
        <div class="header-icon">📚</div>
        <div class="header-text">
          <h1 class="page-title">历史记录</h1>
          <p class="page-subtitle">WATERMARK HISTORY RECORDS</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button class="refresh-button" size="small" @click="loadHistory">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button 
          type="danger" 
          size="small" 
          @click="handleDeleteAll"
          :disabled="watermarkRecords.length === 0"
        >
          <el-icon><Delete /></el-icon>
          清空全部
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stats-row" v-if="stats">
      <el-col :span="6" v-for="(stat, index) in statCards" :key="index">
        <div class="stat-card glass-effect hover-card">
          <div class="stat-icon">{{ stat.icon }}</div>
          <div class="stat-content">
            <div class="stat-value" :class="`color-${index + 1}`">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 筛选和搜索 -->
    <div class="filter-panel glass-effect">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="模型类型">
          <el-select v-model="filters.modelType" placeholder="全部" clearable style="width: 150px">
            <el-option label="全部" value="" />
            <el-option label="DWT-DCT" value="dwtdct" />
            <el-option label="StegaStamp" value="stegastamp" />
            <el-option label="Tree-Ring" value="treering" />
            <el-option label="Stable Signature" value="stablesig" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="filters.startDate"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="filters.endDate"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadHistory">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 历史记录列表 -->
    <div class="records-panel glass-effect">
      <div class="panel-header">
        <div class="panel-title">📋 水印记录列表</div>
        <div class="panel-indicator"></div>
      </div>

      <el-table
        :data="watermarkRecords"
        v-loading="loading"
        class="history-table"
        stripe
        style="width: 100%"
        :row-class-name="tableRowClassName"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="watermark_text" label="水印文本" min-width="200">
          <template #default="{ row }">
            <span class="watermark-text">{{ row.watermark_text }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="model_type" label="模型" width="120">
          <template #default="{ row }">
            <span :class="['model-tag', `model-${row.model_type}`]">
              {{ getModelName(row.model_type) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="balance" label="平衡参数" width="100">
          <template #default="{ row }">
            <span class="table-cell-text">{{ (row.balance * 100).toFixed(0) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="psnr" label="PSNR" width="100">
          <template #default="{ row }">
            <span v-if="row.psnr" class="table-cell-text">{{ row.psnr.toFixed(2) }} dB</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="ssim" label="SSIM" width="100">
          <template #default="{ row }">
            <span v-if="row.ssim" class="table-cell-text">{{ row.ssim.toFixed(4) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="attack_count" label="攻击次数" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.attack_count > 0" class="count-badge attack-badge">
              {{ row.attack_count }}
            </span>
            <span v-else class="text-muted">0</span>
          </template>
        </el-table-column>
        <el-table-column prop="extraction_count" label="提取次数" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.extraction_count > 0" class="count-badge extraction-badge">
              {{ row.extraction_count }}
            </span>
            <span v-else class="text-muted">0</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            <span class="table-cell-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewDetail(row.id)"
            >
              详情
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadHistory"
          @current-change="loadHistory"
        />
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="水印记录详情"
      width="80%"
      class="detail-dialog"
    >
      <div v-if="detailData" class="detail-content">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h3>基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="记录ID">{{ detailData.watermark.id }}</el-descriptions-item>
            <el-descriptions-item label="水印文本">{{ detailData.watermark.watermark_text }}</el-descriptions-item>
            <el-descriptions-item label="模型类型">{{ getModelName(detailData.watermark.model_type) }}</el-descriptions-item>
            <el-descriptions-item label="平衡参数">{{ (detailData.watermark.balance * 100).toFixed(0) }}%</el-descriptions-item>
            <el-descriptions-item label="PSNR">{{ detailData.watermark.psnr ? detailData.watermark.psnr.toFixed(2) + ' dB' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="SSIM">{{ detailData.watermark.ssim ? detailData.watermark.ssim.toFixed(4) : '-' }}</el-descriptions-item>
            <el-descriptions-item label="图片尺寸">{{ detailData.watermark.original_image_size || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(detailData.watermark.created_at) }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 攻击记录 -->
        <div class="detail-section" v-if="detailData.attacks && detailData.attacks.length > 0">
          <h3>攻击记录 ({{ detailData.attacks.length }})</h3>
          <el-table :data="detailData.attacks" size="small">
            <el-table-column prop="attack_type" label="攻击类型" width="150" />
            <el-table-column prop="intensity" label="强度" width="100" />
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 提取记录 -->
        <div class="detail-section" v-if="detailData.extractions && detailData.extractions.length > 0">
          <h3>提取记录 ({{ detailData.extractions.length }})</h3>
          <el-table :data="detailData.extractions" size="small">
            <el-table-column prop="extracted_text" label="提取文本" min-width="200" />
            <el-table-column prop="original_text" label="原始文本" min-width="200" />
            <el-table-column prop="ber" label="BER" width="100">
              <template #default="{ row }">
                <span :class="row.ber < 0.1 ? 'text-success' : 'text-danger'">
                  {{ (row.ber * 100).toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Success' ? 'success' : 'danger'" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Delete } from '@element-plus/icons-vue'
import request from '@/utils/request'

const loading = ref(false)
const watermarkRecords = ref([])
const stats = ref(null)
const detailDialogVisible = ref(false)
const detailData = ref(null)

const filters = reactive({
  modelType: '',
  startDate: '',
  endDate: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 统计卡片数据
const statCards = computed(() => {
  if (!stats.value) return []
  return [
    {
      icon: '📝',
      label: '总水印数',
      value: stats.value.total_watermarks || 0
    },
    {
      icon: '⚔️',
      label: '总攻击数',
      value: stats.value.total_attacks || 0
    },
    {
      icon: '🔍',
      label: '总提取数',
      value: stats.value.total_extractions || 0
    },
    {
      icon: '✅',
      label: '成功提取',
      value: stats.value.success_extractions || 0
    }
  ]
})

// 加载历史记录
const loadHistory = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    
    if (filters.modelType) {
      params.model_type = filters.modelType
    }
    if (filters.startDate) {
      params.start_date = filters.startDate
    }
    if (filters.endDate) {
      params.end_date = filters.endDate
    }

    const response = await request({
      url: '/history/watermarks',
      method: 'get',
      params
    })

    watermarkRecords.value = response
    // 注意：后端没有返回总数，这里假设有足够的数据
    pagination.total = response.length === pagination.pageSize 
      ? (pagination.page * pagination.pageSize) + 1 
      : (pagination.page - 1) * pagination.pageSize + response.length
  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.error('加载历史记录失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// 加载统计信息
const loadStats = async () => {
  try {
    const response = await request({
      url: '/history/stats',
      method: 'get'
    })
    stats.value = response
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

// 查看详情
const viewDetail = async (id) => {
  try {
    const response = await request({
      url: `/history/watermarks/${id}`,
      method: 'get'
    })
    detailData.value = response
    detailDialogVisible.value = true
  } catch (error) {
    console.error('加载详情失败:', error)
    ElMessage.error('加载详情失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 删除记录
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？删除后无法恢复。', '确认删除', {
      type: 'warning'
    })

    await request({
      url: `/history/watermarks/${id}`,
      method: 'delete'
    })

    ElMessage.success('删除成功')
    loadHistory()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

// 清空全部
const handleDeleteAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有记录吗？此操作不可恢复！', '确认清空', {
      type: 'warning',
      confirmButtonText: '确定清空',
      cancelButtonText: '取消'
    })

    await request({
      url: '/history/watermarks',
      method: 'delete'
    })

    ElMessage.success('已清空所有记录')
    loadHistory()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空失败:', error)
      ElMessage.error('清空失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

// 重置筛选
const resetFilters = () => {
  filters.modelType = ''
  filters.startDate = ''
  filters.endDate = ''
  pagination.page = 1
  loadHistory()
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取模型名称
const getModelName = (modelType) => {
  const map = {
    'dwtdct': 'DWT-DCT',
    'stegastamp': 'StegaStamp',
    'treering': 'Tree-Ring',
    'stablesig': 'Stable Signature'
  }
  return map[modelType] || modelType
}

// 获取模型标签类型（已废弃，改用自定义样式）
const getModelTagType = (modelType) => {
  const map = {
    'dwtdct': 'primary',
    'stegastamp': 'success',
    'treering': 'warning',
    'stablesig': 'info'
  }
  return map[modelType] || ''
}

// 表格行类名
const tableRowClassName = ({ row, rowIndex }) => {
  if (rowIndex % 2 === 1) {
    return 'table-row-striped'
  }
  return ''
}

onMounted(() => {
  loadHistory()
  loadStats()
})
</script>

<style scoped>
.history-page {
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

.header-actions {
  display: flex;
  gap: 12px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  padding: 24px;
  border-radius: 16px;
  border: 1px solid rgba(0, 162, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 40px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  font-family: 'SF Mono', monospace;
}

.stat-value.color-1 {
  background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-value.color-2 {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-value.color-3 {
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-value.color-4 {
  background: linear-gradient(135deg, #ffe66d 0%, #ffa500 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

/* 筛选面板 */
.filter-panel {
  padding: 20px;
  margin-bottom: 24px;
  border-radius: 16px;
  border: 1px solid rgba(0, 162, 255, 0.2);
}

.filter-form {
  margin: 0;
}

/* 记录面板 */
.records-panel {
  padding: 24px;
  border-radius: 16px;
  border: 1px solid rgba(0, 162, 255, 0.2);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

@keyframes breathe {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 表格样式 - 确保深色背景和白色文字 */
.history-table {
  background: rgba(0, 18, 51, 0.6) !important;
  border-radius: 8px;
  overflow: hidden;
}

.history-table :deep(.el-table) {
  background: rgba(0, 18, 51, 0.6) !important;
  color: #ffffff !important;
}

.history-table :deep(.el-table__body-wrapper) {
  background: rgba(0, 18, 51, 0.6) !important;
}

.history-table :deep(.el-table__header-wrapper) {
  background: rgba(0, 18, 51, 0.7) !important;
}

.history-table :deep(.el-table__header) {
  background: rgba(0, 18, 51, 0.7) !important;
}

.history-table :deep(.el-table__header th) {
  background: rgba(0, 18, 51, 0.7) !important;
  color: #00d4ff !important;
  font-weight: 600;
  border-bottom: 1px solid rgba(0, 162, 255, 0.3);
}

/* 普通行 - 深色背景 */
.history-table :deep(.el-table__row) {
  background: rgba(0, 18, 51, 0.5) !important;
  color: #ffffff !important;
}

.history-table :deep(.el-table__row td) {
  background: rgba(0, 18, 51, 0.5) !important;
  border-bottom: 1px solid rgba(0, 162, 255, 0.15);
  color: #ffffff !important;
}

/* 条纹行（奇数行）- 更深的背景 */
.history-table :deep(.el-table--striped .el-table__body tr.el-table__row--striped) {
  background: rgba(0, 30, 70, 0.6) !important;
}

.history-table :deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: rgba(0, 30, 70, 0.6) !important;
  color: #ffffff !important;
}

/* 悬停效果 */
.history-table :deep(.el-table__row:hover) {
  background: rgba(0, 102, 255, 0.3) !important;
  box-shadow: 0 0 15px rgba(0, 162, 255, 0.2);
}

.history-table :deep(.el-table__row:hover td) {
  background: rgba(0, 102, 255, 0.3) !important;
  color: #ffffff !important;
}

.watermark-text {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
  color: #ffffff !important;
  font-weight: 500;
}

/* 强制覆盖 Element Plus 的默认白色背景 */
.history-table :deep(.el-table__body) {
  background: rgba(0, 18, 51, 0.6) !important;
}

.history-table :deep(.el-table__body tr) {
  background: rgba(0, 18, 51, 0.5) !important;
}

.history-table :deep(.el-table__body tr td) {
  background: inherit !important;
  color: #ffffff !important;
}

/* 表格单元格文字样式 - 确保所有文字清晰可见 */
.table-cell-text {
  color: #ffffff !important;
  font-weight: 400;
}

.text-muted {
  color: rgba(255, 255, 255, 0.4);
}

/* 表格单元格文字样式 - 确保所有文字清晰可见 */
.table-cell-text {
  color: #ffffff !important;
  font-weight: 400;
}

.text-success {
  color: #00ff88;
}

.text-danger {
  color: #ff6b6b;
}

/* 模型标签样式 - 科技风格 */
.model-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-align: center;
  min-width: 80px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.3s;
}

.model-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.model-dwtdct {
  background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
  color: #fff;
  border: 1px solid rgba(0, 212, 255, 0.5);
  box-shadow: 0 0 10px rgba(0, 102, 255, 0.3);
}

.model-stegastamp {
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  color: #001233;
  border: 1px solid rgba(0, 255, 136, 0.5);
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
}

.model-treering {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: #fff;
  border: 1px solid rgba(255, 107, 107, 0.5);
  box-shadow: 0 0 10px rgba(255, 107, 107, 0.3);
}

.model-stablesig {
  background: linear-gradient(135deg, #9d4edd 0%, #7b2cbf 100%);
  color: #fff;
  border: 1px solid rgba(157, 78, 221, 0.5);
  box-shadow: 0 0 10px rgba(157, 78, 221, 0.3);
}

/* 计数徽章样式 */
.count-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  min-width: 28px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.attack-badge {
  background: linear-gradient(135deg, #ff9500 0%, #ff6b00 100%);
  color: #fff;
  border: 1px solid rgba(255, 149, 0, 0.5);
  box-shadow: 0 0 8px rgba(255, 149, 0, 0.4);
}

.extraction-badge {
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  color: #001233;
  border: 1px solid rgba(0, 255, 136, 0.5);
  box-shadow: 0 0 8px rgba(0, 255, 136, 0.4);
}

/* 分页 */
.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

/* 详情对话框 */
.detail-content {
  padding: 20px 0;
}

.detail-section {
  margin-bottom: 32px;
}

.detail-section h3 {
  color: #00d4ff;
  margin-bottom: 16px;
  font-size: 18px;
}

.detail-section :deep(.el-descriptions) {
  background: rgba(0, 18, 51, 0.3);
}

.detail-section :deep(.el-descriptions__label) {
  color: rgba(255, 255, 255, 0.7);
}

.detail-section :deep(.el-descriptions__content) {
  color: #fff;
}
</style>

