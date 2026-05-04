<template>
  <RouterView />
  <button
    v-show="showBackToTop"
    class="back-to-top"
    type="button"
    aria-label="返回顶部"
    @click="scrollToTop"
  >
    <span>↑</span>
  </button>
  <UiToast />
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { RouterView } from "vue-router";
import UiToast from "@/components/UiToast.vue";

const showBackToTop = ref(false);

function handleScroll() {
  showBackToTop.value = window.scrollY > 420;
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

onMounted(() => {
  handleScroll();
  window.addEventListener("scroll", handleScroll, { passive: true });
});

onBeforeUnmount(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>
