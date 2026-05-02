import {
  DEFAULT_BASE_URL,
  createHttpClient
} from "@shared/index";
import { useSessionStore } from "@/stores/session";

export function useHttp() {
  const store = useSessionStore();
  return createHttpClient({
    baseURL: DEFAULT_BASE_URL,
    getToken: () => store.session?.token ?? null,
    onUnauthorized: () => store.logout()
  });
}
