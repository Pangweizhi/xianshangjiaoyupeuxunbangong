<template>
  <section class="section section--tight">
    <div class="section__header">
      <div>
        <p class="eyebrow">备课资源</p>
        <h1>备课信息以资料卡片展示，适配教师和学生的轻量阅读场景</h1>
      </div>
    </div>

    <div class="content-grid">
      <article v-for="item in materials" :key="item.id" class="feature-card feature-card--compact">
        <img :src="toAsset(item.jiaoxueshipinPhoto)" :alt="item.jiaoxueshipinName" />
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.jiaoxueshipinValue || "备课" }}</span>
            <span class="meta">{{ item.jiaoshiName || "教师待补充" }}</span>
          </div>
          <h3>{{ item.jiaoxueshipinName }}</h3>
          <p>{{ stripHtml(item.jiaoxueshipinContent) }}</p>
          <div class="stack-inline">
            <span class="meta">{{ item.jiaoxueshipinTime?.slice(0, 10) || "时间待定" }}</span>
            <span class="meta">{{ item.jiaoxueshipinFile ? "含资料" : "无附件" }}</span>
          </div>
          <RouterLink class="text-link" :to="`/materials/${item.id}`">查看详情</RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { DEFAULT_BASE_URL, createAssetUrl, type LessonMaterialItem } from "@shared/index";
import { fetchMaterialPage } from "@/api/content";

const materials = ref<LessonMaterialItem[]>([]);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/600x400/dfebe6/203f39&text=Lesson";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 100) || "暂无备课内容";
}

fetchMaterialPage().then((page) => {
  materials.value = page.list;
});
</script>
