<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>阅卷管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-select v-model="filters.recordStatus" placeholder="状态" clearable>
          <el-option label="开始作答" value="started" />
          <el-option label="待阅卷" value="pending_check" />
          <el-option label="已完成" value="checked" />
          <el-option label="已重置" value="reset" />
          <el-option label="已作废" value="voided" />
        </el-select>
        <el-select v-model="filters.passStatus" placeholder="通过状态" clearable>
          <el-option label="通过" value="passed" />
          <el-option label="未通过" value="failed" />
          <el-option label="已重置" value="reset" />
          <el-option label="已作废" value="voided" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
    </div>

    <el-table :data="rows" stripe>
      <el-table-column prop="examName" label="考试" min-width="180" />
      <el-table-column prop="kechengName" label="课程" min-width="160" />
      <el-table-column prop="yonghuName" label="学生" min-width="120" />
      <el-table-column prop="autoScore" label="自动分" min-width="90" />
      <el-table-column prop="manualScore" label="人工分" min-width="90" />
      <el-table-column prop="finalScore" label="总分" min-width="90" />
      <el-table-column prop="recordStatus" label="状态" min-width="120" />
      <el-table-column prop="passStatus" label="结果" min-width="100" />
      <el-table-column label="操作" min-width="260" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openCheck(row)">详情</el-button>
          <el-button v-if="row.recordStatus === 'pending_check' || row.recordStatus === 'checked'" link type="success" @click="openCheck(row)">阅卷</el-button>
          <el-button v-if="row.recordStatus === 'started'" link type="warning" @click="applyRecordAction(row, 'reset')">重置</el-button>
          <el-button v-if="row.recordStatus !== 'voided' && row.recordStatus !== 'reset'" link type="danger" @click="applyRecordAction(row, 'voidRecord')">作废</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.limit" background layout="total, sizes, prev, pager, next" :total="pagination.total" :page-sizes="[10,20,50]" @current-change="loadRows" @size-change="handleSizeChange" />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" title="阅卷详情" width="880px">
    <el-form :model="form" label-width="100px">
      <el-form-item label="考试"><el-input v-model="form.examName" disabled /></el-form-item>
      <el-form-item label="学生"><el-input v-model="form.yonghuName" disabled /></el-form-item>
      <el-form-item label="记录状态"><el-input v-model="form.recordStatus" disabled /></el-form-item>
      <el-form-item label="自动得分"><el-input :model-value="String(form.autoScore ?? 0)" disabled /></el-form-item>
      <el-form-item label="人工得分"><el-input-number v-model="form.manualScore" :min="0" :max="300" :disabled="!canCheckCurrent" /></el-form-item>
      <el-form-item label="评语"><el-input v-model="form.checkRemark" type="textarea" :rows="4" :disabled="!canCheckCurrent" /></el-form-item>
    </el-form>

    <div class="paper-preview">
      <article v-for="(question, index) in parsedQuestions" :key="question.id || index" class="paper-preview__item">
        <div class="paper-preview__head">
          <strong>{{ index + 1 }}. {{ question.title || "未命名题目" }}</strong>
          <span>{{ question.type || "题目" }} / {{ question.score ?? 0 }} 分</span>
        </div>
        <div v-if="parsedOptions(question.options).length" class="paper-preview__options">
          <p v-for="option in parsedOptions(question.options)" :key="option.value">
            {{ option.value }}. {{ option.label }}
          </p>
        </div>
        <p><strong>学生答案：</strong>{{ question.answer || "未作答" }}</p>
        <p v-if="question.correctAnswer"><strong>标准答案：</strong>{{ question.correctAnswer }}</p>
        <p v-if="question.analysisText"><strong>解析：</strong>{{ question.analysisText }}</p>
        <p><strong>自动判定：</strong>{{ renderAutoResult(question) }}</p>
      </article>
    </div>

    <template #footer>
      <el-button @click="dialogVisible=false">关闭</el-button>
      <el-button v-if="canCheckCurrent" type="primary" :loading="saving" @click="submitCheck">提交阅卷</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import type { ExamRecordItem } from "@shared/index";
import { fetchExamRecordPage } from "@/api/dashboard";
import { fetchEntityDetail, postModuleAction } from "@/api/manage";

interface QuestionSnapshotItem {
  id?: number;
  type?: string;
  title?: string;
  score?: number;
  options?: string;
  correctAnswer?: string;
  analysisText?: string;
  answer?: string;
  isSubjective?: boolean;
  autoCorrect?: boolean;
}

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const rows = ref<ExamRecordItem[]>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ recordStatus: "", passStatus: "" });
const form = reactive({
  id: undefined as number | undefined,
  examName: "",
  yonghuName: "",
  recordStatus: "",
  autoScore: 0,
  manualScore: 0,
  checkRemark: "",
  questionSnapshot: ""
});

const canCheckCurrent = computed(() => form.recordStatus === "pending_check" || form.recordStatus === "checked");
const parsedQuestions = computed<QuestionSnapshotItem[]>(() => {
  if (!form.questionSnapshot) return [];
  try {
    return JSON.parse(form.questionSnapshot) as QuestionSnapshotItem[];
  } catch {
    return [];
  }
});

function parsedOptions(raw?: string) {
  if (!raw) return [];
  try {
    const data = JSON.parse(raw) as Record<string, string>;
    return Object.entries(data).map(([value, label]) => ({ value, label }));
  } catch {
    return [];
  }
}

function renderAutoResult(question: QuestionSnapshotItem) {
  if (question.isSubjective) return "主观题，等待教师判分";
  return question.autoCorrect ? "客观题判定正确" : "客观题判定错误";
}

async function loadRows() {
  loading.value = true;
  try {
    const page = await fetchExamRecordPage({
      page: pagination.page,
      limit: pagination.limit,
      recordStatus: filters.recordStatus || undefined,
      passStatus: filters.passStatus || undefined
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

function handleSizeChange() {
  pagination.page = 1;
  loadRows();
}

async function openCheck(row: ExamRecordItem) {
  const detail = await fetchEntityDetail<ExamRecordItem>("examRecord", row.id);
  form.id = row.id;
  form.examName = row.examName || "";
  form.yonghuName = row.yonghuName || "";
  form.recordStatus = detail.recordStatus || row.recordStatus || "";
  form.autoScore = detail.autoScore ?? row.autoScore ?? 0;
  form.manualScore = detail.manualScore ?? 0;
  form.checkRemark = detail.checkRemark || "";
  form.questionSnapshot = detail.questionSnapshot || "";
  dialogVisible.value = true;
}

async function submitCheck() {
  if (!form.id) return;
  saving.value = true;
  try {
    await postModuleAction("examRecord", "check", {
      id: form.id,
      manualScore: form.manualScore,
      checkRemark: form.checkRemark
    });
    ElMessage.success("阅卷完成");
    dialogVisible.value = false;
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "提交失败");
  } finally {
    saving.value = false;
  }
}

async function applyRecordAction(row: ExamRecordItem, action: "reset" | "voidRecord") {
  const title = action === "reset" ? "重置作答" : "作废记录";
  const message = action === "reset"
    ? "该操作会释放未提交的考试记录，学生可重新开始本次考试。是否继续？"
    : "该操作会将本次考试记录作废，不再计入重考次数和成绩。是否继续？";
  await ElMessageBox.confirm(message, title, { type: "warning" });
  try {
    await postModuleAction("examRecord", action, {
      id: row.id,
      checkRemark: action === "reset" ? "教师重置作答记录" : "教师作废考试记录"
    });
    ElMessage.success(action === "reset" ? "已重置作答记录" : "已作废考试记录");
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "操作失败");
  }
}

loadRows();
</script>
