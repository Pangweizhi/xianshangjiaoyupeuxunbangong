<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>学生管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索学生姓名" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button type="success" @click="openCreate">新增学生</el-button>
      </div>
    </div>

    <el-table :data="students" stripe empty-text="暂无学生数据">
      <el-table-column prop="username" label="账号" min-width="140" />
      <el-table-column prop="yonghuName" label="学生姓名" min-width="140" />
      <el-table-column prop="sexValue" label="性别" min-width="100" />
      <el-table-column prop="banjiValue" label="班级" min-width="140" />
      <el-table-column prop="yonghuPhone" label="联系方式" min-width="160" />
      <el-table-column prop="yonghuEmail" label="邮箱" min-width="200" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row.id)">编辑</el-button>
          <el-button link type="danger" @click="removeItem(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.limit" background layout="total, sizes, prev, pager, next" :total="pagination.total" :page-sizes="[10,20,50]" @current-change="loadStudents" @size-change="handleSizeChange" />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑学生' : '新增学生'" width="760px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="账号" prop="username"><el-input v-model="form.username" /></el-form-item>
      <el-form-item label="密码" prop="password"><el-input v-model="form.password" show-password /></el-form-item>
      <el-form-item label="学生姓名" prop="yonghuName"><el-input v-model="form.yonghuName" /></el-form-item>
      <el-form-item label="性别" prop="sexTypes"><el-select v-model="form.sexTypes"><el-option v-for="item in sexOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" /></el-select></el-form-item>
      <el-form-item label="头像"><input type="file" accept="image/*" @change="handleUpload($event, 'yonghuPhoto')" /><p class="upload-tip">{{ form.yonghuPhoto || "未上传" }}</p><img v-if="assetUrl(form.yonghuPhoto)" class="upload-preview" :src="assetUrl(form.yonghuPhoto)" alt="学生头像预览" /></el-form-item>
      <el-form-item label="身份证号" prop="yonghuIdNumber"><el-input v-model="form.yonghuIdNumber" /></el-form-item>
      <el-form-item label="联系方式" prop="yonghuPhone"><el-input v-model="form.yonghuPhone" /></el-form-item>
      <el-form-item label="电子邮箱" prop="yonghuEmail"><el-input v-model="form.yonghuEmail" /></el-form-item>
      <el-form-item label="班级" prop="banjiTypes"><el-select v-model="form.banjiTypes"><el-option v-for="item in banjiOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" /></el-select></el-form-item>
    </el-form>
    <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="submitForm">提交</el-button></template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { DEFAULT_BASE_URL, createAssetUrl, type StudentItem } from "@shared/index";
import { fetchStudents } from "@/api/dashboard";
import { deleteEntities, fetchDictionaryOptions, fetchEntityDetail, saveEntity, uploadAdminFile } from "@/api/manage";

const keyword = ref(""); const students = ref<StudentItem[]>([]); const dialogVisible = ref(false); const saving = ref(false); const loading = ref(false); const formRef = ref<FormInstance>(); const sexOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]); const banjiOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]); const pagination = reactive({ page: 1, limit: 10, total: 0 });
const createForm = () => ({ id: undefined as number | undefined, username: "", password: "123456", yonghuName: "", sexTypes: undefined as number | undefined, yonghuPhoto: "", yonghuIdNumber: "", yonghuPhone: "", yonghuEmail: "", banjiTypes: undefined as number | undefined, yonghuDelete: 1 });
const form = reactive(createForm());
const rules: FormRules = { username: [{ required: true, message: "请输入账号", trigger: "blur" }], password: [{ required: true, message: "请输入密码", trigger: "blur" }], yonghuName: [{ required: true, message: "请输入学生姓名", trigger: "blur" }], sexTypes: [{ required: true, message: "请选择性别", trigger: "change" }], yonghuPhone: [{ required: true, message: "请输入联系方式", trigger: "blur" }], banjiTypes: [{ required: true, message: "请选择班级", trigger: "change" }], yonghuEmail: [{ required: true, message: "请输入电子邮箱", trigger: "blur" }, { type: "email", message: "邮箱格式不正确", trigger: "blur" }] };
function assetUrl(path?: string) { return createAssetUrl(DEFAULT_BASE_URL, path); }
async function loadStudents() { loading.value = true; try { const page = await fetchStudents({ page: pagination.page, limit: pagination.limit, yonghuName: keyword.value || undefined }); students.value = page.list; pagination.total = page.totalCount; } finally { loading.value = false; } }
function handleSearch() { pagination.page = 1; loadStudents(); }
function resetFilters() { keyword.value = ""; pagination.page = 1; loadStudents(); }
function handleSizeChange() { pagination.page = 1; loadStudents(); }
function resetForm() { Object.assign(form, createForm()); }
async function prepareOptions() { const [sex, banji] = await Promise.all([fetchDictionaryOptions("sex_types"), fetchDictionaryOptions("banji_types")]); sexOptions.value = sex; banjiOptions.value = banji; }
async function openCreate() { resetForm(); await prepareOptions(); dialogVisible.value = true; }
async function openEdit(id: number) { resetForm(); await prepareOptions(); Object.assign(form, await fetchEntityDetail("yonghu", id)); dialogVisible.value = true; }
async function handleUpload(event: Event, field: "yonghuPhoto") { const file = (event.target as HTMLInputElement).files?.[0]; if (!file) return; try { form[field] = await uploadAdminFile(file); ElMessage.success("头像已上传"); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "上传失败"); } }
async function submitForm() { await formRef.value?.validate(); saving.value = true; try { await saveEntity("yonghu", form as unknown as Record<string, unknown>); ElMessage.success("学生信息已保存"); dialogVisible.value = false; await loadStudents(); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "保存失败"); } finally { saving.value = false; } }
async function removeItem(id: number) { await deleteEntities("yonghu", [id]); ElMessage.success("学生已删除"); await loadStudents(); }
prepareOptions(); loadStudents();
</script>
