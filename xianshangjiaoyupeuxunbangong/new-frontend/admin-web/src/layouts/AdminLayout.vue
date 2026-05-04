<template>
  <div class="admin-shell">
    <aside class="admin-aside">
      <div class="admin-brand">
        <strong>知行学堂后台</strong>
        <span>{{ isTeacher ? "教师工作台" : "平台管理台" }}</span>
      </div>

      <RouterLink to="/dashboard">仪表盘</RouterLink>
      <RouterLink to="/profile">个人中心</RouterLink>

      <div class="admin-nav-group">
        <span class="admin-nav-group__label">课程管理</span>
        <RouterLink to="/courses">课程管理</RouterLink>
        <RouterLink class="admin-subnav__link" to="/course-types">课程类型管理</RouterLink>
      </div>

      <RouterLink v-if="isTeacher" to="/chapters">章节与资源</RouterLink>
      <RouterLink to="/enrolls">选课管理</RouterLink>
      <RouterLink to="/progress">学习进度</RouterLink>

      <div class="admin-nav-group">
        <span class="admin-nav-group__label">作业管理</span>
        <RouterLink to="/homeworks">作业管理</RouterLink>
        <RouterLink class="admin-subnav__link" to="/homework-types">作业类型管理</RouterLink>
      </div>

      <RouterLink to="/exams">考试管理</RouterLink>
      <RouterLink to="/exam-questions">题库管理</RouterLink>
      <RouterLink to="/exam-records">阅卷管理</RouterLink>
      <RouterLink to="/submissions">作业提交记录</RouterLink>
      <RouterLink v-if="!isTeacher" to="/notices">公告管理</RouterLink>
      <RouterLink to="/forums">论坛管理</RouterLink>
      <RouterLink to="/materials">备课管理</RouterLink>
      <RouterLink to="/meetings">会议管理</RouterLink>
      <RouterLink v-if="!isTeacher" to="/students">学生管理</RouterLink>
      <RouterLink v-if="!isTeacher" to="/teachers">教师管理</RouterLink>
      <RouterLink v-if="!isTeacher" to="/dictionary">字典管理</RouterLink>

      <div v-if="!isTeacher" class="admin-nav-group admin-nav-group--config">
        <span class="admin-nav-group__label">系统配置</span>
        <RouterLink class="admin-subnav__link" to="/config">轮播图管理</RouterLink>
      </div>
    </aside>

    <div class="admin-main">
      <header class="admin-header">
        <div>
          <h1>{{ title }}</h1>
          <p>{{ store.displayRole }}</p>
        </div>
        <div class="admin-header__actions">
          <el-button plain @click="handleLogout">退出登录</el-button>
        </div>
      </header>

      <section class="admin-content">
        <RouterView :key="route.fullPath" />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";
import { useAdminSessionStore } from "@/stores/session";

const route = useRoute();
const router = useRouter();
const store = useAdminSessionStore();

const isTeacher = computed(() => store.session?.tableName === "jiaoshi");

const title = computed(() => {
  const titleMap: Record<string, string> = {
    dashboard: "仪表盘",
    profile: "个人中心",
    courses: "课程管理",
    "course-types": "课程类型管理",
    chapters: "章节与资源",
    resources: "资源管理",
    enrolls: "选课管理",
    progress: "学习进度",
    homeworks: "作业管理",
    "homework-types": "作业类型管理",
    exams: "考试管理",
    "exam-questions": "题库管理",
    "exam-records": "阅卷管理",
    submissions: "作业提交记录",
    notices: "公告管理",
    students: "学生管理",
    teachers: "教师管理",
    dictionary: "字典管理",
    config: "轮播图管理",
    forums: "论坛管理",
    materials: "备课管理",
    meetings: "会议管理",
  };
  return titleMap[String(route.name ?? "dashboard")] || "仪表盘";
});

function handleLogout() {
  store.logout();
  router.push({ name: "login" });
}
</script>

<style scoped>
.admin-header__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.admin-nav-group {
  margin-top: 8px;
  display: grid;
  gap: 8px;
  padding-top: 10px;
  border-top: 1px solid rgba(111, 60, 11, 0.12);
}

.admin-nav-group__label,
.admin-subnav__label {
  padding: 10px 14px 2px;
  color: rgba(90, 47, 8, 0.66);
  font-size: 0.85rem;
}

.admin-subnav__link {
  margin-left: 12px;
}

.admin-nav-group--config {
  margin-top: 10px;
}
</style>
