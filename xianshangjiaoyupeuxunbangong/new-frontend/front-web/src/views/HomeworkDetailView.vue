<template>
  <section class="section section--tight">
    <RouterLink class="paper-back" to="/homeworks">返回作业列表</RouterLink>
    <div v-if="detail" class="paper-layout">
      <section class="paper-main">
        <header class="paper-main__header">
          <div>
            <p class="paper-eyebrow">{{ detail.kechengName || "课程作业" }}</p>
            <h1>{{ detail.zuoyeName }}</h1>
            <p class="paper-summary">{{ stripHtml(detail.zuoyeContent) }}</p>
          </div>
          <div class="paper-main__meta">
            <span>{{ questions.length }} 题</span>
            <span>{{ detail.scoreTotal ?? 0 }} 分</span>
            <span>截止 {{ detail.deadlineTime || "待定" }}</span>
          </div>
        </header>

        <div class="question-list">
          <article v-for="(question, index) in questions" :key="question.id" class="question-card">
            <div class="question-card__header">
              <strong>{{ index + 1 }}. {{ question.questionTitle }}</strong>
              <span>{{ question.questionType || "题目" }} / {{ question.questionScore ?? 0 }} 分</span>
            </div>

            <div v-if="hasChoices(question)" class="choice-group">
              <label v-for="option in parsedOptions(question)" :key="option.value" class="choice-item">
                <input
                  v-if="multiChoiceQuestion(question)"
                  :checked="selectedMulti(question.id, option.value)"
                  :disabled="!canEditAnswers"
                  type="checkbox"
                  @change="handleMultiChange(question.id, option.value, $event)"
                />
                <input
                  v-else
                  v-model="answers[String(question.id)]"
                  :disabled="!canEditAnswers"
                  type="radio"
                  :name="`q-${question.id}`"
                  :value="option.value"
                />
                <span>{{ option.value }}. {{ option.label }}</span>
              </label>
            </div>

            <textarea
              v-else
              v-model="answers[String(question.id)]"
              class="field field--textarea answer-textarea"
              :disabled="!canEditAnswers"
              placeholder="请输入你的答案"
            ></textarea>
          </article>
        </div>
      </section>

      <aside class="paper-side">
        <article class="side-card side-card--accent">
          <p class="paper-eyebrow">作业信息</p>
          <h2>{{ detail.chapterName || "不限章节" }}</h2>
          <div class="side-stats">
            <span>授课教师：{{ detail.jiaoshiName || "待补充" }}</span>
            <span>截止时间：{{ detail.deadlineTime || "待定" }}</span>
            <span>总分：{{ detail.scoreTotal ?? 100 }}</span>
            <span>当前状态：{{ submissionRecord?.submitStatus || "未开始" }}</span>
          </div>
          <a v-if="detail.zuoyeFile" class="paper-link" :href="downloadUrl(detail.zuoyeFile)" target="_blank">查看作业附件</a>
        </article>

        <article class="side-card">
          <p class="paper-eyebrow">作答进度</p>
          <div class="side-progress">
            <div>
              <strong>{{ answeredCount }}</strong>
              <span>已作答</span>
            </div>
            <div>
              <strong>{{ questions.length - answeredCount }}</strong>
              <span>未作答</span>
            </div>
          </div>
          <p v-if="submissionMessage" :class="submissionMessageType === 'error' ? 'field-error' : 'field-help'">
            {{ submissionMessage }}
          </p>
          <p v-if="submissionRecord && submissionRecord.submitStatus !== '作答中'" class="field-help">
            最近一次提交状态：{{ submissionRecord.submitStatus }}，得分 {{ submissionRecord.submitScore ?? submissionRecord.autoScore ?? "待评" }}
          </p>
        </article>

        <article class="side-card">
          <p class="paper-eyebrow">提交作业</p>
          <textarea
            v-model="submissionContent"
            class="field field--textarea"
            placeholder="补充本次作答说明，可不填"
            :disabled="expired || !session.isLoggedIn || !canEditAnswers"
          ></textarea>
          <div class="side-actions">
            <button
              v-if="!recordId"
              class="primary-button primary-button--full"
              :disabled="expired || !session.isLoggedIn || starting"
              @click="startCurrentHomework"
            >
              {{ starting ? "正在进入..." : "开始写作业" }}
            </button>
            <button
              class="primary-button primary-button--full"
              :disabled="!recordId || !session.isLoggedIn || expired || submitting"
              @click="submitCurrentHomework"
            >
              {{ submitting ? "提交中..." : "提交作业" }}
            </button>
          </div>
        </article>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import {
  DEFAULT_BASE_URL,
  createDownloadUrl,
  type ExamQuestionItem,
  type HomeworkItem,
  type HomeworkSubmissionItem
} from "@shared/index";
import {
  fetchHomeworkDetail,
  fetchHomeworkQuestions,
  fetchMyHomeworkSubmissions,
  startHomework,
  submitHomework
} from "@/api/content";
import { useSessionStore } from "@/stores/session";

const route = useRoute();
const session = useSessionStore();
const detail = ref<HomeworkItem | null>(null);
const questions = ref<ExamQuestionItem[]>([]);
const submissionRecord = ref<HomeworkSubmissionItem | null>(null);
const recordId = ref<number | null>(null);
const starting = ref(false);
const submitting = ref(false);
const submissionContent = ref("");
const submissionMessage = ref("");
const submissionMessageType = ref<"success" | "error">("success");
const answers = reactive<Record<string, string>>({});

const expired = computed(() => {
  if (!detail.value?.deadlineTime) return false;
  return new Date(detail.value.deadlineTime).getTime() < Date.now();
});
const canEditAnswers = computed(() => submissionRecord.value?.submitStatus === "作答中");
const answeredCount = computed(() =>
  questions.value.filter((question) => {
    const value = answers[String(question.id)];
    return Boolean(value && value.trim());
  }).length
);

function downloadUrl(fileName?: string) {
  return createDownloadUrl(DEFAULT_BASE_URL, fileName);
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").trim() || "暂无作业说明";
}

function parsedOptions(question: ExamQuestionItem) {
  if (!question.optionJson) {
    if (judgementQuestion(question)) {
      return [
        { value: "A", label: "正确" },
        { value: "B", label: "错误" }
      ];
    }
    return [];
  }
  try {
    const data = JSON.parse(question.optionJson) as Record<string, string>;
    return Object.entries(data).map(([value, label]) => ({ value, label }));
  } catch {
    return [];
  }
}

function questionTypeText(question: ExamQuestionItem) {
  return question.questionType || "";
}

function choiceQuestion(question: ExamQuestionItem) {
  const type = questionTypeText(question);
  return type === "选择题" || type === "单选" || type === "单选题";
}

function multiChoiceQuestion(question: ExamQuestionItem) {
  const type = questionTypeText(question);
  return type === "多选" || type === "多选题";
}

function judgementQuestion(question: ExamQuestionItem) {
  const type = questionTypeText(question);
  return type === "判断题" || type === "判断";
}

function hasChoices(question: ExamQuestionItem) {
  return choiceQuestion(question) || multiChoiceQuestion(question) || judgementQuestion(question);
}

function selectedMulti(questionId: number, value: string) {
  const current = answers[String(questionId)] || "";
  return current.split(",").filter(Boolean).includes(value);
}

function toggleMulti(questionId: number, value: string, checked: boolean) {
  const key = String(questionId);
  const current = answers[key] ? answers[key].split(",").filter(Boolean) : [];
  const next = checked ? [...new Set([...current, value])] : current.filter((item) => item !== value);
  answers[key] = next.join(",");
}

function handleMultiChange(questionId: number, value: string, event: Event) {
  toggleMulti(questionId, value, (event.target as HTMLInputElement).checked);
}

function clearAnswers() {
  Object.keys(answers).forEach((key) => delete answers[key]);
}

function restoreAnswers(snapshot?: string) {
  clearAnswers();
  if (!snapshot) return;
  try {
    const parsed = JSON.parse(snapshot) as Record<string, string>;
    Object.entries(parsed).forEach(([key, value]) => {
      answers[key] = value;
    });
  } catch {
    // ignore malformed snapshot
  }
}

function applySubmission(record: HomeworkSubmissionItem | null) {
  submissionRecord.value = record;
  recordId.value = record?.submitStatus === "作答中" ? record.id : null;
  if (record?.submitStatus === "作答中") {
    restoreAnswers(record.answerSnapshot);
    submissionContent.value = record.submitContent || "";
  } else {
    clearAnswers();
    submissionContent.value = "";
  }
}

async function loadLatestSubmission() {
  if (!session.isLoggedIn) {
    applySubmission(null);
    return;
  }
  const page = await fetchMyHomeworkSubmissions({
    zuoyeId: route.params.id,
    limit: 1
  });
  applySubmission(page.list[0] || null);
}

async function startCurrentHomework() {
  if (expired.value) {
    submissionMessageType.value = "error";
    submissionMessage.value = "该作业已截止，不能继续作答。";
    return;
  }
  if (!session.isLoggedIn) {
    submissionMessageType.value = "error";
    submissionMessage.value = "请先登录后再开始作业。";
    return;
  }
  starting.value = true;
  submissionMessage.value = "";
  try {
    const result = await startHomework({ zuoyeId: Number(route.params.id) });
    if (result.code !== 0) throw new Error(result.msg || "开始作业失败");
    applySubmission(result.data);
    submissionMessageType.value = "success";
    submissionMessage.value = "已进入作答页面，可以开始完成题目。";
  } catch (error) {
    submissionMessageType.value = "error";
    submissionMessage.value = error instanceof Error ? error.message : "开始作业失败";
  } finally {
    starting.value = false;
  }
}

async function submitCurrentHomework() {
  if (!recordId.value) {
    submissionMessageType.value = "error";
    submissionMessage.value = "请先开始写作业。";
    return;
  }
  submitting.value = true;
  submissionMessage.value = "";
  try {
    const result = await submitHomework({
      id: recordId.value,
      answerSnapshot: JSON.stringify(answers),
      submitContent: submissionContent.value.trim()
    });
    if (result.code !== 0) throw new Error(result.msg || "提交作业失败");
    await loadLatestSubmission();
    submissionMessageType.value = "success";
    submissionMessage.value = `提交成功，当前得分 ${result.data.submitScore ?? result.data.autoScore ?? 0} 分。`;
  } catch (error) {
    submissionMessageType.value = "error";
    submissionMessage.value = error instanceof Error ? error.message : "提交作业失败";
  } finally {
    submitting.value = false;
  }
}

Promise.all([fetchHomeworkDetail(route.params.id as string), fetchHomeworkQuestions(route.params.id as string)]).then(
  async ([homework, questionList]) => {
    detail.value = homework;
    questions.value = questionList;
    await loadLatestSubmission();
  }
);
</script>

<style scoped>
.paper-back {
  display: inline-flex;
  margin-bottom: 18px;
  padding: 10px 16px;
  border: 1px solid rgba(241, 159, 84, 0.38);
  border-radius: 999px;
  color: #b86724;
  background: rgba(255, 251, 245, 0.92);
}

.paper-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.75fr) minmax(300px, 0.9fr);
  gap: 24px;
  align-items: start;
}

.paper-main,
.side-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(226, 213, 199, 0.78);
  box-shadow: 0 22px 50px rgba(24, 32, 48, 0.08);
}

.paper-main {
  border-radius: 28px;
  padding: 28px;
}

.paper-main__header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 24px;
}

.paper-eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #c36e29;
}

.paper-main h1,
.paper-side h2 {
  margin: 0;
  color: #1f2937;
}

.paper-summary {
  margin: 12px 0 0;
  color: #5b6472;
  line-height: 1.75;
}

.paper-main__meta {
  display: grid;
  gap: 10px;
  min-width: 160px;
}

.paper-main__meta span,
.side-stats span {
  padding: 10px 14px;
  border-radius: 16px;
  background: #fff7ef;
  color: #874913;
  font-size: 13px;
}

.question-list {
  display: grid;
  gap: 16px;
}

.question-card {
  padding: 18px;
  border-radius: 22px;
  background: #fffdfa;
  border: 1px solid rgba(231, 223, 213, 0.85);
}

.question-card__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
  color: #1f2937;
}

.choice-group {
  display: grid;
  gap: 10px;
}

.choice-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 12px 14px;
  border-radius: 16px;
  background: #f9fbff;
  color: #334155;
}

.answer-textarea {
  min-height: 120px;
}

.paper-side {
  display: grid;
  gap: 16px;
  position: sticky;
  top: 24px;
}

.side-card {
  border-radius: 24px;
  padding: 20px;
}

.side-card--accent {
  background: linear-gradient(180deg, #fffaf2 0%, #ffffff 100%);
}

.side-stats,
.side-actions {
  display: grid;
  gap: 10px;
}

.side-progress {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.side-progress div {
  padding: 16px;
  border-radius: 18px;
  background: #f8fafc;
}

.side-progress strong {
  display: block;
  font-size: 24px;
  color: #111827;
}

.paper-link {
  display: inline-flex;
  margin-top: 14px;
  color: #b86724;
}

.primary-button--full {
  width: 100%;
}

@media (max-width: 1024px) {
  .paper-layout {
    grid-template-columns: 1fr;
  }

  .paper-side {
    position: static;
  }

  .paper-main__header,
  .question-card__header {
    flex-direction: column;
  }
}
</style>
