<template>
  <section class="section section--tight">
    <div class="profile-shell">
      <aside class="profile-card">
        <p class="eyebrow">个人中心</p>
        <h1>{{ profileName }}</h1>
        <p>{{ session.displayRole }}</p>
        <div class="profile-card__meta">
          <span>用户 ID {{ session.session?.userId || "-" }}</span>
          <span>身份表 {{ session.session?.tableName || "-" }}</span>
          <span>账号 {{ session.session?.username || "-" }}</span>
        </div>
      </aside>

      <section class="profile-panel">
        <h2>学习路径</h2>
        <div class="mini-list">
          <RouterLink class="mini-list__row" to="/my-courses">
            <div>
              <strong>我的课程</strong>
              <p>从课程详情继续查看章节和学习资源。</p>
            </div>
          </RouterLink>
          <RouterLink class="mini-list__row" to="/homeworks">
            <div>
              <strong>作业</strong>
              <p>作业按课程组织，进入后再选择具体任务。</p>
            </div>
          </RouterLink>
          <RouterLink class="mini-list__row" to="/exams">
            <div>
              <strong>考试</strong>
              <p>考试与成绩统一在这里查看。</p>
            </div>
          </RouterLink>
        </div>

        <h2 class="profile-panel__subhead">公共入口</h2>
        <div class="mini-list">
          <RouterLink class="mini-list__row" to="/courses">
            <div>
              <strong>课程中心</strong>
              <p>浏览全部课程与授课安排。</p>
            </div>
          </RouterLink>
          <RouterLink class="mini-list__row" to="/forum">
            <div>
              <strong>论坛交流</strong>
              <p>查看帖子、回复问题和参与讨论。</p>
            </div>
          </RouterLink>
          <RouterLink class="mini-list__row" to="/notices">
            <div>
              <strong>公告通知</strong>
              <p>掌握近期教学与办公信息。</p>
            </div>
          </RouterLink>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const profile = ref<Record<string, unknown> | null>(null);

const profileName = computed(() => {
  const current = profile.value;
  return (
    (typeof current?.yonghuName === "string" && current.yonghuName) ||
    (typeof current?.jiaoshiName === "string" && current.jiaoshiName) ||
    (typeof current?.username === "string" && current.username) ||
    session.session?.username ||
    "未命名用户"
  );
});

onMounted(async () => {
  profile.value = await session.hydrateProfile();
});
</script>

<style scoped>
.profile-panel__subhead {
  margin-top: 22px;
}
</style>
