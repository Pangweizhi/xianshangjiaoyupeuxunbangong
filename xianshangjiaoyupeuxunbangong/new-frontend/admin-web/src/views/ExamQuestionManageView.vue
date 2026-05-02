<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>题库管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-select v-model="filters.examId" placeholder="考试" clearable>
          <el-option v-for="item in examOptions" :key="item.id" :label="item.examName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.questionType" placeholder="题型" clearable>
          <el-option label="单选" value="单选" />
          <el-option label="多选" value="多选" />
          <el-option label="判断" value="判断" />
          <el-option label="简答" value="简答" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="success" @click="openCreate">新增题目</el-button>
      </div>
    </div>
    <el-table :data="rows" stripe>
      <el-table-column prop="examName" label="考试" min-width="180" />
      <el-table-column prop="questionType" label="题型" min-width="100" />
      <el-table-column prop="questionTitle" label="题目" min-width="280" show-overflow-tooltip />
      <el-table-column prop="questionScore" label="分值" min-width="90" />
      <el-table-column prop="sortNo" label="排序" min-width="90" />
      <el-table-column label="操作" width="180" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row.id)">编辑</el-button><el-button link type="danger" @click="removeItem(row.id)">删除</el-button></template></el-table-column>
    </el-table>
    <div class="pagination-bar"><el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.limit" background layout="total, sizes, prev, pager, next" :total="pagination.total" :page-sizes="[10,20,50]" @current-change="loadRows" @size-change="handleSizeChange" /></div>
  </section>

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑题目' : '新增题目'" width="760px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="所属考试" prop="examId"><el-select v-model="form.examId"><el-option v-for="item in examOptions" :key="item.id" :label="item.examName" :value="item.id" /></el-select></el-form-item>
      <el-form-item label="题型" prop="questionType"><el-select v-model="form.questionType"><el-option label="单选" value="单选" /><el-option label="多选" value="多选" /><el-option label="判断" value="判断" /><el-option label="简答" value="简答" /></el-select></el-form-item>
      <el-form-item label="题目" prop="questionTitle"><el-input v-model="form.questionTitle" type="textarea" :rows="3" /></el-form-item>
      <el-form-item label="选项JSON"><el-input v-model="form.optionJson" type="textarea" :rows="4" placeholder='如 {"A":"选项A","B":"选项B"}' /></el-form-item>
      <el-form-item label="正确答案"><el-input v-model="form.correctAnswer" placeholder="多选用英文逗号分隔" /></el-form-item>
      <el-form-item label="分值" prop="questionScore"><el-input-number v-model="form.questionScore" :min="1" :max="100" /></el-form-item>
      <el-form-item label="排序"><el-input-number v-model="form.sortNo" :min="1" :max="999" /></el-form-item>
      <el-form-item label="解析"><el-input v-model="form.analysisText" type="textarea" :rows="3" /></el-form-item>
    </el-form>
    <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" :loading="saving" @click="submitForm">提交</el-button></template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import type { ExamItem, ExamQuestionItem } from "@shared/index";
import { fetchExamPage, fetchExamQuestionPage } from "@/api/dashboard";
import { deleteEntities, fetchEntityDetail, saveEntity } from "@/api/manage";

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const formRef = ref<FormInstance>();
const rows = ref<ExamQuestionItem[]>([]);
const examOptions = ref<ExamItem[]>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ examId: undefined as number | undefined, questionType: "" });
const createForm = () => ({ id: undefined as number | undefined, examId: undefined as number | undefined, questionType: "单选", questionTitle: "", optionJson: "", correctAnswer: "", questionScore: 5, sortNo: 1, analysisText: "" });
const form = reactive(createForm());
const rules: FormRules = { examId: [{ required: true, message: "请选择考试", trigger: "change" }], questionType: [{ required: true, message: "请选择题型", trigger: "change" }], questionTitle: [{ required: true, message: "请输入题目", trigger: "blur" }], questionScore: [{ required: true, message: "请填写分值", trigger: "change" }] };

async function loadOptions() { const page = await fetchExamPage({ limit: 200 }); examOptions.value = page.list; }
async function loadRows() { loading.value = true; try { const page = await fetchExamQuestionPage({ page: pagination.page, limit: pagination.limit, examId: filters.examId, questionType: filters.questionType || undefined }); rows.value = page.list; pagination.total = page.totalCount; } finally { loading.value = false; } }
function handleSearch() { pagination.page = 1; loadRows(); }
async function resetFilters() { filters.examId = undefined; filters.questionType = ""; pagination.page = 1; await loadOptions(); loadRows(); }
function handleSizeChange() { pagination.page = 1; loadRows(); }
function resetForm() { Object.assign(form, createForm()); }
async function openCreate() { resetForm(); await loadOptions(); dialogVisible.value = true; }
async function openEdit(id: number) { resetForm(); await loadOptions(); Object.assign(form, await fetchEntityDetail("examQuestion", id)); dialogVisible.value = true; }
async function submitForm() { await formRef.value?.validate(); saving.value = true; try { await saveEntity("examQuestion", form as unknown as Record<string, unknown>); ElMessage.success("题目已保存"); dialogVisible.value = false; await loadRows(); } catch (error) { ElMessage.error(error instanceof Error ? error.message : "保存失败"); } finally { saving.value = false; } }
async function removeItem(id: number) { await deleteEntities("examQuestion", [id]); ElMessage.success("题目已删除"); await loadRows(); }

loadOptions();
loadRows();
</script>
