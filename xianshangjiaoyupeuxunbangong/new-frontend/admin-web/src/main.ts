import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import App from "./App.vue";
import router from "./router";
import "./styles/admin.css";
import { useAdminSessionStore } from "@/stores/session";

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();
  app.use(pinia).use(router).use(ElementPlus);
  const store = useAdminSessionStore(pinia);
  await store.ensureSessionValid();
  await router.isReady();
  app.mount("#app");
}

bootstrap();
