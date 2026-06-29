<template>
  <div class="customers">
    <div class="header">
      <h2>客户管理</h2>
      <el-button type="primary" @click="handleAdd">新增客户</el-button>
    </div>
    <div class="search-bar">
      <el-form :model="searchForm" inline>
        <el-form-item label="客户名称">
          <el-input v-model="searchForm.name" placeholder="客户名称" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="searchForm.contact" placeholder="联系人" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="searchForm.phone" placeholder="联系电话" clearable style="width: 160px" />
        </el-form-item>
      </el-form>
      <div class="search-actions">
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
    </div>
    <el-card style="width: 100%">
      <el-table :data="tableData" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="name" label="客户名称" min-width="130" />
        <el-table-column prop="level" label="等级" width="80" />
        <el-table-column prop="contact" label="联系人" min-width="90" />
        <el-table-column prop="phone" label="联系电话" min-width="130" />
        <el-table-column prop="company_name" label="公司全称" min-width="180" />
        <el-table-column prop="tax_id" label="纳税人识别号" min-width="150" />
        <el-table-column prop="invoice_type" label="发票类型" min-width="120" />
        <el-table-column prop="status" label="合作状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '合作中' : '已停止' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 0" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户编码">
              <el-input v-model="form.code" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户名称" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户等级" prop="level">
              <el-select v-model="form.level" style="width: 100%">
                <el-option label="A级" value="A级" />
                <el-option label="B级" value="B级" />
                <el-option label="C级" value="C级" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发票类型" prop="invoice_type">
              <el-select v-model="form.invoice_type" style="width: 100%">
                <el-option label="增值税专用发票" value="增值税专用发票" />
                <el-option label="增值税普通发票" value="增值税普通发票" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact">
              <el-input v-model="form.contact" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="联系地址" prop="address">
          <el-input v-model="form.address" type="textarea" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="公司全称" prop="company_name">
              <el-input v-model="form.company_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="纳税人识别号" prop="tax_id">
              <el-input v-model="form.tax_id" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开户行" prop="bank_name">
              <el-input v-model="form.bank_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行账号" prop="bank_account">
              <el-input v-model="form.bank_account" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="合作状态" prop="status">
          <el-switch
            v-model="form.status"
            :active-value="1"
            :inactive-value="0"
            active-text="合作中"
            inactive-text="已停止"
          />
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
import { getCustomers, createCustomer, updateCustomer, deleteCustomer } from '../api/modules/customers'
import axios from '../api/index'

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const searchForm = reactive({
  name: '',
  contact: '',
  phone: ''
})

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const form = reactive({
  id: null,
  code: '',
  name: '',
  level: 'A级',
  contact: '',
  phone: '',
  address: '',
  company_name: '',
  tax_id: '',
  bank_name: '',
  bank_account: '',
  invoice_type: '',
  status: 1
})

const rules = {
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  contact: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.pageSize
    }
    if (searchForm.name) params.name = searchForm.name
    if (searchForm.contact) params.contact = searchForm.contact
    if (searchForm.phone) params.phone = searchForm.phone

    const res = await getCustomers(params)
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.name = ''
  searchForm.contact = ''
  searchForm.phone = ''
  pagination.page = 1
  loadData()
}

const fetchNextCode = async () => {
  try {
    const res = await axios.get('/customers/code')
    form.code = res.data.code
  } catch (e) {
    console.error(e)
  }
}

const handleAdd = () => {
  Object.assign(form, {
    id: null, code: '', name: '', level: 'A级', contact: '', phone: '',
    address: '', company_name: '', tax_id: '', bank_name: '', bank_account: '',
    invoice_type: '', status: 1
  })
  dialogTitle.value = '新增客户'
  dialogVisible.value = true
  fetchNextCode()
}

const handleEdit = (row) => {
  Object.assign(form, row)
  dialogTitle.value = '编辑客户'
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定要删除该客户吗？', '提示', { type: 'warning' })
  try {
    await deleteCustomer(row.id)
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
      await updateCustomer(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createCustomer(form)
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
.customers {
  margin: -20px;
  width: calc(100% + 40px);
}
.customers .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 20px;
}
.customers h2 {
  margin: 0;
}
.customers .search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #fff;
  margin-bottom: 0;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
.customers .search-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.customers .el-card {
  border-radius: 0;
}
.customers .el-card :deep(.el-card__body) {
  padding: 20px;
}
</style>
