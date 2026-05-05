<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>作业管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="filters.zuoyeName" placeholder="搜索作业标题" clearable />
        <el-select v-model="filters.kechengId" placeholder="课程" clearable>
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.publishStatus" placeholder="发布状态" clearable>
          <el-option label="草稿" value="draft" />
          <el-option label="已发布" value="published" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="success" @click="openCreate">新增作业</el-button>
      </div>
    </div>

    <el-table :data="items" stripe empty-text="暂无作业数据">
      <el-table-column prop="zuoyeName" label="作业标题" min-width="220" />
      <el-table-column prop="kechengName" label="课程" min-width="180" />
      <el-table-column prop="chapterName" label="章节" min-width="160" />
      <el-table-column prop="scoreTotal" label="总分" min-width="90" />
      <el-table-column prop="deadlineTime" label="截止时间" min-width="180" />
      <el-table-column label="状态" min-width="120">
        <template #default="{ row }">
          {{ formatStatus(row.publishStatus) }}
        </template>
      </el-table-column>
      <el-table-column label="题目数" min-width="100">
        <template #default="{ row }">
          {{ countQuestionIds(row.questionIds) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row.id)">编辑</el-button>
          <el-button v-if="row.publishStatus !== 'published'" link type="success" @click="publishHomework(row.id)">发布</el-button>
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

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑作业' : '新增作业'" width="1080px">
    <div class="homework-editor">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px" class="homework-editor__form">
        <el-form-item label="作业标题" prop="zuoyeName" required>
          <el-input v-model="form.zuoyeName" />
        </el-form-item>
        <el-form-item label="作业类型" prop="zuoyeTypes" required>
          <el-select v-model="form.zuoyeTypes" placeholder="请选择作业类型">
            <el-option v-for="item in typeOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!isTeacher" label="教师" prop="jiaoshiId" required>
          <el-select v-model="form.jiaoshiId" placeholder="请选择教师">
            <el-option v-for="item in teacherOptions" :key="item.id" :label="item.jiaoshiName" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="kechengId" required>
          <el-select v-model="form.kechengId" @change="handleCourseChange">
            <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="章节" prop="chapterId">
          <el-select v-model="form.chapterId" clearable>
            <el-option v-for="item in chapterOptions" :key="item.id" :label="item.chapterName" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止时间" prop="deadlineTime" required>
          <el-date-picker v-model="form.deadlineTime" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item label="作业附件">
          <input type="file" @change="handleUpload($event, 'zuoyeFile')" />
          <p class="upload-tip">{{ form.zuoyeFile || "未上传" }}</p>
        </el-form-item>
        <el-form-item label="封面图">
          <input type="file" accept="image/*" @change="handleUpload($event, 'zuoyePhoto')" />
          <p class="upload-tip">{{ form.zuoyePhoto || "未上传" }}</p>
        </el-form-item>
        <el-form-item label="作业说明">
          <el-input v-model="form.zuoyeContent" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>

      <section class="question-binding">
        <div class="panel-header panel-header--spread">
          <div>
            <h3>从题库中选择题目</h3>
            <p class="panel-note">作业和考试使用同一套题库，课程切换后自动只显示该课程题目。</p>
          </div>
          <span class="panel-note">已选 {{ selectedQuestionIds.length }} 题</span>
        </div>
        <el-transfer
          v-model="selectedQuestionIds"
          :data="transferData"
          filterable
          filter-placeholder="搜索题目"
          :titles="['题库', '作业']"
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
import type { ExamQuestionItem, HomeworkItem } from "@shared/index";
import { fetchHomeworks, fetchExamQuestionPage } from "@/api/dashboard";
import {
  deleteEntities,
  fetchCourseChaptersForSelect,
  fetchCoursesForSelect,
  fetchDictionaryOptions,
  fetchEntityDetail,
  fetchTeachersForSelect,
  postModuleAction,
  saveEntity,
  uploadAdminFile
} from "@/api/manage";
import { useAdminSessionStore } from "@/stores/session";

type TransferItem = {
  key: number;
  label: string;
  disabled?: boolean;
};

const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const formRef = ref<FormInstance>();
const items = ref<HomeworkItem[]>([]);
const teacherOptions = ref<Array<{ id: number; jiaoshiName: string }>>([]);
const typeOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]);
const courseOptions = ref<Array<{ id: number; kechengName: string }>>([]);
const chapterOptions = ref<Array<{ id: number; chapterName: string }>>([]);
const questionPool = ref<ExamQuestionItem[]>([]);
const selectedQuestionIds = ref<number[]>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({
  zuoyeName: "",
  kechengId: undefined as number | undefined,
  publishStatus: ""
});

const createForm = () => ({
  id: undefined as number | undefined,
  zuoyeName: "",
  zuoyeTypes: undefined as number | undefined,
  zuoyePhoto: "",
  zuoyeFile: "",
  jiaoshiId: isTeacher.value ? store.session?.userId : undefined,
  kechengId: undefined as number | undefined,
  chapterId: undefined as number | undefined,
  deadlineTime: "",
  publishStatus: "draft",
  questionIds: "",
  zuoyeContent: "",
  scoreTotal: 100,
  zuoyeDelete: 1
});
const form = reactive(createForm());

const rules: FormRules = {
  zuoyeName: [{ required: true, message: "请输入作业标题", trigger: "blur" }],
  zuoyeTypes: [{ required: true, message: "请选择作业类型", trigger: "change" }],
  jiaoshiId: [{ required: true, message: "请选择教师", trigger: "change" }],
  kechengId: [{ required: true, message: "请选择课程", trigger: "change" }],
  deadlineTime: [{ required: true, message: "请选择截止时间", trigger: "change" }]
};

function formatQuestionType(value?: string) {
  const text = value || "";
  if (text.includes("判断")) return "判断题";
  if (text.includes("填空")) return "填空题";
  if (text.includes("简答") || text.includes("问答")) return "简答题";
  return "选择题";
}

function formatStatus(value?: string) {
  if (value === "published") return "已发布";
  if (value === "draft") return "草稿";
  return value || "草稿";
}

function countQuestionIds(value?: string) {
  if (!value) return 0;
  return value.split(",").filter(Boolean).length;
}

const transferData = computed<TransferItem[]>(() =>
  questionPool.value
    .filter((item) => !form.kechengId || !item.kechengId || item.kechengId === form.kechengId)
    .map((item) => ({
      key: item.id,
      label: `${item.kechengName || "题库"} | ${formatQuestionType(item.questionType)} | ${item.questionTitle}`
    }))
);

async function loadOptions() {
  const teacherTask = isTeacher.value
    ? Promise.resolve([{ id: store.session?.userId ?? 0, jiaoshiName: store.session?.username || "当前教师" }])
    : fetchTeachersForSelect();
  const [courses, teachers, types] = await Promise.all([
    fetchCoursesForSelect(),
    teacherTask,
    fetchDictionaryOptions("zuoye_types")
  ]);
  courseOptions.value = courses;
  teacherOptions.value = teachers as Array<{ id: number; jiaoshiName: string }>;
  typeOptions.value = types;
}

async function loadQuestionPool() {
  const page = await fetchExamQuestionPage({ page: 1, limit: 500 });
  questionPool.value = page.list;
}

async function loadItems() {
  loading.value = true;
  try {
    const page = await fetchHomeworks({
      page: pagination.page,
      limit: pagination.limit,
      zuoyeName: filters.zuoyeName || undefined,
      kechengId: filters.kechengId,
      publishStatus: filters.publishStatus || undefined
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

async function resetFilters() {
  filters.zuoyeName = "";
  filters.kechengId = undefined;
  filters.publishStatus = "";
  pagination.page = 1;
  await loadOptions();
  loadItems();
}

function handleSizeChange() {
  pagination.page = 1;
  loadItems();
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
  Object.assign(form, await fetchEntityDetail("zuoye", id));
  chapterOptions.value = await fetchCourseChaptersForSelect(form.kechengId);
  selectedQuestionIds.value = (form.questionIds || "")
    .split(",")
    .map((item) => Number(item))
    .filter((item) => Number.isFinite(item) && item > 0);
  dialogVisible.value = true;
}

async function handleUpload(event: Event, field: "zuoyePhoto" | "zuoyeFile") {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  try {
    form[field] = await uploadAdminFile(file);
    ElMessage.success(field === "zuoyePhoto" ? "封面图已上传" : "作业附件已上传");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "上传失败");
  }
}

async function submitForm() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) {
    return;
  }
  saving.value = true;
  try {
    form.questionIds = selectedQuestionIds.value.join(",");
    const result = await saveEntity("zuoye", form as unknown as Record<string, unknown>);
    const savedHomework = result?.data as { id?: number } | undefined;
    const zuoyeId = savedHomework?.id || form.id;
    if (zuoyeId) {
      form.id = zuoyeId;
      await postModuleAction("zuoye", "bindQuestions", {
        zuoyeId,
        questionIds: selectedQuestionIds.value
      });
    }
    ElMessage.success("作业已保存");
    dialogVisible.value = false;
    await loadItems();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function publishHomework(id: number) {
  const detail = await fetchEntityDetail<HomeworkItem>("zuoye", id);
  await saveEntity("zuoye", {
    ...detail,
    publishStatus: "published"
  } as unknown as Record<string, unknown>);
  ElMessage.success("作业已发布");
  await loadItems();
}

async function removeItem(id: number) {
  await deleteEntities("zuoye", [id]);
  ElMessage.success("作业已删除");
  await loadItems();
}

loadOptions();
loadItems();
</script>

<style scoped>
.homework-editor {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
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
  .homework-editor {
    grid-template-columns: 1fr;
  }
}
</style>
