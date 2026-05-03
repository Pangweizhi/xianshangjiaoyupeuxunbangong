<template>
  <div v-loading="loading" class="dashboard-stack">
    <div class="dashboard-grid">
      <article class="admin-card accent">
        <span>{{ isTeacher ? "Teacher Report" : "Core Report" }}</span>
        <strong>{{ isTeacher ? "Phase 4 Desk" : "Phase 4 Control" }}</strong>
        <p>Track progress, homework, exams, completion, and credit grants in one view.</p>
      </article>
      <article v-for="card in cards" :key="card.label" class="admin-card">
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
        <p>{{ card.hint }}</p>
      </article>
    </div>

    <div class="panel-grid">
      <section class="admin-panel">
        <div class="panel-header panel-header--spread">
          <h2>Course Settlement</h2>
          <span class="panel-note">Per-course summary for progress, scores, and credits</span>
        </div>
        <el-table :data="courseStats" stripe empty-text="No data">
          <el-table-column prop="courseName" label="Course" min-width="180" />
          <el-table-column prop="teacherName" label="Teacher" min-width="120" />
          <el-table-column prop="enrollCount" label="Enrolls" min-width="100" />
          <el-table-column prop="finishedCount" label="Finished" min-width="100" />
          <el-table-column prop="averageProgressPercent" label="Avg Progress" min-width="110">
            <template #default="{ row }">{{ row.averageProgressPercent ?? 0 }}%</template>
          </el-table-column>
          <el-table-column prop="averageHomeworkScore" label="HW Avg" min-width="100" />
          <el-table-column prop="averageExamScore" label="Exam Avg" min-width="100" />
          <el-table-column prop="creditGrantedCount" label="Credits" min-width="100" />
        </el-table>
      </section>

      <section class="admin-panel">
        <div class="panel-header">
          <h2>{{ isTeacher ? "Teaching Snapshot" : "Platform Snapshot" }}</h2>
        </div>
        <div class="admin-list">
          <article>
            <div>
              <strong>Homework Passed</strong>
              <p>Homework records with score >= 60</p>
            </div>
            <div class="report-figure">{{ reportSummary.passedHomeworkCount ?? 0 }}</div>
          </article>
          <article>
            <div>
              <strong>Exam Passed</strong>
              <p>Exam records that reached the pass line</p>
            </div>
            <div class="report-figure">{{ reportSummary.passedExamCount ?? 0 }}</div>
          </article>
          <article>
            <div>
              <strong>Granted Score</strong>
              <p>Total credit score already granted</p>
            </div>
            <div class="report-figure">{{ reportSummary.creditGrantedScore ?? 0 }}</div>
          </article>
        </div>
      </section>
    </div>

    <div v-if="isTeacher" class="panel-grid panel-grid--teacher">
      <section class="admin-panel">
        <div class="panel-header panel-header--spread">
          <h2>Homework Reviews</h2>
          <div class="toolbar toolbar--wrap">
            <el-input v-model="reportFilters.zuoyeName" placeholder="Homework name" clearable />
            <el-select v-model="reportFilters.submitStatus" placeholder="Status" clearable>
              <el-option label="Pending" value="待批改" />
              <el-option label="Reviewed" value="已批改" />
              <el-option label="Retry" value="需重交" />
            </el-select>
            <el-button type="primary" @click="loadTeacherDashboard">Search</el-button>
            <el-button @click="resetTeacherFilters">Reset</el-button>
          </div>
        </div>
        <el-table :data="teacherSubmissionRows" stripe empty-text="No submissions">
          <el-table-column prop="zuoyeName" label="Homework" min-width="160" />
          <el-table-column prop="yonghuName" label="Student" min-width="120" />
          <el-table-column prop="submitStatus" label="Status" min-width="120" />
          <el-table-column prop="submitScore" label="Score" min-width="100" />
          <el-table-column prop="checkTime" label="Review Time" min-width="180" />
        </el-table>
      </section>

      <section class="admin-panel">
        <div class="panel-header">
          <h2>My Courses</h2>
        </div>
        <el-table :data="teacherCourses" stripe empty-text="No courses">
          <el-table-column prop="kechengName" label="Course" min-width="180" />
          <el-table-column prop="kechengValue" label="Type" min-width="120" />
          <el-table-column prop="kechengTime" label="Start Time" min-width="180" />
        </el-table>
      </section>
    </div>

    <div v-else class="panel-grid">
      <section class="admin-panel">
        <div class="panel-header">
          <h2>Latest Courses</h2>
        </div>
        <el-table :data="courses" stripe empty-text="No courses">
          <el-table-column prop="kechengName" label="Course" min-width="220" />
          <el-table-column prop="jiaoshiName" label="Teacher" min-width="120" />
          <el-table-column prop="kechengValue" label="Type" min-width="120" />
          <el-table-column prop="kechengTime" label="Start Time" min-width="160" />
        </el-table>
      </section>

      <section class="admin-panel">
        <div class="panel-header">
          <h2>Latest Notices</h2>
        </div>
        <div v-if="notices.length > 0" class="admin-list">
          <article v-for="notice in notices" :key="notice.id">
            <strong>{{ notice.newsName }}</strong>
            <span>{{ notice.insertTime?.slice(0, 10) || "Pending" }}</span>
          </article>
        </div>
        <el-empty v-else description="No notices" />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import type {
  CourseItem,
  CourseReportCourseItem,
  CourseReportSummary,
  DashboardCard,
  HomeworkSubmissionItem,
  NoticeItem
} from "@shared/index";
import {
  fetchAdminCourses,
  fetchAdminNotices,
  fetchCourseReportOverview,
  fetchHomeworkSubmissionPage
} from "@/api/dashboard";
import { useAdminSessionStore } from "@/stores/session";

const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");
const loading = ref(false);

const courses = ref<CourseItem[]>([]);
const notices = ref<NoticeItem[]>([]);
const teacherCourses = ref<CourseItem[]>([]);
const teacherSubmissionRows = ref<HomeworkSubmissionItem[]>([]);
const courseStats = ref<CourseReportCourseItem[]>([]);
const reportSummary = reactive<CourseReportSummary>({
  courseCount: 0,
  finishedCount: 0,
  reviewedHomeworkCount: 0,
  checkedExamCount: 0,
  averageHomeworkScore: 0,
  averageExamScore: 0,
  averageProgressPercent: 0,
  enrollCount: 0,
  creditGrantedCount: 0,
  creditGrantedScore: 0,
  homeworkCount: 0,
  passedHomeworkCount: 0,
  examCount: 0,
  passedExamCount: 0
});

const reportFilters = reactive({
  zuoyeName: "",
  submitStatus: ""
});

const cards = computed<DashboardCard[]>(() => {
  if (isTeacher.value) {
    return [
      { label: "Courses", value: reportSummary.courseCount, hint: "Courses under current teacher" },
      { label: "Finished", value: reportSummary.finishedCount, hint: "Enrollments that passed completion rules" },
      { label: "Exam Avg", value: Number((reportSummary.averageExamScore ?? 0).toFixed(1)), hint: "Average checked exam score" },
      { label: "Credit Grants", value: reportSummary.creditGrantedCount ?? 0, hint: "Granted credit records" }
    ];
  }

  return [
    { label: "Courses", value: reportSummary.courseCount, hint: "Courses included in phase 4 reporting" },
    { label: "Enrolls", value: reportSummary.enrollCount ?? 0, hint: "Total enrollment records" },
    { label: "Finished", value: reportSummary.finishedCount, hint: "Enrollments that passed completion rules" },
    { label: "Avg Progress", value: Number((reportSummary.averageProgressPercent ?? 0).toFixed(1)), hint: "Average learning progress" },
    { label: "HW Avg", value: Number((reportSummary.averageHomeworkScore ?? 0).toFixed(1)), hint: "Average reviewed homework score" },
    { label: "Exam Avg", value: Number((reportSummary.averageExamScore ?? 0).toFixed(1)), hint: "Average checked exam score" }
  ];
});

function applyReport(payload: { summary: CourseReportSummary; courseStats: CourseReportCourseItem[] }) {
  courseStats.value = payload.courseStats;
  Object.assign(reportSummary, payload.summary);
}

async function loadTeacherDashboard() {
  const [report, coursePage, submissionPage] = await Promise.all([
    fetchCourseReportOverview(),
    fetchAdminCourses({ limit: 5 }),
    fetchHomeworkSubmissionPage({
      limit: 20,
      zuoyeName: reportFilters.zuoyeName || undefined,
      submitStatus: reportFilters.submitStatus || undefined
    })
  ]);

  applyReport(report);
  teacherCourses.value = coursePage.list;
  teacherSubmissionRows.value = submissionPage.list;
}

async function loadAdminDashboard() {
  const [report, coursePage, noticePage] = await Promise.all([
    fetchCourseReportOverview(),
    fetchAdminCourses({ limit: 5 }),
    fetchAdminNotices({ limit: 5 })
  ]);

  applyReport(report);
  courses.value = coursePage.list;
  notices.value = noticePage.list;
}

function resetTeacherFilters() {
  reportFilters.zuoyeName = "";
  reportFilters.submitStatus = "";
  loadTeacherDashboard();
}

async function loadDashboard() {
  loading.value = true;
  try {
    if (isTeacher.value) {
      await loadTeacherDashboard();
    } else {
      await loadAdminDashboard();
    }
  } finally {
    loading.value = false;
  }
}

loadDashboard();
</script>
