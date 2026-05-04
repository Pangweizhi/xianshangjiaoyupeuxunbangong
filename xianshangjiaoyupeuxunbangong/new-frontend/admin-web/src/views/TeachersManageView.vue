<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>教师管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索教师姓名" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button type="success" @click="openCreate">新增教师</el-button>
      </div>
    </div>
    <el-table :data="teachers" stripe empty-text="暂无教师数据">
      <el-table-column prop="username" label="账号" min-width="140" />
      <el-table-column prop="jiaoshiName" label="教师姓名" min-width="140" />
      <el-table-column prop="sexValue" label="性别" min-width="100" />
      <el-table-column prop="jiaoshiPhone" label="联系方式" min-width="160" />
      <el-table-column prop="jiaoshiEmail" label="邮箱" min-width="200" />
      <el-table-column label="操作" width="180" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row.id)">编辑</el-button><el-button link type="danger" @click="removeItem(row.id)">删除</el-button></template></el-table-column>
    </el-table>
    <div class="pagination-bar"><el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.limit" background layout="total, sizes, prev, pager, next" :total="pagination.total" :page-sizes="[10,20,50]" @current-change="loadTeachers" @size-change="handleSizeChange" /></div>
  </section>
  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑教师' : '新增教师'" width="760px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="账号" prop="username"><el-input v-model="form.username" /></el-form-item>
      <el-form-item label="密码" prop="password"><el-input v-model="form.password" show-password /></el-form-item>
      <el-form-item label="教师姓名" prop="jiaoshiName"><el-input v-model="form.jiaoshiName" /></el-form-item>
      <el-form-item label="性别" prop="sexTypes"><el-select v-model="form.sexTypes"><el-option v-for="item in sexOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" /></el-select></el-form-item>
      <el-form-item label="头像"><input type="file" accept="image/*" @change="handleUpload($event, 'jiaoshiPhoto')" /><p class="upload-tip">{{ form.jiaoshiPhoto || "未上传" }}</p><img v-if="assetUrl(form.jiaoshiPhoto)" class="upload-preview" :src="assetUrl(form.jiaoshiPhoto)" alt="教师头像预览" /></el-form-item>
      <el-form-item label="身份证号" prop="jiaoshiIdNumber"><el-input v-model="form.jiaoshiIdNumber" /></el-form-item>
      <el-form-item label="联系方式" prop="jiaoshiPhone"><el-input v-model="form.jiaoshiPhone" /></el-form-item>
      <el-form-item label="电子邮箱" prop="jiaoshiEmail"><el-input v-model="form.jiaoshiEmail" /></el-form-item>
    </el-form>
    <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="submitForm">提交</el-button></template>
  </el-dialog>
</template>
<script setup lang="ts">
import { reactive, ref } from "vue"; import { ElMessage, type FormInstance, type FormRules } from "element-plus"; import { DEFAULT_BASE_URL, createAssetUrl, type TeacherItem } from "@shared/index"; import { fetchTeachers } from "@/api/dashboard"; import { deleteEntities, fetchDictionaryOptions, fetchEntityDetail, saveEntity, uploadAdminFile } from "@/api/manage";
const keyword = ref(""); const teachers = ref<TeacherItem[]>([]); const dialogVisible = ref(false); const saving = ref(false); const loading = ref(false); const formRef = ref<FormInstance>(); const sexOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]); const pagination = reactive({ page: 1, limit: 10, total: 0 });
const createForm = () => ({ id: undefined as number | undefined, username: "", password: "123456", jiaoshiName: "", sexTypes: undefined as number | undefined, jiaoshiPhoto: "", jiaoshiIdNumber: "", jiaoshiPhone: "", jiaoshiEmail: "", jiaoshiDelete: 1 }); const form = reactive(createForm());
const rules: FormRules = { username: [{ required: true, message: "请输入账号", trigger: "blur" }], password: [{ required: true, message: "请输入密码", trigger: "blur" }], jiaoshiName: [{ required: true, message: "请输入教师姓名", trigger: "blur" }], sexTypes: [{ required: true, message: "请选择性别", trigger: "change" }], jiaoshiPhone: [{ required: true, message: "请输入联系方式", trigger: "blur" }], jiaoshiEmail: [{ required: true, message: "请输入电子邮箱", trigger: "blur" }, { type: "email", message: "邮箱格式不正确", trigger: "blur" }] };
function assetUrl(path?: string) { return createAssetUrl(DEFAULT_BASE_URL, path); }
async function loadTeachers() { loading.value = true; try { const page = await fetchTeachers({ page: pagination.page, limit: pagination.limit, jiaoshiName: keyword.value || undefined }); teachers.value = page.list; pagination.total = page.totalCount; } finally { loading.value = false; } }
function handleSearch() { pagination.page = 1; loadTeachers(); } function resetFilters() { keyword.value = ""; pagination.page = 1; loadTeachers(); } function handleSizeChange() { pagination.page = 1; loadTeachers(); } function resetForm() { Object.assign(form, createForm()); }
async function openCreate() { resetForm(); sexOptions.value = await fetchDictionaryOptions("sex_types"); dialogVisible.value = true; } async function openEdit(id: number) { resetForm(); sexOptions.value = await fetchDictionaryOptions("sex_types"); Object.assign(form, await fetchEntityDetail("jiaoshi", id)); dialogVisible.value = true; }
async function handleUpload(event: Event, field: "jiaoshiPhoto") { const file = (event.target as HTMLInputElement).files?.[0]; if (!file) return; try { form[field] = await uploadAdminFile(file); ElMessage.success("教师头像已上传"); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "上传失败"); } }
async function submitForm() { await formRef.value?.validate(); saving.value = true; try { form.jiaoshiDelete = 1; await saveEntity("jiaoshi", form as unknown as Record<string, unknown>); ElMessage.success("教师信息已保存"); dialogVisible.value = false; await loadTeachers(); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "保存失败"); } finally { saving.value = false; } }
async function removeItem(id: number) { await deleteEntities("jiaoshi", [id]); ElMessage.success("教师已删除"); await loadTeachers(); } loadTeachers();
</script>
