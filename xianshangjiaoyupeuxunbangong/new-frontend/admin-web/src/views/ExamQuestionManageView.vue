<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>题库管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-select v-model="filters.kechengId" placeholder="课程" clearable>
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.questionType" placeholder="题型" clearable>
          <el-option v-for="item in questionTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="success" @click="openCreate">新增题目</el-button>
      </div>
    </div>

    <el-table :data="rows" stripe empty-text="暂无题目">
      <el-table-column label="课程" min-width="180">
        <template #default="{ row }">
          {{ row.kechengName || "未分类" }}
        </template>
      </el-table-column>
      <el-table-column prop="questionType" label="题型" min-width="120">
        <template #default="{ row }">
          {{ formatQuestionType(row.questionType) }}
        </template>
      </el-table-column>
      <el-table-column prop="questionTitle" label="题目" min-width="320" show-overflow-tooltip />
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
      <el-form-item label="选项JSON">
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
import { reactive, ref } from "vue";
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
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ kechengId: undefined as number | undefined, questionType: "" });

const questionTypeOptions = [
  { label: "选择题", value: "选择题" },
  { label: "判断题", value: "判断题" },
  { label: "填空题", value: "填空题" },
  { label: "简答题", value: "简答题" }
];

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
  loadRows();
}

function resetFilters() {
  filters.kechengId = undefined;
  filters.questionType = "";
  pagination.page = 1;
  loadRows();
}

function handleSizeChange() {
  pagination.page = 1;
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
  form.questionType = normalizeQuestionType(form.questionType);
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
