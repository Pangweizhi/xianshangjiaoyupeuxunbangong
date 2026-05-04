<template>
  <section class="section section--tight">
    <RouterLink class="text-link" to="/courses">返回课程列表</RouterLink>

    <div v-if="detail" class="detail-shell">
      <article class="detail-card">
        <img :src="toAsset(detail.kechengPhoto)" :alt="detail.kechengName" class="media-fit-contain media-fit-contain--course" />
        <div class="detail-card__body">
          <div class="stack-inline">
            <span class="tag">{{ detail.kechengValue || "课程" }}</span>
            <span class="meta">{{ detail.jiaoshiName || "教师待补充" }}</span>
            <span class="meta">学分 {{ detail.creditScore ?? 0 }}</span>
          </div>
          <h1>{{ detail.kechengName }}</h1>
          <p>{{ stripHtml(detail.kechengContent) }}</p>
          <div class="status-list">
            <span>开始时间：{{ detail.kechengTime || "待定" }}</span>
            <span>结束时间：{{ detail.kechengEndTime || "待定" }}</span>
            <span>课程时长：{{ detail.kechengShichang || 0 }} 分钟</span>
            <span>班级：{{ detail.banjiValue || "未设置" }}</span>
          </div>
          <button v-if="session.isLoggedIn" class="primary-button" :disabled="enrolling || enrolled" @click="handleEnroll">
            {{ enrolled ? "已选课" : enrolling ? "选课中..." : "立即选课" }}
          </button>
        </div>
      </article>

      <aside class="action-panel">
        <p class="eyebrow">课程章节</p>
        <h2>按章节推进学习</h2>
        <div class="mini-list">
          <article v-for="chapter in chapters" :key="chapter.id" class="mini-list__row chapter-row">
            <div>
              <strong>{{ chapter.chapterSort ? `${chapter.chapterSort}. ` : "" }}{{ chapter.chapterName }}</strong>
              <p>{{ chapter.chapterSummary || "暂无章节说明" }}</p>
            </div>
            <div class="chapter-resources">
              <button
                v-for="resource in resourcesByChapter[chapter.id] || []"
                :key="resource.id"
                class="ghost-button chapter-resource"
                @click="handleResourceAction(resource)"
              >
                {{ resource.resourceName }}
                <small>{{ formatProgress(resource.id) }}</small>
              </button>
            </div>
          </article>
        </div>
      </aside>
    </div>

    <section v-if="resources.length" class="section">
      <div class="section__header section__header--stack">
        <div>
          <p class="eyebrow">学习资源</p>
          <h2>章节资源按课程统一展示</h2>
        </div>
      </div>
      <div class="content-grid">
        <article v-for="resource in resources" :key="resource.id" class="feature-card feature-card--compact">
          <div>
            <div class="stack-inline">
              <span class="tag">{{ resource.resourceType || "资源" }}</span>
              <span class="meta">{{ chapterNameMap[resource.chapterId] || "章节" }}</span>
            </div>
            <h3>{{ resource.resourceName }}</h3>
            <p>学习进度 {{ formatProgress(resource.id) }}</p>
            <div class="status-list">
              <span>时长 {{ resource.durationSeconds || 0 }} 秒</span>
              <span>{{ isVideoResource(resource) ? "站内播放" : "直接下载" }}</span>
            </div>
            <button class="primary-button primary-button--compact" @click="handleResourceAction(resource)">
              {{ isVideoResource(resource) ? "开始播放" : "下载学习" }}
            </button>
          </div>
        </article>
      </div>
    </section>
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
  const percent = progress?.isCompleted === 1 ? 100 : Math.min(99, Math.floor(progress?.progressPercent || 0));
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
    showUiToast("请先登录后再开始学习", "error");
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
.chapter-row {
  align-items: start;
}

.chapter-resources {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.chapter-resource {
  display: inline-grid;
  gap: 4px;
  justify-items: start;
}

.chapter-resource small {
  color: var(--muted);
}
</style>
