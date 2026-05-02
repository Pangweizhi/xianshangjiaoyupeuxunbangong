<template>
  <section class="section section--tight">
    <div class="section__header">
      <div>
        <p class="eyebrow">会议通知</p>
        <h1>会议通知用简洁的时间轴式公告视图承载</h1>
      </div>
    </div>

    <div class="notice-list">
      <article v-for="item in meetings" :key="item.id" class="notice-row notice-row--expanded">
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.kaihuitongzhiValue || "会议" }}</span>
          </div>
          <h3>{{ item.kaihuitongzhiName }}</h3>
          <p>{{ stripHtml(item.kaihuitongzhiContent) }}</p>
          <RouterLink class="text-link" :to="`/meetings/${item.id}`">查看详情</RouterLink>
        </div>
        <span>{{ item.insertTime?.slice(0, 10) || "待更新" }}</span>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import type { MeetingItem } from "@shared/index";
import { fetchMeetingPage } from "@/api/content";

const meetings = ref<MeetingItem[]>([]);

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 120) || "暂无会议内容";
}

fetchMeetingPage().then((page) => {
  meetings.value = page.list;
});
</script>
