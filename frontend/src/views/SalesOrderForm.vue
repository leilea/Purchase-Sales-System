<template>
  <div class="sales-order-form">
    <div class="header">
      <h2>{{ isEdit ? '编辑销售订单' : '新建订单' }}</h2>
      <div class="header-actions">
        <el-button type="info" @click="goBack">返回</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </div>
    </div>
    <el-card>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="客户" prop="customer_id">
              <el-select v-model="form.customer_id" placeholder="请选择客户" style="width: 100%" @change="onCustomerChange">
                <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系人">
              <el-input v-model="form.contact_person" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系电话">
              <el-input v-model="form.contact_phone" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="业务负责人">
              <el-input v-model="form.business_manager" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="开发票">
              <el-switch v-model="form.invoice_required" :active-value="1" :inactive-value="0" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="发票税率">
              <el-select v-model="form.invoice_tax_rate" placeholder="请选择" style="width: 100%">
                <el-option label="13%" value="13%" />
                <el-option label="9%" value="9%" />
                <el-option label="6%" value="6%" />
                <el-option label="3%" value="3%" />
                <el-option label="0%" value="0%" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="业务联系电话">
              <el-input v-model="form.business_manager_phone" />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="地址" prop="address">
              <el-input v-model="form.address" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="运费承担方">
              <el-select v-model="form.freight_responsible" placeholder="请选择" style="width: 100%">
                <el-option label="己方承担" value="己方承担" />
                <el-option label="客户承担" value="客户承担" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="运费">
              <el-input-number v-model="form.freight" :min="0" :precision="2" style="width: 100%" @change="calcTotal" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="订单金额">
              <span style="font-size: 18px; font-weight: bold; color: #f56c6c">{{ totalAmount.toFixed(2) }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="付款方式">
              <el-input v-model="form.payment_method" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="订单日期" prop="order_date">
              <el-date-picker v-model="form.order_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="采购金额">
              <span style="font-size: 18px; font-weight: bold; color: #f56c6c">{{ costAmount.toFixed(2) }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="物流与杂费">
              <span style="font-size: 18px; font-weight: bold; color: #f56c6c">{{ logisticsTotal.toFixed(2) }}</span>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="毛利润">
              <span style="font-size: 18px; font-weight: bold; color: #f56c6c">{{ grossProfit.toFixed(2) }}</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
        <el-tabs type="border-card" style="margin-top: 22px;">
          <el-tab-pane label="订单信息">
            <div style="overflow-x: auto">
              <el-table :data="displayItems" border size="small" style="width: 100%">
                <el-table-column label="序号" min-width="50" type="index" />
                <el-table-column label="产品名称" min-width="200">
                  <template #default="{ row, $index }">
                    <div style="display: flex; gap: 4px;">
                      <el-input v-model="row.product_name" size="small" placeholder="选择商品" style="flex: 1;" />
                      <el-button size="small" icon="Search" @click="openProductSelector($index + (itemPage - 1) * pageSize)" />
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="规格" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.spec" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="材质等级" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.material_grade" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="表面处理" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.surface_treatment" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="件装数量" min-width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.package_quantity" maxlength="20" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="件数" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.package_count" maxlength="20" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="配套" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.matching" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="计量单位" min-width="80">
                  <template #default="{ row }">
                    <el-input v-model="row.unit_name" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="数量" min-width="110">
                  <template #default="{ row }">
                    <el-input-number v-model="row.quantity" :min="0.01" :precision="2" size="small" style="width: 100%" @change="calcItemAmount(row)" />
                  </template>
                </el-table-column>
                <el-table-column label="单价" min-width="110">
                  <template #default="{ row }">
                    <el-input-number v-model="row.unit_price" :min="0" :precision="2" size="small" style="width: 100%" @change="calcItemAmount(row)" />
                  </template>
                </el-table-column>
                <el-table-column label="金额" min-width="110">
                  <template #default="{ row }">
                    <span style="color: #f56c6c">{{ row.amount?.toFixed(2) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="备注" min-width="130">
                  <template #default="{ row }">
                    <el-input v-model="row.remark" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" min-width="60" fixed="right">
                  <template #default="{ $index }">
                    <el-button type="danger" size="small" @click="deleteItem($index)">删除</el-button>
                  </template>
                </el-table-column>
                <template #append>
                  <div style="padding: 8px; border-top: 1px solid #ebeef5">
                    <el-button type="primary" size="small" @click="addItem">添加商品</el-button>
                  </div>
                </template>
              </el-table>
              <el-pagination
                v-if="form.items.length > 10"
                v-model:current-page="itemPage"
                :page-size="10"
                :total="form.items.length"
                layout="total, prev, pager, next"
                small
                style="margin-top: 10px; justify-content: center"
              />
            </div>
          </el-tab-pane>
          <el-tab-pane label="供应商/委外加工信息">
            <div style="overflow-x: auto">
              <el-table :data="displaySuppliers" border size="small" style="width: 100%">
                <el-table-column label="序号" min-width="50" type="index" />
                <el-table-column label="供应商" min-width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.supplier" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="供应产品" min-width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.product" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="规格" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.spec" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="等级" min-width="80">
                  <template #default="{ row }">
                    <el-input v-model="row.grade" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="表面处理" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.surface_treatment" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="数量" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.quantity" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="总重" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.total_weight" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="单重" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.unit_weight" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="价格" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.price" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="包装" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.packaging" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="税费" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.tax" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="成本小计" min-width="100">
                  <template #default="{ row }">
                    <span>{{ ((row.price || 0) * (row.quantity || 0) + (row.tax ? parseFloat(row.tax) : 0)).toFixed(2) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="操作" min-width="60" fixed="right">
                  <template #default="{ $index }">
                    <el-button type="danger" size="small" @click="deleteSupplier($index)">删除</el-button>
                  </template>
                </el-table-column>
                <template #append>
                  <div style="padding: 8px; border-top: 1px solid #ebeef5">
                    <el-button type="primary" size="small" @click="addSupplier">添加供货信息</el-button>
                  </div>
                </template>
              </el-table>
              <el-pagination
                v-if="form.suppliers.length > 10"
                v-model:current-page="supplierPage"
                :page-size="10"
                :total="form.suppliers.length"
                layout="total, prev, pager, next"
                small
                style="margin-top: 10px; justify-content: center"
              />
            </div>
          </el-tab-pane>
          <el-tab-pane label="物流与杂费">
            <div style="overflow-x: auto">
              <el-table :data="form.logistics" border size="small" style="width: 100%">
                <el-table-column label="序号" min-width="50" type="index" />
                <el-table-column label="物流公司" min-width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.company" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="联系人电话" min-width="130">
                  <template #default="{ row }">
                    <el-input v-model="row.contact_phone" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="开始时间" min-width="160">
                  <template #default="{ row }">
                    <el-date-picker v-model="row.start_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
                  </template>
                </el-table-column>
                <el-table-column label="完成时间" min-width="160">
                  <template #default="{ row }">
                    <el-date-picker v-model="row.end_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
                  </template>
                </el-table-column>
                <el-table-column label="运输情况" min-width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.transport_status" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="运费" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.freight" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="包装费" min-width="110">
                  <template #default="{ row }">
                    <el-input v-model="row.forklift_fee" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="其它费用" min-width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.other_fee" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="杂费小计" min-width="100">
                  <template #default="{ row }">
                    <span>{{ (parseFloat(row.freight || 0) + parseFloat(row.forklift_fee || 0) + parseFloat(row.other_fee || 0)).toFixed(2) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="备注" min-width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.remark" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" min-width="60" fixed="right">
                  <template #default="{ $index }">
                    <el-button type="danger" size="small" @click="form.logistics.splice($index, 1)">删除</el-button>
                  </template>
                </el-table-column>
                <template #append>
                  <div style="padding: 8px; border-top: 1px solid #ebeef5">
                    <el-button type="primary" size="small" @click="addLogistics">添加物流</el-button>
                  </div>
                </template>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-form>
    </el-card>

    <el-dialog v-model="productDialogVisible" title="选择商品" width="900px">
      <div style="display: flex; gap: 20px;">
        <div style="flex: 1; min-width: 0;">
          <el-form inline :model="dialogSearch" style="margin-bottom: 12px;">
            <el-form-item label="商品名称">
              <el-input v-model="dialogSearch.keyword" placeholder="商品名称" clearable style="width: 200px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="searchDialogProducts">查询</el-button>
              <el-button @click="resetDialogSearch">重置</el-button>
            </el-form-item>
          </el-form>
          <el-table ref="productTableRef" :data="dialogProducts" v-loading="dialogLoading" stripe border @selection-change="onDialogSelectionChange">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="name" label="商品名称" min-width="140" />
            <el-table-column prop="spec" label="规格型号" width="120" />
            <el-table-column prop="material_grade" label="材质等级" width="100" />
            <el-table-column prop="surface_treatment" label="表面处理" width="130" />
            <el-table-column prop="unit_name" label="计量单位" width="100" />
          </el-table>
          <el-pagination
            v-model:current-page="dialogPage"
            :page-size="10"
            :total="dialogTotal"
            layout="total, prev, pager, next"
            style="margin-top: 10px; justify-content: center"
            @current-change="loadDialogProducts"
          />
        </div>
        <div style="width: 200px; border-left: 1px solid #ebeef5; padding-left: 16px;">
          <h4 style="margin-top: 0;">已选商品</h4>
          <div v-if="dialogSelectedProducts.length === 0" style="color: #999; font-size: 13px;">暂无选择</div>
          <el-tag
            v-for="p in dialogSelectedProducts"
            :key="p.id"
            closable
            @close="removeDialogSelection(p)"
            style="display: block; margin-bottom: 8px;"
          >
            {{ p.name }}
          </el-tag>
        </div>
      </div>
      <template #footer>
        <el-button @click="productDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmDialogSelection">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSale, createSale, updateSale } from '../api/modules/sales'
import { getCustomers } from '../api/modules/customers'
import { getProducts } from '../api/modules/products'

const route = useRoute()
const router = useRouter()
const itemPage = ref(1)
const supplierPage = ref(1)
const pageSize = 10

const isEdit = computed(() => !!route.params.id)

const customers = ref([])
const formRef = ref()
const form = reactive({
  id: null,
  customer_id: null,
  contact_person: '',
  contact_phone: '',
  business_manager: '',
  business_manager_phone: '',
  address: '',
  freight_responsible: '',
  freight: 0,
  payment_method: '',
  invoice_tax_rate: '',
  invoice_required: 0,
  order_date: '',
  remark: '',
  items: [],
  suppliers: [],
  logistics: []
})

const rules = {
  customer_id: [{ required: true, message: '请选择客户', trigger: 'change' }],
  order_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

const displayItems = computed(() => {
  const start = (itemPage.value - 1) * pageSize
  return form.items.slice(start, start + pageSize)
})

const displaySuppliers = computed(() => {
  const start = (supplierPage.value - 1) * pageSize
  return form.suppliers.slice(start, start + pageSize)
})

const totalAmount = computed(() => {
  const itemsTotal = form.items.reduce((sum, row) => sum + (row.amount || 0), 0)
  return itemsTotal + (form.freight || 0)
})

const costAmount = computed(() => {
  return form.suppliers.reduce((sum, row) => sum + (row.price || 0) * (row.quantity || 0) + (parseFloat(row.tax) || 0), 0)
})

const logisticsTotal = computed(() => {
  return form.logistics.reduce((sum, row) => sum + parseFloat(row.freight || 0) + parseFloat(row.forklift_fee || 0) + parseFloat(row.other_fee || 0), 0)
})

const grossProfit = computed(() => {
  return totalAmount.value - costAmount.value - logisticsTotal.value
})

const goBack = () => {
  router.push('/sales')
}

const productDialogVisible = ref(false)
const dialogProducts = ref([])
const dialogLoading = ref(false)
const dialogPage = ref(1)
const dialogTotal = ref(0)
const dialogSelectedProducts = ref([])
const productTableRef = ref()
const dialogSearch = reactive({ keyword: '' })

const loadOptions = async () => {
  try {
    const cRes = await getCustomers({ page: 1, per_page: 100 })
    customers.value = cRes.data.items || []
  } catch (e) {
    console.error(e)
  }
}

const loadOrder = async (id) => {
  try {
    const res = await getSale(id)
    const data = res.data
    Object.assign(form, { ...data, items: data.items || [], suppliers: data.suppliers || [], logistics: data.logistics || [] })
  } catch (e) {
    console.error(e)
  }
}

const onCustomerChange = () => {
  const customer = customers.value.find(c => c.id === form.customer_id)
  if (customer) {
    form.address = customer.address || ''
  }
}

const deleteItem = (idx) => {
  const actualIdx = (itemPage.value - 1) * pageSize + idx
  form.items.splice(actualIdx, 1)
  if (form.items.length <= (itemPage.value - 1) * pageSize && itemPage.value > 1) {
    itemPage.value--
  }
}

const deleteSupplier = (idx) => {
  const actualIdx = (supplierPage.value - 1) * pageSize + idx
  form.suppliers.splice(actualIdx, 1)
  if (form.suppliers.length <= (supplierPage.value - 1) * pageSize && supplierPage.value > 1) {
    supplierPage.value--
  }
}

const addSupplier = () => {
  form.suppliers.push({ supplier: '', product: '', spec: '', grade: '', surface_treatment: '', cost: 0, quantity: 0, total_weight: 0, unit_weight: 0, price: 0, packaging: '', freight: 0, ton_bag_forklift: '', remark: '' })
  supplierPage.value = Math.ceil(form.suppliers.length / pageSize)
}

const editingItemIndex = ref(null)

const addItem = () => {
  form.items.push({ product_id: null, product_name: '', spec: '', material_grade: '', surface_treatment: '', package_quantity: 0, package_count: 0, matching: '', unit_name: '', quantity: 1, unit_price: 0, amount: 0, remark: '' })
  itemPage.value = Math.ceil(form.items.length / pageSize)
}

const addLogistics = () => {
  form.logistics.push({ company: '', contact_phone: '', start_time: '', end_time: '', transport_status: '', freight: 0, forklift_fee: '', other_fee: '', remark: '' })
}

const openProductSelector = (index) => {
  editingItemIndex.value = index
  productDialogVisible.value = true
  dialogSelectedProducts.value = []
  dialogSearch.keyword = ''
  dialogPage.value = 1
  loadDialogProducts()
}

const loadDialogProducts = async () => {
  dialogLoading.value = true
  try {
    const res = await getProducts({ page: dialogPage.value, per_page: 10, search: dialogSearch.keyword || '' })
    dialogProducts.value = res.data.items || []
    dialogTotal.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    dialogLoading.value = false
  }
}

const searchDialogProducts = () => {
  dialogPage.value = 1
  loadDialogProducts()
}

const resetDialogSearch = () => {
  dialogSearch.keyword = ''
  dialogPage.value = 1
  loadDialogProducts()
}

const onDialogSelectionChange = (selection) => {
  dialogSelectedProducts.value = selection
}

const removeDialogSelection = (product) => {
  const idx = dialogSelectedProducts.value.findIndex(p => p.id === product.id)
  if (idx > -1) {
    dialogSelectedProducts.value.splice(idx, 1)
    if (productTableRef.value) {
      productTableRef.value.toggleRowSelection(product, false)
    }
  }
}

const confirmDialogSelection = () => {
  const selected = dialogSelectedProducts.value
  if (selected.length === 0) {
    productDialogVisible.value = false
    return
  }
  const makeItem = (p) => ({
    product_id: p.id,
    product_name: p.name,
    spec: p.spec || '',
    material_grade: p.material_grade || '',
    surface_treatment: p.surface_treatment || '',
    unit_name: p.unit_name || '',
    package_quantity: 0,
    package_count: 0,
    matching: '',
    quantity: 1,
    unit_price: p.sale_price || 0,
    amount: p.sale_price || 0,
    remark: ''
  })
  if (editingItemIndex.value !== null) {
    form.items[editingItemIndex.value] = makeItem(selected[0])
    for (let i = 1; i < selected.length; i++) {
      form.items.splice(editingItemIndex.value + i, 0, makeItem(selected[i]))
    }
  } else {
    for (const p of selected) {
      form.items.push(makeItem(p))
    }
  }
  editingItemIndex.value = null
  productDialogVisible.value = false
  itemPage.value = Math.ceil(form.items.length / pageSize)
}

const calcItemAmount = (row) => {
  row.amount = (row.quantity || 0) * (row.unit_price || 0)
}

const calcTotal = () => {
  // computed handles this
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  const payload = { ...form, gross_profit: grossProfit.value }

  try {
    if (form.id) {
      await updateSale(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createSale(payload)
      ElMessage.success('创建成功')
    }
    router.push('/sales')
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  await loadOptions()
  if (route.params.id) {
    await loadOrder(route.params.id)
  } else {
    form.order_date = new Date().toISOString().split('T')[0]
  }
})
</script>

<style scoped>
.sales-order-form .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.sales-order-form .header .el-button {
  font-size: 20px;
}
.sales-order-form .header h2 {
  margin: 0;
}
.sales-order-form .header-actions {
  display: flex;
  gap: 12px;
}
</style>
