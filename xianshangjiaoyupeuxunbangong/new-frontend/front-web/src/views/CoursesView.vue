<template>
  <section class="section section--tight">
    <div class="section__header">
      <div>
        <p class="eyebrow">课程中心</p>
        <h1>课程列表重写为内容优先的探索视图</h1>
      </div>
    </div>

    <div class="filter-bar">
      <input v-model="keyword" class="field" placeholder="搜索课程标题" />
      <button class="primary-button" @click="loadCourses">查询</button>
    </div>

    <div class="content-grid">
      <article v-for="course in courses" :key="course.id" class="feature-card feature-card--compact">
        <img :src="toAsset(course.kechengPhoto)" :alt="course.kechengName" />
        <div>
          <div class="stack-inline">
            <span class="tag">{{ course.kechengValue || "课程" }}</span>
            <span class="meta">{{ course.jiaoshiName || "教师待补全" }}</span>
          </div>
          <h3>{{ course.kechengName }}</h3>
          <p>{{ stripHtml(course.kechengContent) }}</p>
          <div class="stack-inline">
            <span class="meta">时长 {{ course.kechengShichang || 0 }} 分钟</span>
            <span class="meta">{{ course.kechengTime?.slice(0, 10) || "时间待定" }}</span>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { DEFAULT_BASE_URL, createAssetUrl, type CourseItem } from "@shared/index";
import { fetchCoursePage } from "@/api/content";

const keyword = ref("");
const courses = ref<CourseItem[]>([]);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/600x400/d6d0c4/1f2521&text=Course";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 100) || "暂无课程简介";
}

async function loadCourses() {
  const page = await fetchCoursePage({ kechengName: keyword.value || undefined });
  courses.value = page.list;
}

loadCourses();
</script>
