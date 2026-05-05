<template>
  <section class="section section--tight" v-loading="loading">
    <RouterLink class="paper-back" to="/exams">返回考试列表</RouterLink>

    <div v-if="blocked" class="blocked-panel">
      <h2>暂时无法进入考试</h2>
      <p>{{ blockedMessage }}</p>
    </div>

    <div v-else-if="detail" class="paper-layout">
      <section class="paper-main">
        <header class="paper-main__header">
          <div>
            <p class="paper-eyebrow">{{ detail.kechengName || "课程考试" }}</p>
            <div class="title-row">
              <h1>{{ detail.examName }}</h1>
              <span v-if="isAttemptRunning" class="status-badge status-badge--danger">进行中</span>
            </div>
            <p class="paper-summary">
              {{ detail.examSummary || "点击开始考试后才会显示题目。离开页面时，考试仍会继续计时。" }}
            </p>
          </div>
          <div class="paper-main__meta">
            <span>{{ questions.length }} 题</span>
            <span>{{ detail.totalScore ?? 0 }} 分</span>
            <span>{{ detail.passScore ?? 60 }} 分及格</span>
          </div>
        </header>

        <section v-if="!showQuestions" class="start-panel">
          <div>
            <p class="paper-eyebrow">考试已就绪</p>
            <h2>{{ isAttemptRunning ? "继续当前考试" : "开始本场考试" }}</h2>
            <p>进入后题目才会显示。考试进行中退出页面，计时不会停止。</p>
          </div>
          <button
            class="primary-button"
            :disabled="starting || submitting"
            @click="isAttemptRunning ? restoreCurrentAttempt() : startNewAttempt()"
          >
            {{ startButtonText }}
          </button>
        </section>

        <div v-else class="question-list">
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
              placeholder="请输入答案"
            ></textarea>
          </article>
        </div>
      </section>

      <aside class="paper-side">
        <article class="side-card side-card--accent">
          <p class="paper-eyebrow">考试信息</p>
          <h2>{{ detail.chapterName || "不限章节" }}</h2>
          <div class="side-stats">
            <span>开始时间：{{ detail.startTime || "待定" }}</span>
            <span>结束时间：{{ detail.endTime || "待定" }}</span>
            <span>考试时长：{{ detail.durationMinutes ?? 0 }} 分钟</span>
            <span>最多重考：{{ detail.maxAttemptCount ?? 1 }} 次</span>
            <span>当前状态：{{ currentStatusText }}</span>
            <span v-if="remainingText">剩余时间：{{ remainingText }}</span>
          </div>
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
          <p v-if="recordSummary" class="field-help">{{ recordSummary }}</p>
          <p v-if="message" :class="messageType === 'error' ? 'field-error' : 'field-help'">{{ message }}</p>
        </article>

        <article class="side-card">
          <p class="paper-eyebrow">考试操作</p>
          <div class="side-actions">
            <button
              v-if="!isAttemptRunning"
              class="primary-button primary-button--full"
              :disabled="starting || submitting"
              @click="startNewAttempt"
            >
              {{ startButtonText }}
            </button>
            <button
              v-else-if="!showQuestions"
              class="ghost-button ghost-button--full"
              :disabled="starting || submitting"
              @click="restoreCurrentAttempt"
            >
              继续考试
            </button>
            <button
              v-else
              class="primary-button primary-button--full"
              :disabled="submitting || !canSubmit"
              @click="handleSubmitClick"
            >
              {{ submitting ? "提交中..." : "提交试卷" }}
            </button>
          </div>
        </article>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { onBeforeRouteLeave, RouterLink, useRoute, useRouter } from "vue-router";
import type { ExamItem, ExamQuestionItem, ExamRecordItem } from "@shared/index";
import {
  fetchExamDetail,
  fetchExamQuestionPage,
  fetchMyCoursePage,
  fetchMyExamRecordPage,
  startExam,
  submitExam
} from "@/api/content";

const route = useRoute();
const router = useRouter();
const detail = ref<ExamItem | null>(null);
const questions = ref<ExamQuestionItem[]>([]);
const latestRecord = ref<ExamRecordItem | null>(null);
const recordId = ref<number | null>(null);
const showQuestions = ref(false);
const loading = ref(false);
const blocked = ref(false);
const starting = ref(false);
const submitting = ref(false);
const message = ref("");
const messageType = ref<"success" | "error">("success");
const blockedMessage = ref("");
const answers = reactive<Record<string, string>>({});
const remainingSeconds = ref<number | null>(null);
const restoredFromHistory = ref(false);
let timer: ReturnType<typeof setInterval> | null = null;

const answeredCount = computed(() =>
  questions.value.filter((question) => {
    const value = answers[String(question.id)];
    return Boolean(value && value.trim());
  }).length
);

const isAttemptRunning = computed(() => latestRecord.value?.recordStatus === "started" && Boolean(recordId.value));
const canEditAnswers = computed(() => isAttemptRunning.value);
const canSubmit = computed(
  () => canEditAnswers.value && !submitting.value && (remainingSeconds.value === null || remainingSeconds.value > 0)
);
const startButtonText = computed(() => {
  if (isAttemptRunning.value) return "继续考试";
  if (latestRecord.value) return "重新开始考试";
  return "开始考试";
});
const remainingText = computed(() => {
  if (remainingSeconds.value === null) return "";
  const safe = Math.max(remainingSeconds.value, 0);
  const minutes = Math.floor(safe / 60);
  const seconds = safe % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
});
const currentStatusText = computed(() => {
  if (isAttemptRunning.value) return "进行中";
  if (latestRecord.value?.recordStatus === "pending_check") return "已提交，待批改";
  if (latestRecord.value?.recordStatus === "checked") return "已批改";
  return "未开始";
});
const recordSummary = computed(() => {
  if (!latestRecord.value) return "";
  if (latestRecord.value.recordStatus === "started") {
    return detail.value?.allowResume === 1
      ? `当前第 ${latestRecord.value.attemptNo || 1} 次作答，可继续完成后再提交。`
      : "考试进行中，离开页面仍继续计时。";
  }
  if (latestRecord.value.recordStatus === "pending_check") {
    return "最近一次试卷已提交，正在等待教师批改。";
  }
  if (latestRecord.value.recordStatus === "checked") {
    return `最近一次成绩为 ${latestRecord.value.finalScore ?? 0} 分。`;
  }
  return "";
});

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

function stopTimer() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

function resolveDeadline(record: ExamRecordItem) {
  if (!detail.value || !record.startTime) return null;
  const startedAt = new Date(record.startTime).getTime();
  const durationEnd = startedAt + (detail.value.durationMinutes ?? 0) * 60 * 1000;
  const examEnd = detail.value.endTime ? new Date(detail.value.endTime).getTime() : Number.POSITIVE_INFINITY;
  return Math.min(durationEnd, examEnd);
}

function startTimer(record: ExamRecordItem) {
  stopTimer();
  if (record.recordStatus !== "started") {
    remainingSeconds.value = null;
    return;
  }
  const deadline = resolveDeadline(record);
  if (!deadline || !Number.isFinite(deadline)) {
    remainingSeconds.value = null;
    return;
  }
  const tick = () => {
    const seconds = Math.floor((deadline - Date.now()) / 1000);
    remainingSeconds.value = Math.max(seconds, 0);
    if (seconds <= 0) {
      stopTimer();
      if (recordId.value && latestRecord.value?.recordStatus === "started" && !submitting.value) {
        submitCurrentExam(true);
      }
    }
  };
  tick();
  timer = setInterval(tick, 1000);
}

function applyRecord(record: ExamRecordItem | null, fromHistory = false) {
  latestRecord.value = record;
  restoredFromHistory.value = fromHistory;
  const active = record?.recordStatus === "started";
  recordId.value = active ? record.id : null;
  if (active && detail.value?.allowResume === 1) {
    restoreAnswers(record?.answerSnapshot);
  } else if (!fromHistory) {
    clearAnswers();
  }
  if (active) {
    startTimer(record as ExamRecordItem);
  } else {
    stopTimer();
    remainingSeconds.value = null;
    if (!fromHistory) {
      clearAnswers();
    }
    showQuestions.value = false;
  }
}

async function loadLatestRecord() {
  const page = await fetchMyExamRecordPage({ examId: route.params.id, limit: 1 });
  return page.list[0] || null;
}

async function verifyCourseProgress(exam: ExamItem) {
  const page = await fetchMyCoursePage({ kechengId: exam.kechengId, limit: 1 });
  const enroll = page.list[0];
  const progressPercent = Number(enroll?.progressPercent ?? 0);
  if (!enroll || progressPercent < 100) {
    blocked.value = true;
    blockedMessage.value = "当前课程学习进度未达到 100%，暂时无法进入考试。";
    window.alert(blockedMessage.value);
    router.replace("/exams");
    return false;
  }
  return true;
}

async function loadPage() {
  loading.value = true;
  try {
    const exam = await fetchExamDetail(route.params.id as string);
    detail.value = exam;
    const allowed = await verifyCourseProgress(exam);
    if (!allowed) return;
    const [questionPage, latest] = await Promise.all([
      fetchExamQuestionPage({ examId: route.params.id }),
      loadLatestRecord()
    ]);
    questions.value = questionPage.list;
    applyRecord(latest, true);
  } catch (error) {
    messageType.value = "error";
    message.value = error instanceof Error ? error.message : "加载考试失败";
  } finally {
    loading.value = false;
  }
}

async function startNewAttempt() {
  starting.value = true;
  message.value = "";
  try {
    const result = await startExam({ examId: Number(route.params.id) });
    if (result.code !== 0) throw new Error(result.msg || "开始考试失败");
    applyRecord(result.data, false);
    showQuestions.value = true;
    messageType.value = "success";
    message.value = "考试已开始，请在规定时间内完成作答。";
  } catch (error) {
    messageType.value = "error";
    message.value = error instanceof Error ? error.message : "开始考试失败";
  } finally {
    starting.value = false;
  }
}

function restoreCurrentAttempt() {
  if (!latestRecord.value || detail.value?.allowResume !== 1) return;
  applyRecord(latestRecord.value, true);
  showQuestions.value = true;
  messageType.value = "success";
  message.value = "已恢复上一次未提交的作答。";
}

async function submitCurrentExam(byTimeout = false) {
  if (!recordId.value) {
    messageType.value = "error";
    message.value = "请先开始考试。";
    return;
  }
  submitting.value = true;
  try {
    const result = await submitExam({ id: recordId.value, answerSnapshot: JSON.stringify(answers) });
    if (result.code !== 0) throw new Error(result.msg || "提交失败");
    const latest = await loadLatestRecord();
    applyRecord(latest, false);
    messageType.value = "success";
    message.value = byTimeout
      ? `考试时间已到，系统已自动提交。当前成绩 ${result.data.finalScore ?? result.data.autoScore ?? 0} 分。`
      : `提交成功，当前成绩 ${result.data.finalScore ?? result.data.autoScore ?? 0} 分。`;
  } catch (error) {
    messageType.value = "error";
    message.value = error instanceof Error ? error.message : "提交失败";
  } finally {
    submitting.value = false;
  }
}

function handleSubmitClick() {
  submitCurrentExam(false);
}

function handleBeforeUnload(event: BeforeUnloadEvent) {
  if (!isAttemptRunning.value) return;
  event.preventDefault();
  event.returnValue = "";
}

onMounted(() => {
  window.addEventListener("beforeunload", handleBeforeUnload);
  loadPage();
});

onBeforeRouteLeave(async () => {
  if (!isAttemptRunning.value) return true;
  return window.confirm("考试正在进行中，退出仍继续计时");
});

onBeforeUnmount(() => {
  window.removeEventListener("beforeunload", handleBeforeUnload);
  stopTimer();
});
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

.blocked-panel {
  padding: 28px;
  border-radius: 24px;
  border: 1px solid rgba(226, 213, 199, 0.78);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 22px 50px rgba(24, 32, 48, 0.08);
}

.paper-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.75fr) minmax(300px, 0.9fr);
  gap: 24px;
  align-items: start;
  height: calc(100vh - 180px);
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
  max-height: 100%;
  overflow: auto;
}

.paper-main__header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 24px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  color: #8a3412;
  background: #fff1e7;
}

.status-badge--danger {
  color: #9d1c1c;
  background: #ffe7e7;
}

.paper-eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #c36e29;
}

.paper-main h1,
.paper-side h2,
.blocked-panel h2,
.start-panel h2 {
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
  min-width: 140px;
}

.paper-main__meta span,
.side-stats span {
  padding: 10px 14px;
  border-radius: 16px;
  background: #fff7ef;
  color: #874913;
  font-size: 13px;
}

.start-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 22px;
  border-radius: 22px;
  border: 1px dashed rgba(226, 213, 199, 0.95);
  background: linear-gradient(180deg, #fffaf2 0%, #ffffff 100%);
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
  max-height: 100%;
  overflow: auto;
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
  margin-bottom: 6px;
  font-size: 22px;
  color: #1f2937;
}

.side-progress span {
  color: #64748b;
}

@media (max-width: 1100px) {
  .paper-layout {
    grid-template-columns: 1fr;
    height: auto;
  }

  .paper-main,
  .paper-side {
    max-height: none;
    overflow: visible;
  }
}

@media (max-width: 720px) {
  .paper-main__header,
  .start-panel {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
