<template>
  <section class="section section--tight">
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
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import type { ForumItem } from "@shared/index";
import { fetchForumPage } from "@/api/content";

const filters = reactive({
  keyword: "",
  role: "",
  scope: ""
});
const forums = ref<ForumItem[]>([]);

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
.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 960px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
