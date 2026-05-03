import type { AuthSession, UserTable } from "./types";

const DEFAULT_CONTEXT_PATH = "/xianshangjiaoyupeuxunbangong";

function normalizeBaseUrl(baseUrl: string) {
  const trimmed = baseUrl.replace(/\/$/, "");
  if (trimmed.endsWith(DEFAULT_CONTEXT_PATH)) {
    return trimmed;
  }
  return `${trimmed}${DEFAULT_CONTEXT_PATH}`;
}

function resolveBaseUrl() {
  const envValue =
    typeof import.meta !== "undefined" &&
    (import.meta as { env?: Record<string, string | undefined> }).env
      ? (import.meta as { env?: Record<string, string | undefined> }).env?.VITE_API_BASE_URL
      : undefined;

  if (envValue) {
    return normalizeBaseUrl(envValue);
  }

  if (typeof window !== "undefined" && window.location?.origin) {
    return normalizeBaseUrl(window.location.origin);
  }

  return normalizeBaseUrl("http://localhost:8080");
}

export const DEFAULT_BASE_URL = resolveBaseUrl();

export const loginEndpointMap: Record<UserTable, string> = {
  users: "/users/login",
  jiaoshi: "/jiaoshi/login",
  yonghu: "/yonghu/login"
};

export const sessionEndpointMap: Record<UserTable, string> = {
  users: "/users/session",
  jiaoshi: "/jiaoshi/session",
  yonghu: "/yonghu/session"
};

export const roleLabels: Record<UserTable, string> = {
  users: "管理员",
  jiaoshi: "教师",
  yonghu: "学生"
};

export function readSession(storageKey: string): AuthSession | null {
  const raw = localStorage.getItem(storageKey);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    localStorage.removeItem(storageKey);
    return null;
  }
}

export function writeSession(storageKey: string, session: AuthSession | null) {
  if (!session) {
    localStorage.removeItem(storageKey);
    return;
  }
  localStorage.setItem(storageKey, JSON.stringify(session));
}

export function createAssetUrl(baseUrl: string, path?: string | null) {
  if (!path) {
    return "";
  }
  const normalizedPath = path.replace(/\\/g, "/");
  if (/^https?:\/\//.test(normalizedPath)) {
    return encodeURI(normalizedPath);
  }
  if (normalizedPath.startsWith("/")) {
    return encodeURI(`${baseUrl}${normalizedPath}`);
  }
  if (!normalizedPath.includes("/")) {
    return `${baseUrl}/file/download?fileName=${encodeURIComponent(normalizedPath)}`;
  }
  return encodeURI(`${baseUrl}/${normalizedPath}`);
}

export function createDownloadUrl(baseUrl: string, fileName?: string | null) {
  if (!fileName) {
    return "";
  }
  const normalized = fileName.replace(/\\/g, "/");
  const value = normalized.startsWith("/") ? normalized.slice(1) : normalized;
  if (value.includes("/")) {
    return encodeURI(`${baseUrl}/${value}`);
  }
  return `${baseUrl}/file/download?fileName=${encodeURIComponent(value)}`;
}
