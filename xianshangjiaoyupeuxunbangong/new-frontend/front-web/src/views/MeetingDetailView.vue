<template>
  <section class="section section--tight">
    <RouterLink class="text-link" to="/meetings">Back to meetings</RouterLink>
    <div v-if="detail" class="detail-shell">
      <article class="detail-article">
        <div class="stack-inline">
          <span class="tag">{{ detail.kaihuitongzhiValue || "Meeting" }}</span>
          <span class="meta">{{ formatDateTime(detail.insertTime || detail.createTime) }}</span>
        </div>
        <h1>{{ detail.kaihuitongzhiName }}</h1>
        <div class="meeting-content">
          <p v-for="(block, index) in contentBlocks" :key="index">{{ block }}</p>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import type { MeetingItem } from "@shared/index";
import { fetchMeetingDetail } from "@/api/content";

const route = useRoute();
const detail = ref<MeetingItem | null>(null);

const contentBlocks = computed(() => splitContent(detail.value?.kaihuitongzhiContent));

function splitContent(value?: string) {
  const normalized = value
    ?.replace(/<\s*br\s*\/?>/gi, "\n")
    .replace(/<\/p>/gi, "\n")
    .replace(/<p[^>]*>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/\r\n/g, "\n")
    .trim();

  if (!normalized) {
    return ["No meeting details"];
  }

  return normalized
    .split(/\n{2,}/)
    .flatMap((part) => part.split(/\n+/))
    .map((part) => part.trim())
    .filter(Boolean);
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

fetchMeetingDetail(route.params.id as string).then((data) => {
  detail.value = data;
});
</script>

<style scoped>
.meeting-content {
  margin-top: 18px;
  display: grid;
  gap: 14px;
}

.meeting-content :deep(p) {
  margin: 0;
  color: #4b5563;
  line-height: 1.85;
  white-space: pre-line;
  word-break: break-word;
}
</style>
