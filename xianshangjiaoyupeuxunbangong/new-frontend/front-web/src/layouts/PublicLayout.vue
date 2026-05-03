<template>
  <div class="shell">
    <header class="topbar topbar--shell">
      <div class="nav-shell">
        <div class="nav-shell__left">
          <BrandMark />
          <section class="nav-group">
            <div class="nav-group__row nav-group__row--left">
              <span class="nav-group__label">公共服务</span>
              <nav class="topbar__nav topbar__nav--left">
                <RouterLink to="/">首页</RouterLink>
                <RouterLink to="/courses">课程</RouterLink>
                <RouterLink to="/notices">公告</RouterLink>
                <RouterLink to="/forum">论坛</RouterLink>
                <RouterLink to="/materials">备课</RouterLink>
              </nav>
            </div>
          </section>
        </div>

        <div class="nav-shell__right">
          <div class="topbar__actions">
            <template v-if="session.isLoggedIn">
              <RouterLink class="ai-entry" :to="aiLink">问AI</RouterLink>
              <span class="tag">{{ session.displayRole }}</span>
              <button class="ghost-button" @click="handleLogout">退出登录</button>
            </template>
            <RouterLink v-else class="primary-button primary-button--compact" to="/login">登录</RouterLink>
          </div>

          <section class="nav-group nav-group--right">
            <div class="nav-group__row nav-group__row--right">
              <span class="nav-group__label">我的学习</span>
              <nav class="topbar__nav topbar__nav--right">
                <RouterLink to="/my-courses">我的课程</RouterLink>
                <RouterLink to="/homeworks">作业</RouterLink>
                <RouterLink to="/exams">考试</RouterLink>
                <RouterLink to="/meetings">会议</RouterLink>
                <RouterLink to="/center">个人中心</RouterLink>
              </nav>
            </div>
          </section>
        </div>
      </div>
    </header>

    <main class="main-shell">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";
import BrandMark from "@/components/BrandMark.vue";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const route = useRoute();
const router = useRouter();

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

function handleLogout() {
  session.logout();
  router.push({ name: "login" });
}
</script>

<style scoped>
.topbar--shell {
  display: block;
  width: 100%;
  padding: 22px 28px;
}

.nav-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: start;
  gap: 28px;
  width: 100%;
  min-width: 0;
}

.nav-shell__left,
.nav-shell__right {
  display: grid;
  gap: 18px;
  min-width: 0;
}

.nav-shell__right {
  justify-items: end;
  text-align: right;
  align-self: start;
  transform: translateY(-6px);
}

.nav-group {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.nav-group__row {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 48px;
}

.nav-group__row--left {
  justify-content: flex-start;
}

.nav-group__row--right {
  justify-content: flex-end;
}

.nav-group--right {
  justify-items: end;
  margin-top: -8px;
}

.nav-group__label {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.14);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: var(--muted);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  line-height: 1;
  white-space: nowrap;
}

.topbar__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
  width: 100%;
}

.topbar__nav {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}

.topbar__nav--left {
  justify-content: flex-start;
  min-height: 48px;
}

.topbar__nav--right {
  justify-content: flex-end;
  margin-left: auto;
  max-width: 100%;
  min-height: 48px;
}

.topbar__nav a {
  padding: 10px 14px;
  border-radius: 999px;
  color: var(--muted-strong);
  white-space: nowrap;
  transition:
    transform 0.2s ease,
    color 0.2s ease,
    background 0.2s ease;
}

.topbar__nav a:hover,
.topbar__nav a:focus-visible {
  color: var(--text);
  background: rgba(255, 122, 26, 0.12);
  transform: translateY(-1px);
}

.ai-entry {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 82px;
  min-height: 42px;
  padding: 0.58rem 1rem;
  border-radius: 999px;
  color: #fff;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.92rem;
  letter-spacing: 0.03em;
  white-space: nowrap;
  background: linear-gradient(135deg, #ff7b38, #ff4f88, #f03f6b);
  box-shadow: 0 14px 30px rgba(240, 63, 107, 0.28);
  animation: aiPulse 2.2s ease-in-out infinite;
}

.ai-entry::before {
  content: "AI";
  margin-right: 0.4rem;
  font-size: 0.72rem;
}

.topbar__actions .ghost-button {
  min-height: 42px;
  padding: 0 16px;
  font-size: 0.92rem;
}

.topbar__actions .tag {
  min-height: 38px;
  padding: 6px 11px;
  font-size: 0.82rem;
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

@media (max-width: 1120px) {
  .nav-shell {
    grid-template-columns: 1fr;
  }

  .nav-shell__right {
    justify-items: stretch;
    text-align: left;
    transform: none;
  }

  .nav-group--right {
    justify-items: stretch;
    margin-top: 0;
  }

  .nav-group__row,
  .topbar__actions,
  .topbar__nav--right {
    justify-content: flex-start;
    margin-left: 0;
  }
}

@media (max-width: 720px) {
  .topbar--shell {
    padding: 20px;
  }

  .topbar__actions,
  .nav-group__row,
  .topbar__nav {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
