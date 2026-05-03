<template>
  <section class="ai-chat-page">
    <aside class="ai-chat-page__sidebar">
      <div class="ai-chat-page__sidebar-head">
        <div>
          <p class="eyebrow">智能问答</p>
          <h2>我的会话</h2>
        </div>
        <button class="new-session-button" @click="handleNewSession">新建</button>
      </div>
      <div class="suggestion-box">
        <span>猜你想问</span>
        <button
          v-for="question in recommendQuestions"
          :key="question"
          type="button"
          @click="applyQuestion(question)"
        >
          {{ question }}
        </button>
      </div>
      <div class="session-list">
        <button
          v-for="item in sessions"
          :key="item.id"
          type="button"
          class="session-card"
          :class="{ 'session-card--active': item.id === activeSessionId }"
          @click="activateSession(item.id)"
        >
          <strong>{{ item.sessionTitle }}</strong>
          <span>{{ item.lastMessageAt || "刚刚创建" }}</span>
        </button>
      </div>
    </aside>

    <div class="ai-chat-page__main">
      <header class="ai-chat-page__header">
        <div>
          <p class="eyebrow">当前场景</p>
          <h1>{{ sceneTitle }}</h1>
        </div>
        <p class="scene-tip">当前版本可回答课程学习、作业、考试、成绩和系统导航问题。</p>
      </header>

      <div class="message-list">
        <div v-if="!messages.length" class="empty-panel">
          <h3>开始一段新对话</h3>
          <p>可以先从左侧推荐问题开始，或者直接输入你的问题。</p>
        </div>
        <article
          v-for="message in messages"
          :key="message.id"
          class="message-bubble"
          :class="message.messageRole === 'user' ? 'message-bubble--user' : 'message-bubble--assistant'"
        >
          <span class="message-role">{{ message.messageRole === "user" ? "我" : "AI" }}</span>
          <p>{{ message.content }}</p>
        </article>
      </div>

      <footer class="composer">
        <textarea
          v-model="draft"
          rows="4"
          maxlength="1000"
          placeholder="输入课程学习、作业考试、成绩或系统操作相关问题"
          @keydown.enter.exact.prevent="handleSend()"
        />
        <div class="composer__actions">
          <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
          <button class="send-button" :disabled="sending || !draft.trim()" @click="handleSend()">
            {{ sending ? "发送中..." : "发送" }}
          </button>
        </div>
      </footer>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import type { AiChatMessageItem, AiChatSessionItem } from "@shared/index";
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

const bizScene = computed(() => String(route.query.bizScene ?? "system_nav"));
const courseId = computed(() => {
  const value = route.query.courseId;
  return value ? Number(value) : undefined;
});
const chapterId = computed(() => {
  const value = route.query.chapterId;
  return value ? Number(value) : undefined;
});
const pageCode = computed(() => String(route.query.pageCode ?? "ai-chat"));

const sceneTitle = computed(() => {
  if (bizScene.value === "course_learning") {
    return "课程学习助手";
  }
  return "系统导航助手";
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
    courseId: courseId.value,
    chapterId: chapterId.value
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
    courseId: courseId.value,
    chapterId: chapterId.value,
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
    courseId: courseId.value,
    chapterId: chapterId.value,
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
      courseId: courseId.value,
      chapterId: chapterId.value,
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
.ai-chat-page {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 1.5rem;
}

.ai-chat-page__sidebar,
.ai-chat-page__main {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 28px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
}

.ai-chat-page__sidebar {
  padding: 1.25rem;
}

.ai-chat-page__sidebar-head,
.ai-chat-page__header,
.composer__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.ai-chat-page__header {
  padding: 1.5rem 1.75rem 0;
}

.ai-chat-page__main {
  display: flex;
  flex-direction: column;
  min-height: 76vh;
}

.eyebrow {
  margin: 0 0 0.35rem;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #f03f6b;
}

.ai-chat-page h1,
.ai-chat-page h2,
.empty-panel h3 {
  margin: 0;
}

.scene-tip {
  margin: 0;
  max-width: 28rem;
  color: #64748b;
}

.new-session-button,
.send-button {
  border: none;
  border-radius: 999px;
  cursor: pointer;
  color: #fff;
  background: linear-gradient(135deg, #ff7b38, #ff4f88);
}

.new-session-button {
  padding: 0.7rem 1rem;
}

.send-button {
  min-width: 104px;
  padding: 0.9rem 1.4rem;
}

.send-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.suggestion-box {
  margin-top: 1.25rem;
  display: grid;
  gap: 0.65rem;
}

.suggestion-box > span {
  color: #475569;
  font-size: 0.92rem;
}

.suggestion-box button,
.session-card {
  width: 100%;
  text-align: left;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: #fff;
  border-radius: 18px;
  padding: 0.9rem 1rem;
  cursor: pointer;
}

.session-list {
  margin-top: 1.25rem;
  display: grid;
  gap: 0.75rem;
  max-height: 56vh;
  overflow: auto;
}

.session-card {
  display: grid;
  gap: 0.45rem;
}

.session-card span {
  color: #64748b;
  font-size: 0.82rem;
}

.session-card--active {
  border-color: rgba(240, 63, 107, 0.45);
  background: linear-gradient(180deg, rgba(255, 123, 56, 0.08), rgba(240, 63, 107, 0.08));
}

.message-list {
  flex: 1;
  padding: 1.5rem 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow: auto;
}

.empty-panel {
  margin: auto;
  text-align: center;
  color: #64748b;
}

.message-bubble {
  max-width: 75%;
  padding: 1rem 1.1rem;
  border-radius: 22px;
}

.message-bubble--assistant {
  align-self: flex-start;
  background: #fff3ef;
  border: 1px solid rgba(255, 123, 56, 0.18);
}

.message-bubble--user {
  align-self: flex-end;
  color: #fff;
  background: linear-gradient(135deg, #f03f6b, #ff7b38);
}

.message-role {
  display: inline-block;
  margin-bottom: 0.4rem;
  font-size: 0.78rem;
  opacity: 0.75;
}

.message-bubble p {
  margin: 0;
  line-height: 1.7;
  white-space: pre-wrap;
}

.composer {
  padding: 0 1.75rem 1.5rem;
}

.composer textarea {
  width: 100%;
  resize: vertical;
  border-radius: 22px;
  border: 1px solid rgba(15, 23, 42, 0.12);
  padding: 1rem 1.1rem;
  font: inherit;
  min-height: 120px;
}

.error-text {
  color: #dc2626;
  font-size: 0.92rem;
}

@media (max-width: 960px) {
  .ai-chat-page {
    grid-template-columns: 1fr;
  }

  .ai-chat-page__main {
    min-height: auto;
  }

  .message-bubble {
    max-width: 100%;
  }
}
</style>
