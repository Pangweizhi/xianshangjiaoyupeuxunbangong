<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>备课管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索备课标题" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button type="success" @click="openCreate">新增备课</el-button>
      </div>
    </div>
    <el-table :data="items" stripe empty-text="暂无备课数据">
      <el-table-column prop="jiaoxueshipinName" label="标题" min-width="220" />
      <el-table-column prop="jiaoxueshipinValue" label="类型" min-width="120" />
      <el-table-column prop="jiaoshiName" label="教师" min-width="120" />
      <el-table-column prop="jiaoxueshipinTime" label="上课时间" min-width="180" />
      <el-table-column label="操作" width="180" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row.id)">编辑</el-button><el-button link type="danger" @click="removeItem(row.id)">删除</el-button></template></el-table-column>
    </el-table>
    <div class="pagination-bar"><el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.limit" background layout="total, sizes, prev, pager, next" :total="pagination.total" :page-sizes="[10,20,50]" @current-change="loadItems" @size-change="handleSizeChange" /></div>
  </section>
  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑备课' : '新增备课'" width="760px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="标题" prop="jiaoxueshipinName"><el-input v-model="form.jiaoxueshipinName" /></el-form-item>
      <el-form-item label="备课类型" prop="jiaoxueshipinTypes"><el-select v-model="form.jiaoxueshipinTypes"><el-option v-for="item in typeOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" /></el-select></el-form-item>
      <el-form-item label="教师" prop="jiaoshiId"><el-select v-model="form.jiaoshiId"><el-option v-for="item in teacherOptions" :key="item.id" :label="item.jiaoshiName" :value="item.id" /></el-select></el-form-item>
      <el-form-item label="上课时间" prop="jiaoxueshipinTime"><el-date-picker v-model="form.jiaoxueshipinTime" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" placeholder="请选择上课时间" /></el-form-item>
      <el-form-item label="封面图"><input type="file" accept="image/*" @change="handleUpload($event, 'jiaoxueshipinPhoto')" /><p class="upload-tip">{{ form.jiaoxueshipinPhoto || "未上传" }}</p><img v-if="assetUrl(form.jiaoxueshipinPhoto)" class="upload-preview" :src="assetUrl(form.jiaoxueshipinPhoto)" alt="备课封面预览" /></el-form-item>
      <el-form-item label="资料附件" prop="jiaoxueshipinFile"><input type="file" @change="handleUpload($event, 'jiaoxueshipinFile')" /><p class="upload-tip">{{ form.jiaoxueshipinFile || "未上传" }}</p><a v-if="form.jiaoxueshipinFile" class="upload-link" :href="downloadUrl(form.jiaoxueshipinFile)" target="_blank">查看当前附件</a></el-form-item>
      <el-form-item label="备课详情" prop="jiaoxueshipinContent"><el-input v-model="form.jiaoxueshipinContent" type="textarea" :rows="5" /></el-form-item>
    </el-form>
    <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="submitForm">提交</el-button></template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref } from "vue"; import { ElMessage, type FormInstance, type FormRules } from "element-plus"; import { DEFAULT_BASE_URL, createAssetUrl, createDownloadUrl, type LessonMaterialItem } from "@shared/index"; import { fetchMaterials } from "@/api/dashboard"; import { deleteEntities, fetchDictionaryOptions, fetchEntityDetail, fetchTeachersForSelect, saveEntity, uploadAdminFile } from "@/api/manage";
const keyword = ref(""); const items = ref<LessonMaterialItem[]>([]); const dialogVisible = ref(false); const saving = ref(false); const loading = ref(false); const formRef = ref<FormInstance>(); const teacherOptions = ref<Array<{ id: number; jiaoshiName: string }>>([]); const typeOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]); const pagination = reactive({ page: 1, limit: 10, total: 0 });
const createForm = () => ({ id: undefined as number | undefined, jiaoxueshipinName: "", jiaoxueshipinPhoto: "", jiaoxueshipinFile: "", jiaoxueshipinTypes: undefined as number | undefined, jiaoshiId: undefined as number | undefined, jiaoxueshipinTime: "", jiaoxueshipinContent: "", jiaoxueshipinDelete: 1 }); const form = reactive(createForm());
const rules: FormRules = { jiaoxueshipinName: [{ required: true, message: "请输入备课标题", trigger: "blur" }], jiaoxueshipinTypes: [{ required: true, message: "请选择备课类型", trigger: "change" }], jiaoshiId: [{ required: true, message: "请选择教师", trigger: "change" }], jiaoxueshipinTime: [{ required: true, message: "请选择上课时间", trigger: "change" }], jiaoxueshipinFile: [{ required: true, message: "请上传资料附件", trigger: "change" }], jiaoxueshipinContent: [{ required: true, message: "请输入备课详情", trigger: "blur" }] };
function assetUrl(path?: string) { return createAssetUrl(DEFAULT_BASE_URL, path); } function downloadUrl(fileName?: string) { return createDownloadUrl(DEFAULT_BASE_URL, fileName); }
async function loadItems() { loading.value = true; try { const page = await fetchMaterials({ page: pagination.page, limit: pagination.limit, jiaoxueshipinName: keyword.value || undefined }); items.value = page.list; pagination.total = page.totalCount; } finally { loading.value = false; } }
function handleSearch() { pagination.page = 1; loadItems(); } function resetFilters() { keyword.value = ""; pagination.page = 1; loadItems(); } function handleSizeChange() { pagination.page = 1; loadItems(); } function resetForm() { Object.assign(form, createForm()); }
async function prepareOptions() { const [teachers, types] = await Promise.all([fetchTeachersForSelect(), fetchDictionaryOptions("jiaoxueshipin_types")]); teacherOptions.value = teachers; typeOptions.value = types; }
async function openCreate() { resetForm(); await prepareOptions(); dialogVisible.value = true; } async function openEdit(id: number) { resetForm(); await prepareOptions(); Object.assign(form, await fetchEntityDetail("jiaoxueshipin", id)); dialogVisible.value = true; }
async function handleUpload(event: Event, field: "jiaoxueshipinPhoto" | "jiaoxueshipinFile") { const file = (event.target as HTMLInputElement).files?.[0]; if (!file) return; try { form[field] = await uploadAdminFile(file); ElMessage.success(field === "jiaoxueshipinPhoto" ? "封面图已上传" : "资料附件已上传"); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "上传失败"); } }
async function submitForm() { await formRef.value?.validate(); saving.value = true; try { await saveEntity("jiaoxueshipin", form as unknown as Record<string, unknown>); ElMessage.success("备课信息已保存"); dialogVisible.value = false; await loadItems(); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "保存失败"); } finally { saving.value = false; } }
async function removeItem(id: number) { await deleteEntities("jiaoxueshipin", [id]); ElMessage.success("备课信息已删除"); await loadItems(); } loadItems();
</script>
