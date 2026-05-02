<template>
  <section class="section section--tight">
    <div class="section__header section__header--stack">
      <div>
        <p class="eyebrow">我的成绩</p>
        <h1>查看考试得分与通过状态</h1>
      </div>
    </div>
    <div class="content-grid">
      <article v-for="item in records" :key="item.id" class="feature-card feature-card--compact">
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.passStatus || "pending" }}</span>
            <span class="meta">{{ item.kechengName || "课程待补充" }}</span>
          </div>
          <h3>{{ item.examName }}</h3>
          <div class="status-list">
            <span>第 {{ item.attemptNo ?? 1 }} 次</span>
            <span>自动分：{{ item.autoScore ?? 0 }}</span>
            <span>人工分：{{ item.manualScore ?? 0 }}</span>
            <span>总分：{{ item.finalScore ?? 0 }}</span>
            <span>状态：{{ item.recordStatus || "started" }}</span>
            <span>提交时间：{{ item.submitTime || "未提交" }}</span>
          </div>
          <p>{{ item.checkRemark || "暂无阅卷评语" }}</p>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { ExamRecordItem } from "@shared/index";
import { fetchMyExamRecordPage } from "@/api/content";

const records = ref<ExamRecordItem[]>([]);

fetchMyExamRecordPage().then((page) => {
  records.value = page.list;
});
</script>
