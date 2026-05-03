<template>
  <section class="section section--tight">
    <div class="section__header section__header--stack">
      <div>
        <p class="eyebrow">My Scores</p>
        <h1>Course Performance Summary</h1>
        <p class="section__summary">
          Phase 4 summary for progress, homework, exams, completion, and granted credits.
        </p>
      </div>
    </div>

    <div class="dashboard-grid">
      <article class="dashboard-card">
        <span class="meta-label">Courses</span>
        <strong>{{ report.summary.courseCount || 0 }}</strong>
        <p>Courses already enrolled</p>
      </article>
      <article class="dashboard-card">
        <span class="meta-label">Finished</span>
        <strong>{{ report.summary.finishedCount || 0 }}</strong>
        <p>Courses that have completed settlement</p>
      </article>
      <article class="dashboard-card">
        <span class="meta-label">Credits</span>
        <strong>{{ report.summary.grantedCreditScore || 0 }}</strong>
        <p>Total granted credit score</p>
      </article>
    </div>

    <div class="content-grid">
      <article v-for="item in report.courseSummaries" :key="item.courseId" class="feature-card feature-card--compact">
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.enrollStatus || "enrolled" }}</span>
            <span class="meta">{{ item.teacherName || "teacher pending" }}</span>
          </div>
          <h3>{{ item.courseName }}</h3>
          <div class="status-list">
            <span>Progress: {{ Math.round(item.progressPercent || 0) }}%</span>
            <span>Homework: {{ item.passedHomeworkCount || 0 }}/{{ item.homeworkTotal || 0 }}</span>
            <span>Homework Avg: {{ item.averageHomeworkScore ?? 0 }}</span>
            <span>Exam: {{ item.passedExamCount || 0 }}/{{ item.examTotal || 0 }}</span>
            <span>Exam Avg: {{ item.averageExamScore ?? 0 }}</span>
            <span>Best Exam: {{ item.bestExamScore ?? 0 }}</span>
            <span>Credit: {{ item.grantStatus || "pending" }}</span>
            <span>Granted: {{ item.grantedCreditScore ?? 0 }}</span>
          </div>
          <p>{{ item.grantRemark || "No extra remark" }}</p>
        </div>
      </article>
    </div>

    <section class="section">
      <div class="section__header section__header--stack">
        <div>
          <p class="eyebrow">Exam Records</p>
          <h2>Recent Attempts</h2>
        </div>
      </div>
      <div class="mini-list">
        <article v-for="item in records" :key="item.id" class="mini-list__row">
          <div>
            <strong>{{ item.examName }}</strong>
            <p>{{ item.kechengName || "Course pending" }}</p>
          </div>
          <div class="status-list">
            <span>{{ item.passStatus || "pending" }}</span>
            <span>Attempt {{ item.attemptNo ?? 1 }}</span>
            <span>Final {{ item.finalScore ?? 0 }}</span>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import type { ExamRecordItem, StudentCoursePerformanceResponse } from "@shared/index";
import { fetchMyCoursePerformanceSummary, fetchMyExamRecordPage } from "@/api/content";

const report = reactive<StudentCoursePerformanceResponse>({
  summary: {
    courseCount: 0,
    finishedCount: 0,
    grantedCreditCount: 0,
    grantedCreditScore: 0,
    averageProgressPercent: 0,
    reviewedHomeworkCount: 0,
    averageHomeworkScore: 0,
    checkedExamCount: 0,
    averageExamScore: 0
  },
  courseSummaries: []
});

const records = ref<ExamRecordItem[]>([]);

Promise.all([fetchMyCoursePerformanceSummary(), fetchMyExamRecordPage({ limit: 10 })]).then(([summary, page]) => {
  Object.assign(report, summary);
  records.value = page.list;
});
</script>
