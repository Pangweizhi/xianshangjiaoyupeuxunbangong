<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <div>
        <h2>作业批改</h2>
        <p class="panel-note">作业提交已切换为题库作答模式，支持查看作答快照、自动得分和教师最终评分。</p>
      </div>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="filters.zuoyeName" placeholder="搜索作业标题" clearable />
        <el-input v-model="filters.yonghuName" placeholder="搜索学生姓名" clearable />
        <el-select v-model="filters.submitStatus" placeholder="状态" clearable>
          <el-option label="作答中" value="作答中" />
          <el-option label="待批改" value="待批改" />
          <el-option label="已批改" value="已批改" />
          <el-option label="需重交" value="需重交" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
    </div>

    <el-table :data="items" stripe>
      <el-table-column prop="zuoyeName" label="作业" min-width="180" />
      <el-table-column prop="yonghuName" label="学生" min-width="120" />
      <el-table-column prop="autoScore" label="自动分" min-width="90" />
      <el-table-column prop="submitScore" label="最终分" min-width="90" />
      <el-table-column prop="submitStatus" label="状态" min-width="120" />
      <el-table-column prop="checkTime" label="批改时间" min-width="180" />
      <el-table-column label="操作" min-width="260" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openReview(row)">详情</el-button>
          <el-button v-if="row.submitStatus === '待批改' || row.submitStatus === '已批改'" link type="success" @click="openReview(row)">批改</el-button>
          <el-button v-if="row.submitStatus !== '需重交'" link type="warning" @click="markRedo(row)">退回重交</el-button>
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
        @current-change="loadItems"
        @size-change="handleSizeChange"
      />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" title="作业批改详情" width="920px">
    <el-form :model="form" label-width="100px">
      <el-form-item label="作业"><el-input v-model="form.zuoyeName" disabled /></el-form-item>
      <el-form-item label="学生"><el-input v-model="form.yonghuName" disabled /></el-form-item>
      <el-form-item label="状态"><el-input v-model="form.submitStatus" disabled /></el-form-item>
      <el-form-item label="自动得分"><el-input :model-value="String(form.autoScore ?? 0)" disabled /></el-form-item>
      <el-form-item label="最终得分">
        <el-input-number v-model="form.submitScore" :min="0" :max="300" :disabled="!canCheckCurrent" />
      </el-form-item>
      <el-form-item label="评语">
        <el-input v-model="form.submitRemark" type="textarea" :rows="4" :disabled="!canCheckCurrent" />
      </el-form-item>
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
      <el-button @click="dialogVisible = false">关闭</el-button>
      <el-button v-if="canCheckCurrent" type="primary" :loading="saving" @click="submitCheck">提交批改</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import type { HomeworkSubmissionItem } from "@shared/index";
import { fetchHomeworkSubmissionPage } from "@/api/dashboard";
import { deleteEntities, fetchEntityDetail, postModuleAction, saveEntity } from "@/api/manage";

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
const items = ref<HomeworkSubmissionItem[]>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ zuoyeName: "", yonghuName: "", submitStatus: "" });
const form = reactive({
  id: undefined as number | undefined,
  zuoyeId: undefined as number | undefined,
  yonghuId: undefined as number | undefined,
  zuoyeName: "",
  yonghuName: "",
  submitStatus: "",
  autoScore: 0,
  submitScore: 0,
  submitRemark: "",
  questionSnapshot: ""
});

const canCheckCurrent = computed(() => form.submitStatus === "待批改" || form.submitStatus === "已批改");
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

async function loadItems() {
  loading.value = true;
  try {
    const page = await fetchHomeworkSubmissionPage({
      page: pagination.page,
      limit: pagination.limit,
      zuoyeName: filters.zuoyeName || undefined,
      yonghuName: filters.yonghuName || undefined,
      submitStatus: filters.submitStatus || undefined
    });
    items.value = page.list;
    pagination.total = page.totalCount;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  loadItems();
}

function handleSizeChange() {
  pagination.page = 1;
  loadItems();
}

async function openReview(row: HomeworkSubmissionItem) {
  const detail = await fetchEntityDetail<HomeworkSubmissionItem>("zuoyeSubmit", row.id);
  form.id = row.id;
  form.zuoyeId = row.zuoyeId;
  form.yonghuId = row.yonghuId;
  form.zuoyeName = row.zuoyeName || "";
  form.yonghuName = row.yonghuName || "";
  form.submitStatus = detail.submitStatus || row.submitStatus || "";
  form.autoScore = detail.autoScore ?? row.autoScore ?? 0;
  form.submitScore = detail.submitScore ?? row.submitScore ?? detail.autoScore ?? 0;
  form.submitRemark = detail.submitRemark || "";
  form.questionSnapshot = detail.questionSnapshot || "";
  dialogVisible.value = true;
}

async function submitCheck() {
  if (!form.id) return;
  saving.value = true;
  try {
    await postModuleAction("zuoyeSubmit", "check", {
      id: form.id,
      submitScore: form.submitScore,
      submitRemark: form.submitRemark
    });
    ElMessage.success("作业批改已保存");
    dialogVisible.value = false;
    await loadItems();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "提交失败");
  } finally {
    saving.value = false;
  }
}

async function markRedo(row: HomeworkSubmissionItem) {
  try {
    await saveEntity("zuoyeSubmit", {
      id: row.id,
      zuoyeId: row.zuoyeId,
      yonghuId: row.yonghuId,
      submitStatus: "需重交",
      submitScore: null,
      submitRemark: row.submitRemark || "教师已退回，请根据要求修改后重新提交。"
    });
    ElMessage.success("已退回重交");
    await loadItems();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "操作失败");
  }
}

async function removeItem(id: number) {
  await deleteEntities("zuoyeSubmit", [id]);
  ElMessage.success("提交记录已删除");
  await loadItems();
}

loadItems();
</script>
