<template>
  <section class="hero">
    <div class="hero__copy">
      <p class="eyebrow">新版前台重写</p>
      <h1>把课程、公告、作业与教师协同放进一套真正统一的学习门户。</h1>
      <p class="hero__lead">
        新前端保留原后端接口，重做信息架构、视觉语言和移动端体验。当前首批页面已接入课程与公告数据流。
      </p>
      <div class="hero__actions">
        <RouterLink class="primary-button" to="/courses">浏览课程</RouterLink>
        <RouterLink class="ghost-button" to="/login">进入系统</RouterLink>
      </div>
    </div>
    <aside class="hero__panel">
      <div class="metric-card">
        <strong>{{ courses.length }}</strong>
        <span>课程模块已接入</span>
      </div>
      <div class="metric-card">
        <strong>{{ notices.length }}</strong>
        <span>公告模块已接入</span>
      </div>
      <div class="metric-card">
        <strong>3</strong>
        <span>角色体系已预留</span>
      </div>
    </aside>
  </section>

  <section class="section">
    <div class="section__header">
      <div>
        <p class="eyebrow">课程推荐</p>
        <h2>围绕教务信息流重构内容卡片</h2>
      </div>
      <RouterLink class="text-link" to="/courses">查看全部</RouterLink>
    </div>
    <div class="content-grid">
      <article v-for="course in courses" :key="course.id" class="feature-card">
        <img :src="toAsset(course.kechengPhoto)" :alt="course.kechengName" />
        <div>
          <span class="tag">{{ course.kechengValue || "课程" }}</span>
          <h3>{{ course.kechengName }}</h3>
          <p>{{ course.kechengContent || "课程详情将在下一阶段拆成详情页与报名流程。" }}</p>
        </div>
      </article>
    </div>
  </section>

  <section class="section">
    <div class="section__header">
      <div>
        <p class="eyebrow">通知公告</p>
        <h2>信息发布区采用更轻的阅读结构</h2>
      </div>
      <RouterLink class="text-link" to="/notices">公告列表</RouterLink>
    </div>
    <div class="notice-list">
      <article v-for="notice in notices" :key="notice.id" class="notice-row">
        <div>
          <h3>{{ notice.newsName }}</h3>
          <p>{{ stripHtml(notice.newsContent) }}</p>
        </div>
        <span>{{ notice.insertTime?.slice(0, 10) || "待更新" }}</span>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { DEFAULT_BASE_URL, createAssetUrl, type CourseItem, type NoticeItem } from "@shared/index";
import { fetchCoursePage, fetchNoticePage } from "@/api/content";

const courses = ref<CourseItem[]>([]);
const notices = ref<NoticeItem[]>([]);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/600x400/e4dccf/1f2521&text=Course";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 80) || "暂无内容摘要";
}

onMounted(async () => {
  try {
    const [coursePage, noticePage] = await Promise.all([
      fetchCoursePage(),
      fetchNoticePage()
    ]);
    courses.value = coursePage.list;
    notices.value = noticePage.list;
  } catch (error) {
    console.error(error);
  }
});
</script>
