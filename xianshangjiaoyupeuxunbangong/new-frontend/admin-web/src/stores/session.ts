import { computed, ref } from "vue";
import { defineStore } from "pinia";
import axios from "axios";
import {
  DEFAULT_BASE_URL,
  loginEndpointMap,
  readSession,
  roleLabels,
  sessionEndpointMap,
  writeSession,
  type AuthSession,
  type UserTable
} from "@shared/index";

const STORAGE_KEY = "admin-web-session";

export const useAdminSessionStore = defineStore("admin-session", () => {
  const session = ref<AuthSession | null>(readSession(STORAGE_KEY));
  const pending = ref(false);
  let validationPromise: Promise<boolean> | null = null;

  const isLoggedIn = computed(() => Boolean(session.value?.token));
  const displayRole = computed(() =>
    session.value ? roleLabels[session.value.tableName] : "未登录"
  );

  function setSession(next: AuthSession | null) {
    session.value = next;
    writeSession(STORAGE_KEY, next);
  }

  async function login(username: string, password: string, tableName: UserTable = "users") {
    pending.value = true;
    try {
      const { data } = await axios.post(
        `${DEFAULT_BASE_URL}${loginEndpointMap[tableName]}`,
        null,
        { params: { username, password } }
      );
      if (data.code !== 0) {
        throw new Error(data.msg || "登录失败");
      }
      setSession({
        token: data.token,
        role: data.role,
        userId: data.userId,
        tableName,
        username
      });
    } finally {
      pending.value = false;
    }
  }

  async function ensureSessionValid() {
    if (!session.value) {
      return false;
    }
    if (validationPromise) {
      return validationPromise;
    }
    validationPromise = axios
      .get(`${DEFAULT_BASE_URL}${sessionEndpointMap[session.value.tableName]}`, {
        headers: {
          Token: session.value.token
        }
      })
      .then(() => true)
      .catch(() => {
        setSession(null);
        return false;
      })
      .finally(() => {
        validationPromise = null;
      });
    return validationPromise;
  }

  function logout() {
    setSession(null);
  }

  return {
    session,
    pending,
    isLoggedIn,
    displayRole,
    login,
    ensureSessionValid,
    logout
  };
});
