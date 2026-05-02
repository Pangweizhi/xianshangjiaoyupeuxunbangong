import type { AuthSession, UserTable } from "./types";

export const DEFAULT_BASE_URL =
  "http://localhost:8080/xianshangjiaoyupeuxunbangong";

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
  if (/^https?:\/\//.test(path)) {
    return path;
  }
  return `${baseUrl}${path.startsWith("/") ? path : `/${path}`}`;
}

export function createDownloadUrl(baseUrl: string, fileName?: string | null) {
  if (!fileName) {
    return "";
  }
  const value = fileName.startsWith("/") ? fileName.slice(1) : fileName;
  if (value.includes("/")) {
    return `${baseUrl}/${value}`;
  }
  return `${baseUrl}/file/download?fileName=${encodeURIComponent(value)}`;
}
