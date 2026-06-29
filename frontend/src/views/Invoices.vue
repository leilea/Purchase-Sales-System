<template>
  <div class="invoices">
    <div class="header">
      <h2>发票管理</h2>
      <el-button type="primary" @click="handleAdd">新增发票</el-button>
    </div>
    <el-card>
      <el-form :inline="true" @keyup.enter="loadData" style="margin-bottom: 16px">
        <el-form-item label="订货单号">
          <el-input v-model="search.order_no" placeholder="请输入" clearable @clear="loadData" />
        </el-form-item>
        <el-form-item label="客户名称">
          <el-input v-model="search.customer_name" placeholder="请输入" clearable @clear="loadData" />
        </el-form-item>
        <el-form-item label="订单金额">
          <el-input-number v-model="search.total_amount_min" :min="0" :precision="2" placeholder="最低" style="width: 130px" controls-position="right" />
          <span style="margin: 0 8px">-</span>
          <el-input-number v-model="search.total_amount_max" :min="0" :precision="2" placeholder="最高" style="width: 130px" controls-position="right" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="order_no" label="订货单号" width="180" />
        <el-table-column prop="total_amount" label="订单金额" width="120" :formatter="(r) => formatAmount(r.total_amount)" />
        <el-table-column prop="customer_name" label="客户名称" width="150" />
        <el-table-column prop="tax_id" label="纳税人识别码" width="150" />
        <el-table-column prop="invoice_type" label="发票类型" width="100" />
        <el-table-column prop="invoice_amount" label="发票金额" width="120" :formatter="(r) => formatAmount(r.invoice_amount)" />
        <el-table-column prop="invoice_date" label="开票日期" width="120" />
        <el-table-column prop="attachment" label="发票附件" min-width="150">
          <template #default="{ row }">
            <el-link v-if="row.attachment" :href="row.attachment" target="_blank" type="primary">查看附件</el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
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
        @change="onPageChange"
        style="margin-top: 20px"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-form-item label="订货单号" prop="order_no">
          <el-input v-model="form.order_no" />
        </el-form-item>
        <el-form-item label="订单金额" prop="total_amount">
          <el-input-number v-model="form.total_amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="客户名称" prop="customer_name">
          <el-input v-model="form.customer_name" />
        </el-form-item>
        <el-form-item label="纳税人识别码" prop="tax_id">
          <el-input v-model="form.tax_id" />
        </el-form-item>
        <el-form-item label="发票类型" prop="invoice_type">
          <el-select v-model="form.invoice_type" placeholder="请选择" style="width: 100%">
            <el-option label="增值税专用发票" value="增值税专用发票" />
            <el-option label="增值税普通发票" value="增值税普通发票" />
            <el-option label="电子发票" value="电子发票" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="发票金额" prop="invoice_amount">
          <el-input-number v-model="form.invoice_amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="开票日期" prop="invoice_date">
          <el-date-picker v-model="form.invoice_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="发票附件" prop="attachment">
          <el-input v-model="form.attachment" placeholder="输入附件链接" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getInvoices, createInvoice, updateInvoice, deleteInvoice } from '../api/modules/invoices'

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const search = reactive({
  order_no: '',
  customer_name: '',
  total_amount_min: null,
  total_amount_max: null
})

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const form = reactive({
  id: null,
  order_no: '',
  total_amount: 0,
  customer_name: '',
  tax_id: '',
  invoice_type: '',
  invoice_amount: 0,
  invoice_date: '',
  attachment: '',
  remark: ''
})

const rules = {
  order_no: [{ required: true, message: '请输入订货单号', trigger: 'blur' }]
}

function formatAmount(val) {
  const num = Number(val) || 0
  return '¥' + num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

const buildParams = () => {
  const params = { page: pagination.page, per_page: pagination.pageSize }
  if (search.order_no) params.order_no = search.order_no
  if (search.customer_name) params.customer_name = search.customer_name
  if (search.total_amount_min !== null) params.total_amount_min = search.total_amount_min
  if (search.total_amount_max !== null) params.total_amount_max = search.total_amount_max
  return params
}

const loadData = async () => {
  loading.value = true
  pagination.page = 1
  try {
    const res = await getInvoices(buildParams())
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const onPageChange = async () => {
  loading.value = true
  try {
    const res = await getInvoices(buildParams())
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  Object.assign(form, { id: null, order_no: '', total_amount: 0, customer_name: '', tax_id: '', invoice_type: '', invoice_amount: 0, invoice_date: '', attachment: '', remark: '' })
  dialogTitle.value = '新增发票'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, row)
  dialogTitle.value = '编辑发票'
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定要删除该发票吗？', '提示', { type: 'warning' })
  try {
    await deleteInvoice(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    console.error(e)
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    if (form.id) {
      await updateInvoice(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createInvoice(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadData)
</script>

<style scoped>
.invoices .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.invoices h2 {
  margin: 0;
}
</style>
