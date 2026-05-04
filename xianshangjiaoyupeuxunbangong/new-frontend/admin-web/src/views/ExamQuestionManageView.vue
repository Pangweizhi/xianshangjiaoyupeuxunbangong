<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>题库管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-select v-model="filters.examId" placeholder="考试" clearable>
          <el-option v-for="item in examOptions" :key="item.id" :label="item.examName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.questionType" placeholder="题型" clearable>
          <el-option v-for="item in questionTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="success" @click="openCreate">新增题目</el-button>
      </div>
    </div>

    <el-table :data="rows" stripe>
      <el-table-column prop="examName" label="归属考试" min-width="160">
        <template #default="{ row }">
          {{ row.examName || "题库" }}
        </template>
      </el-table-column>
      <el-table-column prop="questionType" label="题型" min-width="120" />
      <el-table-column prop="questionTitle" label="题目" min-width="280" show-overflow-tooltip />
      <el-table-column prop="questionScore" label="分值" min-width="90" />
      <el-table-column prop="sortNo" label="排序" min-width="90" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row.id)">编辑</el-button>
          <el-button link type="danger" @click="removeItem(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        background
        layout="total, sizes, prev, pager, next"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        @current-change="loadRows"
        @size-change="handleSizeChange"
      />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑题目' : '新增题目'" width="760px">
    <div v-if="!form.id" class="question-ai-helper">
      <div class="question-ai-helper__text">
        <strong>AI 出题辅助</strong>
        <p>可用于生成题干初稿、选项建议、参考答案和解析草稿，教师再结合课程内容人工审核后保存。</p>
      </div>
      <el-button type="primary" plain @click="openAiAssistant">AI 辅助出题</el-button>
    </div>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="题型" prop="questionType">
        <el-select v-model="form.questionType">
          <el-option v-for="item in questionTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="题目" prop="questionTitle">
        <el-input v-model="form.questionTitle" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="选项 JSON">
        <el-input v-model="form.optionJson" type="textarea" :rows="4" placeholder='如 {"A":"正确","B":"错误"}' />
      </el-form-item>
      <el-form-item label="正确答案">
        <el-input
          v-model="form.correctAnswer"
          placeholder="选择题和判断题填写选项字母，填空题填写标准答案，简答题可写参考要点"
        />
      </el-form-item>
      <el-form-item label="分值" prop="questionScore">
        <el-input-number v-model="form.questionScore" :min="1" :max="100" />
      </el-form-item>
      <el-form-item label="排序">
        <el-input-number v-model="form.sortNo" :min="1" :max="999" />
      </el-form-item>
      <el-form-item label="解析">
        <el-input v-model="form.analysisText" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitForm">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import type { ExamItem, ExamQuestionItem } from "@shared/index";
import { fetchExamPage, fetchExamQuestionPage } from "@/api/dashboard";
import { deleteEntities, fetchEntityDetail, saveEntity } from "@/api/manage";

const router = useRouter();
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const formRef = ref<FormInstance>();
const rows = ref<ExamQuestionItem[]>([]);
const examOptions = ref<ExamItem[]>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ examId: undefined as number | undefined, questionType: "" });

const questionTypeOptions = [
  { label: "选择题", value: "选择题" },
  { label: "判断题", value: "判断题" },
  { label: "填空题", value: "填空题" },
  { label: "简答题", value: "简答题" }
];

const createForm = () => ({
  id: undefined as number | undefined,
  questionType: "选择题",
  questionTitle: "",
  optionJson: "",
  correctAnswer: "",
  questionScore: 5,
  sortNo: 1,
  analysisText: ""
});
const form = reactive(createForm());

const rules: FormRules = {
  questionType: [{ required: true, message: "请选择题型", trigger: "change" }],
  questionTitle: [{ required: true, message: "请输入题目", trigger: "blur" }],
  questionScore: [{ required: true, message: "请填写分值", trigger: "change" }]
};

async function loadOptions() {
  const page = await fetchExamPage({ limit: 200 });
  examOptions.value = page.list;
}

async function loadRows() {
  loading.value = true;
  try {
    const page = await fetchExamQuestionPage({
      page: pagination.page,
      limit: pagination.limit,
      examId: filters.examId,
      questionType: filters.questionType || undefined
    });
    rows.value = page.list;
    pagination.total = page.totalCount;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  loadRows();
}

async function resetFilters() {
  filters.examId = undefined;
  filters.questionType = "";
  pagination.page = 1;
  await loadOptions();
  loadRows();
}

function handleSizeChange() {
  pagination.page = 1;
  loadRows();
}

function resetForm() {
  Object.assign(form, createForm());
}

function normalizeQuestionType(value?: string) {
  if (!value) return "选择题";
  if (value.includes("判断")) return "判断题";
  if (value.includes("填空")) return "填空题";
  if (value.includes("简答") || value.includes("问答")) return "简答题";
  return "选择题";
}

async function openCreate() {
  resetForm();
  await loadOptions();
  dialogVisible.value = true;
}

function openAiAssistant() {
  void router.push({
    name: "ai-chat",
    query: {
      bizScene: "teacher_question_generation",
      pageCode: "exam-question-create",
      questionType: form.questionType
    }
  });
}

async function openEdit(id: number) {
  resetForm();
  await loadOptions();
  Object.assign(form, await fetchEntityDetail("examQuestion", id));
  form.questionType = normalizeQuestionType(form.questionType);
  if (!form.id) {
    form.id = id;
  }
  dialogVisible.value = true;
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    await saveEntity("examQuestion", form as unknown as Record<string, unknown>);
    ElMessage.success("题目已保存");
    dialogVisible.value = false;
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  await deleteEntities("examQuestion", [id]);
  ElMessage.success("题目已删除");
  await loadRows();
}

loadOptions();
loadRows();
</script>

<style scoped>
.question-ai-helper {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(255, 227, 195, 0.92), rgba(255, 248, 240, 0.98));
  border: 1px solid rgba(255, 195, 91, 0.42);
}

.question-ai-helper__text {
  min-width: 0;
}

.question-ai-helper strong {
  display: block;
  margin-bottom: 4px;
  color: #7a4300;
  font-size: 14px;
}

.question-ai-helper p {
  margin: 0;
  color: #85531a;
  line-height: 1.6;
  font-size: 13px;
}

.question-ai-helper :deep(.el-button) {
  flex: 0 0 auto;
  margin-top: 2px;
}
</style>
