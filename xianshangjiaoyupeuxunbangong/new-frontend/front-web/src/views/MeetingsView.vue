<template>
  <section class="section section--tight">
    <div class="filter-bar filter-bar--surface filter-grid">
      <input v-model="filters.keyword" class="field" placeholder="Search meeting title" />
      <select v-model="filters.type" class="field">
        <option value="">All types</option>
        <option v-for="item in typeOptions" :key="item" :value="item">{{ item }}</option>
      </select>
      <select v-model="filters.order" class="field">
        <option value="desc">Newest first</option>
        <option value="asc">Oldest first</option>
      </select>
      <button class="primary-button" @click="loadMeetings">Search</button>
    </div>

    <div class="notice-list">
      <article v-for="item in meetings" :key="item.id" class="notice-row notice-row--expanded">
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.kaihuitongzhiValue || "Meeting" }}</span>
            <span class="meta">{{ formatDateTime(item.insertTime || item.createTime) }}</span>
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
  const text = value?.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
  if (!text) {
    return "No meeting content.";
  }
  return text.length > 120 ? `${text.slice(0, 120)}...` : text;
}

function formatDateTime(value?: string) {
  if (!value) {
    return "Pending";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

async function loadMeetings() {
  const page = await fetchMeetingPage({
    limit: 100,
    kaihuitongzhiName: filters.keyword || undefined,
    order: filters.order
  });
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
