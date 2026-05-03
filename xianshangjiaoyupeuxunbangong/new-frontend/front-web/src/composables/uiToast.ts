import { reactive } from "vue";

type ToastTone = "success" | "error";

export const uiToastState = reactive({
  visible: false,
  tone: "success" as ToastTone,
  message: ""
});

let timer: number | undefined;

export function showUiToast(message: string, tone: ToastTone = "success") {
  uiToastState.message = message;
  uiToastState.tone = tone;
  uiToastState.visible = true;
  if (timer) {
    window.clearTimeout(timer);
  }
  timer = window.setTimeout(() => {
    uiToastState.visible = false;
  }, 2600);
}

export function hideUiToast() {
  uiToastState.visible = false;
  if (timer) {
    window.clearTimeout(timer);
  }
}
