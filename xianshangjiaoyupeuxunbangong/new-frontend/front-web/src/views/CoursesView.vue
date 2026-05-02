<template>
  <section class="section section--tight">
    <div class="section__header section__header--stack">
      <div>
        <p class="eyebrow">课程中心</p>
        <h1>按课程主题集中浏览教学内容</h1>
        <p class="section__summary">支持按课程名称快速筛选，优先展示封面、分类、教师与摘要信息。</p>
      </div>
    </div>

    <div class="filter-bar filter-bar--surface">
      <input v-model="keyword" class="field" placeholder="搜索课程标题" />
      <button class="primary-button" @click="loadCourses">查询</button>
    </div>

    <div class="content-grid">
      <article v-for="course in courses" :key="course.id" class="feature-card feature-card--compact">
        <img :src="toAsset(course.kechengPhoto)" :alt="course.kechengName" />
        <div>
          <div class="stack-inline">
            <span class="tag">{{ course.kechengValue || "课程" }}</span>
            <span class="meta">{{ course.jiaoshiName || "教师待补充" }}</span>
            <span class="meta">学分 {{ course.creditScore ?? 0 }}</span>
          </div>
          <h3>{{ course.kechengName }}</h3>
          <p>{{ stripHtml(course.kechengContent) }}</p>
          <div class="stack-inline">
            <span class="meta">时长 {{ course.kechengShichang || 0 }} 分钟</span>
            <span class="meta">{{ course.kechengTime?.slice(0, 10) || "时间待定" }}</span>
            <RouterLink class="ghost-button" :to="`/courses/${course.id}`">查看详情</RouterLink>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { DEFAULT_BASE_URL, createAssetUrl, type CourseItem } from "@shared/index";
import { fetchCoursePage } from "@/api/content";

const keyword = ref("");
const courses = ref<CourseItem[]>([]);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/600x400/f4e4d2/1c2430&text=Course";
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
