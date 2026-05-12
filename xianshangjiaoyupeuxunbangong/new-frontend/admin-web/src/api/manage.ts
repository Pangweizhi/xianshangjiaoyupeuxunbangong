import axios from "axios";
import { DEFAULT_BASE_URL } from "@shared/index";
import { useAdminHttp } from "./client";
import { useAdminSessionStore } from "@/stores/session";

export async function fetchEntityDetail<T>(module: string, id: number | string) {
  const http = useAdminHttp();
  const { data } = await http.get(`/${module}/info/${id}`);
  return data.data as T;
}

export async function fetchCurrentEntitySession<T>(module: string) {
  const http = useAdminHttp();
  const { data } = await http.get(`/${module}/session`);
  return data.data as T;
}

export async function saveEntity(module: string, payload: Record<string, unknown>) {
  const http = useAdminHttp();
  const hasId = Boolean(payload.id);
  const { data } = await http.post(`/${module}/${hasId ? "update" : "save"}`, payload);
  return data;
}

export async function deleteEntities(module: string, ids: Array<number | string>) {
  const http = useAdminHttp();
  const { data } = await http.post(`/${module}/delete`, ids);
  return data;
}

export async function postModuleAction(module: string, action: string, payload: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.post(`/${module}/${action}`, payload);
  return data;
}

export async function fetchDictionaryOptions(dicCode: string) {
  const http = useAdminHttp();
  const { data } = await http.get("/dictionary/page", {
    params: {
      page: 1,
      limit: 200,
      sort: "code_index",
      order: "asc",
      dicCode
    }
  });
  const list = data?.data?.list;
  return Array.isArray(list) ? (list as Array<{ codeIndex: number; indexName: string }>) : [];
}

export async function fetchTeachersForSelect() {
  const http = useAdminHttp();
  const { data } = await http.get("/jiaoshi/page", {
    params: { page: 1, limit: 200, sort: "id", order: "desc" }
  });
  const list = data?.data?.list;
  return Array.isArray(list) ? (list as Array<{ id: number; jiaoshiName: string }>) : [];
}

export async function fetchStudentsForSelect() {
  const http = useAdminHttp();
  const { data } = await http.get("/yonghu/page", {
    params: { page: 1, limit: 200, sort: "id", order: "desc" }
  });
  const list = data?.data?.list;
  return Array.isArray(list) ? (list as Array<{ id: number; yonghuName: string }>) : [];
}

export async function fetchCoursesForSelect() {
  const http = useAdminHttp();
  const { data } = await http.get("/kecheng/page", {
    params: { page: 1, limit: 200, sort: "id", order: "desc" }
  });
  const list = data?.data?.list;
  return Array.isArray(list) ? (list as Array<{ id: number; kechengName: string }>) : [];
}

export async function fetchCourseChaptersForSelect(kechengId?: number | string) {
  const http = useAdminHttp();
  const { data } = await http.get("/courseChapter/page", {
    params: { page: 1, limit: 200, sort: "id", order: "desc", kechengId: kechengId || undefined }
  });
  const list = data?.data?.list;
  return Array.isArray(list) ? (list as Array<{ id: number; chapterName: string; kechengId: number }>) : [];
}

export async function uploadAdminFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const session = useAdminSessionStore();
  const { data } = await axios.post(`${DEFAULT_BASE_URL}/file/upload`, formData, {
    headers: session.session?.token ? { Token: session.session.token } : undefined,
    withCredentials: true
  });
  return data.file as string;
}
