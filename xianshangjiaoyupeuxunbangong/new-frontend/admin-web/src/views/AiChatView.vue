<template>
  <div class="ai-admin-page">
    <aside class="ai-admin-page__sidebar">
      <div class="ai-admin-page__header">
        <div>
          <span class="kicker">智能问答</span>
          <h2>历史会话</h2>
        </div>
        <el-button type="primary" @click="handleNewSession">新建会话</el-button>
      </div>

      <div class="ai-admin-page__tips">
        <strong>猜你想问</strong>
        <el-button
          v-for="question in recommendQuestions"
          :key="question"
          text
          class="suggest-button"
          @click="applyQuestion(question)"
        >
          {{ question }}
        </el-button>
      </div>

      <div class="session-stack">
        <button
          v-for="item in sessions"
          :key="item.id"
          type="button"
          class="session-item"
          :class="{ 'session-item--active': item.id === activeSessionId }"
          @click="activateSession(item.id)"
        >
          <strong>{{ item.sessionTitle }}</strong>
          <span>{{ item.lastMessageAt || "刚刚创建" }}</span>
        </button>
      </div>
    </aside>

    <section class="ai-admin-page__main">
      <header class="chat-header">
        <div>
          <span class="kicker">当前场景</span>
          <h1>{{ sceneTitle }}</h1>
        </div>
        <p>{{ sceneDescription }}</p>
      </header>

      <div class="chat-scroll">
        <div v-if="!messages.length" class="empty-state">
          <h3>开始向 AI 提问</h3>
          <p>{{ emptyHint }}</p>
        </div>
        <article
          v-for="message in messages"
          :key="message.id"
          class="chat-card"
          :class="message.messageRole === 'user' ? 'chat-card--user' : 'chat-card--assistant'"
        >
          <span>{{ message.messageRole === "user" ? "我" : "AI" }}</span>
          <div
            v-if="message.messageRole === 'assistant'"
            class="chat-card__content chat-card__content--rich"
            v-html="renderRichText(message.content)"
          />
          <p v-else class="chat-card__content">{{ message.content }}</p>
        </article>
      </div>

      <footer class="chat-composer">
        <el-input
          v-model="draft"
          type="textarea"
          :rows="4"
          maxlength="1000"
          show-word-limit
          resize="none"
          placeholder="输入课程管理、章节资源、作业考试或后台操作相关问题"
          @keydown.enter.exact.prevent="handleSend()"
        />
        <div class="chat-composer__actions">
          <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
          <el-button type="primary" :loading="sending" @click="handleSend()">发送</el-button>
        </div>
      </footer>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { renderRichText, type AiChatMessageItem, type AiChatSessionItem } from "@shared/index";
import {
  createAiSession,
  fetchAiMessagePage,
  fetchAiRecommendQuestions,
  fetchAiSessionPage,
  sendAiMessage
} from "@/api/ai";

const route = useRoute();
const sessions = ref<AiChatSessionItem[]>([]);
const messages = ref<AiChatMessageItem[]>([]);
const recommendQuestions = ref<string[]>([]);
const activeSessionId = ref<number | null>(null);
const draft = ref("");
const sending = ref(false);
const errorMessage = ref("");

const bizScene = computed(() => String(route.query.bizScene ?? "course_manage"));
const pageCode = computed(() => String(route.query.pageCode ?? "admin-ai-chat"));

const sceneTitle = computed(() => {
  if (bizScene.value === "course_manage") {
    return "教师/后台管理助手";
  }
  if (bizScene.value === "teacher_question_generation") {
    return "教师出题助手";
  }
  return "智能问答助手";
});

const sceneDescription = computed(() => {
  if (bizScene.value === "teacher_question_generation") {
    return "这里用于生成题干、选项、答案和解析草稿，最终仍由教师在题库中审核保存。";
  }
  return "这里主要用于系统导航、课程管理、作业考试和统计口径问答。";
});

const emptyHint = computed(() => {
  if (bizScene.value === "teacher_question_generation") {
    return "可以直接问“请按高等数学生成 5 道选择题”“给这道题补一个答案和解析”或“按判断题格式重写题干”。";
  }
  return "可以直接问“如何新增课程”“如何发布考试”或“怎么看课程成绩汇总”。";
});

async function loadSessions() {
  const page = await fetchAiSessionPage();
  sessions.value = page.list;
  if (!activeSessionId.value && sessions.value.length) {
    await activateSession(sessions.value[0].id);
  }
}

async function loadRecommendQuestions() {
  recommendQuestions.value = await fetchAiRecommendQuestions({
    bizScene: bizScene.value,
    pageCode: pageCode.value
  });
}

async function activateSession(sessionId: number) {
  activeSessionId.value = sessionId;
  const page = await fetchAiMessagePage(sessionId);
  messages.value = page.list;
}

async function ensureSession() {
  if (activeSessionId.value) {
    return activeSessionId.value;
  }
  const result = await createAiSession({
    bizScene: bizScene.value,
    pageCode: pageCode.value
  });
  activeSessionId.value = result.session.id;
  sessions.value = [result.session, ...sessions.value.filter((item) => item.id !== result.session.id)];
  recommendQuestions.value = result.recommendQuestions;
  return activeSessionId.value;
}

async function handleNewSession() {
  errorMessage.value = "";
  const result = await createAiSession({
    bizScene: bizScene.value,
    pageCode: pageCode.value
  });
  activeSessionId.value = result.session.id;
  messages.value = [];
  sessions.value = [result.session, ...sessions.value.filter((item) => item.id !== result.session.id)];
  recommendQuestions.value = result.recommendQuestions;
}

function applyQuestion(question: string) {
  draft.value = question;
  void handleSend(question);
}

async function handleSend(override?: string) {
  const content = (override ?? draft.value).trim();
  if (!content || sending.value) {
    return;
  }
  sending.value = true;
  errorMessage.value = "";
  try {
    const sessionId = await ensureSession();
    const result = await sendAiMessage({
      sessionId,
      content,
      bizScene: bizScene.value,
      pageCode: pageCode.value
    });
    draft.value = "";
    messages.value = [...messages.value, result.userMessage, result.assistantMessage];
    recommendQuestions.value = result.recommendQuestions;
    sessions.value = [result.session, ...sessions.value.filter((item) => item.id !== result.session.id)];
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "发送失败";
  } finally {
    sending.value = false;
  }
}

onMounted(async () => {
  await Promise.all([loadSessions(), loadRecommendQuestions()]);
});
</script>

<style scoped>
.ai-admin-page {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 1rem;
  min-height: 72vh;
}

.ai-admin-page__sidebar,
.ai-admin-page__main {
  background: #fff;
  border-radius: 24px;
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.ai-admin-page__sidebar {
  padding: 1rem;
}

.ai-admin-page__header,
.chat-header,
.chat-composer__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.kicker {
  display: inline-block;
  margin-bottom: 0.3rem;
  font-size: 0.78rem;
  color: #e85d04;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.ai-admin-page h1,
.ai-admin-page h2,
.empty-state h3 {
  margin: 0;
}

.ai-admin-page__tips {
  margin-top: 1rem;
  padding: 1rem;
  background: linear-gradient(180deg, rgba(251, 106, 61, 0.08), rgba(235, 59, 90, 0.04));
  border-radius: 18px;
}

.suggest-button {
  display: block;
  width: 100%;
  margin-top: 0.35rem;
  text-align: left;
  justify-content: flex-start;
}

.session-stack {
  display: grid;
  gap: 0.75rem;
  margin-top: 1rem;
}

.session-item {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 16px;
  background: #fff;
  text-align: left;
  padding: 0.9rem 1rem;
  cursor: pointer;
}

.session-item strong,
.session-item span {
  display: block;
}

.session-item span {
  margin-top: 0.4rem;
  font-size: 0.82rem;
  color: #64748b;
}

.session-item--active {
  border-color: rgba(232, 93, 4, 0.35);
  background: rgba(251, 106, 61, 0.08);
}

.ai-admin-page__main {
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 1.4rem 1.5rem 0;
}

.chat-header p {
  margin: 0;
  color: #64748b;
}

.chat-scroll {
  flex: 1;
  padding: 1.4rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow: auto;
}

.empty-state {
  margin: auto;
  text-align: center;
  color: #64748b;
}

.chat-card {
  max-width: 78%;
  padding: 1rem 1.1rem;
  border-radius: 18px;
}

.chat-card span {
  display: inline-block;
  margin-bottom: 0.35rem;
  font-size: 0.78rem;
  opacity: 0.72;
}

.chat-card p {
  margin: 0;
  line-height: 1.7;
  white-space: pre-wrap;
}

.chat-card__content {
  margin: 0;
  line-height: 1.7;
  word-break: break-word;
}

.chat-card__content--rich :deep(p) {
  margin: 0 0 0.75rem;
}

.chat-card__content--rich :deep(p:last-child) {
  margin-bottom: 0;
}

.chat-card__content--rich :deep(ul),
.chat-card__content--rich :deep(ol) {
  margin: 0.5rem 0 0.75rem;
  padding-left: 1.4rem;
}

.chat-card__content--rich :deep(li) {
  margin: 0.25rem 0;
}

.chat-card__content--rich :deep(pre) {
  margin: 0.75rem 0;
  padding: 0.85rem 1rem;
  border-radius: 16px;
  overflow: auto;
  background: rgba(15, 23, 42, 0.08);
}

.chat-card__content--rich :deep(code) {
  padding: 0.12rem 0.34rem;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.08);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

.chat-card--assistant .chat-card__content--rich :deep(a) {
  color: #b64a18;
  text-decoration: underline;
}

.chat-card--assistant {
  background: #fff5ef;
  border: 1px solid rgba(232, 93, 4, 0.14);
}

.chat-card--user {
  align-self: flex-end;
  color: #fff;
  background: linear-gradient(135deg, #fb6a3d, #eb3b5a);
}

.chat-composer {
  padding: 0 1.5rem 1.5rem;
}

.chat-composer__actions {
  margin-top: 0.9rem;
}

.error-text {
  color: #dc2626;
}

@media (max-width: 960px) {
  .ai-admin-page {
    grid-template-columns: 1fr;
  }

  .chat-card {
    max-width: 100%;
  }
}
</style>
