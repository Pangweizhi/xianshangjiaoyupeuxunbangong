<template>
  <div v-loading="loading" class="dashboard-stack">
    <div class="dashboard-grid">
      <article class="admin-card accent">
        <span>{{ isTeacher ? "教师工作台" : "后台总览" }}</span>
        <strong>{{ isTeacher ? "Teaching Desk" : "Control Room" }}</strong>
        <p>
          {{ isTeacher ? "聚合作业批改、课程安排、备课资料和提交统计。" : "聚合课程、公告、用户、提交记录等核心指标。" }}
        </p>
      </article>
      <article v-for="card in cards" :key="card.label" class="admin-card">
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
        <p>{{ card.hint }}</p>
      </article>
    </div>

    <div v-if="isTeacher" class="panel-grid panel-grid--teacher">
      <section class="admin-panel">
        <div class="panel-header panel-header--spread">
          <h2>批改统计</h2>
          <div class="toolbar toolbar--wrap">
            <el-input v-model="reportFilters.zuoyeName" placeholder="筛选作业标题" clearable />
            <el-select v-model="reportFilters.submitStatus" placeholder="状态" clearable>
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
          <el-table-column prop="submitScore" label="评分" min-width="100" />
          <el-table-column prop="checkTime" label="批改时间" min-width="180" />
        </el-table>
      </section>

      <section class="admin-panel">
        <div class="panel-header">
          <h2>教师报表</h2>
        </div>
        <div class="admin-list" v-if="teacherReports.length > 0">
          <article v-for="item in teacherReports" :key="item.label">
            <div>
              <strong>{{ item.label }}</strong>
              <p>{{ item.hint }}</p>
            </div>
            <div class="report-figure">{{ item.value }}</div>
          </article>
        </div>
        <el-empty v-else description="暂无统计结果" />
      </section>

      <section class="admin-panel">
        <div class="panel-header">
          <h2>我的课程</h2>
        </div>
        <el-table :data="teacherCourses" stripe empty-text="暂无课程">
          <el-table-column prop="kechengName" label="课程标题" min-width="180" />
          <el-table-column prop="kechengValue" label="类型" min-width="120" />
          <el-table-column prop="kechengTime" label="开始时间" min-width="180" />
        </el-table>
      </section>

      <section class="admin-panel">
        <div class="panel-header">
          <h2>我的备课资料</h2>
        </div>
        <el-table :data="teacherMaterials" stripe empty-text="暂无备课资料">
          <el-table-column prop="jiaoxueshipinName" label="标题" min-width="180" />
          <el-table-column prop="jiaoxueshipinValue" label="类型" min-width="120" />
          <el-table-column prop="jiaoxueshipinTime" label="上课时间" min-width="180" />
        </el-table>
      </section>
    </div>

    <div v-else class="panel-grid">
      <section class="admin-panel">
        <div class="panel-header">
          <h2>最新课程</h2>
        </div>
        <el-table :data="courses" stripe empty-text="暂无课程">
          <el-table-column prop="kechengName" label="课程标题" min-width="220" />
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
            <span>{{ notice.insertTime?.slice(0, 10) || "待更新" }}</span>
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
  DashboardCard,
  HomeworkSubmissionItem,
  LessonMaterialItem,
  NoticeItem
} from "@shared/index";
import {
  fetchAdminCourses,
  fetchAdminNotices,
  fetchHomeworks,
  fetchHomeworkSubmissionPage,
  fetchMaterials,
  fetchStudents,
  fetchTeachers
} from "@/api/dashboard";
import { useAdminSessionStore } from "@/stores/session";

const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");
const loading = ref(false);

const courses = ref<CourseItem[]>([]);
const notices = ref<NoticeItem[]>([]);
const teacherCourses = ref<CourseItem[]>([]);
const teacherMaterials = ref<LessonMaterialItem[]>([]);
const teacherSubmissionRows = ref<HomeworkSubmissionItem[]>([]);

const adminSummary = reactive({
  courses: 0,
  notices: 0,
  students: 0,
  teachers: 0,
  submissions: 0
});

const teacherSummary = reactive({
  homeworks: 0,
  materials: 0,
  submissions: 0,
  pending: 0,
  rejected: 0,
  averageScore: 0
});

const reportFilters = reactive({
  zuoyeName: "",
  submitStatus: ""
});

const cards = computed<DashboardCard[]>(() => {
  if (isTeacher.value) {
    return [
      { label: "我的作业", value: teacherSummary.homeworks, hint: "当前教师名下作业数量" },
      { label: "待批改", value: teacherSummary.pending, hint: "提交后仍未完成批改" },
      { label: "需重交", value: teacherSummary.rejected, hint: "已退回重交的提交记录" },
      { label: "平均分", value: Number(teacherSummary.averageScore.toFixed(1)), hint: "已批改提交的平均得分" }
    ];
  }
  return [
    { label: "课程记录", value: adminSummary.courses, hint: "来自 /kecheng/page" },
    { label: "公告记录", value: adminSummary.notices, hint: "来自 /news/page" },
    { label: "学生数量", value: adminSummary.students, hint: "来自 /yonghu/page" },
    { label: "教师数量", value: adminSummary.teachers, hint: "来自 /jiaoshi/page" },
    { label: "提交记录", value: adminSummary.submissions, hint: "来自 /zuoyeSubmit/page" }
  ];
});

const teacherReports = computed<DashboardCard[]>(() => [
  { label: "提交总量", value: teacherSummary.submissions, hint: "教师名下全部提交记录" },
  { label: "备课资料", value: teacherSummary.materials, hint: "教师名下备课信息数量" },
  { label: "已批改", value: teacherSummary.submissions - teacherSummary.pending - teacherSummary.rejected, hint: "已完成评分或反馈的提交" }
]);

async function loadAdminDashboard() {
  const [coursePage, noticePage, studentPage, teacherPage, submissionPage] = await Promise.all([
    fetchAdminCourses({ limit: 5 }),
    fetchAdminNotices({ limit: 5 }),
    fetchStudents({ limit: 1 }),
    fetchTeachers({ limit: 1 }),
    fetchHomeworkSubmissionPage({ limit: 1 })
  ]);
  courses.value = coursePage.list;
  notices.value = noticePage.list;
  adminSummary.courses = coursePage.totalCount;
  adminSummary.notices = noticePage.totalCount;
  adminSummary.students = studentPage.totalCount;
  adminSummary.teachers = teacherPage.totalCount;
  adminSummary.submissions = submissionPage.totalCount;
}

async function loadTeacherDashboard() {
  const [coursePage, homeworkPage, materialPage, submissionPage] = await Promise.all([
    fetchAdminCourses({ limit: 5 }),
    fetchHomeworks({ limit: 5 }),
    fetchMaterials({ limit: 5 }),
    fetchHomeworkSubmissionPage({
      limit: 20,
      zuoyeName: reportFilters.zuoyeName || undefined,
      submitStatus: reportFilters.submitStatus || undefined
    })
  ]);

  const reviewedScores = submissionPage.list
    .map((item) => item.submitScore)
    .filter((value): value is number => typeof value === "number");

  teacherCourses.value = coursePage.list;
  teacherMaterials.value = materialPage.list;
  teacherSubmissionRows.value = submissionPage.list;
  teacherSummary.homeworks = homeworkPage.totalCount;
  teacherSummary.materials = materialPage.totalCount;
  teacherSummary.submissions = submissionPage.totalCount;
  teacherSummary.pending = submissionPage.list.filter((item) => item.submitStatus === "待批改").length;
  teacherSummary.rejected = submissionPage.list.filter((item) => item.submitStatus === "需重交").length;
  teacherSummary.averageScore =
    reviewedScores.length > 0
      ? reviewedScores.reduce((sum, value) => sum + value, 0) / reviewedScores.length
      : 0;

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
