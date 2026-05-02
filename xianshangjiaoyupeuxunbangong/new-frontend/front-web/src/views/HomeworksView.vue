<template>
  <section class="section section--tight">
    <div class="section__header section__header--stack">
      <div>
        <p class="eyebrow">作业中心</p>
        <h1>按课程和章节查看当前可提交的作业</h1>
        <p class="section__summary">
          这里集中展示已发布作业的课程归属、截止时间、总分和附件状态，便于学生按学习路径完成任务。
        </p>
      </div>
      <div class="toolbar toolbar--wrap">
        <input v-model="keyword" class="field" placeholder="搜索作业标题" />
        <select v-model="selectedCourseId" class="field">
          <option value="">全部课程</option>
          <option v-for="item in courses" :key="item.id" :value="String(item.id)">
            {{ item.kechengName }}
          </option>
        </select>
        <button class="ghost-button" @click="loadHomeworks">查询</button>
      </div>
    </div>

    <div class="content-grid">
      <article v-for="item in homeworks" :key="item.id" class="feature-card feature-card--compact">
        <img :src="toAsset(item.zuoyePhoto)" :alt="item.zuoyeName" />
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.zuoyeValue || "作业" }}</span>
            <span class="meta">{{ item.kechengName || "未关联课程" }}</span>
          </div>
          <h3>{{ item.zuoyeName }}</h3>
          <p>{{ stripHtml(item.zuoyeContent) }}</p>
          <div class="status-list">
            <span>章节：{{ item.chapterName || "未指定" }}</span>
            <span>总分：{{ item.scoreTotal ?? 100 }}</span>
            <span>截止：{{ formatTime(item.deadlineTime) }}</span>
            <span>{{ isExpired(item.deadlineTime) ? "已截止" : "进行中" }}</span>
          </div>
          <div class="stack-inline">
            <span class="meta">{{ item.jiaoshiName || "教师待补充" }}</span>
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
import { DEFAULT_BASE_URL, createAssetUrl, type CourseItem, type HomeworkItem } from "@shared/index";
import { fetchCoursePage, fetchHomeworkPage } from "@/api/content";

const homeworks = ref<HomeworkItem[]>([]);
const courses = ref<CourseItem[]>([]);
const keyword = ref("");
const selectedCourseId = ref("");

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/600x400/f3d8c5/1c2430&text=Homework";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 100) || "暂无作业说明";
}

function formatTime(value?: string) {
  return value || "未设置";
}

function isExpired(value?: string) {
  if (!value) return false;
  return new Date(value).getTime() < Date.now();
}

async function loadHomeworks() {
  const page = await fetchHomeworkPage({
    zuoyeName: keyword.value || undefined,
    kechengId: selectedCourseId.value || undefined
  });
  homeworks.value = page.list;
}

Promise.all([fetchCoursePage({ limit: 100 }), loadHomeworks()]).then(([page]) => {
  courses.value = page.list;
});
</script>
