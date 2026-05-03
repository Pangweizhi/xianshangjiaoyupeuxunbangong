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
    const { origin } = window.location;
    return normalizeBaseUrl(origin);
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
    return normalizedPath;
  }
  if (normalizedPath.startsWith("/")) {
    return `${baseUrl}${normalizedPath}`;
  }
  if (!normalizedPath.includes("/")) {
    return `${baseUrl}/upload/${normalizedPath}`;
  }
  return `${baseUrl}/${normalizedPath}`;
}

export function createDownloadUrl(baseUrl: string, fileName?: string | null) {
  if (!fileName) {
    return "";
  }
  const value = fileName.replace(/\\/g, "/").startsWith("/")
    ? fileName.replace(/\\/g, "/").slice(1)
    : fileName.replace(/\\/g, "/");
  if (value.includes("/")) {
    return `${baseUrl}/${value}`;
  }
  return `${baseUrl}/file/download?fileName=${encodeURIComponent(value)}`;
}
