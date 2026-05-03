<template>
  <section class="section section--tight">
    <div class="filter-bar filter-bar--surface filter-grid">
      <input v-model="filters.keyword" class="field" placeholder="搜索会议标题" />
      <select v-model="filters.type" class="field">
        <option value="">全部类型</option>
        <option v-for="item in typeOptions" :key="item" :value="item">{{ item }}</option>
      </select>
      <select v-model="filters.order" class="field">
        <option value="desc">最新优先</option>
        <option value="asc">最早优先</option>
      </select>
      <button class="primary-button" @click="loadMeetings">查询</button>
    </div>

    <div class="notice-list">
      <article v-for="item in meetings" :key="item.id" class="notice-row notice-row--expanded">
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.kaihuitongzhiValue || "会议" }}</span>
            <span class="meta">{{ item.insertTime?.slice(0, 10) || "待更新" }}</span>
          </div>
          <h3>{{ item.kaihuitongzhiName }}</h3>
          <p>{{ stripHtml(item.kaihuitongzhiContent) }}</p>
          <RouterLink class="text-link" :to="`/meetings/${item.id}`">查看详情</RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import type { MeetingItem } from "@shared/index";
import { fetchMeetingPage } from "@/api/content";

const filters = reactive({
  keyword: "",
  type: "",
  order: "desc"
});
const meetings = ref<MeetingItem[]>([]);

const typeOptions = computed(() =>
  Array.from(new Set(meetings.value.map((item) => item.kaihuitongzhiValue).filter(Boolean) as string[]))
);

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 120) || "暂无会议内容。";
}

async function loadMeetings() {
  const page = await fetchMeetingPage({ limit: 100, kaihuitongzhiName: filters.keyword || undefined, order: filters.order });
  meetings.value = page.list.filter((item) => !filters.type || item.kaihuitongzhiValue === filters.type);
}

loadMeetings();
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
