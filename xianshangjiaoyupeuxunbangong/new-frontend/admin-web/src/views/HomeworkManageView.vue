<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>作业管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索作业标题" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button type="success" @click="openCreate">新增作业</el-button>
      </div>
    </div>
    <el-table :data="items" stripe empty-text="暂无作业数据">
      <el-table-column prop="zuoyeName" label="作业标题" min-width="220" />
      <el-table-column prop="zuoyeValue" label="作业类型" min-width="120" />
      <el-table-column prop="jiaoshiName" label="教师" min-width="120" />
      <el-table-column prop="insertTime" label="发布时间" min-width="180" />
      <el-table-column label="操作" width="180" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row.id)">编辑</el-button><el-button link type="danger" @click="removeItem(row.id)">删除</el-button></template></el-table-column>
    </el-table>
    <div class="pagination-bar"><el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.limit" background layout="total, sizes, prev, pager, next" :total="pagination.total" :page-sizes="[10,20,50]" @current-change="loadItems" @size-change="handleSizeChange" /></div>
  </section>
  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑作业' : '新增作业'" width="760px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="作业标题" prop="zuoyeName"><el-input v-model="form.zuoyeName" /></el-form-item>
      <el-form-item label="作业类型" prop="zuoyeTypes"><el-select v-model="form.zuoyeTypes"><el-option v-for="item in typeOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" /></el-select></el-form-item>
      <el-form-item label="教师" prop="jiaoshiId"><el-select v-model="form.jiaoshiId"><el-option v-for="item in teacherOptions" :key="item.id" :label="item.jiaoshiName" :value="item.id" /></el-select></el-form-item>
      <el-form-item label="作业图片"><input type="file" accept="image/*" @change="handleUpload($event, 'zuoyePhoto')" /><p class="upload-tip">{{ form.zuoyePhoto || "未上传" }}</p><img v-if="assetUrl(form.zuoyePhoto)" class="upload-preview" :src="assetUrl(form.zuoyePhoto)" alt="作业图片预览" /></el-form-item>
      <el-form-item label="作业附件" prop="zuoyeFile"><input type="file" @change="handleUpload($event, 'zuoyeFile')" /><p class="upload-tip">{{ form.zuoyeFile || "未上传" }}</p><a v-if="form.zuoyeFile" class="upload-link" :href="downloadUrl(form.zuoyeFile)" target="_blank">查看当前附件</a></el-form-item>
      <el-form-item label="作业详情" prop="zuoyeContent"><el-input v-model="form.zuoyeContent" type="textarea" :rows="5" /></el-form-item>
    </el-form>
    <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="submitForm">提交</el-button></template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref } from "vue"; import { ElMessage, type FormInstance, type FormRules } from "element-plus"; import { DEFAULT_BASE_URL, createAssetUrl, createDownloadUrl, type HomeworkItem } from "@shared/index"; import { fetchHomeworks } from "@/api/dashboard"; import { deleteEntities, fetchDictionaryOptions, fetchEntityDetail, fetchTeachersForSelect, saveEntity, uploadAdminFile } from "@/api/manage";
const keyword = ref(""); const items = ref<HomeworkItem[]>([]); const dialogVisible = ref(false); const saving = ref(false); const loading = ref(false); const formRef = ref<FormInstance>(); const teacherOptions = ref<Array<{ id: number; jiaoshiName: string }>>([]); const typeOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]); const pagination = reactive({ page: 1, limit: 10, total: 0 });
const createForm = () => ({ id: undefined as number | undefined, zuoyeName: "", zuoyePhoto: "", zuoyeTypes: undefined as number | undefined, zuoyeFile: "", jiaoshiId: undefined as number | undefined, zuoyeContent: "", zuoyeDelete: 1 }); const form = reactive(createForm());
const rules: FormRules = { zuoyeName: [{ required: true, message: "请输入作业标题", trigger: "blur" }], zuoyeTypes: [{ required: true, message: "请选择作业类型", trigger: "change" }], jiaoshiId: [{ required: true, message: "请选择教师", trigger: "change" }], zuoyeFile: [{ required: true, message: "请上传作业附件", trigger: "change" }], zuoyeContent: [{ required: true, message: "请输入作业详情", trigger: "blur" }] };
function assetUrl(path?: string) { return createAssetUrl(DEFAULT_BASE_URL, path); } function downloadUrl(fileName?: string) { return createDownloadUrl(DEFAULT_BASE_URL, fileName); }
async function loadItems() { loading.value = true; try { const page = await fetchHomeworks({ page: pagination.page, limit: pagination.limit, zuoyeName: keyword.value || undefined }); items.value = page.list; pagination.total = page.totalCount; } finally { loading.value = false; } }
function handleSearch() { pagination.page = 1; loadItems(); } function resetFilters() { keyword.value = ""; pagination.page = 1; loadItems(); } function handleSizeChange() { pagination.page = 1; loadItems(); } function resetForm() { Object.assign(form, createForm()); }
async function prepareOptions() { const [teachers, types] = await Promise.all([fetchTeachersForSelect(), fetchDictionaryOptions("zuoye_types")]); teacherOptions.value = teachers; typeOptions.value = types; }
async function openCreate() { resetForm(); await prepareOptions(); dialogVisible.value = true; } async function openEdit(id: number) { resetForm(); await prepareOptions(); Object.assign(form, await fetchEntityDetail("zuoye", id)); dialogVisible.value = true; }
async function handleUpload(event: Event, field: "zuoyePhoto" | "zuoyeFile") { const file = (event.target as HTMLInputElement).files?.[0]; if (!file) return; try { form[field] = await uploadAdminFile(file); ElMessage.success(field === "zuoyePhoto" ? "作业图片已上传" : "作业附件已上传"); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "上传失败"); } }
async function submitForm() { await formRef.value?.validate(); saving.value = true; try { await saveEntity("zuoye", form as unknown as Record<string, unknown>); ElMessage.success("作业已保存"); dialogVisible.value = false; await loadItems(); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "保存失败"); } finally { saving.value = false; } }
async function removeItem(id: number) { await deleteEntities("zuoye", [id]); ElMessage.success("作业已删除"); await loadItems(); } loadItems();
</script>
