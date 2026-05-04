<template>
  <section class="section section--tight">
    <div class="filter-bar filter-bar--surface filter-grid">
      <input v-model="filters.keyword" class="field" placeholder="搜索课程名称" />
      <select v-model="filters.status" class="field">
        <option value="">全部状态</option>
        <option value="已选课">已选课</option>
        <option value="学习中">学习中</option>
        <option value="已结课">已结课</option>
      </select>
      <select v-model="filters.teacher" class="field">
        <option value="">全部教师</option>
        <option v-for="item in teacherOptions" :key="item" :value="item">{{ item }}</option>
      </select>
      <button class="primary-button" @click="loadPage">查询</button>
    </div>

    <div class="content-grid">
      <article v-for="course in courses" :key="course.id" class="feature-card feature-card--compact">
        <img :src="toAsset(course.kechengPhoto)" :alt="course.kechengName" class="media-fit-contain media-fit-contain--course" />
        <div>
          <div class="stack-inline">
            <span class="tag">{{ course.enrollStatus || "已选课" }}</span>
            <span class="meta">{{ course.jiaoshiName || "教师待补充" }}</span>
          </div>
          <h3>{{ course.kechengName }}</h3>
          <p>学习进度 {{ Math.round(course.progressPercent || 0) }}%，进入课程详情即可继续学习章节与资源。</p>
          <div class="status-list">
            <span>学分：{{ course.creditScore ?? 0 }}</span>
            <span>结课：{{ course.finishTime || "未结课" }}</span>
          </div>
          <RouterLink class="ghost-button" :to="`/courses/${course.kechengId}`">进入课程</RouterLink>
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

      <div class="filter-bar filter-bar--surface filter-grid filter-grid--compact">
        <input v-model="creditKeyword" class="field" placeholder="搜索学分课程" />
        <select v-model="creditStatus" class="field">
          <option value="">全部发放状态</option>
          <option value="已发放">已发放</option>
          <option value="待发放">待发放</option>
        </select>
      </div>

      <div class="mini-list">
        <article v-for="record in filteredCredits" :key="record.id" class="mini-list__row">
          <div>
            <strong>{{ record.kechengName }}</strong>
            <p>{{ record.grantRemark || "系统自动结算学分。" }}</p>
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
import { computed, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { DEFAULT_BASE_URL, createAssetUrl, type CourseEnrollItem, type CreditRecordItem } from "@shared/index";
import { fetchMyCoursePage, fetchMyCreditPage } from "@/api/content";

const filters = reactive({
  keyword: "",
  status: "",
  teacher: ""
});
const creditKeyword = ref("");
const creditStatus = ref("");
const courses = ref<CourseEnrollItem[]>([]);
const credits = ref<CreditRecordItem[]>([]);

const teacherOptions = computed(() =>
  Array.from(new Set(courses.value.map((item) => item.jiaoshiName).filter(Boolean) as string[]))
);
const filteredCredits = computed(() =>
  credits.value.filter((item) => {
    const matchKeyword = !creditKeyword.value || (item.kechengName || "").includes(creditKeyword.value);
    const matchStatus = !creditStatus.value || (item.grantStatus || "待发放") === creditStatus.value;
    return matchKeyword && matchStatus;
  })
);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/800x480/f3d8c5/1c2430&text=Course";
}

async function loadPage() {
  const [coursePage, creditPage] = await Promise.all([
    fetchMyCoursePage({ limit: 100 }),
    fetchMyCreditPage({ limit: 100 })
  ]);
  courses.value = coursePage.list.filter((item) => {
    const matchKeyword = !filters.keyword || (item.kechengName || "").includes(filters.keyword);
    const matchStatus = !filters.status || (item.enrollStatus || "已选课") === filters.status;
    const matchTeacher = !filters.teacher || item.jiaoshiName === filters.teacher;
    return matchKeyword && matchStatus && matchTeacher;
  });
  credits.value = creditPage.list;
}

loadPage();
</script>

<style scoped>
.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.filter-grid--compact {
  grid-template-columns: repeat(2, minmax(0, 220px));
  justify-content: start;
  margin-bottom: 18px;
}

@media (max-width: 960px) {
  .filter-grid,
  .filter-grid--compact {
    grid-template-columns: 1fr;
  }
}
</style>
