<template>
  <section class="login-screen">
    <form class="login-panel" @submit.prevent="submit">
      <p class="eyebrow">统一登录入口</p>
      <h1>用一套登录流承接学生、教师和管理员。</h1>
      <p class="login-panel__hint">
        后端继续使用 `/users`、`/jiaoshi`、`/yonghu` 三套登录接口，新前端只重做交互与状态管理。
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

      <p class="field-help">登录成功后会自动按原系统角色加载对应会话。</p>
      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      <button class="primary-button primary-button--full" :disabled="session.pending">
        {{ session.pending ? "登录中..." : "进入新版前端" }}
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
