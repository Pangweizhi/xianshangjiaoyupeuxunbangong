<template>
  <section class="section section--tight">
    <div class="filter-bar filter-bar--surface filter-grid">
      <input v-model="filters.keyword" class="field" placeholder="搜索考试名称" />
      <select v-model="filters.courseId" class="field">
        <option value="">全部课程</option>
        <option v-for="item in courses" :key="item.id" :value="String(item.id)">{{ item.kechengName }}</option>
      </select>
      <select v-model="filters.status" class="field">
        <option value="">全部状态</option>
        <option value="未开始">未开始</option>
        <option value="进行中">进行中</option>
        <option value="已结束">已结束</option>
      </select>
      <button class="primary-button" @click="loadExams">查询</button>
    </div>

    <div class="content-grid">
      <article v-for="item in filteredExams" :key="item.id" class="feature-card feature-card--compact">
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.kechengName || "课程考试" }}</span>
            <span class="meta">{{ item.jiaoshiName || "教师待补充" }}</span>
            <span v-if="ongoingExamIds.has(item.id)" class="status-pill status-pill--danger">进行中</span>
          </div>
          <h3>{{ item.examName }}</h3>
          <p>{{ item.examSummary || "暂无考试说明。" }}</p>
          <div class="status-list">
            <span>章节：{{ item.chapterName || "不限" }}</span>
            <span>总分：{{ item.totalScore ?? 0 }}</span>
            <span>及格：{{ item.passScore ?? 60 }}</span>
            <span>开始：{{ item.startTime || "待定" }}</span>
          </div>
          <RouterLink class="text-link" :to="`/exams/${item.id}`">进入考试</RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import type { CourseItem, ExamItem, ExamRecordItem } from "@shared/index";
import { fetchCoursePage, fetchExamPage, fetchMyExamRecordPage } from "@/api/content";

const filters = reactive({
  keyword: "",
  courseId: "",
  status: ""
});
const exams = ref<ExamItem[]>([]);
const courses = ref<CourseItem[]>([]);
const ongoingExamIds = ref(new Set<number>());

const filteredExams = computed(() =>
  exams.value.filter((item) => {
    if (!filters.status) return true;
    return resolveDisplayStatus(item) === filters.status;
  })
);

function resolveDisplayStatus(item: ExamItem) {
  if (ongoingExamIds.value.has(item.id)) {
    return "进行中";
  }
  const now = Date.now();
  const start = item.startTime ? new Date(item.startTime).getTime() : null;
  const end = item.endTime ? new Date(item.endTime).getTime() : null;
  if (start && now < start) return "未开始";
  if (end && now > end) return "已结束";
  return "进行中";
}

async function loadExams() {
  const [coursePage, examPage, recordPage] = await Promise.all([
    fetchCoursePage({ limit: 100 }),
    fetchExamPage({
      limit: 100,
      examName: filters.keyword || undefined,
      kechengId: filters.courseId || undefined,
      examStatus: undefined
    }),
    fetchMyExamRecordPage({ limit: 200 })
  ]);
  courses.value = coursePage.list;
  exams.value = examPage.list;
  const ongoing = new Set<number>();
  recordPage.list.forEach((record: ExamRecordItem) => {
    if (record.recordStatus === "started") {
      ongoing.add(record.examId);
    }
  });
  ongoingExamIds.value = ongoing;
}

loadExams();
</script>

<style scoped>
.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 1;
  background: #fff1e7;
  color: #8a3412;
}

.status-pill--danger {
  background: #ffe7e7;
  color: #9d1c1c;
}

@media (max-width: 960px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
