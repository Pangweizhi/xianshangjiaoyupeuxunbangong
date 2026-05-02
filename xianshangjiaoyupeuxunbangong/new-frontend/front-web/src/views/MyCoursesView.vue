<template>
  <section class="section section--tight">
    <div class="section__header section__header--stack">
      <div>
        <p class="eyebrow">我的课程</p>
        <h1>已选课程与学分记录</h1>
        <p class="section__summary">展示选课状态、进度百分比和已发放学分。</p>
      </div>
    </div>

    <div class="content-grid">
      <article v-for="course in courses" :key="course.id" class="feature-card feature-card--compact">
        <img :src="toAsset(course.kechengPhoto)" :alt="course.kechengName" />
        <div>
          <div class="stack-inline">
            <span class="tag">{{ course.enrollStatus || "已选课" }}</span>
            <span class="meta">{{ course.jiaoshiName || "教师待补充" }}</span>
          </div>
          <h3>{{ course.kechengName }}</h3>
          <p>学习进度 {{ Math.round(course.progressPercent || 0) }}%</p>
          <div class="stack-inline">
            <span class="meta">学分 {{ course.creditScore ?? 0 }}</span>
            <RouterLink class="ghost-button" :to="`/courses/${course.kechengId}`">继续学习</RouterLink>
          </div>
        </div>
      </article>
    </div>

    <section class="section">
      <div class="section__header section__header--stack">
        <div>
          <p class="eyebrow">学分发放</p>
          <h2>课程结算结果</h2>
        </div>
      </div>
      <div class="mini-list">
        <article v-for="record in credits" :key="record.id" class="mini-list__row">
          <div>
            <strong>{{ record.kechengName }}</strong>
            <p>{{ record.grantRemark || "系统自动发放" }}</p>
          </div>
          <div class="status-list">
            <span>{{ record.grantStatus || "待发放" }}</span>
            <span>{{ record.creditScore || 0 }} 学分</span>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { DEFAULT_BASE_URL, createAssetUrl, type CourseEnrollItem, type CreditRecordItem } from "@shared/index";
import { fetchMyCoursePage, fetchMyCreditPage } from "@/api/content";

const courses = ref<CourseEnrollItem[]>([]);
const credits = ref<CreditRecordItem[]>([]);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/800x480/f3d8c5/1c2430&text=Course";
}

Promise.all([fetchMyCoursePage(), fetchMyCreditPage()]).then(([coursePage, creditPage]) => {
  courses.value = coursePage.list;
  credits.value = creditPage.list;
});
</script>
