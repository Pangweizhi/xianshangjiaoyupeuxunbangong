<template>
  <section class="admin-panel exam-question-page" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <div>
        <h2>题库管理</h2>
        <p class="panel-note">可按课程和题型筛选，也可以通过 AI 面板生成草稿并保存到题库中。</p>
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
        <el-button @click="expandAllCourses">展开全部</el-button>
        <el-button @click="collapseAllCourses">收起全部</el-button>
        <el-button type="warning" plain @click="openAiPanel">AI 出题</el-button>
        <el-button type="success" @click="openCreate">新增题目</el-button>
      </div>
    </div>

    <div v-if="groupedRows.length" class="question-groups">
      <section v-for="group in groupedRows" :key="group.courseName" class="question-group">
        <div class="question-group__header">
          <div>
            <h3>{{ group.courseName }}</h3>
            <p>本课程共 {{ group.total }} 题</p>
          </div>
          <div class="question-group__actions">
            <el-tag type="info" round>{{ group.total }}</el-tag>
            <el-button text type="primary" @click="toggleCourseGroup(group.courseName)">
              {{ isCourseCollapsed(group.courseName) ? "展开" : "收起" }}
            </el-button>
          </div>
        </div>

        <div v-show="!isCourseCollapsed(group.courseName)" class="question-group__types">
          <article v-for="typeGroup in group.typeGroups" :key="`${group.courseName}-${typeGroup.type}`" class="question-type-card">
            <div class="question-type-card__header">
              <div>
                <strong>{{ typeGroup.type }}</strong>
                <p>{{ typeGroup.items.length }} questions</p>
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

    <el-empty v-else description="暂无题目" />

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
      <el-form-item label="课程" prop="kechengId" required>
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
        <el-input v-model="form.optionJson" type="textarea" :rows="4" placeholder="选择题或判断题请使用 JSON 格式" />
      </el-form-item>
      <el-form-item label="答案">
        <el-input v-model="form.correctAnswer" placeholder="参考答案" />
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

  <el-dialog v-model="aiDialogVisible" title="AI 出题面板" width="1180px" class="ai-question-dialog">
    <div class="ai-question-panel">
      <section class="ai-question-panel__settings">
        <div class="ai-question-panel__section-title">
          <h3>生成设置</h3>
          <p>选择课程、题型和数量，AI 会结合课程上下文生成题目草稿。</p>
        </div>

        <el-form :model="aiForm" label-width="92px" class="ai-question-form">
          <el-form-item label="课程">
            <el-select v-model="aiForm.kechengId" placeholder="请选择课程" filterable>
              <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="章节">
            <el-select v-model="aiForm.chapterId" placeholder="可选" clearable filterable>
              <el-option v-for="item in chapterOptions" :key="item.id" :label="item.chapterName" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="题型">
            <el-select v-model="aiForm.questionType" placeholder="请选择题型">
              <el-option v-for="item in questionTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="数量">
            <el-input-number v-model="aiForm.questionCount" :min="1" :max="10" />
          </el-form-item>
          <el-form-item label="分值">
            <el-input-number v-model="aiForm.questionScore" :min="1" :max="100" />
          </el-form-item>
          <el-form-item label="难度">
            <el-select v-model="aiForm.difficulty" placeholder="请选择难度">
              <el-option v-for="item in difficultyOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="备注">
            <el-input
              v-model="aiForm.requirements"
              type="textarea"
              :rows="5"
              maxlength="500"
              show-word-limit
              placeholder="例如：贴合章节重点，干扰项合理，包含答案和解析"
            />
          </el-form-item>
        </el-form>

        <div class="ai-question-panel__actions">
          <el-button type="primary" :loading="aiGenerating" @click="generateAiDrafts">一键生成</el-button>
          <el-button @click="resetAiForm">重置</el-button>
        </div>

        <div class="ai-question-panel__summary" v-if="aiSummaryText">
          {{ aiSummaryText }}
        </div>
      </section>

      <section class="ai-question-panel__results">
        <div class="ai-question-panel__section-title">
          <h3>题目草稿</h3>
          <p>可以将草稿回填到表单，也可以直接确认保存到题库。</p>
        </div>

        <el-empty v-if="!generatedDrafts.length && !aiGenerating" description="题目草稿会显示在这里" />

        <div v-else class="ai-result-list">
          <article v-for="(draft, index) in generatedDrafts" :key="draftKey(draft, index)" class="ai-result-card">
            <div class="ai-result-card__header">
              <div>
                <strong>草稿 {{ index + 1 }}</strong>
                <p>{{ formatQuestionType(draft.questionType || aiForm.questionType) }}</p>
              </div>
              <el-tag :type="draft._saved ? 'success' : 'warning'" round>{{ draft._saved ? "已保存" : "待保存" }}</el-tag>
            </div>

            <h4 class="ai-result-card__title">{{ draft.questionTitle }}</h4>

            <div v-if="parseDraftOptions(draft.optionJson).length" class="ai-result-card__options">
              <div v-for="option in parseDraftOptions(draft.optionJson)" :key="`${draftKey(draft, index)}-${option.value}`" class="option-item">
                <strong>{{ option.value }}</strong>
                <span>{{ option.label }}</span>
              </div>
            </div>

            <div class="ai-result-card__meta">
              <span>分值：{{ draft.questionScore ?? aiForm.questionScore }}</span>
              <span>答案：{{ draft.correctAnswer || "暂无" }}</span>
              <span>排序：{{ draft.sortNo ?? index + 1 }}</span>
            </div>

            <p v-if="draft.analysisText" class="ai-result-card__analysis">解析：{{ draft.analysisText }}</p>

            <div class="ai-result-card__actions">
              <el-button @click="applyGeneratedDraft(draft)">回填表单</el-button>
              <el-button type="primary" :loading="savingDraftKey === draftKey(draft, index)" @click="saveGeneratedDraft(draft, index)">
                确认保存
              </el-button>
            </div>
          </article>
        </div>
      </section>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import type { CourseChapterItem, ExamQuestionItem, GeneratedExamQuestionDraft, QuestionGenerationResponse } from "@shared/index";
import { generateExamQuestionDrafts } from "@/api/ai";
import { fetchCourseChaptersForSelect, deleteEntities, fetchEntityDetail, fetchCoursesForSelect, saveEntity } from "@/api/manage";
import { fetchExamQuestionPage } from "@/api/dashboard";

type DraftViewItem = GeneratedExamQuestionDraft & { _saved?: boolean };
type DraftOption = { value: string; label: string };

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const aiDialogVisible = ref(false);
const aiGenerating = ref(false);
const savingDraftKey = ref("");
const formRef = ref<FormInstance>();
const rows = ref<ExamQuestionItem[]>([]);
const courseOptions = ref<Array<{ id: number; kechengName: string }>>([]);
const chapterOptions = ref<Array<Pick<CourseChapterItem, "id" | "chapterName" | "kechengId">>>([]);
const collapsedCourseNames = ref<string[]>([]);
const generatedDrafts = ref<DraftViewItem[]>([]);
const pagination = reactive({ page: 1, limit: 500, total: 0 });
const filters = reactive({ kechengId: undefined as number | undefined, questionType: "" });
const aiForm = reactive({
  kechengId: undefined as number | undefined,
  chapterId: undefined as number | undefined,
  questionType: "选择题",
  questionCount: 3,
  questionScore: 5,
  difficulty: "medium",
  requirements: ""
});

const questionTypeOptions = [
  { label: "选择题", value: "选择题" },
  { label: "判断题", value: "判断题" },
  { label: "填空题", value: "填空题" },
  { label: "简答题", value: "简答题" }
];

const difficultyOptions = [
  { label: "简单", value: "easy" },
  { label: "中等", value: "medium" },
  { label: "困难", value: "hard" }
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

const aiSummaryText = computed(() => {
  if (!aiForm.kechengId) {
    return "请选择一个课程开始生成。";
  }
  const courseName = courseNameMap.value.get(aiForm.kechengId) || "当前课程";
  const chapterName = chapterOptions.value.find((item) => item.id === aiForm.chapterId)?.chapterName;
  const typeText = formatQuestionType(aiForm.questionType);
  return `课程：${courseName}${chapterName ? `，章节：${chapterName}` : ""}。共 ${aiForm.questionCount} 道${typeText}，每题 ${aiForm.questionScore} 分。`;
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

watch(
  () => aiForm.kechengId,
  async (courseId) => {
    if (!courseId) {
      chapterOptions.value = [];
      aiForm.chapterId = undefined;
      return;
    }
    chapterOptions.value = await fetchCourseChaptersForSelect(courseId);
    if (!chapterOptions.value.some((item) => item.id === aiForm.chapterId)) {
      aiForm.chapterId = undefined;
    }
  }
);

function normalizeQuestionType(value?: string) {
  const text = value || "";
  if (!text) return "选择题";
  if (text.includes("选择") || text.includes("choice") || text.includes("select") || text.includes("single")) return "选择题";
  if (text.includes("判断") || text.includes("true") || text.includes("false") || text.includes("judge")) return "判断题";
  if (text.includes("填空") || text.includes("fill") || text.includes("blank")) return "填空题";
  if (text.includes("简答") || text.includes("问答") || text.includes("short") || text.includes("answer")) return "简答题";
  return "选择题";
}

function formatQuestionType(value?: string) {
  const type = normalizeQuestionType(value);
  const map: Record<string, string> = {
    选择题: "选择题",
    判断题: "判断题",
    填空题: "填空题",
    简答题: "简答题"
  };
  return map[type] || "选择题";
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
  void loadRows();
}

function resetFilters() {
  filters.kechengId = undefined;
  filters.questionType = "";
  pagination.page = 1;
  expandAllCourses();
  void loadRows();
}

function handleSizeChange() {
  pagination.page = 1;
  expandAllCourses();
  void loadRows();
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
    if (!valid) return;
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

async function openAiPanel() {
  await loadOptions();
  aiForm.kechengId = filters.kechengId || courseOptions.value[0]?.id;
  aiForm.questionType = filters.questionType ? normalizeQuestionType(filters.questionType) : "选择题";
  aiForm.questionCount = 3;
  aiForm.questionScore = 5;
  aiForm.difficulty = "medium";
  aiForm.requirements = "";
  aiForm.chapterId = undefined;
  generatedDrafts.value = [];
  aiDialogVisible.value = true;
}

function resetAiForm() {
  aiForm.kechengId = filters.kechengId || courseOptions.value[0]?.id;
  aiForm.chapterId = undefined;
  aiForm.questionType = filters.questionType ? normalizeQuestionType(filters.questionType) : "选择题";
  aiForm.questionCount = 3;
  aiForm.questionScore = 5;
  aiForm.difficulty = "medium";
  aiForm.requirements = "";
  generatedDrafts.value = [];
}

async function generateAiDrafts() {
  if (!aiForm.kechengId) {
    ElMessage.warning("Please select a course first");
    return;
  }
  aiGenerating.value = true;
  generatedDrafts.value = [];
  try {
    const result = await generateExamQuestionDrafts({
      courseId: aiForm.kechengId,
      chapterId: aiForm.chapterId,
      questionType: normalizeQuestionType(aiForm.questionType),
      questionCount: aiForm.questionCount,
      questionScore: aiForm.questionScore,
      difficulty: aiForm.difficulty,
      requirements: aiForm.requirements,
      bizScene: "teacher_question_generation",
      pageCode: "admin-exam-question-manage"
    });
    let drafts = extractGeneratedDrafts(result);
    if (!drafts.length) {
      drafts = buildLocalFallbackDrafts();
      ElMessage.warning("AI 返回为空，已使用本地兜底草稿");
    }
    generatedDrafts.value = drafts.map((item) => ({
      ...item,
      questionType: normalizeQuestionType(item.questionType),
      questionScore: item.questionScore ?? aiForm.questionScore,
      sortNo: item.sortNo ?? 1
    }));
    if (!generatedDrafts.value.length) {
      ElMessage.warning("未返回可用草稿");
      return;
    }
    ElMessage.success(`已生成 ${generatedDrafts.value.length} 个草稿`);
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "生成失败");
  } finally {
    aiGenerating.value = false;
  }
}

function parseDraftOptions(optionJson?: string): DraftOption[] {
  if (!optionJson) return [];
  try {
    const parsed = JSON.parse(optionJson);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .map((item) => ({
        value: String(item?.value ?? ""),
        label: String(item?.label ?? "")
      }))
      .filter((item) => item.value || item.label);
  } catch {
    return [];
  }
}

function extractGeneratedDrafts(result: unknown): GeneratedExamQuestionDraft[] {
  const directDrafts = (result as QuestionGenerationResponse | undefined)?.drafts;
  if (Array.isArray(directDrafts)) {
    return directDrafts;
  }
  const nestedDrafts = (result as { data?: QuestionGenerationResponse } | undefined)?.data?.drafts;
  if (Array.isArray(nestedDrafts)) {
    return nestedDrafts;
  }
  return [];
}

function buildLocalFallbackDrafts(): GeneratedExamQuestionDraft[] {
  const count = Math.min(Math.max(Number(aiForm.questionCount) || 1, 1), 10);
  const courseName = courseNameMap.value.get(aiForm.kechengId || 0) || "当前课程";
  const chapterName = chapterOptions.value.find((item) => item.id === aiForm.chapterId)?.chapterName || "";
  const questionType = normalizeQuestionType(aiForm.questionType);
  const difficultyLabel = difficultyOptions.find((item) => item.value === aiForm.difficulty)?.label || "";
  return Array.from({ length: count }).map((_, index) => {
    const sortNo = index + 1;
    return {
      kechengId: aiForm.kechengId,
      examId: 0,
      questionType,
      questionTitle: buildLocalFallbackTitle(courseName, chapterName, questionType, sortNo, difficultyLabel, aiForm.requirements),
      optionJson: buildLocalFallbackOptions(questionType),
      correctAnswer: buildLocalFallbackAnswer(questionType, sortNo),
      questionScore: aiForm.questionScore,
      sortNo,
      analysisText: buildLocalFallbackAnalysis(courseName, chapterName, questionType)
    };
  });
}

function buildLocalFallbackTitle(courseName: string, chapterName: string, questionType: string, index: number, difficultyLabel: string, requirements: string) {
  let title = `【${courseName}】`;
  if (chapterName) {
    title += `【${chapterName}】`;
  }
  title += `第${index}题：`;
  if (questionType === "判断题") {
    title += `下列关于${courseName}的说法是否正确？`;
  } else if (questionType === "填空题") {
    title += `请补全${courseName}的核心概念：______。`;
  } else if (questionType === "简答题") {
    title += `请简述${courseName}的关键知识点。`;
  } else {
    title += `关于${courseName}的核心知识，下列说法正确的是？`;
  }
  if (difficultyLabel) {
    title += `（${difficultyLabel}）`;
  }
  if (requirements) {
    title += ` ${requirements.slice(0, 40)}`;
  }
  return title;
}

function buildLocalFallbackOptions(questionType: string) {
  if (questionType === "判断题") {
    return JSON.stringify([
      { value: "对", label: "正确" },
      { value: "错", label: "错误" }
    ]);
  }
  if (questionType === "选择题") {
    return JSON.stringify([
      { value: "A", label: "选项A" },
      { value: "B", label: "选项B" },
      { value: "C", label: "选项C" },
      { value: "D", label: "选项D" }
    ]);
  }
  return "";
}

function buildLocalFallbackAnswer(questionType: string, index: number) {
  if (questionType === "判断题") {
    return index % 2 === 0 ? "错" : "对";
  }
  if (questionType === "选择题") {
    return "A";
  }
  if (questionType === "填空题") {
    return "核心概念";
  }
  return "请结合课程内容作答";
}

function buildLocalFallbackAnalysis(courseName: string, chapterName: string, questionType: string) {
  const context = chapterName ? `《${courseName}》的${chapterName}` : `《${courseName}》`;
  if (questionType === "简答题") {
    return `参考课程${context}内容作答，建议覆盖定义、步骤、结论与示例。`;
  }
  if (questionType === "填空题") {
    return "答案应与课程中的核心概念保持一致，注意关键术语准确。";
  }
  if (questionType === "判断题") {
    return "判断题重点考查对概念的理解，注意表述是否与课程内容一致。";
  }
  return "选择题应确保正确选项与课程知识点一致，干扰项与概念相近但不正确。";
}

function draftKey(draft: DraftViewItem, index: number) {
  return `${draft.questionType || "draft"}-${index}-${draft.sortNo ?? "na"}-${draft.questionTitle}`;
}

function buildDraftPayload(draft: DraftViewItem) {
  return {
    id: undefined,
    kechengId: aiForm.kechengId,
    examId: 0,
    questionType: normalizeQuestionType(draft.questionType || aiForm.questionType),
    questionTitle: draft.questionTitle,
    optionJson: draft.optionJson || "",
    correctAnswer: draft.correctAnswer || "",
    questionScore: draft.questionScore ?? aiForm.questionScore,
    sortNo: draft.sortNo ?? 1,
    analysisText: draft.analysisText || ""
  };
}

function applyGeneratedDraft(draft: DraftViewItem) {
  resetForm();
  Object.assign(form, buildDraftPayload(draft));
  dialogVisible.value = true;
}

async function saveGeneratedDraft(draft: DraftViewItem, index: number) {
  if (!aiForm.kechengId) {
    ElMessage.warning("请先选择课程");
    return;
  }
  const key = draftKey(draft, index);
  try {
    await ElMessageBox.confirm("是否将该 AI 草稿保存到题库中？", "确认保存", { type: "warning" });
  } catch {
    return;
  }

  savingDraftKey.value = key;
  try {
    await saveEntity("examQuestion", buildDraftPayload(draft) as unknown as Record<string, unknown>);
    draft._saved = true;
    generatedDrafts.value = [...generatedDrafts.value];
    ElMessage.success("保存成功");
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    savingDraftKey.value = "";
  }
}

async function initializePage() {
  await Promise.all([loadOptions(), loadRows()]);
}

onMounted(() => {
  void initializePage();
});
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

.ai-question-panel {
  display: grid;
  grid-template-columns: minmax(320px, 400px) minmax(0, 1fr);
  gap: 18px;
}

.ai-question-panel__settings,
.ai-question-panel__results {
  min-height: 560px;
  padding: 18px;
  border-radius: 22px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: linear-gradient(180deg, rgba(255, 251, 247, 0.95), rgba(255, 255, 255, 0.99));
}

.ai-question-panel__section-title {
  margin-bottom: 14px;
}

.ai-question-panel__section-title h3 {
  margin: 0;
}

.ai-question-panel__section-title p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
}

.ai-question-form :deep(.el-form-item) {
  margin-bottom: 14px;
}

.ai-question-form :deep(.el-select),
.ai-question-form :deep(.el-input-number),
.ai-question-form :deep(.el-input) {
  width: 100%;
}

.ai-question-panel__actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.ai-question-panel__summary {
  margin-top: 16px;
  padding: 14px;
  border-radius: 16px;
  background: rgba(255, 122, 26, 0.08);
  color: #9a4c12;
  line-height: 1.7;
}

.ai-question-panel__results {
  display: flex;
  flex-direction: column;
}

.ai-result-list {
  display: grid;
  gap: 14px;
  overflow: auto;
  padding-right: 4px;
}

.ai-result-card {
  padding: 16px;
  border-radius: 18px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: #fff;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.04);
}

.ai-result-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.ai-result-card__header strong {
  font-size: 15px;
  color: #0f172a;
}

.ai-result-card__header p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

.ai-result-card__title {
  margin: 14px 0 12px;
  color: #1f2937;
  line-height: 1.7;
}

.ai-result-card__options {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.option-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(248, 250, 252, 0.98);
}

.option-item strong {
  min-width: 24px;
  color: #d76413;
}

.option-item span {
  color: #334155;
  line-height: 1.6;
}

.ai-result-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  color: #64748b;
  font-size: 13px;
}

.ai-result-card__analysis {
  margin: 12px 0 0;
  color: #475569;
  line-height: 1.7;
}

.ai-result-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

@media (max-width: 1100px) {
  .ai-question-panel {
    grid-template-columns: 1fr;
  }

  .ai-question-panel__settings,
  .ai-question-panel__results {
    min-height: auto;
  }
}
</style>
