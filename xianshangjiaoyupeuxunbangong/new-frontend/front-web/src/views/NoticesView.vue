<template>
  <section class="section section--tight">
    <div class="section__header">
      <div>
        <p class="eyebrow">公告中心</p>
        <h1>保留原公告接口，重写阅读层次和发布时间表达</h1>
      </div>
    </div>

    <div class="notice-list">
      <article v-for="notice in notices" :key="notice.id" class="notice-row notice-row--expanded">
        <div>
          <div class="stack-inline">
            <span class="tag">{{ notice.newsValue || "公告" }}</span>
            <span class="meta">{{ notice.insertTime?.slice(0, 10) || "待更新" }}</span>
          </div>
          <h3>{{ notice.newsName }}</h3>
          <p>{{ stripHtml(notice.newsContent) }}</p>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { NoticeItem } from "@shared/index";
import { fetchNoticePage } from "@/api/content";

const notices = ref<NoticeItem[]>([]);

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 140) || "暂无公告内容";
}

fetchNoticePage().then((page) => {
  notices.value = page.list;
});
</script>
