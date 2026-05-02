import axios, { type AxiosInstance } from "axios";
import type { ApiResponse } from "./types";

interface CreateHttpOptions {
  baseURL: string;
  getToken: () => string | null;
  onUnauthorized?: () => void;
}

export function createHttpClient(options: CreateHttpOptions): AxiosInstance {
  const client = axios.create({
    baseURL: options.baseURL,
    timeout: 10000,
    withCredentials: true
  });

  client.interceptors.request.use((config) => {
    const token = options.getToken();
    if (token) {
      config.headers.Token = token;
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => {
      const payload = response.data as ApiResponse<unknown>;
      if (payload?.code === 401) {
        options.onUnauthorized?.();
        return Promise.reject(new Error(payload.msg || "登录状态已失效"));
      }
      if (payload?.code && payload.code !== 0) {
        return Promise.reject(new Error(payload.msg || "请求失败"));
      }
      return response;
    },
    (error) => {
      if (error?.response?.status === 401) {
        options.onUnauthorized?.();
      }
      return Promise.reject(error);
    }
  );

  return client;
}

export function unwrap<T>(payload: ApiResponse<T>): T {
  return payload.data;
}
