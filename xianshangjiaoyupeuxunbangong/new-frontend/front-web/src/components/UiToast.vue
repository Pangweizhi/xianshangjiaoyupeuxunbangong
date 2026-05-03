<template>
  <transition name="ui-toast">
    <div v-if="uiToastState.visible" class="ui-toast" :class="`ui-toast--${uiToastState.tone}`">
      <span>{{ uiToastState.message }}</span>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { uiToastState } from "@/composables/uiToast";
</script>

<style scoped>
.ui-toast {
  position: fixed;
  top: 72px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 60;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 220px;
  max-width: min(420px, calc(100vw - 36px));
  padding: 14px 18px;
  border-radius: 18px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 18px 42px rgba(31, 41, 55, 0.16);
  backdrop-filter: blur(14px);
  text-align: center;
}

.ui-toast--success {
  background: rgba(216, 244, 223, 0.96);
  color: #1a4a2b;
}

.ui-toast--error {
  background: rgba(255, 241, 239, 0.96);
  color: #8f2d1f;
}

.ui-toast-enter-active,
.ui-toast-leave-active {
  transition: opacity 0.28s ease, transform 0.28s ease;
}

.ui-toast-enter-from,
.ui-toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}
</style>
