<template>
  <div class="shell">
    <div class="topline">
      <span>课程、作业、考试、论坛与备课资源统一呈现</span>
      <RouterLink class="topline__link" to="/courses">查看课程中心</RouterLink>
    </div>

    <header class="topbar">
      <BrandMark />
      <nav class="topbar__nav">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/courses">课程</RouterLink>
        <RouterLink to="/my-courses">我的课程</RouterLink>
        <RouterLink to="/homeworks">作业</RouterLink>
        <RouterLink to="/exams">考试</RouterLink>
        <RouterLink to="/my-scores">我的成绩</RouterLink>
        <RouterLink to="/notices">公告</RouterLink>
        <RouterLink to="/forum">论坛</RouterLink>
        <RouterLink to="/materials">备课</RouterLink>
        <RouterLink to="/meetings">会议</RouterLink>
        <RouterLink to="/center">个人中心</RouterLink>
      </nav>
      <div class="topbar__actions">
        <template v-if="session.isLoggedIn">
          <RouterLink class="ai-entry" :to="aiLink">问AI</RouterLink>
          <span class="tag">{{ session.displayRole }}</span>
          <button class="ghost-button" @click="session.logout">退出登录</button>
        </template>
        <RouterLink v-else class="primary-button primary-button--compact" to="/login">登录</RouterLink>
      </div>
    </header>

    <main class="main-shell">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import BrandMark from "@/components/BrandMark.vue";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const route = useRoute();

const aiLink = computed(() => {
  const query: Record<string, string | number> = {
    bizScene: route.name === "course-detail" ? "course_learning" : "system_nav",
    pageCode: String(route.name ?? "public")
  };
  if (route.name === "course-detail" && route.params.id) {
    query.courseId = Number(route.params.id);
  }
  return { name: "ai-chat", query };
});
</script>

<style scoped>
.ai-entry {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 94px;
  padding: 0.7rem 1.15rem;
  border-radius: 999px;
  color: #fff;
  text-decoration: none;
  font-weight: 700;
  letter-spacing: 0.04em;
  background: linear-gradient(135deg, #ff7b38, #ff4f88, #f03f6b);
  box-shadow: 0 14px 30px rgba(240, 63, 107, 0.28);
  animation: aiPulse 2.2s ease-in-out infinite;
}

.ai-entry::before {
  content: "✦";
  margin-right: 0.4rem;
  font-size: 0.9rem;
}

@keyframes aiPulse {
  0%,
  100% {
    transform: translateY(0);
    box-shadow: 0 14px 30px rgba(240, 63, 107, 0.28);
  }
  50% {
    transform: translateY(-1px);
    box-shadow: 0 18px 38px rgba(240, 63, 107, 0.36);
  }
}
</style>
