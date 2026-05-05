<template>
  <section class="section section--tight">
    <RouterLink class="paper-back" to="/exams">返回考试列表</RouterLink>
    <div v-if="detail" class="paper-layout">
      <section class="paper-main">
        <header class="paper-main__header">
          <div>
            <p class="paper-eyebrow">{{ detail.kechengName || "课程考试" }}</p>
            <h1>{{ detail.examName }}</h1>
            <p class="paper-summary">{{ detail.examSummary || "请在规定时间内完成本次考试并提交试卷。" }}</p>
          </div>
          <div class="paper-main__meta">
            <span>{{ questions.length }} 题</span>
            <span>{{ detail.totalScore ?? 0 }} 分</span>
            <span>{{ detail.passScore ?? 60 }} 分及格</span>
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
          <p class="paper-eyebrow">考试信息</p>
          <h2>{{ detail.chapterName || "不限章节" }}</h2>
          <div class="side-stats">
            <span>开始时间：{{ detail.startTime || "待定" }}</span>
            <span>结束时间：{{ detail.endTime || "待定" }}</span>
            <span>考试时长：{{ detail.durationMinutes ?? 0 }} 分钟</span>
            <span>重考次数：最多 {{ detail.maxAttemptCount ?? 1 }} 次</span>
            <span>当前状态：{{ latestRecord?.recordStatus || "未开始" }}</span>
            <span v-if="recordId && remainingText">剩余时间：{{ remainingText }}</span>
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
              v-if="!recordId || latestRecord?.recordStatus !== 'started'"
              class="primary-button primary-button--full"
              :disabled="starting || submitting"
              @click="startNewAttempt"
            >
              {{ starting ? "正在准备..." : latestRecord ? "重新开始考试" : "开始考试" }}
            </button>
            <button
              v-else-if="detail.allowResume === 1"
              class="ghost-button ghost-button--full"
              :disabled="starting || submitting"
              @click="restoreCurrentAttempt"
            >
              恢复上次作答
            </button>
            <button class="primary-button primary-button--full" :disabled="!recordId || !canSubmit" @click="handleSubmitClick">
              {{ submitting ? "提交中..." : "提交试卷" }}
            </button>
          </div>
        </article>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import type { ExamItem, ExamQuestionItem, ExamRecordItem } from "@shared/index";
import { fetchExamDetail, fetchExamQuestionPage, fetchMyExamRecordPage, startExam, submitExam } from "@/api/content";

const route = useRoute();
const detail = ref<ExamItem | null>(null);
const questions = ref<ExamQuestionItem[]>([]);
const latestRecord = ref<ExamRecordItem | null>(null);
const recordId = ref<number | null>(null);
const starting = ref(false);
const submitting = ref(false);
const message = ref("");
const messageType = ref<"success" | "error">("success");
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
const canEditAnswers = computed(
  () => latestRecord.value?.recordStatus === "started" && (detail.value?.allowResume === 1 || !hasRecoveredStartedRecord.value)
);
const canSubmit = computed(
  () => canEditAnswers.value && !submitting.value && (remainingSeconds.value === null || remainingSeconds.value > 0)
);
const hasRecoveredStartedRecord = computed(() => Boolean(latestRecord.value?.recordStatus === "started" && restoredFromHistory.value));
const remainingText = computed(() => {
  if (remainingSeconds.value === null) return "";
  const safe = Math.max(remainingSeconds.value, 0);
  const minutes = Math.floor(safe / 60);
  const seconds = safe % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
});
const recordSummary = computed(() => {
  if (!latestRecord.value) return "";
  if (latestRecord.value.recordStatus === "started") {
    return detail.value?.allowResume === 1
      ? `已进入第 ${latestRecord.value.attemptNo || 1} 次作答，可继续完成并提交。`
      : "当前考试退出后不可恢复，请一次性完成作答。";
  }
  if (latestRecord.value.recordStatus === "pending_check") {
    return "最近一次试卷已提交，正在等待教师阅卷。";
  }
  if (latestRecord.value.recordStatus === "checked") {
    return `最近一次成绩 ${latestRecord.value.finalScore ?? 0} 分，结果为 ${latestRecord.value.passStatus || "pending"}。`;
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
  recordId.value = record?.recordStatus === "started" ? record.id : null;
  if (record?.recordStatus === "started" && detail.value?.allowResume === 1) {
    restoreAnswers(record.answerSnapshot);
  } else if (!fromHistory) {
    clearAnswers();
  }
  if (record) {
    startTimer(record);
  } else {
    stopTimer();
    remainingSeconds.value = null;
    clearAnswers();
  }
}

async function loadLatestRecord() {
  const page = await fetchMyExamRecordPage({ examId: route.params.id, limit: 1 });
  return page.list[0] || null;
}

async function startNewAttempt() {
  starting.value = true;
  message.value = "";
  try {
    const result = await startExam({ examId: Number(route.params.id) });
    if (result.code !== 0) throw new Error(result.msg || "开始考试失败");
    applyRecord(result.data, false);
    messageType.value = "success";
    message.value = result.data.answerSnapshot && detail.value?.allowResume === 1 ? "已恢复上次未提交答案。" : "考试已开始，可以开始作答。";
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
  messageType.value = "success";
  message.value = "已恢复最近一次未提交试卷。";
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

Promise.all([
  fetchExamDetail(route.params.id as string),
  fetchExamQuestionPage({ examId: route.params.id }),
  loadLatestRecord()
]).then(([exam, questionPage, latest]) => {
  detail.value = exam;
  questions.value = questionPage.list;
  applyRecord(latest, true);
});

onBeforeUnmount(() => {
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

.ghost-button--full,
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
