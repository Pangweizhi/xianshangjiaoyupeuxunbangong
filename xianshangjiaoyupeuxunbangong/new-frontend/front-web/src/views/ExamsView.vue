<template>
  <section class="section section--tight">
    <div class="section__header section__header--stack">
      <div>
        <p class="eyebrow">考试中心</p>
        <h1>按课程查看已发布考试</h1>
        <p class="section__summary">这里汇总考试时间、时长、总分和及格线，学生可按选课路径进入在线考试。</p>
      </div>
    </div>
    <div class="content-grid">
      <article v-for="item in exams" :key="item.id" class="feature-card feature-card--compact">
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.kechengName || "课程考试" }}</span>
            <span class="meta">{{ item.jiaoshiName || "教师待补充" }}</span>
          </div>
          <h3>{{ item.examName }}</h3>
          <p>{{ item.examSummary || "暂无考试说明" }}</p>
          <div class="status-list">
            <span>章节：{{ item.chapterName || "不限" }}</span>
            <span>总分：{{ item.totalScore ?? 0 }}</span>
            <span>及格：{{ item.passScore ?? 60 }}</span>
            <span>时长：{{ item.durationMinutes ?? 0 }} 分钟</span>
            <span>开始：{{ item.startTime || "待定" }}</span>
          </div>
          <RouterLink class="text-link" :to="`/exams/${item.id}`">进入考试</RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import type { ExamItem } from "@shared/index";
import { fetchExamPage } from "@/api/content";

const exams = ref<ExamItem[]>([]);

fetchExamPage().then((page) => {
  exams.value = page.list;
});
</script>
