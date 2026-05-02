<template>
  <section class="section section--tight">
    <RouterLink class="text-link" to="/meetings">返回会议列表</RouterLink>
    <div v-if="detail" class="detail-shell">
      <article class="detail-article">
        <div class="stack-inline">
          <span class="tag">{{ detail.kaihuitongzhiValue || "会议" }}</span>
          <span class="meta">{{ detail.insertTime?.slice(0, 10) || "待更新" }}</span>
        </div>
        <h1>{{ detail.kaihuitongzhiName }}</h1>
        <p>{{ stripHtml(detail.kaihuitongzhiContent) }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import type { MeetingItem } from "@shared/index";
import { fetchMeetingDetail } from "@/api/content";

const route = useRoute();
const detail = ref<MeetingItem | null>(null);

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").trim() || "暂无会议详情";
}

fetchMeetingDetail(route.params.id as string).then((data) => {
  detail.value = data;
});
</script>
