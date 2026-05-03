<template>
  <div class="admin-shell">
    <aside class="admin-aside">
      <div class="admin-brand">
        <strong>教学管理中心</strong>
        <span>{{ isTeacher ? "教师工作台" : "平台管理台" }}</span>
      </div>

      <RouterLink to="/dashboard">仪表盘</RouterLink>
      <RouterLink to="/courses">课程管理</RouterLink>
      <RouterLink v-if="isTeacher" to="/chapters">章节与资源</RouterLink>
      <RouterLink to="/enrolls">选课管理</RouterLink>
      <RouterLink to="/progress">学习进度</RouterLink>
      <RouterLink to="/homeworks">作业管理</RouterLink>
      <RouterLink to="/exams">考试管理</RouterLink>
      <RouterLink to="/exam-questions">题库管理</RouterLink>
      <RouterLink to="/exam-records">阅卷管理</RouterLink>
      <RouterLink to="/submissions">提交记录</RouterLink>
      <RouterLink v-if="!isTeacher" to="/notices">公告管理</RouterLink>
      <RouterLink to="/forums">论坛管理</RouterLink>
      <RouterLink to="/materials">备课管理</RouterLink>
      <RouterLink to="/meetings">会议管理</RouterLink>
      <RouterLink :to="aiLink">智能问答</RouterLink>
      <RouterLink v-if="!isTeacher" to="/students">学生管理</RouterLink>
      <RouterLink v-if="!isTeacher" to="/teachers">教师管理</RouterLink>
      <RouterLink v-if="!isTeacher" to="/dictionary">字典管理</RouterLink>

      <div v-if="!isTeacher" class="admin-subnav">
        <span class="admin-subnav__label">系统配置</span>
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
          <RouterLink class="admin-ai-entry" :to="aiLink">问 AI</RouterLink>
          <el-button plain @click="handleLogout">退出登录</el-button>
        </div>
      </header>
      <section class="admin-content">
        <RouterView />
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
const aiLink = computed(() => ({
  name: "ai-chat",
  query: {
    bizScene: "course_manage",
    pageCode: String(route.name ?? "admin")
  }
}));

const title = computed(() => {
  switch (route.name) {
    case "courses":
      return "课程管理";
    case "chapters":
      return "章节与资源";
    case "enrolls":
      return "选课管理";
    case "progress":
      return "学习进度";
    case "homeworks":
      return "作业管理";
    case "exams":
      return "考试管理";
    case "exam-questions":
      return "题库管理";
    case "exam-records":
      return "阅卷管理";
    case "submissions":
      return "提交记录";
    case "notices":
      return "公告管理";
    case "students":
      return "学生管理";
    case "teachers":
      return "教师管理";
    case "dictionary":
      return "字典管理";
    case "config":
      return "轮播图管理";
    case "forums":
      return "论坛管理";
    case "materials":
      return "备课管理";
    case "meetings":
      return "会议管理";
    case "ai-chat":
      return "智能问答助手";
    default:
      return "仪表盘";
  }
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

.admin-ai-entry {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 86px;
  padding: 0.68rem 1rem;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #fb6a3d, #eb3b5a);
  box-shadow: 0 12px 28px rgba(235, 59, 90, 0.24);
}

.admin-subnav {
  margin-top: 10px;
  display: grid;
  gap: 8px;
}

.admin-subnav__label {
  padding: 10px 14px 2px;
  color: rgba(237, 242, 255, 0.72);
  font-size: 0.85rem;
}

.admin-subnav__link {
  margin-left: 12px;
}
</style>
