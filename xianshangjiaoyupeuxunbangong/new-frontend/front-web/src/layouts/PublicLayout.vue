<template>
  <div class="shell">
    <header class="topbar">
      <BrandMark />
      <nav class="topbar__nav">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/courses">课程</RouterLink>
        <RouterLink to="/notices">公告</RouterLink>
        <RouterLink to="/homeworks">作业</RouterLink>
        <RouterLink to="/forum">论坛</RouterLink>
        <RouterLink to="/materials">备课</RouterLink>
        <RouterLink to="/meetings">会议</RouterLink>
        <RouterLink to="/center">个人中心</RouterLink>
      </nav>
      <div class="topbar__actions">
        <template v-if="session.isLoggedIn">
          <span class="tag">{{ session.displayRole }}</span>
          <button class="ghost-button" @click="session.logout">退出</button>
        </template>
        <RouterLink v-else class="ghost-button" to="/login">登录</RouterLink>
      </div>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import BrandMark from "@/components/BrandMark.vue";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
</script>
