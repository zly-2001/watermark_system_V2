<template>
  <div class="dashboard fade-in-up">
    <!-- 页面头部 -->
    <div class="page-header glass-effect">
      <div class="header-content">
        <div class="header-icon">📊</div>
        <div class="header-text">
          <h1 class="page-title">算法效能看板</h1>
          <p class="page-subtitle">PERFORMANCE ANALYTICS DASHBOARD</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button class="refresh-button" size="small" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- KPI 卡片 -->
    <el-row :gutter="24" class="kpi-row">
      <el-col :span="6" v-for="(kpi, index) in kpiData" :key="index">
        <div class="kpi-card glass-effect hover-card">
          <div class="kpi-icon">{{ kpi.icon }}</div>
          <div class="kpi-content">
            <div class="kpi-value" :class="`color-${index + 1}`">{{ kpi.value }}</div>
            <div class="kpi-label">{{ kpi.label }}</div>
            <div class="kpi-trend" :class="kpi.trend">
              <el-icon><Top v-if="kpi.trend === 'up'" /><Bottom v-else /></el-icon>
              {{ kpi.change }}
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="24" class="chart-row">
      <!-- 攻击强度 vs 提取准确率 -->
      <el-col :span="12">
        <div class="chart-panel glass-effect hover-card">
          <div class="chart-header">
            <div class="chart-title">攻击强度 vs 提取准确率</div>
            <el-tag size="small" effect="dark" class="tech-tag">实时监控</el-tag>
          </div>
          <div ref="accuracyChartRef" class="chart-container"></div>
        </div>
      </el-col>

      <!-- 算法对比 -->
      <el-col :span="12">
        <div class="chart-panel glass-effect hover-card">
          <div class="chart-header">
            <div class="chart-title">三种水印模型对比</div>
            <el-tag size="small" effect="dark" class="tech-tag" type="success">多模型评估</el-tag>
          </div>
          <div ref="comparisonChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 第二行图表 -->
    <el-row :gutter="24" class="chart-row">
      <!-- 攻击类型分布 -->
      <el-col :span="12">
        <div class="chart-panel glass-effect hover-card">
          <div class="chart-header">
            <div class="chart-title">攻击类型分布</div>
            <el-tag size="small" effect="dark" class="tech-tag" type="warning">多维分析</el-tag>
          </div>
          <div ref="attackTypeChartRef" class="chart-container"></div>
        </div>
      </el-col>

      <!-- 时间序列趋势 -->
      <el-col :span="12">
        <div class="chart-panel glass-effect hover-card">
          <div class="chart-header">
            <div class="chart-title">性能趋势分析</div>
            <el-tag size="small" effect="dark" class="tech-tag" type="info">7天数据</el-tag>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 数据统计面板 -->
    <div class="stats-panel glass-effect">
      <div class="panel-header">
        <div class="panel-title">📈 核心指标统计</div>
      </div>
      <el-row :gutter="24" class="stats-content">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">测试场景</div>
            <div class="stat-value-text">AIGC 重绘攻击</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">测试样本</div>
            <div class="stat-value-text">1,000 张图片</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均准确率</div>
            <div class="stat-value-highlight success">94.5%</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">LSB 对比</div>
            <div class="stat-value-highlight warning">62.3%</div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { Refresh, Top, Bottom } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const accuracyChartRef = ref(null)
const comparisonChartRef = ref(null)
const attackTypeChartRef = ref(null)
const trendChartRef = ref(null)

// KPI 数据
const kpiData = ref([
  { icon: '🎯', label: '总体准确率', value: '94.5%', change: '+2.3%', trend: 'up' },
  { icon: '⚡', label: '处理速度', value: '0.8s', change: '-0.1s', trend: 'up' },
  { icon: '🛡️', label: '鲁棒性指数', value: '9.2', change: '+0.4', trend: 'up' },
  { icon: '💎', label: '图像质量', value: '42.3dB', change: '+1.2dB', trend: 'up' }
])

// ECharts 通用配置
const getChartTheme = () => ({
  backgroundColor: 'transparent',
  textStyle: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontFamily: 'SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif'
  },
  grid: {
    left: '10%',
    right: '10%',
    top: '15%',
    bottom: '15%',
    containLabel: true
  }
})

// 攻击强度 vs 准确率
const initAccuracyChart = () => {
  const chart = echarts.init(accuracyChartRef.value)
  const option = {
    ...getChartTheme(),
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(13, 27, 62, 0.95)',
      borderColor: 'rgba(0, 162, 255, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#fff' },
      formatter: (params) => {
        let html = `<div style="padding: 8px;">`
        html += `<div style="margin-bottom: 8px; font-weight: 600;">${params[0].axisValue}</div>`
        params.forEach(item => {
          html += `<div style="margin: 4px 0;">
                    <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${item.color};margin-right:8px;"></span>
                    ${item.seriesName}: <span style="font-weight: 600;">${item.value}%</span>
                  </div>`
        })
        html += `</div>`
        return html
      }
    },
    legend: {
      data: ['DWT-DCT', 'StegaStamp', 'Tree-Ring'],
      textStyle: { color: 'rgba(255, 255, 255, 0.8)' },
      top: '5%'
    },
    xAxis: {
      type: 'category',
      data: ['无攻击', '轻度', '中度', '重度', 'AIGC重绘'],
      axisLine: { lineStyle: { color: 'rgba(0, 162, 255, 0.3)' } },
      axisLabel: { color: 'rgba(255, 255, 255, 0.6)' }
    },
    yAxis: {
      type: 'value',
      name: '准确率 (%)',
      nameTextStyle: { color: 'rgba(255, 255, 255, 0.6)' },
      axisLine: { lineStyle: { color: 'rgba(0, 162, 255, 0.3)' } },
      splitLine: { lineStyle: { color: 'rgba(0, 162, 255, 0.1)' } },
      axisLabel: { color: 'rgba(255, 255, 255, 0.6)' }
    },
    series: [
      {
        name: 'DWT-DCT',
        type: 'line',
        data: [98.5, 95.2, 88.7, 75.3, 8.2],
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: '#00d4ff' },
        itemStyle: { color: '#00d4ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.05)' }
          ])
        }
      },
      {
        name: 'StegaStamp',
        type: 'line',
        data: [99.2, 97.8, 94.5, 89.2, 78.1],
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: '#00a2ff' },
        itemStyle: { color: '#00a2ff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 162, 255, 0.4)' },
            { offset: 1, color: 'rgba(0, 162, 255, 0.05)' }
          ])
        }
      },
      {
        name: 'Tree-Ring',
        type: 'line',
        data: [99.5, 98.7, 96.8, 93.5, 92.1],
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3, color: '#00ff88' },
        itemStyle: { color: '#00ff88' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 255, 136, 0.4)' },
            { offset: 1, color: 'rgba(0, 255, 136, 0.05)' }
          ])
        }
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

// 算法对比雷达图
const initComparisonChart = () => {
  const chart = echarts.init(comparisonChartRef.value)
  const option = {
    ...getChartTheme(),
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(13, 27, 62, 0.95)',
      borderColor: 'rgba(0, 162, 255, 0.3)',
      borderWidth: 1
    },
    legend: {
      data: ['DWT-DCT', 'StegaStamp', 'Tree-Ring'],
      textStyle: { color: 'rgba(255, 255, 255, 0.8)' },
      top: '5%'
    },
    radar: {
      indicator: [
        { name: 'AIGC抵抗', max: 100 },
        { name: '传统抗攻击', max: 100 },
        { name: '隐蔽性', max: 100 },
        { name: '速度', max: 100 },
        { name: '图像质量', max: 100 }
      ],
      splitArea: {
        areaStyle: {
          color: ['rgba(0, 102, 255, 0.05)', 'rgba(0, 102, 255, 0.1)']
        }
      },
      axisLine: { lineStyle: { color: 'rgba(0, 162, 255, 0.3)' } },
      splitLine: { lineStyle: { color: 'rgba(0, 162, 255, 0.2)' } },
      name: { textStyle: { color: 'rgba(255, 255, 255, 0.8)' } }
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: [10, 88, 95, 98, 92],
          name: 'DWT-DCT',
          itemStyle: { color: '#00d4ff' },
          areaStyle: { color: 'rgba(0, 212, 255, 0.2)' }
        },
        {
          value: [78, 92, 85, 75, 88],
          name: 'StegaStamp',
          itemStyle: { color: '#00a2ff' },
          areaStyle: { color: 'rgba(0, 162, 255, 0.2)' }
        },
        {
          value: [95, 85, 82, 70, 90],
          name: 'Tree-Ring',
          itemStyle: { color: '#00ff88' },
          areaStyle: { color: 'rgba(0, 255, 136, 0.2)' }
        }
      ]
    }]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

// 攻击类型分布饼图
const initAttackTypeChart = () => {
  const chart = echarts.init(attackTypeChartRef.value)
  const option = {
    ...getChartTheme(),
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}次 ({d}%)',
      backgroundColor: 'rgba(13, 27, 62, 0.95)',
      borderColor: 'rgba(0, 162, 255, 0.3)',
      borderWidth: 1
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: { color: 'rgba(255, 255, 255, 0.8)' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: 'rgba(0, 18, 51, 0.8)',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold',
          color: '#fff'
        }
      },
      data: [
        { value: 450, name: 'JPEG 压缩', itemStyle: { color: '#00a2ff' } },
        { value: 280, name: 'AIGC 重绘', itemStyle: { color: '#00d4ff' } },
        { value: 150, name: '几何变换', itemStyle: { color: '#0066ff' } },
        { value: 80, name: '噪声添加', itemStyle: { color: '#00ffaa' } },
        { value: 40, name: '其他', itemStyle: { color: '#ff6b6b' } }
      ]
    }]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

// 性能趋势图
const initTrendChart = () => {
  const chart = echarts.init(trendChartRef.value)
  const option = {
    ...getChartTheme(),
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(13, 27, 62, 0.95)',
      borderColor: 'rgba(0, 162, 255, 0.3)',
      borderWidth: 1,
      axisPointer: {
        type: 'cross',
        crossStyle: { color: 'rgba(0, 162, 255, 0.5)' }
      }
    },
    legend: {
      data: ['准确率', '处理量'],
      textStyle: { color: 'rgba(255, 255, 255, 0.8)' },
      top: '5%'
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: { lineStyle: { color: 'rgba(0, 162, 255, 0.3)' } },
      axisLabel: { color: 'rgba(255, 255, 255, 0.6)' }
    },
    yAxis: [
      {
        type: 'value',
        name: '准确率 (%)',
        position: 'left',
        nameTextStyle: { color: 'rgba(255, 255, 255, 0.6)' },
        axisLine: { lineStyle: { color: 'rgba(0, 162, 255, 0.3)' } },
        splitLine: { lineStyle: { color: 'rgba(0, 162, 255, 0.1)' } },
        axisLabel: { color: 'rgba(255, 255, 255, 0.6)' }
      },
      {
        type: 'value',
        name: '处理量',
        position: 'right',
        nameTextStyle: { color: 'rgba(255, 255, 255, 0.6)' },
        axisLine: { lineStyle: { color: 'rgba(0, 162, 255, 0.3)' } },
        splitLine: { show: false },
        axisLabel: { color: 'rgba(255, 255, 255, 0.6)' }
      }
    ],
    series: [
      {
        name: '准确率',
        type: 'line',
        data: [93.2, 94.1, 93.8, 94.5, 95.2, 94.8, 94.5],
        smooth: true,
        lineStyle: { width: 3, color: '#00a2ff' },
        itemStyle: { color: '#00a2ff' }
      },
      {
        name: '处理量',
        type: 'bar',
        yAxisIndex: 1,
        data: [120, 145, 138, 165, 180, 172, 158],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.6)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.2)' }
          ]),
          borderRadius: [6, 6, 0, 0]
        }
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const refreshData = () => {
  ElMessage.success('数据已刷新')
  // 这里可以添加实际的数据刷新逻辑
}

onMounted(() => {
  setTimeout(() => {
    initAccuracyChart()
    initComparisonChart()
    initAttackTypeChart()
    initTrendChart()
  }, 100)
})
</script>

<style scoped>
.dashboard {
  width: 100%;
  max-width: 1800px;
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

.refresh-button {
  background: rgba(0, 102, 255, 0.2);
  border: 1px solid rgba(0, 162, 255, 0.3);
  color: #00a2ff;
  transition: all 0.3s;
}

.refresh-button:hover {
  background: rgba(0, 102, 255, 0.3);
  border-color: rgba(0, 162, 255, 0.5);
  transform: translateY(-2px);
}

/* KPI 卡片 */
.kpi-row {
  margin-bottom: 24px;
}

.kpi-card {
  padding: 24px;
  border-radius: 16px;
  border: 1px solid rgba(0, 162, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 20px;
  min-height: 120px;
}

.kpi-icon {
  font-size: 48px;
  filter: drop-shadow(0 0 15px rgba(0, 162, 255, 0.4));
}

.kpi-content {
  flex: 1;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  font-family: 'SF Mono', monospace;
  margin-bottom: 4px;
}

.kpi-value.color-1 {
  background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.kpi-value.color-2 {
  background: linear-gradient(135deg, #00ffaa 0%, #00a2ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.kpi-value.color-3 {
  background: linear-gradient(135deg, #ff6b6b 0%, #ffa500 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.kpi-value.color-4 {
  background: linear-gradient(135deg, #a78bfa 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.kpi-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 8px;
}

.kpi-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(0, 255, 136, 0.1);
  color: #00ff88;
}

.kpi-trend.up {
  background: rgba(0, 255, 136, 0.1);
  color: #00ff88;
}

.kpi-trend.down {
  background: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
}

/* 图表区域 */
.chart-row {
  margin-bottom: 24px;
}

.chart-panel {
  padding: 24px;
  border-radius: 16px;
  border: 1px solid rgba(0, 162, 255, 0.2);
  min-height: 420px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(0, 162, 255, 0.1);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #00d4ff;
}

.tech-tag {
  background: rgba(0, 102, 255, 0.2);
  border: 1px solid rgba(0, 162, 255, 0.3);
  color: #00d4ff;
  border-radius: 6px;
}

.chart-container {
  width: 100%;
  height: 320px;
}

/* 数据统计面板 */
.stats-panel {
  padding: 28px;
  border-radius: 16px;
  border: 1px solid rgba(0, 162, 255, 0.2);
  margin-top: 24px;
}

.panel-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(0, 162, 255, 0.1);
}

.panel-title {
  font-size: 18px;
  font-weight: 600;
  color: #00d4ff;
}

.stats-content {
  padding: 16px 0;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 12px;
}

.stat-value-text {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.stat-value-highlight {
  font-size: 28px;
  font-weight: 700;
  font-family: 'SF Mono', monospace;
}

.stat-value-highlight.success {
  background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-value-highlight.warning {
  background: linear-gradient(135deg, #ffa500 0%, #ff6b6b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
