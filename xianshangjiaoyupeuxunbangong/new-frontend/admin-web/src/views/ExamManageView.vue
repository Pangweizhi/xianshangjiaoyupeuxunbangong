<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>考试管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="filters.examName" placeholder="搜索考试名称" clearable />
        <el-select v-model="filters.kechengId" placeholder="课程" clearable>
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.examStatus" placeholder="状态" clearable>
          <el-option label="草稿" value="draft" />
          <el-option label="已发布" value="published" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="success" @click="openCreate">新增考试</el-button>
      </div>
    </div>

    <el-table :data="rows" stripe empty-text="暂无考试数据">
      <el-table-column prop="examName" label="考试名称" min-width="220" />
      <el-table-column prop="kechengName" label="课程" min-width="180" />
      <el-table-column prop="totalScore" label="总分" min-width="90" />
      <el-table-column prop="passScore" label="及格分" min-width="90" />
      <el-table-column label="状态" min-width="120">
        <template #default="{ row }">
          {{ formatExamStatus(row.examStatus) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row.id)">编辑</el-button>
          <el-button v-if="row.examStatus !== 'published'" link type="success" @click="publishExam(row.id)">发布</el-button>
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

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑考试' : '新增考试'" width="1080px">
    <div class="exam-editor">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px" class="exam-editor__form">
        <el-form-item label="考试名称" prop="examName" required>
          <el-input v-model="form.examName" />
        </el-form-item>
        <el-form-item label="课程" prop="kechengId" required>
          <el-select v-model="form.kechengId">
            <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试时长（分）" prop="durationMinutes" required>
          <el-input-number v-model="form.durationMinutes" :min="1" :max="300" />
        </el-form-item>
        <el-form-item label="及格分" prop="passScore" required>
          <el-input-number v-model="form.passScore" :min="1" :max="300" />
        </el-form-item>
        <el-form-item label="允许重考" prop="allowRetake" required>
          <el-radio-group v-model="form.allowRetake">
            <el-radio :label="0">否</el-radio>
            <el-radio :label="1">是</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="最多次数" prop="maxAttemptCount" required>
          <el-input-number v-model="form.maxAttemptCount" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="允许续考" prop="allowResume" required>
          <el-radio-group v-model="form.allowResume">
            <el-radio :label="0">否</el-radio>
            <el-radio :label="1">是</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="开始时间" prop="startTime" required>
          <el-date-picker v-model="form.startTime" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item label="结束时间" prop="endTime" required>
          <el-date-picker v-model="form.endTime" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item label="考试说明">
          <el-input v-model="form.examSummary" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>

      <section class="question-binding">
        <div class="panel-header panel-header--spread">
          <div>
            <h3>从题库中选择题目</h3>
            <p class="panel-note">这里只显示当前课程的题目。</p>
          </div>
          <span class="panel-note">已选 {{ selectedQuestionIds.length }} 道</span>
        </div>
        <el-transfer
          v-model="selectedQuestionIds"
          :data="transferData"
          filterable
          filter-placeholder="搜索题目"
          :titles="['题库', '试卷']"
          class="question-transfer"
        />
      </section>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import type { ExamItem, ExamQuestionItem } from "@shared/index";
import { fetchCoursesForSelect, deleteEntities, fetchEntityDetail, saveEntity, postModuleAction } from "@/api/manage";
import { fetchExamPage, fetchExamQuestionPage } from "@/api/dashboard";

type TransferItem = {
  key: number;
  label: string;
  disabled?: boolean;
};

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const formRef = ref<FormInstance>();
const rows = ref<ExamItem[]>([]);
const courseOptions = ref<Array<{ id: number; kechengName: string }>>([]);
const questionPool = ref<ExamQuestionItem[]>([]);
const selectedQuestionIds = ref<number[]>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ examName: "", kechengId: undefined as number | undefined, examStatus: "" });

const createForm = () => ({
  id: undefined as number | undefined,
  examName: "",
  kechengId: undefined as number | undefined,
  durationMinutes: 60,
  passScore: 60,
  allowRetake: 0,
  maxAttemptCount: 1,
  allowResume: 1,
  startTime: "",
  endTime: "",
  examSummary: ""
});
const form = reactive(createForm());

const rules: FormRules = {
  examName: [{ required: true, message: "请输入考试名称", trigger: "blur" }],
  kechengId: [{ required: true, message: "请选择课程", trigger: "change" }],
  durationMinutes: [{ required: true, message: "请输入考试时长", trigger: "change" }],
  passScore: [{ required: true, message: "请输入及格分", trigger: "change" }],
  allowRetake: [{ required: true, message: "请选择是否允许重考", trigger: "change" }],
  maxAttemptCount: [{ required: true, message: "请输入最多次数", trigger: "change" }],
  allowResume: [{ required: true, message: "请选择是否允许续考", trigger: "change" }],
  startTime: [{ required: true, message: "请选择开始时间", trigger: "change" }],
  endTime: [{ required: true, message: "请选择结束时间", trigger: "change" }]
};

function formatQuestionType(value?: string) {
  const text = value || "";
  if (text.includes("判断") || text.includes("True")) {
    return "判断题";
  }
  if (text.includes("填空") || text.includes("Fill")) {
    return "填空题";
  }
  if (text.includes("简答") || text.includes("问答") || text.includes("Short")) {
    return "简答题";
  }
  return "选择题";
}

function formatExamStatus(value?: string) {
  if (value === "published") return "已发布";
  if (value === "draft") return "草稿";
  return value || "草稿";
}

const transferData = computed<TransferItem[]>(() =>
  questionPool.value
    .filter((item) => !form.kechengId || !item.kechengId || item.kechengId === form.kechengId)
    .map((item) => ({
      key: item.id,
      label: `${item.kechengName || "题库"} | ${formatQuestionType(item.questionType)} | ${item.questionTitle}`,
      disabled: Boolean((item.examId && item.examId !== form.id) || (item.kechengId && form.kechengId && item.kechengId !== form.kechengId))
    }))
);

async function loadOptions() {
  courseOptions.value = await fetchCoursesForSelect();
}

async function loadQuestionPool() {
  const page = await fetchExamQuestionPage({ page: 1, limit: 500 });
  questionPool.value = page.list;
}

async function loadRows() {
  loading.value = true;
  try {
    const page = await fetchExamPage({
      page: pagination.page,
      limit: pagination.limit,
      examName: filters.examName || undefined,
      kechengId: filters.kechengId,
      examStatus: filters.examStatus || undefined
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
  filters.examName = "";
  filters.kechengId = undefined;
  filters.examStatus = "";
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
  selectedQuestionIds.value = [];
}

async function openCreate() {
  resetForm();
  await Promise.all([loadOptions(), loadQuestionPool()]);
  dialogVisible.value = true;
}

async function openEdit(id: number) {
  resetForm();
  await Promise.all([loadOptions(), loadQuestionPool()]);
  Object.assign(form, await fetchEntityDetail("exam", id));
  selectedQuestionIds.value = questionPool.value
    .filter((item) => item.examId === form.id)
    .filter((item) => !form.kechengId || !item.kechengId || item.kechengId === form.kechengId)
    .map((item) => item.id);
  dialogVisible.value = true;
}

async function submitForm() {
  try {
    const valid = await formRef.value?.validate().catch(() => false);
    if (!valid) {
      return;
    }
    saving.value = true;
    const result = await saveEntity("exam", form as unknown as Record<string, unknown>);
    const savedExam = result?.data as { id?: number } | undefined;
    const examId = savedExam?.id || form.id;
    if (examId) {
      form.id = examId;
      await postModuleAction("examQuestion", "bindToExam", {
        examId,
        questionIds: selectedQuestionIds.value
      });
    }
    ElMessage.success("考试已保存");
    dialogVisible.value = false;
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function publishExam(id: number) {
  await postModuleAction("exam", "publish", { id });
  ElMessage.success("考试已发布");
  await loadRows();
}

async function removeItem(id: number) {
  await deleteEntities("exam", [id]);
  ElMessage.success("考试已删除");
  await loadRows();
}

loadOptions();
loadRows();
</script>

<style scoped>
.exam-editor {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.question-binding {
  padding: 18px;
  border-radius: 20px;
  background: rgba(247, 243, 238, 0.8);
}

.question-transfer {
  margin-top: 14px;
}

@media (max-width: 1024px) {
  .exam-editor {
    grid-template-columns: 1fr;
  }
}
</style>
