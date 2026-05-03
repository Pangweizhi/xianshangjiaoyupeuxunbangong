<template>
  <div class="admin-login">
    <form class="admin-login__panel" @submit.prevent="submit">
      <p class="admin-kicker">后台登录</p>
      <h1>进入教学管理工作台</h1>
      <el-select v-model="tableName" size="large">
        <el-option label="管理员后台" value="users" />
        <el-option label="教师工作台" value="jiaoshi" />
      </el-select>
      <el-input v-model="username" :placeholder="tableName === 'users' ? '管理员账号' : '教师账号'" size="large" />
      <el-input
        v-model="password"
        type="password"
        :placeholder="tableName === 'users' ? '管理员密码' : '教师密码'"
        size="large"
        show-password
      />
      <el-alert
        v-if="errorMessage"
        :closable="false"
        type="error"
        :title="errorMessage"
      />
      <el-button
        class="admin-login__button"
        type="primary"
        native-type="submit"
        :loading="store.pending"
      >
        进入后台
      </el-button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import type { UserTable } from "@shared/index";
import { useAdminSessionStore } from "@/stores/session";

const router = useRouter();
const store = useAdminSessionStore();
const tableName = ref<UserTable>("users");
const username = ref("");
const password = ref("");
const errorMessage = ref("");

async function submit() {
  errorMessage.value = "";
  if (!username.value.trim()) {
    errorMessage.value = tableName.value === "users" ? "请输入管理员账号" : "请输入教师账号";
    ElMessage.error(errorMessage.value);
    return;
  }
  if (!password.value.trim()) {
    errorMessage.value = tableName.value === "users" ? "请输入管理员密码" : "请输入教师密码";
    ElMessage.error(errorMessage.value);
    return;
  }
  try {
    await store.login(username.value, password.value, tableName.value);
    await router.push("/dashboard");
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "登录失败，请稍后重试";
  }
}
</script>
