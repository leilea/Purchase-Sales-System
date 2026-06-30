<template>
  <div class="dashboard">
    <div class="header-row">
      <h2>仪表盘</h2>
      <el-date-picker
        v-model="currentMonth"
        type="month"
        value-format="YYYY-MM"
        placeholder="选择月份"
        style="width: 180px"
      />
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#409eff"><Coin /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ formatAmount(stats.monthly.total_amount) }}</div>
              <div class="stat-label">当月订单金额统计</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#67c23a"><TrendCharts /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ formatAmount(stats.monthly.gross_profit) }}</div>
              <div class="stat-label">当月毛利润统计</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#e6a23c"><UserFilled /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.monthly.new_customers }}</div>
              <div class="stat-label">当月新增客户统计</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <span>当年每月趋势</span>
      </template>
      <div ref="chartRef" style="height: 360px"></div>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>当月客户订单排名</span>
          </template>
          <el-table :data="stats.monthly_customer_ranking.slice(0, 10)" size="small" max-height="360">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="customer_name" label="客户名称" />
            <el-table-column prop="total_amount" label="订单金额" :formatter="(r) => formatAmount(r.total_amount)" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>当年客户订单排名</span>
          </template>
          <el-table :data="stats.yearly_customer_ranking.slice(0, 10)" size="small" max-height="360">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="customer_name" label="客户名称" />
            <el-table-column prop="total_amount" label="订单金额" :formatter="(r) => formatAmount(r.total_amount)" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { Coin, TrendCharts, UserFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getDashboardStats } from '../api/modules/dashboard'


const currentMonth = ref(new Date().toISOString().slice(0, 7))
const chartRef = ref(null)
let chartInstance = null

const stats = ref({
  monthly: { total_amount: 0, gross_profit: 0, new_customers: 0 },
  yearly: [],
  monthly_customer_ranking: [],
  yearly_customer_ranking: []
})

function formatAmount(val) {
  const num = Number(val) || 0
  return '¥' + num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

function initChart() {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

function updateChart() {
  if (!chartInstance) return
  const months = stats.value.yearly.map((_, i) => `${i + 1}月`)
  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      valueFormatter: (v) => '¥' + Number(v).toLocaleString()
    },
    legend: {
      data: ['订单金额', '毛利润'],
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (v) => '¥' + (v >= 10000 ? (v / 10000).toFixed(1).replace(/\.0$/, '') + 'w' : v)
      }
    },
    series: [
      {
        name: '订单金额',
        type: 'bar',
        data: stats.value.yearly.map((d) => d.total_amount),
        itemStyle: { color: '#409eff' }
      },
      {
        name: '毛利润',
        type: 'bar',
        data: stats.value.yearly.map((d) => d.gross_profit),
        itemStyle: { color: '#67c23a' }
      }
    ]
  })
}

async function loadData() {
  try {
    const sRes = await getDashboardStats({ month: currentMonth.value })
    stats.value = sRes.data
    await nextTick()
    updateChart()
  } catch (e) {
    console.error(e)
  }
}

watch(currentMonth, loadData)

onMounted(async () => {
  await loadData()
  await nextTick()
  initChart()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.dashboard h2 {
  margin: 0;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}
.stat-icon {
  font-size: 48px;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
}
.stat-label {
  color: #999;
  font-size: 14px;
}
</style>
