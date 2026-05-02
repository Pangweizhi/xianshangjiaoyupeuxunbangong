import type { ApiResponse } from "./types";

interface CreateHttpOptions {
  baseURL: string;
  getToken: () => string | null;
  onUnauthorized?: () => void;
}

interface RequestConfig {
  params?: Record<string, unknown>;
}

export interface SimpleHttpClient {
  get(url: string, config?: RequestConfig): Promise<{ data: any }>;
  post(url: string, body?: unknown, config?: RequestConfig): Promise<{ data: any }>;
}

function buildUrl(baseURL: string, url: string, params?: Record<string, unknown>) {
  const target = new URL(url, baseURL.endsWith("/") ? baseURL : `${baseURL}/`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        target.searchParams.set(key, String(value));
      }
    });
  }
  return target.toString();
}

async function request(
  method: "GET" | "POST",
  options: CreateHttpOptions,
  url: string,
  body?: unknown,
  config?: RequestConfig
) {
  const headers: Record<string, string> = {};
  const token = options.getToken();
  if (token) {
    headers.Token = token;
  }
  if (body !== undefined && body !== null) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(buildUrl(options.baseURL, url, config?.params), {
    method,
    credentials: "include",
    headers,
    body: body === undefined || body === null ? undefined : JSON.stringify(body)
  });
  if (response.status === 401) {
    options.onUnauthorized?.();
    throw new Error("登录状态已失效");
  }
  const payload = (await response.json()) as ApiResponse<unknown>;
  if (payload?.code === 401) {
    options.onUnauthorized?.();
    throw new Error(payload.msg || "登录状态已失效");
  }
  if (payload?.code && payload.code !== 0) {
    throw new Error(payload.msg || "请求失败");
  }
  return { data: payload };
}

export function createHttpClient(options: CreateHttpOptions): SimpleHttpClient {
  return {
    get(url: string, config?: RequestConfig) {
      return request("GET", options, url, undefined, config);
    },
    post(url: string, body?: unknown, config?: RequestConfig) {
      return request("POST", options, url, body, config);
    }
  };
}

export function unwrap<T>(payload: ApiResponse<T>): T {
  return payload.data;
}
