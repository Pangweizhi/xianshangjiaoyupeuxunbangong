<template>
  <div v-loading="loading" class="dashboard-stack">
    <div class="dashboard-grid">
      <article class="admin-card accent">
        <span>{{ isTeacher ? "教师概览" : "平台概览" }}</span>
        <strong>{{ isTeacher ? "教学工作台" : "运营驾驶舱" }}</strong>
        <p>课程、作业、考试、学习进度与学分统计统一查看。</p>
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
          <h2>课程结算统计</h2>
          <span class="panel-note">按课程汇总学习进度、成绩和学分</span>
        </div>
        <el-table :data="courseStats" stripe empty-text="暂无数据">
          <el-table-column prop="courseName" label="课程" min-width="180" />
          <el-table-column prop="teacherName" label="教师" min-width="120" />
          <el-table-column prop="enrollCount" label="选课人数" min-width="100" />
          <el-table-column prop="finishedCount" label="完成人数" min-width="100" />
          <el-table-column prop="averageProgressPercent" label="平均进度" min-width="110">
            <template #default="{ row }">{{ row.averageProgressPercent ?? 0 }}%</template>
          </el-table-column>
          <el-table-column prop="averageHomeworkScore" label="作业均分" min-width="100" />
          <el-table-column prop="averageExamScore" label="考试均分" min-width="100" />
          <el-table-column prop="creditGrantedCount" label="已发学分" min-width="100" />
        </el-table>
      </section>

      <section class="admin-panel">
        <div class="panel-header">
          <h2>{{ isTeacher ? "教学快照" : "平台快照" }}</h2>
        </div>
        <div class="admin-list">
          <article>
            <div>
              <strong>作业达标数</strong>
              <p>分数大于等于 60 的作业记录</p>
            </div>
            <div class="report-figure">{{ reportSummary.passedHomeworkCount ?? 0 }}</div>
          </article>
          <article>
            <div>
              <strong>考试通过数</strong>
              <p>达到及格线的考试记录</p>
            </div>
            <div class="report-figure">{{ reportSummary.passedExamCount ?? 0 }}</div>
          </article>
          <article>
            <div>
              <strong>已发学分</strong>
              <p>累计已发放学分值</p>
            </div>
            <div class="report-figure">{{ reportSummary.creditGrantedScore ?? 0 }}</div>
          </article>
        </div>
      </section>
    </div>

    <div v-if="isTeacher" class="panel-grid panel-grid--teacher">
      <section class="admin-panel">
        <div class="panel-header panel-header--spread">
          <h2>作业批改</h2>
          <div class="toolbar toolbar--wrap">
            <el-input v-model="reportFilters.zuoyeName" placeholder="作业名称" clearable />
            <el-select v-model="reportFilters.submitStatus" placeholder="批改状态" clearable>
              <el-option label="待批改" value="待批改" />
              <el-option label="已批改" value="已批改" />
              <el-option label="需重交" value="需重交" />
            </el-select>
            <el-button type="primary" @click="loadTeacherDashboard">查询</el-button>
            <el-button @click="resetTeacherFilters">重置</el-button>
          </div>
        </div>
        <el-table :data="teacherSubmissionRows" stripe empty-text="暂无提交记录">
          <el-table-column prop="zuoyeName" label="作业" min-width="160" />
          <el-table-column prop="yonghuName" label="学生" min-width="120" />
          <el-table-column prop="submitStatus" label="状态" min-width="120" />
          <el-table-column prop="submitScore" label="分数" min-width="100" />
          <el-table-column prop="checkTime" label="批改时间" min-width="180" />
        </el-table>
      </section>

      <section class="admin-panel">
        <div class="panel-header">
          <h2>我的课程</h2>
        </div>
        <el-table :data="teacherCourses" stripe empty-text="暂无课程">
          <el-table-column prop="kechengName" label="课程" min-width="180" />
          <el-table-column prop="kechengValue" label="类型" min-width="120" />
          <el-table-column prop="kechengTime" label="开始时间" min-width="180" />
          <el-table-column prop="kechengEndTime" label="结束时间" min-width="180" />
        </el-table>
      </section>
    </div>

    <div v-else class="panel-grid">
      <section class="admin-panel">
        <div class="panel-header">
          <h2>最新课程</h2>
        </div>
        <el-table :data="courses" stripe empty-text="暂无课程">
          <el-table-column prop="kechengName" label="课程" min-width="220" />
          <el-table-column prop="jiaoshiName" label="教师" min-width="120" />
          <el-table-column prop="kechengValue" label="类型" min-width="120" />
          <el-table-column prop="kechengTime" label="开始时间" min-width="160" />
        </el-table>
      </section>

      <section class="admin-panel">
        <div class="panel-header">
          <h2>最新公告</h2>
        </div>
        <div v-if="notices.length > 0" class="admin-list">
          <article v-for="notice in notices" :key="notice.id">
            <strong>{{ notice.newsName }}</strong>
            <span>{{ notice.insertTime?.slice(0, 10) || "待发布" }}</span>
          </article>
        </div>
        <el-empty v-else description="暂无公告" />
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
      { label: "课程数", value: reportSummary.courseCount, hint: "当前教师名下课程" },
      { label: "完成人数", value: reportSummary.finishedCount, hint: "满足结课规则的选课记录" },
      { label: "考试均分", value: Number((reportSummary.averageExamScore ?? 0).toFixed(1)), hint: "已批改考试平均分" },
      { label: "学分发放", value: reportSummary.creditGrantedCount ?? 0, hint: "已发放学分记录数" }
    ];
  }

  return [
    { label: "课程数", value: reportSummary.courseCount, hint: "纳入统计的课程总数" },
    { label: "选课人数", value: reportSummary.enrollCount ?? 0, hint: "总选课记录数" },
    { label: "完成人数", value: reportSummary.finishedCount, hint: "满足结课规则的选课记录" },
    { label: "平均进度", value: Number((reportSummary.averageProgressPercent ?? 0).toFixed(1)), hint: "整体学习进度" },
    { label: "作业均分", value: Number((reportSummary.averageHomeworkScore ?? 0).toFixed(1)), hint: "已批改作业平均分" },
    { label: "考试均分", value: Number((reportSummary.averageExamScore ?? 0).toFixed(1)), hint: "已批改考试平均分" }
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
    teacherCourses.value = Array.isArray(coursePage?.list) ? coursePage.list : [];
    teacherSubmissionRows.value = Array.isArray(submissionPage?.list) ? submissionPage.list : [];
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
