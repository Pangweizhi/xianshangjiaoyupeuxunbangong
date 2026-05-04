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

    <el-table :data="rows" stripe>
      <el-table-column prop="examName" label="考试名称" min-width="220" />
      <el-table-column prop="kechengName" label="课程" min-width="180" />
      <el-table-column prop="chapterName" label="章节" min-width="160" />
      <el-table-column prop="totalScore" label="总分" min-width="90" />
      <el-table-column prop="passScore" label="及格线" min-width="90" />
      <el-table-column label="规则" min-width="220">
        <template #default="{ row }">
          <span>{{ row.allowRetake === 1 ? "允许重考" : "禁止重考" }}</span>
          <span> / 最多 {{ row.maxAttemptCount ?? 1 }} 次</span>
          <span> / {{ row.allowResume === 1 ? "可恢复" : "不可恢复" }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="startTime" label="开始时间" min-width="180" />
      <el-table-column prop="endTime" label="结束时间" min-width="180" />
      <el-table-column prop="examStatus" label="状态" min-width="120" />
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
        <el-form-item label="考试名称" prop="examName"><el-input v-model="form.examName" /></el-form-item>
        <el-form-item label="所属课程" prop="kechengId">
          <el-select v-model="form.kechengId" @change="handleCourseChange">
            <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属章节">
          <el-select v-model="form.chapterId" clearable>
            <el-option v-for="item in chapterOptions" :key="item.id" :label="item.chapterName" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="时长(分钟)" prop="durationMinutes"><el-input-number v-model="form.durationMinutes" :min="1" :max="300" /></el-form-item>
        <el-form-item label="及格线" prop="passScore"><el-input-number v-model="form.passScore" :min="1" :max="300" /></el-form-item>
        <el-form-item label="允许重复考试" prop="allowRetake">
          <el-radio-group v-model="form.allowRetake">
            <el-radio :label="0">否</el-radio>
            <el-radio :label="1">是</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="最大次数" prop="maxAttemptCount">
          <el-input-number v-model="form.maxAttemptCount" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="允许退出恢复" prop="allowResume">
          <el-radio-group v-model="form.allowResume">
            <el-radio :label="0">否</el-radio>
            <el-radio :label="1">是</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="开始时间" prop="startTime"><el-date-picker v-model="form.startTime" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" /></el-form-item>
        <el-form-item label="结束时间" prop="endTime"><el-date-picker v-model="form.endTime" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" /></el-form-item>
        <el-form-item label="考试说明"><el-input v-model="form.examSummary" type="textarea" :rows="4" /></el-form-item>
      </el-form>

      <section class="question-binding">
        <div class="panel-header panel-header--spread">
          <div>
            <h3>从题库中选题</h3>
            <p class="panel-note">先在题库中维护题目，再在这里选择本场考试要使用的题目。</p>
          </div>
          <span class="panel-note">已选 {{ selectedQuestionIds.length }} 题</span>
        </div>
        <el-transfer
          v-model="selectedQuestionIds"
          :data="transferData"
          filterable
          filter-placeholder="搜索题目"
          :titles="['题库', '本考试']"
          class="question-transfer"
        />
      </section>
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitForm">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import type { ExamItem, ExamQuestionItem } from "@shared/index";
import { fetchExamPage, fetchExamQuestionPage } from "@/api/dashboard";
import { deleteEntities, fetchCourseChaptersForSelect, fetchCoursesForSelect, fetchEntityDetail, postModuleAction, saveEntity } from "@/api/manage";

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
const chapterOptions = ref<Array<{ id: number; chapterName: string; kechengId: number }>>([]);
const questionPool = ref<ExamQuestionItem[]>([]);
const selectedQuestionIds = ref<number[]>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ examName: "", kechengId: undefined as number | undefined, examStatus: "" });

const createForm = () => ({
  id: undefined as number | undefined,
  examName: "",
  kechengId: undefined as number | undefined,
  chapterId: undefined as number | undefined,
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
  durationMinutes: [{ required: true, message: "请填写时长", trigger: "change" }],
  passScore: [{ required: true, message: "请填写及格线", trigger: "change" }],
  allowRetake: [{ required: true, message: "请选择是否允许重考", trigger: "change" }],
  maxAttemptCount: [{ required: true, message: "请填写最大次数", trigger: "change" }],
  allowResume: [{ required: true, message: "请选择是否允许恢复", trigger: "change" }],
  startTime: [{ required: true, message: "请选择开始时间", trigger: "change" }],
  endTime: [{ required: true, message: "请选择结束时间", trigger: "change" }]
};

const transferData = computed<TransferItem[]>(() =>
  questionPool.value.map((item) => ({
    key: item.id,
    label: `${item.questionType || "题目"}｜${item.questionTitle}`,
    disabled: Boolean(item.examId && item.examId !== form.id)
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

async function handleCourseChange() {
  form.chapterId = undefined;
  chapterOptions.value = await fetchCourseChaptersForSelect(form.kechengId);
}

function resetForm() {
  Object.assign(form, createForm());
  chapterOptions.value = [];
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
  chapterOptions.value = await fetchCourseChaptersForSelect(form.kechengId);
  selectedQuestionIds.value = questionPool.value.filter((item) => item.examId === form.id).map((item) => item.id);
  dialogVisible.value = true;
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;
  try {
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
