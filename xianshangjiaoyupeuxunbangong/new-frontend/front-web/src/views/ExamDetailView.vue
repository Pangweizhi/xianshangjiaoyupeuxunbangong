<template>
  <section class="section section--tight">
    <RouterLink class="text-link" to="/exams">返回考试列表</RouterLink>
    <div v-if="detail" class="detail-shell">
      <article class="detail-card">
        <div class="detail-card__body">
          <div class="stack-inline">
            <span class="tag">{{ detail.kechengName || "课程考试" }}</span>
            <span class="meta">{{ detail.chapterName || "不限章节" }}</span>
            <span class="meta">{{ latestRecord?.recordStatus || "未开始" }}</span>
          </div>
          <h1>{{ detail.examName }}</h1>
          <p>{{ detail.examSummary || "暂无考试说明" }}</p>
          <div class="status-list">
            <span>开始时间：{{ detail.startTime || "待定" }}</span>
            <span>结束时间：{{ detail.endTime || "待定" }}</span>
            <span>考试时长：{{ detail.durationMinutes ?? 0 }} 分钟</span>
            <span>总分：{{ detail.totalScore ?? 0 }}</span>
            <span>及格线：{{ detail.passScore ?? 60 }}</span>
            <span>重考：{{ detail.allowRetake === 1 ? "允许" : "不允许" }}</span>
            <span>次数：最多 {{ detail.maxAttemptCount ?? 1 }} 次</span>
            <span>恢复：{{ detail.allowResume === 1 ? "允许" : "不允许" }}</span>
            <span v-if="recordId && remainingText">剩余时间：{{ remainingText }}</span>
          </div>
          <div class="stack-inline">
            <button
              v-if="!recordId || latestRecord?.recordStatus !== 'started'"
              class="primary-button"
              :disabled="starting || submitting"
              @click="startNewAttempt"
            >
              {{ starting ? "准备中..." : latestRecord ? "重新开始考试" : "开始考试" }}
            </button>
            <button
              v-else-if="detail.allowResume === 1"
              class="ghost-button"
              :disabled="starting || submitting"
              @click="restoreCurrentAttempt"
            >
              恢复上次作答
            </button>
          </div>
          <p v-if="recordSummary" class="field-help">{{ recordSummary }}</p>
          <p v-if="message" :class="messageType === 'error' ? 'field-error' : 'field-help'">{{ message }}</p>
        </div>
      </article>

      <aside class="action-panel">
        <p class="eyebrow">在线答题</p>
        <h2>{{ detail.allowResume === 1 ? "支持刷新后恢复作答" : "退出后不能恢复本次作答" }}</h2>
        <p class="hero__lead">
          系统会按考试规则控制重考次数、是否允许恢复，以及超时自动提交。
        </p>
        <div class="mini-list">
          <article v-for="question in questions" :key="question.id" class="mini-list__row">
            <div>
              <strong>{{ question.sortNo }}. {{ question.questionTitle }}</strong>
              <p class="meta">{{ question.questionType }} / {{ question.questionScore }} 分</p>
              <div v-if="hasChoices(question)" class="mini-list">
                <label v-for="option in parsedOptions(question)" :key="option.value" class="stack-inline">
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
                class="field field--textarea"
                :disabled="!canEditAnswers"
                placeholder="请输入答案"
              ></textarea>
            </div>
          </article>
        </div>
        <button class="primary-button primary-button--full" :disabled="!recordId || !canSubmit" @click="handleSubmitClick">
          {{ submitting ? "提交中..." : "提交试卷" }}
        </button>
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
let timer: ReturnType<typeof setInterval> | null = null;

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
const restoredFromHistory = ref(false);
const recordSummary = computed(() => {
  if (!latestRecord.value) return "";
  if (latestRecord.value.recordStatus === "started") {
    if (detail.value?.allowResume === 1) {
      return `已进入第 ${latestRecord.value.attemptNo || 1} 次作答，可继续完成并提交。`;
    }
    return `当前考试不允许退出后恢复。若你已离开作答页，本次记录不能继续恢复。`;
  }
  if (latestRecord.value.recordStatus === "pending_check") {
    return "最近一次答卷已提交，正在等待教师阅卷。";
  }
  if (latestRecord.value.recordStatus === "checked") {
    return `最近一次成绩 ${latestRecord.value.finalScore ?? 0} 分，结果：${latestRecord.value.passStatus || "pending"}。`;
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

function fillQuestion(question: ExamQuestionItem) {
  const type = questionTypeText(question);
  return type === "填空题" || type === "填空";
}

function subjectiveQuestion(question: ExamQuestionItem) {
  const type = questionTypeText(question);
  return type === "简答题" || type === "简答" || type === "问答";
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
  message.value = "已恢复最近一次未提交的答卷。";
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
