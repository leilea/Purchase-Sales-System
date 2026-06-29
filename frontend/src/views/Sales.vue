<template>
  <div class="sales">
    <div class="header">
      <h2>销售管理</h2>
      <div>
        <input ref="fileInput" type="file" accept=".xls,.xlsx" style="display:none" @change="handleFileUpload" />
        <el-button type="warning" @click="handleExport" :disabled="selectedRows.length !== 1">导出</el-button>
        <el-button type="warning" @click="handleCopy" :disabled="selectedRows.length !== 1">复制</el-button>
        <el-button type="success" @click="$refs.fileInput.click()">导入订货单</el-button>
        <el-button type="primary" @click="handleAdd">新建订货单</el-button>
      </div>
    </div>
    <el-card style="margin-bottom: 16px">
      <el-form :inline="true" :model="filters">
        <el-form-item label="订货单号">
          <el-input v-model="filters.order_no" placeholder="订货单号" clearable @clear="loadData" @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="客户">
          <el-input v-model="filters.customer_name" placeholder="客户名称" clearable @clear="loadData" @keyup.enter="loadData" />
        </el-form-item>
        <el-form-item label="订单日期">
          <el-date-picker v-model="filters.dateRange" type="daterange" value-format="YYYY-MM-DD" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" @change="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-card>
      <el-table ref="tableRef" :data="tableData" v-loading="loading" stripe @selection-change="handleSelectionChange" @select="handleSelect">
        <el-table-column type="selection" width="55" :selectable="(row) => row.status === 'delivered'" />
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="order_no" label="订货单号" width="150" />
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="order_date" label="订单日期" width="120" />
        <el-table-column prop="total_amount" label="订单金额" width="120" />
        <el-table-column prop="gross_profit" label="毛利润" width="120" />
        <el-table-column label="毛利率" width="100">
          <template #default="{ row }">
            <span>{{ row.total_amount && Number(row.total_amount) ? (Number(row.gross_profit) / Number(row.total_amount) * 100).toFixed(1) + '%' : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'draft'" size="small" type="primary" @click="handleDeliver(row)">出库</el-button>
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="loadData"
        style="margin-top: 20px"
      />
    </el-card>


  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSales, deleteSale, deliverSale, uploadSale, copySale, exportSale } from '../api/modules/sales'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const selectedRows = ref([])
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const filters = reactive({ order_no: '', customer_name: '', dateRange: null })

const tableRef = ref()
const fileInput = ref()

const getStatusType = (status) => {
  const types = { draft: 'info', confirmed: 'warning', delivered: 'success', cancelled: 'danger' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { draft: '草稿', confirmed: '已确认', delivered: '已出库', cancelled: '已取消' }
  return texts[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: pagination.page, per_page: pagination.pageSize }
    if (filters.order_no) params.order_no = filters.order_no
    if (filters.customer_name) params.customer_name = filters.customer_name
    if (filters.dateRange) {
      params.start_date = filters.dateRange[0]
      params.end_date = filters.dateRange[1]
    }
    const res = await getSales(params)
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.order_no = ''
  filters.customer_name = ''
  filters.dateRange = null
  pagination.page = 1
  loadData()
}

const handleAdd = () => {
  router.push('/sales/create')
}

const handleFileUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  try {
    await uploadSale(file)
    ElMessage.success('导入成功')
    loadData()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '导入失败')
  } finally {
    fileInput.value.value = ''
  }
}

const handleEdit = (row) => {
  router.push(`/sales/${row.id}/edit`)
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定要删除该订单吗？', '提示', { type: 'warning' })
  try {
    await deleteSale(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    console.error(e)
  }
}

const handleDeliver = async (row) => {
  await ElMessageBox.confirm('确认出库？', '提示', { type: 'info' })
  try {
    await deliverSale(row.id)
    ElMessage.success('出库成功')
    loadData()
  } catch (e) {
    console.error(e)
  }
}

const handleSelect = (selection, row) => {
  if (selection.some(r => r.id === row.id) && selection.length > 1) {
    const toRemove = selection.filter(r => r.id !== row.id)
    toRemove.forEach(r => tableRef.value.toggleRowSelection(r, false))
  }
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const handleExport = async () => {
  if (selectedRows.value.length !== 1) return
  try {
    const res = await exportSale(selectedRows.value[0].id)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `订货单_${selectedRows.value[0].order_no}.xlsx`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

const handleCopy = async () => {
  if (selectedRows.value.length !== 1) return
  await ElMessageBox.confirm('确定复制该订货单吗？', '提示', { type: 'info' })
  try {
    await copySale(selectedRows.value[0].id)
    ElMessage.success('复制成功')
    loadData()
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.sales .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.sales h2 {
  margin: 0;
}
</style>
