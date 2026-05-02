import axios from "axios";
import { DEFAULT_BASE_URL } from "@shared/index";
import { useAdminHttp } from "./client";
import { useAdminSessionStore } from "@/stores/session";

export async function fetchEntityDetail<T>(module: string, id: number | string) {
  const http = useAdminHttp();
  const { data } = await http.get(`/${module}/info/${id}`);
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
  return data.data.list as Array<{ codeIndex: number; indexName: string }>;
}

export async function fetchTeachersForSelect() {
  const http = useAdminHttp();
  const { data } = await http.get("/jiaoshi/page", {
    params: { page: 1, limit: 200, sort: "id", order: "desc" }
  });
  return data.data.list as Array<{ id: number; jiaoshiName: string }>;
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
