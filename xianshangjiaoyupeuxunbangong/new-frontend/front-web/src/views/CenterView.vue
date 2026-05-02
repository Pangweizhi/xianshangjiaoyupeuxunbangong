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
        <h2>常用入口</h2>
        <div class="mini-list">
          <RouterLink class="mini-list__row" to="/courses">
            <div>
              <strong>课程中心</strong>
              <p>查看课程与授课安排</p>
            </div>
          </RouterLink>
          <RouterLink class="mini-list__row" to="/my-courses">
            <div>
              <strong>我的课程</strong>
              <p>查看选课进度与学分发放</p>
            </div>
          </RouterLink>
          <RouterLink class="mini-list__row" to="/homeworks">
            <div>
              <strong>作业中心</strong>
              <p>进入作业详情与提交记录</p>
            </div>
          </RouterLink>
          <RouterLink class="mini-list__row" to="/forum">
            <div>
              <strong>论坛交流</strong>
              <p>查看帖子、发布回复与参与讨论</p>
            </div>
          </RouterLink>
          <RouterLink class="mini-list__row" to="/notices">
            <div>
              <strong>公告通知</strong>
              <p>掌握近期教学与办公信息</p>
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
