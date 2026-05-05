import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./styles/base.css";
import { useSessionStore } from "@/stores/session";

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();
  app.use(pinia).use(router);
  const session = useSessionStore(pinia);
  await session.ensureSessionValid();
  await router.isReady();
  app.mount("#app");
}

bootstrap();
