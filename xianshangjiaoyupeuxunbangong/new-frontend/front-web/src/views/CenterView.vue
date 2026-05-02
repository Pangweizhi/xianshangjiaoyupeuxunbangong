<template>
  <section class="section section--tight">
    <div class="profile-shell">
      <aside class="profile-card">
        <p class="eyebrow">个人中心</p>
        <h1>{{ profile?.username || session.session?.username || "未命名用户" }}</h1>
        <p>{{ session.displayRole }}</p>
        <div class="profile-card__meta">
          <span>用户 ID {{ session.session?.userId }}</span>
          <span>身份表 {{ session.session?.tableName }}</span>
        </div>
      </aside>

      <section class="profile-panel">
        <h2>重写进度</h2>
        <ul class="progress-list">
          <li>登录态与鉴权请求头已统一</li>
          <li>个人中心入口已从旧静态页迁移到 Vue Router</li>
          <li>下一阶段接入资料编辑、作业、论坛与通知汇总</li>
        </ul>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const profile = ref<Record<string, unknown> | null>(null);

onMounted(async () => {
  profile.value = await session.hydrateProfile();
});
</script>
