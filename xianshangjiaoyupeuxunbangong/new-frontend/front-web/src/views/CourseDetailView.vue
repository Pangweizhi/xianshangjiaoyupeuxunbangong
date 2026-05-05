<template>
  <section class="section section--tight">
    <RouterLink class="detail-back" to="/courses">返回课程列表</RouterLink>

    <div v-if="detail" class="course-detail-layout">
      <section class="course-detail-main">
        <article class="course-hero">
          <img :src="toAsset(detail.kechengPhoto)" :alt="detail.kechengName" class="course-hero__cover" />
          <div class="course-hero__body">
            <div class="stack-inline">
              <span class="tag">{{ detail.kechengValue || "课程" }}</span>
              <span class="meta">{{ detail.jiaoshiName || "教师待补充" }}</span>
              <span class="meta">学分 {{ detail.creditScore ?? 0 }}</span>
            </div>
            <h1>{{ detail.kechengName }}</h1>
            <p class="course-hero__summary">{{ stripHtml(detail.kechengContent) }}</p>

            <div class="course-stats">
              <span>开始时间：{{ detail.kechengTime || "待定" }}</span>
              <span>结束时间：{{ detail.kechengEndTime || "待定" }}</span>
              <span>课程时长：{{ detail.kechengShichang || 0 }} 分钟</span>
              <span>适用班级：{{ detail.banjiValue || "未设置" }}</span>
            </div>

            <button v-if="session.isLoggedIn" class="primary-button" :disabled="enrolling || enrolled" @click="handleEnroll">
              {{ enrolled ? "已选课" : enrolling ? "选课中..." : "立即选课" }}
            </button>
          </div>
        </article>

        <article v-if="resources.length" class="resource-overview">
          <div class="section__header section__header--stack">
            <div>
              <p class="eyebrow">课程资源总览</p>
              <h2>全部学习资源</h2>
            </div>
          </div>
          <div class="resource-grid">
            <article v-for="resource in resources" :key="resource.id" class="resource-card">
              <div class="stack-inline">
                <span class="tag">{{ resource.resourceType || "资源" }}</span>
                <span class="meta">{{ chapterNameMap[resource.chapterId] || "章节" }}</span>
              </div>
              <h3>{{ resource.resourceName }}</h3>
              <p>学习进度 {{ formatProgress(resource.id) }}</p>
              <div class="resource-card__meta">
                <span>时长 {{ resource.durationSeconds || 0 }} 秒</span>
                <span>{{ isVideoResource(resource) ? "视频资源" : "附件资源" }}</span>
              </div>
              <button class="primary-button primary-button--compact" @click="handleResourceAction(resource)">
                {{ isVideoResource(resource) ? "进入学习" : "下载资源" }}
              </button>
            </article>
          </div>
        </article>
      </section>

      <aside class="course-detail-side">
        <article class="side-panel">
          <div class="section__header section__header--stack">
            <div>
              <p class="eyebrow">章节与资源</p>
              <h2>按章节推进学习</h2>
            </div>
          </div>

          <div class="chapter-stack">
            <article v-for="chapter in chapters" :key="chapter.id" class="chapter-card">
              <div class="chapter-card__head">
                <div>
                  <strong>{{ chapter.chapterSort ? `${chapter.chapterSort}. ` : "" }}{{ chapter.chapterName }}</strong>
                  <p>{{ chapter.chapterSummary || "暂无章节说明" }}</p>
                </div>
                <span class="chapter-card__badge">{{ (resourcesByChapter[chapter.id] || []).length }} 个资源</span>
              </div>

              <div class="chapter-resource-list">
                <button
                  v-for="resource in resourcesByChapter[chapter.id] || []"
                  :key="resource.id"
                  class="chapter-resource"
                  @click="handleResourceAction(resource)"
                >
                  <div class="chapter-resource__body">
                    <strong>{{ resource.resourceName }}</strong>
                    <small>{{ resource.resourceType || "资源" }} · 学习进度 {{ formatProgress(resource.id) }}</small>
                  </div>
                  <span class="chapter-resource__action">
                    {{ isVideoResource(resource) ? "进入学习" : "下载资源" }}
                  </span>
                </button>
              </div>
            </article>
          </div>
        </article>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import {
  DEFAULT_BASE_URL,
  createAssetUrl,
  createDownloadUrl,
  type CourseChapterItem,
  type CourseItem,
  type CourseResourceItem,
  type StudyProgressItem
} from "@shared/index";
import {
  createCourseEnroll,
  fetchCourseChapterPage,
  fetchCourseDetail,
  fetchCourseResourcePage,
  fetchMyCoursePage,
  fetchStudyProgressPage
} from "@/api/content";
import { showUiToast } from "@/composables/uiToast";
import { useSessionStore } from "@/stores/session";

const route = useRoute();
const router = useRouter();
const session = useSessionStore();
const detail = ref<CourseItem | null>(null);
const chapters = ref<CourseChapterItem[]>([]);
const resources = ref<CourseResourceItem[]>([]);
const progresses = ref<StudyProgressItem[]>([]);
const enrolling = ref(false);
const enrolled = ref(false);

const chapterNameMap = computed(() => Object.fromEntries(chapters.value.map((item) => [item.id, item.chapterName])));
const progressMap = computed(() => Object.fromEntries(progresses.value.map((item) => [item.resourceId, item])));
const resourcesByChapter = computed(() => {
  const map: Record<number, CourseResourceItem[]> = {};
  resources.value.forEach((item) => {
    if (!map[item.chapterId]) {
      map[item.chapterId] = [];
    }
    map[item.chapterId].push(item);
  });
  return map;
});

function listOf<T>(value: { list?: T[] } | null | undefined) {
  return Array.isArray(value?.list) ? value.list : [];
}

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/800x480/f3d8c5/1c2430&text=Course";
}

function downloadUrl(fileName?: string) {
  return createDownloadUrl(DEFAULT_BASE_URL, fileName);
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").trim() || "暂无课程介绍";
}

function isVideoResource(resource: CourseResourceItem) {
  const type = resource.resourceType || "";
  const url = resource.resourceUrl || "";
  return type.includes("视频") || /\.(mp4|m3u8|webm|mov)$/i.test(url);
}

function formatProgress(resourceId: number) {
  const progress = progressMap.value[resourceId];
  const percent = progress?.isCompleted === 1 || (progress?.progressPercent || 0) >= 100 ? 100 : Math.min(99, Math.floor(progress?.progressPercent || 0));
  return `${percent}%`;
}

async function refreshProgress() {
  const progressPage = await fetchStudyProgressPage({ kechengId: route.params.id });
  progresses.value = listOf(progressPage);
}

async function checkEnrollStatus() {
  if (!session.isLoggedIn) {
    enrolled.value = false;
    return;
  }
  const page = await fetchMyCoursePage({ kechengId: route.params.id, limit: 1 });
  enrolled.value = listOf(page).length > 0;
}

async function handleEnroll() {
  if (!session.isLoggedIn) {
    showUiToast("请先登录后再选课", "error");
    return;
  }
  enrolling.value = true;
  try {
    const result = await createCourseEnroll({ kechengId: Number(route.params.id) });
    if (result.code !== 0) {
      throw new Error(result.msg || "选课失败");
    }
    enrolled.value = true;
    showUiToast("选课成功");
  } catch (error) {
    showUiToast(error instanceof Error ? error.message : "选课失败", "error");
  } finally {
    enrolling.value = false;
  }
}

function handleResourceAction(resource: CourseResourceItem) {
  if (!session.isLoggedIn) {
    showUiToast("请先登录", "error");
    return;
  }

  if (isVideoResource(resource)) {
    router.push({
      name: "course-video",
      params: { courseId: route.params.id, resourceId: resource.id }
    });
    return;
  }

  window.open(downloadUrl(resource.resourceUrl), "_blank");
}

async function loadPage() {
  const [course, chapterPage, resourcePage] = await Promise.all([
    fetchCourseDetail(route.params.id as string),
    fetchCourseChapterPage({ kechengId: route.params.id }),
    fetchCourseResourcePage({ kechengId: route.params.id })
  ]);
  detail.value = course;
  chapters.value = listOf(chapterPage);
  resources.value = listOf(resourcePage);
  if (session.isLoggedIn) {
    await refreshProgress();
    await checkEnrollStatus();
  }
}

loadPage();
</script>

<style scoped>
.detail-back {
  display: inline-flex;
  margin-bottom: 18px;
  padding: 10px 16px;
  border: 1px solid rgba(241, 159, 84, 0.34);
  border-radius: 999px;
  color: #b86724;
  background: rgba(255, 251, 245, 0.92);
}

.course-detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(340px, 0.92fr);
  gap: 24px;
  align-items: start;
}

.course-detail-main,
.course-detail-side {
  display: grid;
  gap: 18px;
}

.course-hero,
.resource-overview,
.side-panel {
  border-radius: 28px;
  border: 1px solid rgba(226, 213, 199, 0.78);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 22px 50px rgba(24, 32, 48, 0.08);
}

.course-hero {
  display: grid;
  grid-template-columns: minmax(220px, 0.68fr) minmax(0, 1fr);
  gap: 22px;
  padding: 22px;
}

.course-hero__cover {
  width: 100%;
  height: 100%;
  min-height: 280px;
  border-radius: 22px;
  object-fit: cover;
  background: #f6efe8;
}

.course-hero__body h1 {
  margin: 10px 0 12px;
  color: #162033;
}

.course-hero__summary {
  margin: 0;
  color: #5b6472;
  line-height: 1.8;
}

.course-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 18px 0 20px;
}

.course-stats span,
.chapter-card__badge,
.resource-card__meta span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 14px;
  border-radius: 16px;
  background: #fff7ef;
  color: #8a4f18;
  font-size: 13px;
}

.resource-overview,
.side-panel {
  padding: 22px;
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.resource-card {
  padding: 16px;
  border-radius: 22px;
  background: #fffdfa;
  border: 1px solid rgba(231, 223, 213, 0.85);
}

.resource-card h3 {
  margin: 12px 0 8px;
  color: #162033;
}

.resource-card p {
  margin: 0 0 12px;
  color: #5b6472;
}

.resource-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
}

.chapter-stack {
  display: grid;
  gap: 14px;
}

.chapter-card {
  padding: 16px;
  border-radius: 22px;
  background: #fffdfa;
  border: 1px solid rgba(231, 223, 213, 0.85);
}

.chapter-card__head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.chapter-card__head strong {
  color: #162033;
}

.chapter-card__head p {
  margin: 8px 0 0;
  color: #5b6472;
  line-height: 1.7;
}

.chapter-resource-list {
  display: grid;
  gap: 10px;
}

.chapter-resource {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  width: 100%;
  padding: 14px 16px;
  border: 1px solid rgba(225, 213, 201, 0.92);
  border-radius: 18px;
  background: #ffffff;
  text-align: left;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
}

.chapter-resource:hover {
  transform: translateY(-1px);
  border-color: rgba(228, 135, 59, 0.42);
  box-shadow: 0 14px 26px rgba(31, 41, 55, 0.08);
}

.chapter-resource__body {
  display: grid;
  gap: 6px;
}

.chapter-resource__body strong {
  color: #162033;
}

.chapter-resource__body small {
  color: #6b7280;
}

.chapter-resource__action {
  flex: none;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255, 122, 26, 0.12);
  color: #d76413;
  font-size: 12px;
  font-weight: 700;
}

@media (max-width: 1100px) {
  .course-detail-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .course-hero {
    grid-template-columns: 1fr;
  }

  .resource-grid,
  .course-stats {
    grid-template-columns: 1fr;
  }

  .chapter-card__head,
  .chapter-resource {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
