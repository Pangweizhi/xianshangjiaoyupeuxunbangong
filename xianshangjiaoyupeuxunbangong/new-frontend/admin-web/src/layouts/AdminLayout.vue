<template>
  <div class="admin-shell">
    <aside class="admin-aside">
      <div class="admin-brand">
        <strong>Control Room</strong>
        <span>重写后台管理端</span>
      </div>
      <RouterLink to="/dashboard">仪表盘</RouterLink>
      <RouterLink v-if="store.session?.tableName === 'jiaoshi'" to="/submissions">提交记录</RouterLink>
      <RouterLink to="/courses">课程管理</RouterLink>
      <RouterLink v-if="!isTeacher" to="/notices">公告管理</RouterLink>
      <RouterLink to="/homeworks">作业管理</RouterLink>
      <RouterLink to="/forums">论坛管理</RouterLink>
      <RouterLink to="/materials">备课管理</RouterLink>
      <RouterLink to="/meetings">会议管理</RouterLink>
      <RouterLink v-if="!isTeacher" to="/submissions">提交记录</RouterLink>
      <RouterLink v-if="!isTeacher" to="/students">学生管理</RouterLink>
      <RouterLink v-if="!isTeacher" to="/teachers">教师管理</RouterLink>
      <RouterLink v-if="!isTeacher" to="/dictionary">字典管理</RouterLink>
      <RouterLink v-if="!isTeacher" to="/config">系统配置</RouterLink>
    </aside>

    <div class="admin-main">
      <header class="admin-header">
        <div>
          <h1>{{ title }}</h1>
          <p>{{ store.displayRole }} · 基于原 Spring Boot 接口重写</p>
        </div>
        <el-button plain @click="store.logout">退出登录</el-button>
      </header>
      <section class="admin-content">
        <RouterView />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { useAdminSessionStore } from "@/stores/session";

const route = useRoute();
const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");

const title = computed(() => {
  switch (route.name) {
    case "courses":
      return "课程管理";
    case "notices":
      return "公告管理";
    case "students":
      return "学生管理";
    case "teachers":
      return "教师管理";
    case "homeworks":
      return "作业管理";
    case "forums":
      return "论坛管理";
    case "materials":
      return "备课管理";
    case "meetings":
      return "会议管理";
    case "submissions":
      return "提交记录";
    case "dictionary":
      return "字典管理";
    case "config":
      return "系统配置";
    default:
      return "仪表盘";
  }
});
</script>
