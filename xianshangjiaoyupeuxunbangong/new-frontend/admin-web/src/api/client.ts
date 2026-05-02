import { DEFAULT_BASE_URL, createHttpClient } from "@shared/index";
import { useAdminSessionStore } from "@/stores/session";

export function useAdminHttp() {
  const store = useAdminSessionStore();
  return createHttpClient({
    baseURL: DEFAULT_BASE_URL,
    getToken: () => store.session?.token ?? null,
    onUnauthorized: () => store.logout()
  });
}
