<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <div>
        <h2>题库管理</h2>
        <p class="panel-note">默认按所属课程、题型分类展示，可按课程折叠和展开，方便集中阅览题目。</p>
      </div>
      <div class="toolbar toolbar--wrap">
        <el-select v-model="filters.kechengId" placeholder="课程" clearable>
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.questionType" placeholder="题型" clearable>
          <el-option v-for="item in questionTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button @click="expandAllCourses">全部展开</el-button>
        <el-button @click="collapseAllCourses">全部折叠</el-button>
        <el-button type="success" @click="openCreate">新增题目</el-button>
      </div>
    </div>

    <div v-if="groupedRows.length" class="question-groups">
      <section v-for="group in groupedRows" :key="group.courseName" class="question-group">
        <div class="question-group__header">
          <div>
            <h3>{{ group.courseName }}</h3>
            <p>当前页共 {{ group.total }} 道题，按题型分组展示</p>
          </div>
          <div class="question-group__actions">
            <el-tag type="info" round>{{ group.total }}</el-tag>
            <el-button text type="primary" @click="toggleCourseGroup(group.courseName)">
              {{ isCourseCollapsed(group.courseName) ? "展开" : "折叠" }}
            </el-button>
          </div>
        </div>

        <div v-show="!isCourseCollapsed(group.courseName)" class="question-group__types">
          <article
            v-for="typeGroup in group.typeGroups"
            :key="`${group.courseName}-${typeGroup.type}`"
            class="question-type-card"
          >
            <div class="question-type-card__header">
              <div>
                <strong>{{ typeGroup.type }}</strong>
                <p>共 {{ typeGroup.items.length }} 道题</p>
              </div>
              <span class="question-type-card__count">{{ typeGroup.items.length }}</span>
            </div>

            <el-table :data="typeGroup.items" stripe>
              <el-table-column prop="questionTitle" label="题目" min-width="360" show-overflow-tooltip />
              <el-table-column prop="questionScore" label="分值" min-width="90" />
              <el-table-column prop="sortNo" label="排序" min-width="90" />
              <el-table-column label="操作" width="180" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="openEdit(row.id)">编辑</el-button>
                  <el-button link type="danger" @click="removeItem(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </article>
        </div>
      </section>
    </div>

    <el-empty v-else description="暂无题目数据" />

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        background
        layout="total, sizes, prev, pager, next"
        :total="pagination.total"
        :page-sizes="[50, 100, 200, 500]"
        @current-change="loadRows"
        @size-change="handleSizeChange"
      />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑题目' : '新增题目'" width="760px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="所属课程" prop="kechengId" required>
        <el-select v-model="form.kechengId" placeholder="请选择课程">
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="题型" prop="questionType" required>
        <el-select v-model="form.questionType" placeholder="请选择题型">
          <el-option v-for="item in questionTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="题目" prop="questionTitle" required>
        <el-input v-model="form.questionTitle" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="选项 JSON">
        <el-input v-model="form.optionJson" type="textarea" :rows="4" />
      </el-form-item>
      <el-form-item label="正确答案">
        <el-input v-model="form.correctAnswer" placeholder="请输入参考答案" />
      </el-form-item>
      <el-form-item label="分值" prop="questionScore" required>
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
      <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import type { ExamQuestionItem } from "@shared/index";
import { fetchCoursesForSelect, deleteEntities, fetchEntityDetail, saveEntity } from "@/api/manage";
import { fetchExamQuestionPage } from "@/api/dashboard";

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const formRef = ref<FormInstance>();
const rows = ref<ExamQuestionItem[]>([]);
const courseOptions = ref<Array<{ id: number; kechengName: string }>>([]);
const collapsedCourseNames = ref<string[]>([]);
const pagination = reactive({ page: 1, limit: 500, total: 0 });
const filters = reactive({ kechengId: undefined as number | undefined, questionType: "" });

const questionTypeOptions = [
  { label: "选择题", value: "选择题" },
  { label: "判断题", value: "判断题" },
  { label: "填空题", value: "填空题" },
  { label: "简答题", value: "简答题" }
];

const courseNameMap = computed(() => {
  const map = new Map<number, string>();
  courseOptions.value.forEach((item) => map.set(item.id, item.kechengName));
  return map;
});

const groupedRows = computed(() => {
  const groups = new Map<string, Map<string, ExamQuestionItem[]>>();
  rows.value.forEach((item) => {
    const courseName = item.kechengName || courseNameMap.value.get(item.kechengId ?? -1) || "未分类";
    const questionType = formatQuestionType(item.questionType);
    if (!groups.has(courseName)) {
      groups.set(courseName, new Map<string, ExamQuestionItem[]>());
    }
    const typeMap = groups.get(courseName)!;
    const current = typeMap.get(questionType) || [];
    current.push(item);
    typeMap.set(questionType, current);
  });
  return Array.from(groups.entries()).map(([courseName, typeMap]) => {
    const typeGroups = Array.from(typeMap.entries()).map(([type, items]) => ({ type, items }));
    const total = typeGroups.reduce((sum, item) => sum + item.items.length, 0);
    return { courseName, total, typeGroups };
  });
});

const createForm = () => ({
  id: undefined as number | undefined,
  kechengId: undefined as number | undefined,
  examId: 0,
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
  kechengId: [{ required: true, message: "请选择课程", trigger: "change" }],
  questionType: [{ required: true, message: "请选择题型", trigger: "change" }],
  questionTitle: [{ required: true, message: "请输入题目", trigger: "blur" }],
  questionScore: [{ required: true, message: "请输入分值", trigger: "change" }]
};

function normalizeQuestionType(value?: string) {
  const text = value || "";
  if (!text) {
    return "选择题";
  }
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

function formatQuestionType(value?: string) {
  return normalizeQuestionType(value);
}

function isCourseCollapsed(courseName: string) {
  return collapsedCourseNames.value.includes(courseName);
}

function toggleCourseGroup(courseName: string) {
  if (isCourseCollapsed(courseName)) {
    collapsedCourseNames.value = collapsedCourseNames.value.filter((item) => item !== courseName);
    return;
  }
  collapsedCourseNames.value = [...collapsedCourseNames.value, courseName];
}

function collapseAllCourses() {
  collapsedCourseNames.value = groupedRows.value.map((item) => item.courseName);
}

function expandAllCourses() {
  collapsedCourseNames.value = [];
}

async function loadOptions() {
  courseOptions.value = await fetchCoursesForSelect();
}

async function loadRows() {
  loading.value = true;
  try {
    const page = await fetchExamQuestionPage({
      page: pagination.page,
      limit: pagination.limit,
      kechengId: filters.kechengId,
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
  expandAllCourses();
  loadRows();
}

function resetFilters() {
  filters.kechengId = undefined;
  filters.questionType = "";
  pagination.page = 1;
  expandAllCourses();
  loadRows();
}

function handleSizeChange() {
  pagination.page = 1;
  expandAllCourses();
  loadRows();
}

function resetForm() {
  Object.assign(form, createForm());
}

async function openCreate() {
  resetForm();
  await loadOptions();
  dialogVisible.value = true;
}

async function openEdit(id: number) {
  resetForm();
  await loadOptions();
  Object.assign(form, await fetchEntityDetail("examQuestion", id));
  form.questionType = questionTypeOptions.find((item) => item.value === normalizeQuestionType(form.questionType))?.value || "选择题";
  if (form.examId == null) {
    form.examId = 0;
  }
  dialogVisible.value = true;
}

async function submitForm() {
  try {
    const valid = await formRef.value?.validate().catch(() => false);
    if (!valid) {
      return;
    }
    saving.value = true;
    await saveEntity("examQuestion", form as unknown as Record<string, unknown>);
    ElMessage.success("保存成功");
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
  ElMessage.success("删除成功");
  await loadRows();
}

loadOptions();
loadRows();
</script>

<style scoped>
.question-groups {
  display: grid;
  gap: 18px;
}

.question-group {
  padding: 18px;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 24px;
  background: linear-gradient(180deg, rgba(255, 251, 247, 0.94), rgba(255, 255, 255, 0.98));
  box-shadow: 0 18px 36px rgba(31, 41, 55, 0.05);
}

.question-group__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.question-group__header h3 {
  margin: 0;
  font-size: 16px;
  color: #0f172a;
}

.question-group__header p {
  margin: 6px 0 0;
  font-size: 13px;
  color: #64748b;
}

.question-group__actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.question-group__types {
  display: grid;
  gap: 14px;
}

.question-type-card {
  padding: 14px;
  border-radius: 20px;
  border: 1px solid rgba(15, 23, 42, 0.06);
  background: rgba(255, 255, 255, 0.88);
}

.question-type-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.question-type-card__header strong {
  color: #0f172a;
}

.question-type-card__header p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 12px;
}

.question-type-card__count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  padding: 0 10px;
  border-radius: 999px;
  background: rgba(255, 122, 26, 0.12);
  color: #d76413;
  font-weight: 700;
}
</style>
