<template>
  <section class="section section--tight">
    <div class="filter-bar filter-bar--surface filter-grid">
      <input v-model="filters.keyword" class="field" placeholder="搜索作业标题" />
      <select v-model="filters.courseId" class="field">
        <option value="">全部课程</option>
        <option v-for="item in courses" :key="item.id" :value="String(item.id)">{{ item.kechengName }}</option>
      </select>
      <select v-model="filters.type" class="field">
        <option value="">全部类型</option>
        <option v-for="item in typeOptions" :key="item" :value="item">{{ item }}</option>
      </select>
      <button class="primary-button" @click="loadHomeworks">查询</button>
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
            <span>截止：{{ item.deadlineTime || "未设置" }}</span>
          </div>
          <RouterLink class="text-link" :to="`/homeworks/${item.id}`">查看详情</RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { DEFAULT_BASE_URL, createAssetUrl, type CourseItem, type HomeworkItem } from "@shared/index";
import { fetchCoursePage, fetchHomeworkPage } from "@/api/content";

const filters = reactive({
  keyword: "",
  courseId: "",
  type: ""
});
const homeworks = ref<HomeworkItem[]>([]);
const courses = ref<CourseItem[]>([]);

const typeOptions = computed(() =>
  Array.from(new Set(homeworks.value.map((item) => item.zuoyeValue).filter(Boolean) as string[]))
);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/600x400/f3d8c5/1c2430&text=Homework";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 100) || "暂无作业说明。";
}

async function loadHomeworks() {
  const [coursePage, homeworkPage] = await Promise.all([
    fetchCoursePage({ limit: 100 }),
    fetchHomeworkPage({
      limit: 100,
      zuoyeName: filters.keyword || undefined,
      kechengId: filters.courseId || undefined
    })
  ]);
  courses.value = coursePage.list;
  homeworks.value = homeworkPage.list.filter((item) => !filters.type || item.zuoyeValue === filters.type);
}

loadHomeworks();
</script>

<style scoped>
.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 960px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
