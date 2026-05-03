import type {
  AiChatMessageItem,
  AiChatSendResponse,
  AiChatSessionCreateResponse,
  AiChatSessionItem,
  PagePayload
} from "@shared/index";
import { unwrap } from "@shared/index";
import { useAdminHttp } from "./client";

export async function fetchAiSessionPage(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/aiChat/session/page", {
    params: { page: 1, limit: 20, ...params }
  });
  return unwrap<PagePayload<AiChatSessionItem>>(data);
}

export async function createAiSession(payload: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.post("/aiChat/session/create", payload);
  return unwrap<AiChatSessionCreateResponse>(data);
}

export async function fetchAiMessagePage(sessionId: number, params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/aiChat/message/page", {
    params: { sessionId, page: 1, limit: 100, ...params }
  });
  return unwrap<PagePayload<AiChatMessageItem>>(data);
}

export async function sendAiMessage(payload: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.post("/aiChat/message/send", payload);
  return unwrap<AiChatSendResponse>(data);
}

export async function fetchAiRecommendQuestions(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/aiChat/recommendQuestions", { params });
  return unwrap<string[]>(data);
}
