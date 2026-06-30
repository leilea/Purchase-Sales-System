<template>
  <div class="sales">
    <div class="header">
      <h2>销售管理</h2>
      <div>
        <input ref="fileInput" type="file" accept=".xls,.xlsx" style="display:none" @change="handleFileUpload" />
        <el-button @click="handleExport" :disabled="selectedRows.length !== 1">导出</el-button>
        <el-button type="info" @click="handleCopy" :disabled="selectedRows.length !== 1">复制</el-button>
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
      <el-table ref="tableRef" :data="tableData" v-loading="loading" stripe border @selection-change="handleSelectionChange" @select="handleSelect">
        <el-table-column type="selection" width="55" :selectable="(row) => row.status === 'delivered'" />
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="order_no" label="订货单号" width="180" />
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
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'draft'" size="small" type="primary" @click="handleDeliver(row)">出库</el-button>
            <el-button v-if="row.status === 'draft'" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'draft'" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
            <el-button v-if="row.status === 'delivered'" size="small" @click="handleView(row)">查看</el-button>
            <el-button v-if="row.status === 'delivered'" size="small" type="warning" @click="handleWithdraw(row)">撤回</el-button>
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

    <el-dialog v-model="viewDialogVisible" title="订货单详情" width="900px">
      <el-form label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户">
              <span>{{ viewData.customer_name }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系人">
              <span>{{ viewData.contact_person }}</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系电话">
              <span>{{ viewData.contact_phone }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="业务负责人">
              <span>{{ viewData.business_manager }}</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="订单日期">
              <span>{{ viewData.order_date }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="订单金额">
              <span>{{ viewData.total_amount?.toFixed(2) }}</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="毛利润">
              <span>{{ viewData.gross_profit?.toFixed(2) }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-tag :type="getStatusType(viewData.status)">{{ getStatusText(viewData.status) }}</el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="付款方式">
          <span>{{ viewData.payment_method }}</span>
        </el-form-item>
        <el-form-item label="地址">
          <span>{{ viewData.address }}</span>
        </el-form-item>
        <el-form-item label="备注">
          <span>{{ viewData.remark }}</span>
        </el-form-item>
        <el-form-item label="商品明细">
          <el-table :data="viewData.items" border size="small" max-height="300">
            <el-table-column label="商品" width="140">
              <template #default="{ row }">{{ row.product_name }}</template>
            </el-table-column>
            <el-table-column label="规格" width="90">
              <template #default="{ row }">{{ row.spec }}</template>
            </el-table-column>
            <el-table-column label="材质等级" width="90">
              <template #default="{ row }">{{ row.material_grade }}</template>
            </el-table-column>
            <el-table-column label="数量" width="80">
              <template #default="{ row }">{{ row.quantity }}</template>
            </el-table-column>
            <el-table-column label="单价" width="80">
              <template #default="{ row }">{{ row.unit_price }}</template>
            </el-table-column>
            <el-table-column label="金额" width="90">
              <template #default="{ row }">{{ row.amount?.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="备注" min-width="100">
              <template #default="{ row }">{{ row.remark }}</template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSales, getSale, deleteSale, deliverSale, uploadSale, copySale, exportSale, withdrawSale } from '../api/modules/sales'

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

const viewDialogVisible = ref(false)
const viewData = reactive({
  id: null, order_no: '', customer_name: '', contact_person: '', contact_phone: '',
  business_manager: '', business_manager_phone: '', order_date: '', total_amount: 0,
  gross_profit: 0, status: '', remark: '', payment_method: '', address: '', items: []
})

const handleView = async (row) => {
  try {
    const res = await getSale(row.id)
    Object.assign(viewData, res.data)
    viewDialogVisible.value = true
  } catch (e) {
    console.error(e)
  }
}

const handleWithdraw = async (row) => {
  await ElMessageBox.confirm('确认撤回？撤回后该订货单将恢复为草稿状态。', '提示', { type: 'warning' })
  try {
    await withdrawSale(row.id)
    ElMessage.success('撤回成功')
    loadData()
  } catch (e) {
    console.error(e)
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
