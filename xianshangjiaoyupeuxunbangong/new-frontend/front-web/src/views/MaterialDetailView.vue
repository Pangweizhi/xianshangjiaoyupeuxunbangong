<template>
  <section class="section section--tight">
    <RouterLink class="text-link" to="/materials">返回备课列表</RouterLink>
    <div v-if="detail" class="detail-shell">
      <article class="detail-card">
        <img :src="toAsset(detail.jiaoxueshipinPhoto)" :alt="detail.jiaoxueshipinName" />
        <div class="detail-card__body">
          <div class="stack-inline">
            <span class="tag">{{ detail.jiaoxueshipinValue || "备课" }}</span>
            <span class="meta">{{ detail.jiaoshiName || "教师待补充" }}</span>
          </div>
          <h1>{{ detail.jiaoxueshipinName }}</h1>
          <p>{{ stripHtml(detail.jiaoxueshipinContent) }}</p>
          <div class="stack-inline">
            <span class="meta">{{ detail.jiaoxueshipinTime?.slice(0, 16) || "时间待定" }}</span>
          </div>
          <a v-if="detail.jiaoxueshipinFile" class="primary-button" :href="downloadUrl(detail.jiaoxueshipinFile)" target="_blank">
            下载备课资料
          </a>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import {
  DEFAULT_BASE_URL,
  createAssetUrl,
  createDownloadUrl,
  type LessonMaterialItem
} from "@shared/index";
import { fetchMaterialDetail } from "@/api/content";

const route = useRoute();
const detail = ref<LessonMaterialItem | null>(null);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/800x480/dfebe6/203f39&text=Lesson";
}

function downloadUrl(fileName?: string) {
  return createDownloadUrl(DEFAULT_BASE_URL, fileName);
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").trim() || "暂无备课详情";
}

fetchMaterialDetail(route.params.id as string).then((data) => {
  detail.value = data;
});
</script>
