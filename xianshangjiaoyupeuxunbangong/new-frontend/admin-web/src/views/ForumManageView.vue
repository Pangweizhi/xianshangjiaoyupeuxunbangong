<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>论坛管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索帖子标题" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button type="success" @click="openCreate">新增帖子</el-button>
      </div>
    </div>
    <el-table :data="items" stripe empty-text="暂无帖子数据">
      <el-table-column prop="forumName" label="帖子标题" min-width="220" />
      <el-table-column prop="forumStateValue" label="状态" min-width="120" />
      <el-table-column label="发布者" min-width="140"><template #default="{ row }">{{ row.yonghuName || row.jiaoshiName || row.uusername || "-" }}</template></el-table-column>
      <el-table-column prop="insertTime" label="发布时间" min-width="180" />
      <el-table-column label="操作" width="180" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row.id)">编辑</el-button><el-button link type="danger" @click="removeItem(row.id)">删除</el-button></template></el-table-column>
    </el-table>
    <div class="pagination-bar"><el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.limit" background layout="total, sizes, prev, pager, next" :total="pagination.total" :page-sizes="[10,20,50]" @current-change="loadItems" @size-change="handleSizeChange" /></div>
  </section>
  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑帖子' : '新增帖子'" width="720px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="帖子标题" prop="forumName"><el-input v-model="form.forumName" /></el-form-item>
      <el-form-item label="父帖 ID"><el-input-number v-model="form.superIds" :min="0" :max="999999" /></el-form-item>
      <el-form-item label="帖子状态" prop="forumStateTypes"><el-select v-model="form.forumStateTypes"><el-option v-for="item in stateOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" /></el-select></el-form-item>
      <el-form-item label="发布内容" prop="forumContent"><el-input v-model="form.forumContent" type="textarea" :rows="6" /></el-form-item>
    </el-form>
    <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="submitForm">提交</el-button></template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref } from "vue"; import { ElMessage, type FormInstance, type FormRules } from "element-plus"; import type { ForumItem } from "@shared/index"; import { fetchForums } from "@/api/dashboard"; import { deleteEntities, fetchDictionaryOptions, fetchEntityDetail, saveEntity } from "@/api/manage";
const keyword = ref(""); const items = ref<ForumItem[]>([]); const dialogVisible = ref(false); const saving = ref(false); const loading = ref(false); const formRef = ref<FormInstance>(); const stateOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]); const pagination = reactive({ page: 1, limit: 10, total: 0 });
const createForm = () => ({ id: undefined as number | undefined, forumName: "", forumContent: "", superIds: 0, forumStateTypes: undefined as number | undefined }); const form = reactive(createForm());
const rules: FormRules = { forumName: [{ required: true, message: "请输入帖子标题", trigger: "blur" }], forumStateTypes: [{ required: true, message: "请选择帖子状态", trigger: "change" }], forumContent: [{ required: true, message: "请输入发布内容", trigger: "blur" }] };
async function loadItems() { loading.value = true; try { const page = await fetchForums({ page: pagination.page, limit: pagination.limit, forumName: keyword.value || undefined }); items.value = page.list; pagination.total = page.totalCount; } finally { loading.value = false; } }
function handleSearch() { pagination.page = 1; loadItems(); } function resetFilters() { keyword.value = ""; pagination.page = 1; loadItems(); } function handleSizeChange() { pagination.page = 1; loadItems(); } function resetForm() { Object.assign(form, createForm()); }
async function openCreate() { resetForm(); stateOptions.value = await fetchDictionaryOptions("forum_state_types"); dialogVisible.value = true; } async function openEdit(id: number) { resetForm(); stateOptions.value = await fetchDictionaryOptions("forum_state_types"); Object.assign(form, await fetchEntityDetail("forum", id)); dialogVisible.value = true; }
async function submitForm() { await formRef.value?.validate(); saving.value = true; try { await saveEntity("forum", form as unknown as Record<string, unknown>); ElMessage.success("帖子已保存"); dialogVisible.value = false; await loadItems(); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "保存失败"); } finally { saving.value = false; } }
async function removeItem(id: number) { await deleteEntities("forum", [id]); ElMessage.success("帖子已删除"); await loadItems(); } loadItems();
</script>
