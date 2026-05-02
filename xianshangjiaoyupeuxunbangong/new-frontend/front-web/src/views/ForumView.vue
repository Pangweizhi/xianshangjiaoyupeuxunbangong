<template>
  <section class="section section--tight">
    <div class="section__header section__header--stack">
      <div>
        <p class="eyebrow">交流论坛</p>
        <h1>围绕课程与任务组织讨论话题</h1>
        <p class="section__summary">帖子列表优先展示标题、作者、状态和摘要，方便快速进入问题讨论与回复。</p>
      </div>
    </div>

    <div class="notice-list">
      <article v-for="item in forums" :key="item.id" class="notice-row notice-row--expanded">
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.forumStateValue || "讨论中" }}</span>
            <span class="meta">{{ resolveAuthor(item) }}</span>
          </div>
          <h3>{{ item.forumName }}</h3>
          <p>{{ stripHtml(item.forumContent) }}</p>
          <RouterLink class="text-link" :to="`/forum/${item.id}`">查看讨论</RouterLink>
        </div>
        <span>{{ item.insertTime?.slice(0, 10) || "待更新" }}</span>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import type { ForumItem } from "@shared/index";
import { fetchForumPage } from "@/api/content";

const forums = ref<ForumItem[]>([]);

function resolveAuthor(item: ForumItem) {
  return item.yonghuName || item.jiaoshiName || item.uusername || "匿名发布";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 120) || "暂无帖子内容";
}

fetchForumPage().then((page) => {
  forums.value = page.list;
});
</script>
