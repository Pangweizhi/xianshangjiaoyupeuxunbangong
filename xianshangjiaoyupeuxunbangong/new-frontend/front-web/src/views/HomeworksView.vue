<template>
  <section class="section section--tight">
    <div class="section__header">
      <div>
        <p class="eyebrow">作业中心</p>
        <h1>把原有作业列表从表格页重构为任务看板式内容流</h1>
      </div>
    </div>

    <div class="content-grid">
      <article v-for="item in homeworks" :key="item.id" class="feature-card feature-card--compact">
        <img :src="toAsset(item.zuoyePhoto)" :alt="item.zuoyeName" />
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.zuoyeValue || "作业" }}</span>
            <span class="meta">{{ item.jiaoshiName || "教师待补充" }}</span>
          </div>
          <h3>{{ item.zuoyeName }}</h3>
          <p>{{ stripHtml(item.zuoyeContent) }}</p>
          <div class="stack-inline">
            <span class="meta">{{ item.insertTime?.slice(0, 10) || "时间待定" }}</span>
            <span class="meta">{{ item.zuoyeFile ? "含附件" : "无附件" }}</span>
          </div>
          <RouterLink class="text-link" :to="`/homeworks/${item.id}`">查看详情</RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { DEFAULT_BASE_URL, createAssetUrl, type HomeworkItem } from "@shared/index";
import { fetchHomeworkPage } from "@/api/content";

const homeworks = ref<HomeworkItem[]>([]);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/600x400/e8ddd2/2b312d&text=Homework";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 100) || "暂无作业说明";
}

fetchHomeworkPage().then((page) => {
  homeworks.value = page.list;
});
</script>
