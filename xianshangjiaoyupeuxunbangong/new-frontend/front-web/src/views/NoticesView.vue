<template>
  <section class="section section--tight">
    <div class="filter-bar filter-bar--surface filter-grid">
      <input v-model="filters.keyword" class="field" placeholder="搜索公告标题" />
      <select v-model="filters.type" class="field">
        <option value="">全部类型</option>
        <option v-for="item in typeOptions" :key="item" :value="item">{{ item }}</option>
      </select>
      <select v-model="filters.order" class="field">
        <option value="desc">最新优先</option>
        <option value="asc">最早优先</option>
      </select>
      <button class="primary-button" @click="loadNotices">查询</button>
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
import { computed, reactive, ref } from "vue";
import type { NoticeItem } from "@shared/index";
import { fetchNoticePage } from "@/api/content";

const filters = reactive({
  keyword: "",
  type: "",
  order: "desc"
});
const notices = ref<NoticeItem[]>([]);

const typeOptions = computed(() =>
  Array.from(new Set(notices.value.map((item) => item.newsValue).filter(Boolean) as string[]))
);

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 140) || "暂无公告内容。";
}

async function loadNotices() {
  const page = await fetchNoticePage({ limit: 100, order: filters.order });
  notices.value = page.list.filter((item) => {
    const matchKeyword = !filters.keyword || item.newsName?.includes(filters.keyword);
    const matchType = !filters.type || item.newsValue === filters.type;
    return matchKeyword && matchType;
  });
}

loadNotices();
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
