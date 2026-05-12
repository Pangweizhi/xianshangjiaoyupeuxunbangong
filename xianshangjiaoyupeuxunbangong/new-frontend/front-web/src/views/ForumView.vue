<template>
  <section class="section section--tight forum-page">
    <div class="panel-header panel-header--stack forum-page__header">
      <div>
        <p class="eyebrow">论坛</p>
        <h2>主题帖与讨论流</h2>
        <p class="section__summary">
          浏览课程讨论、查看回复内容，也可以在登录后发起新的主题帖。
        </p>
      </div>
      <div class="forum-page__actions">
        <button class="ghost-button" @click="loadForums">刷新</button>
        <button class="primary-button" @click="handleOpenCreate">
          {{ createEntryLabel }}
        </button>
      </div>
    </div>

    <div class="filter-bar filter-bar--surface filter-grid">
      <input v-model="filters.keyword" class="field" placeholder="搜索帖子标题" />
      <select v-model="filters.role" class="field">
        <option value="">全部身份</option>
        <option value="教师">教师</option>
        <option value="学生">学生</option>
      </select>
      <select v-model="filters.scope" class="field">
        <option value="">全部帖子</option>
        <option value="topic">仅主题帖</option>
        <option value="reply">仅回复帖</option>
      </select>
      <button class="primary-button" @click="loadForums">查询</button>
    </div>

    <div class="notice-list">
      <article v-for="item in filteredForums" :key="item.id" class="notice-row notice-row--expanded">
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.superIds ? "回复帖" : "主题帖" }}</span>
            <span class="meta">{{ resolveRole(item) }}</span>
            <span class="meta">{{ item.forumStateValue || "讨论中" }}</span>
          </div>
          <h3>{{ item.forumName }}</h3>
          <p>{{ stripHtml(item.forumContent) }}</p>
          <p v-if="item.superIds && forumMap[item.superIds]" class="meta">所属主题：{{ forumMap[item.superIds].forumName }}</p>
          <RouterLink class="text-link" :to="`/forum/${item.id}`">查看讨论</RouterLink>
        </div>
        <span>{{ item.insertTime?.slice(0, 16) || "待更新" }}</span>
      </article>
    </div>

    <div v-if="postFeedback" class="forum-page__feedback meta">
      {{ postFeedback }}
    </div>
  </section>

  <div v-if="createDialogVisible" class="forum-dialog__overlay" @click.self="closeCreateDialog">
    <div class="forum-dialog">
      <div class="forum-dialog__header">
        <div>
          <p class="eyebrow">学生发帖</p>
          <h3>发布主题帖</h3>
        </div>
        <button class="forum-dialog__close" type="button" aria-label="关闭" @click="closeCreateDialog">×</button>
      </div>

      <p class="forum-dialog__tip">
        主题帖发布后会出现在论坛列表中，方便老师和同学继续跟帖讨论。
      </p>

      <div class="forum-dialog__body">
        <input v-model.trim="postForm.forumName" class="field" placeholder="帖子标题" />
        <textarea
          v-model.trim="postForm.forumContent"
          class="field field--textarea"
          placeholder="输入帖子内容"
        ></textarea>
      </div>

      <div class="forum-dialog__footer">
        <button class="ghost-button" type="button" @click="closeCreateDialog">取消</button>
        <button class="primary-button" type="button" :disabled="posting" @click="submitPost">
          {{ posting ? "提交中..." : "提交主题帖" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { RouterLink, useRouter } from "vue-router";
import type { ForumItem } from "@shared/index";
import { createForumPost, fetchForumPage } from "@/api/content";
import { useSessionStore } from "@/stores/session";

const router = useRouter();
const session = useSessionStore();

const filters = reactive({
  keyword: "",
  role: "",
  scope: ""
});
const forums = ref<ForumItem[]>([]);
const createDialogVisible = ref(false);
const posting = ref(false);
const postFeedback = ref("");

const postForm = reactive({
  forumName: "",
  forumContent: ""
});

const forumMap = computed(() =>
  Object.fromEntries(forums.value.map((item) => [item.id, item]))
);
const filteredForums = computed(() =>
  forums.value.filter((item) => {
    const role = resolveRole(item);
    const matchRole = !filters.role || role === filters.role;
    const matchScope =
      !filters.scope ||
      (filters.scope === "topic" && !item.superIds) ||
      (filters.scope === "reply" && Boolean(item.superIds));
    return matchRole && matchScope;
  })
);
const createEntryLabel = computed(() => {
  if (!session.isLoggedIn) {
    return "登录后发帖";
  }
  if (session.session?.tableName !== "yonghu") {
    return "仅学生可发帖";
  }
  return "学生发帖";
});

function resolveAuthor(item: ForumItem) {
  return item.yonghuName || item.jiaoshiName || item.uusername || "匿名用户";
}

function resolveRole(item: ForumItem) {
  if (item.jiaoshiName) return "教师";
  if (item.yonghuName) return "学生";
  return "管理员";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 120) || "暂无帖子内容。";
}

function resetPostForm() {
  postForm.forumName = "";
  postForm.forumContent = "";
}

function closeCreateDialog() {
  createDialogVisible.value = false;
  postFeedback.value = "";
}

function handleOpenCreate() {
  if (!session.isLoggedIn) {
    router.push({ name: "login", query: { redirect: "/forum" } });
    return;
  }
  if (session.session?.tableName !== "yonghu") {
    postFeedback.value = "当前账号不是学生，暂时无法发帖。";
    return;
  }
  resetPostForm();
  postFeedback.value = "";
  createDialogVisible.value = true;
}

async function submitPost() {
  if (!postForm.forumName.trim()) {
    postFeedback.value = "请输入帖子标题。";
    return;
  }
  if (!postForm.forumContent.trim()) {
    postFeedback.value = "请输入帖子内容。";
    return;
  }

  posting.value = true;
  postFeedback.value = "";
  try {
    const result = await createForumPost({
      forumName: postForm.forumName.trim(),
      forumContent: postForm.forumContent.trim(),
      forumStateTypes: 1
    });
    if (result.code !== 0) {
      throw new Error(result.msg || "发帖失败");
    }
    postFeedback.value = "主题帖已发布。";
    createDialogVisible.value = false;
    resetPostForm();
    await loadForums();
  } catch (error) {
    postFeedback.value = error instanceof Error ? error.message : "发帖失败";
  } finally {
    posting.value = false;
  }
}

async function loadForums() {
  const page = await fetchForumPage({
    limit: 100,
    forumName: filters.keyword || undefined
  });
  forums.value = page.list.map((item) => ({ ...item, uusername: resolveAuthor(item) }));
}

loadForums();
</script>

<style scoped>
.forum-page {
  position: relative;
}

.forum-page__header {
  align-items: end;
}

.forum-page__actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.forum-page__feedback {
  margin-top: 14px;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.forum-dialog__overlay {
  position: fixed;
  inset: 0;
  z-index: 40;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(16, 24, 40, 0.45);
  backdrop-filter: blur(10px);
}

.forum-dialog {
  width: min(720px, 100%);
  border-radius: 28px;
  border: 1px solid var(--line);
  background: var(--surface-strong);
  box-shadow: var(--shadow);
  padding: 24px;
}

.forum-dialog__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.forum-dialog__header h3 {
  margin: 8px 0 0;
  font-family: "STZhongsong", "FangSong", serif;
}

.forum-dialog__close {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.06);
  color: var(--text);
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
}

.forum-dialog__tip {
  margin: 14px 0 18px;
  color: var(--muted-strong);
  line-height: 1.75;
}

.forum-dialog__body {
  display: grid;
  gap: 14px;
}

.forum-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 18px;
}

@media (max-width: 960px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }

  .forum-page__actions,
  .forum-dialog__footer {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
