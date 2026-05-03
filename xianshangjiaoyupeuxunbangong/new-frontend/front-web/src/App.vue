<template>
  <RouterView />
  <UiToast />
</template>

<script setup lang="ts">
import { RouterView } from "vue-router";
import UiToast from "@/components/UiToast.vue";
</script>
