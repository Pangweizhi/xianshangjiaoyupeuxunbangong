<template>
  <section class="login-screen">
    <div class="login-backdrop"></div>
    <form class="login-panel" @submit.prevent="submit">
      <p class="eyebrow">统一登录</p>
      <h1>选择身份后进入对应学习空间</h1>
      <p class="login-panel__hint">
        支持学生、教师和管理员三类身份登录，登录后可直接进入个人中心与业务页面。
      </p>

      <label class="field-group">
        <span>登录身份</span>
        <select v-model="form.tableName" class="field">
          <option value="yonghu">学生</option>
          <option value="jiaoshi">教师</option>
          <option value="users">管理员</option>
        </select>
      </label>

      <label class="field-group">
        <span>账号</span>
        <input v-model="form.username" class="field" placeholder="请输入账号" />
      </label>

      <label class="field-group">
        <span>密码</span>
        <input
          v-model="form.password"
          class="field"
          type="password"
          placeholder="请输入密码"
        />
      </label>

      <p class="field-help">登录成功后将自动跳转到个人中心。</p>
      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      <button class="primary-button primary-button--full" :disabled="session.pending">
        {{ session.pending ? "登录中..." : "进入系统" }}
      </button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { UserTable } from "@shared/index";
import { useSessionStore } from "@/stores/session";

const router = useRouter();
const route = useRoute();
const session = useSessionStore();
const errorMessage = ref("");

const form = reactive<{
  tableName: UserTable;
  username: string;
  password: string;
}>({
  tableName: "yonghu",
  username: "",
  password: ""
});

async function submit() {
  errorMessage.value = "";
  if (!form.username.trim()) {
    errorMessage.value = "请输入账号";
    return;
  }
  if (!form.password.trim()) {
    errorMessage.value = "请输入密码";
    return;
  }
  try {
    await session.login({
      tableName: form.tableName,
      username: form.username.trim(),
      password: form.password
    });
    await router.push(String(route.query.redirect || "/center"));
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "登录失败，请稍后重试";
  }
}
</script>
