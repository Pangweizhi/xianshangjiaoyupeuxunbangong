<template>
  <section class="section section--tight">
    <div class="filter-bar filter-bar--surface filter-grid">
      <input v-model="filters.keyword" class="field" placeholder="搜索课程名称" />
      <select v-model="filters.teacher" class="field">
        <option value="">全部教师</option>
        <option v-for="item in teacherOptions" :key="item" :value="item">{{ item }}</option>
      </select>
      <select v-model="filters.type" class="field">
        <option value="">全部类型</option>
        <option v-for="item in typeOptions" :key="item" :value="item">{{ item }}</option>
      </select>
      <button class="primary-button" @click="loadCourses">查询</button>
    </div>

    <div v-if="courses.length" class="content-grid">
      <article v-for="course in courses" :key="course.id" class="feature-card feature-card--compact">
        <img :src="toAsset(course.kechengPhoto)" :alt="course.kechengName" class="media-fit-contain media-fit-contain--course" />
        <div>
          <div class="stack-inline">
            <span class="tag">{{ course.kechengValue || "课程" }}</span>
            <span v-if="selectedCourseIds.has(course.id)" class="tag tag--selected">已选</span>
            <span class="meta">{{ course.jiaoshiName || "教师待补充" }}</span>
            <span class="meta">学分 {{ course.creditScore ?? 0 }}</span>
          </div>
          <h3>{{ course.kechengName }}</h3>
          <p>{{ stripHtml(course.kechengContent) }}</p>
          <div class="status-list">
            <span>开始：{{ course.kechengTime || "待定" }}</span>
            <span>结束：{{ course.kechengEndTime || "待定" }}</span>
            <span>时长：{{ course.kechengShichang || 0 }} 分钟</span>
          </div>
          <RouterLink class="ghost-button" :to="`/courses/${course.id}`">查看详情</RouterLink>
        </div>
      </article>
    </div>

    <article v-else class="note-card empty-card">
      <strong>当前没有可显示的课程</strong>
      <p>如果后台已经配置课程但这里仍为空，请继续检查课程数据和图片路径。</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { DEFAULT_BASE_URL, createAssetUrl, type CourseEnrollItem, type CourseItem } from "@shared/index";
import { fetchCoursePage, fetchMyCoursePage } from "@/api/content";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const filters = reactive({
  keyword: "",
  teacher: "",
  type: ""
});
const allCourses = ref<CourseItem[]>([]);
const courses = ref<CourseItem[]>([]);
const enrolledCourses = ref<CourseEnrollItem[]>([]);

const selectedCourseIds = computed(() => new Set(enrolledCourses.value.map((item) => Number(item.kechengId))));
const teacherOptions = computed(() =>
  Array.from(new Set(allCourses.value.map((item) => item.jiaoshiName).filter(Boolean) as string[]))
);
const typeOptions = computed(() =>
  Array.from(new Set(allCourses.value.map((item) => item.kechengValue).filter(Boolean) as string[]))
);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/600x400/f4e4d2/1c2430&text=Course";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 100) || "暂无课程简介。";
}

function applyFilters() {
  courses.value = allCourses.value.filter((item) => {
    const matchKeyword = !filters.keyword || item.kechengName?.includes(filters.keyword);
    const matchTeacher = !filters.teacher || item.jiaoshiName === filters.teacher;
    const matchType = !filters.type || item.kechengValue === filters.type;
    return matchKeyword && matchTeacher && matchType;
  });
}

async function loadCourses() {
  const [coursePage, myCoursePage] = await Promise.all([
    fetchCoursePage({ page: 1, limit: 200 }),
    session.isLoggedIn ? fetchMyCoursePage({ limit: 100 }) : Promise.resolve({ list: [] } as { list: CourseEnrollItem[] })
  ]);
  allCourses.value = Array.isArray(coursePage.list) ? coursePage.list : [];
  enrolledCourses.value = Array.isArray(myCoursePage.list) ? myCoursePage.list : [];
  applyFilters();
}

loadCourses();
</script>

<style scoped>
.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.tag--selected {
  background: rgba(26, 78, 216, 0.12);
  color: #1a4ed8;
}

.empty-card {
  padding: 28px;
}

@media (max-width: 960px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
