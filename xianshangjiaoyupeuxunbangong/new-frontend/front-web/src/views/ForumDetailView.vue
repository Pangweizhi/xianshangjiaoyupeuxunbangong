<template>
  <section class="section section--tight">
    <RouterLink class="text-link" to="/forum">返回论坛</RouterLink>
    <div v-if="detail" class="detail-shell">
      <article class="detail-article">
        <div class="stack-inline">
          <span class="tag">{{ detail.forumStateValue || "讨论中" }}</span>
          <span class="meta">{{ authorName }}</span>
        </div>
        <h1>{{ detail.forumName }}</h1>
        <p>{{ stripHtml(detail.forumContent) }}</p>
      </article>

      <aside class="action-panel">
        <p class="eyebrow">发帖与回帖</p>
        <input v-model="replyTitle" class="field" placeholder="回复标题" />
        <textarea v-model="replyContent" class="field field--textarea" placeholder="输入回复内容"></textarea>
        <button class="primary-button primary-button--full" :disabled="submitting" @click="submitReply">
          {{ submitting ? "提交中..." : "提交回复" }}
        </button>
        <p v-if="feedback" class="meta">{{ feedback }}</p>
      </aside>
    </div>

    <div class="section">
      <div class="section__header">
        <div>
          <p class="eyebrow">回帖列表</p>
          <h2>以父帖 ID 组织当前讨论</h2>
        </div>
      </div>
      <div class="notice-list">
        <article v-for="item in replies" :key="item.id" class="notice-row notice-row--expanded">
          <div>
            <div class="stack-inline">
              <span class="tag">{{ item.forumStateValue || "回复" }}</span>
              <span class="meta">{{ resolveAuthor(item) }}</span>
            </div>
            <h3>{{ item.forumName }}</h3>
            <p>{{ stripHtml(item.forumContent) }}</p>
          </div>
          <span>{{ item.insertTime?.slice(0, 10) || "待更新" }}</span>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import type { ForumItem } from "@shared/index";
import { createForumPost, fetchForumDetail, fetchForumPage } from "@/api/content";
import { useSessionStore } from "@/stores/session";

const route = useRoute();
const session = useSessionStore();
const detail = ref<ForumItem | null>(null);
const replies = ref<ForumItem[]>([]);
const replyTitle = ref("");
const replyContent = ref("");
const submitting = ref(false);
const feedback = ref("");

const authorName = computed(
  () => detail.value?.yonghuName || detail.value?.jiaoshiName || detail.value?.uusername || "匿名发布"
);

function resolveAuthor(item: ForumItem) {
  return item.yonghuName || item.jiaoshiName || item.uusername || "匿名发布";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").trim() || "暂无内容";
}

async function loadReplies() {
  const page = await fetchForumPage({ superIds: route.params.id });
  replies.value = page.list.filter((item) => item.id !== Number(route.params.id));
}

async function submitReply() {
  if (!session.isLoggedIn) {
    feedback.value = "请先登录后再回复。";
    return;
  }
  submitting.value = true;
  feedback.value = "";
  try {
    const payload = {
      forumName: replyTitle.value || `回复：${detail.value?.forumName || ""}`,
      forumContent: replyContent.value,
      superIds: Number(route.params.id),
      forumStateTypes: 1
    };
    const result = await createForumPost(payload);
    if (result.code !== 0) {
      throw new Error(result.msg || "回复失败");
    }
    feedback.value = "回复已提交。";
    replyTitle.value = "";
    replyContent.value = "";
    await loadReplies();
  } catch (error) {
    feedback.value = error instanceof Error ? error.message : "回复失败";
  } finally {
    submitting.value = false;
  }
}

fetchForumDetail(route.params.id as string).then((data) => {
  detail.value = data;
});
loadReplies();
</script>
