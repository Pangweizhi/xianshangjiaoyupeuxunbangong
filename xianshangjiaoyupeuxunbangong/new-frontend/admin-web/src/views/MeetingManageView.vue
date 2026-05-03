<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>会议管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索会议标题" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button type="success" @click="openCreate">新增会议</el-button>
      </div>
    </div>
    <el-table :data="items" stripe empty-text="暂无会议数据">
      <el-table-column prop="kaihuitongzhiName" label="会议标题" min-width="240" />
      <el-table-column prop="kaihuitongzhiValue" label="会议类型" min-width="140" />
      <el-table-column prop="insertTime" label="发布时间" min-width="180" />
      <el-table-column label="操作" width="180" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row.id)">编辑</el-button><el-button link type="danger" @click="removeItem(row.id)">删除</el-button></template></el-table-column>
    </el-table>
    <div class="pagination-bar"><el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.limit" background layout="total, sizes, prev, pager, next" :total="pagination.total" :page-sizes="[10,20,50]" @current-change="loadItems" @size-change="handleSizeChange" /></div>
  </section>
  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑会议' : '新增会议'" width="680px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="会议标题" prop="kaihuitongzhiName"><el-input v-model="form.kaihuitongzhiName" /></el-form-item>
      <el-form-item label="会议类型" prop="kaihuitongzhiTypes"><el-select v-model="form.kaihuitongzhiTypes"><el-option v-for="item in typeOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" /></el-select></el-form-item>
      <el-form-item label="会议详情" prop="kaihuitongzhiContent"><el-input v-model="form.kaihuitongzhiContent" type="textarea" :rows="6" /></el-form-item>
    </el-form>
    <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="submitForm">提交</el-button></template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref } from "vue"; import { ElMessage, type FormInstance, type FormRules } from "element-plus"; import type { MeetingItem } from "@shared/index"; import { fetchMeetings } from "@/api/dashboard"; import { deleteEntities, fetchDictionaryOptions, fetchEntityDetail, saveEntity } from "@/api/manage";
const keyword = ref(""); const items = ref<MeetingItem[]>([]); const dialogVisible = ref(false); const saving = ref(false); const loading = ref(false); const formRef = ref<FormInstance>(); const typeOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]); const pagination = reactive({ page: 1, limit: 10, total: 0 });
const createForm = () => ({ id: undefined as number | undefined, kaihuitongzhiName: "", kaihuitongzhiTypes: undefined as number | undefined, kaihuitongzhiContent: "", kaihuitongzhiDelete: 1 }); const form = reactive(createForm());
const rules: FormRules = { kaihuitongzhiName: [{ required: true, message: "请输入会议标题", trigger: "blur" }], kaihuitongzhiTypes: [{ required: true, message: "请选择会议类型", trigger: "change" }], kaihuitongzhiContent: [{ required: true, message: "请输入会议详情", trigger: "blur" }] };
async function loadItems() { loading.value = true; try { const page = await fetchMeetings({ page: pagination.page, limit: pagination.limit, kaihuitongzhiName: keyword.value || undefined }); items.value = page.list; pagination.total = page.totalCount; } finally { loading.value = false; } }
function handleSearch() { pagination.page = 1; loadItems(); } function resetFilters() { keyword.value = ""; pagination.page = 1; loadItems(); } function handleSizeChange() { pagination.page = 1; loadItems(); } function resetForm() { Object.assign(form, createForm()); }
async function openCreate() { resetForm(); typeOptions.value = await fetchDictionaryOptions("kaihuitongzhi_types"); dialogVisible.value = true; } async function openEdit(id: number) { resetForm(); typeOptions.value = await fetchDictionaryOptions("kaihuitongzhi_types"); Object.assign(form, await fetchEntityDetail("kaihuitongzhi", id)); dialogVisible.value = true; }
async function submitForm() { await formRef.value?.validate(); saving.value = true; try { await saveEntity("kaihuitongzhi", form as unknown as Record<string, unknown>); ElMessage.success("会议已保存"); dialogVisible.value = false; await loadItems(); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "保存失败"); } finally { saving.value = false; } }
async function removeItem(id: number) { await deleteEntities("kaihuitongzhi", [id]); ElMessage.success("会议已删除"); await loadItems(); } loadItems();
</script>
