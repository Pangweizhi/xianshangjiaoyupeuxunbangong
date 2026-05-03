<template>
  <section class="section section--tight">
    <RouterLink class="text-link" to="/courses">返回课程列表</RouterLink>
    <div v-if="detail" class="detail-shell">
      <article class="detail-card">
        <img :src="toAsset(detail.kechengPhoto)" :alt="detail.kechengName" />
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
          <button
            v-if="session.isLoggedIn"
            class="primary-button"
            :disabled="enrolling || enrolled"
            @click="handleEnroll"
          >
            {{ enrolled ? "已选课" : enrolling ? "选课中..." : "立即选课" }}
          </button>
          <p v-if="message" :class="messageType === 'error' ? 'field-error' : 'field-help'">{{ message }}</p>
        </div>
      </article>

      <aside class="action-panel">
        <p class="eyebrow">课程章节</p>
        <h2>按章节推进学习</h2>
        <div class="mini-list">
          <article v-for="chapter in chapters" :key="chapter.id" class="mini-list__row">
            <div>
              <strong>{{ chapter.chapterSort ? `${chapter.chapterSort}. ` : "" }}{{ chapter.chapterName }}</strong>
              <p>{{ chapter.chapterSummary || "暂无章节说明" }}</p>
              <p class="meta">资源数 {{ resourcesByChapter[chapter.id]?.length || 0 }}</p>
            </div>
          </article>
        </div>
      </aside>
    </div>

    <section v-if="resources.length" class="section">
      <div class="section__header section__header--stack">
        <div>
          <p class="eyebrow">学习资源</p>
          <h2>课程资源已按章节归集</h2>
        </div>
      </div>
      <div class="content-grid">
        <article v-for="resource in resources" :key="resource.id" class="feature-card feature-card--compact">
          <img :src="toAsset(resource.coverUrl)" :alt="resource.resourceName" />
          <div>
            <div class="stack-inline">
              <span class="tag">{{ resource.resourceType || "资源" }}</span>
              <span class="meta">{{ chapterNameMap[resource.chapterId] || "章节" }}</span>
            </div>
            <h3>{{ resource.resourceName }}</h3>
            <p>时长 {{ resource.durationSeconds || 0 }} 秒</p>
            <div class="stack-inline">
              <a v-if="resource.resourceUrl" class="ghost-button" :href="downloadUrl(resource.resourceUrl)" target="_blank">
                打开资源
              </a>
              <button
                v-if="session.isLoggedIn"
                class="primary-button primary-button--compact"
                @click="markAsLearned(resource)"
              >
                记录学习
              </button>
            </div>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import {
  DEFAULT_BASE_URL,
  createAssetUrl,
  createDownloadUrl,
  type CourseChapterItem,
  type CourseItem,
  type CourseResourceItem
} from "@shared/index";
import {
  createCourseEnroll,
  fetchCourseChapterPage,
  fetchCourseDetail,
  fetchCourseResourcePage,
  fetchMyCoursePage,
  saveStudyProgress
} from "@/api/content";
import { useSessionStore } from "@/stores/session";

const route = useRoute();
const session = useSessionStore();
const detail = ref<CourseItem | null>(null);
const chapters = ref<CourseChapterItem[]>([]);
const resources = ref<CourseResourceItem[]>([]);
const enrolling = ref(false);
const enrolled = ref(false);
const message = ref("");
const messageType = ref<"success" | "error">("success");

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/800x480/f3d8c5/1c2430&text=Course";
}

function downloadUrl(fileName?: string) {
  return createDownloadUrl(DEFAULT_BASE_URL, fileName);
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").trim() || "暂无课程介绍";
}

const chapterNameMap = computed(() => Object.fromEntries(chapters.value.map((item) => [item.id, item.chapterName])));
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

async function checkEnrollStatus() {
  if (!session.isLoggedIn) {
    enrolled.value = false;
    return;
  }
  const page = await fetchMyCoursePage({ kechengId: route.params.id, limit: 1 });
  enrolled.value = page.list.length > 0;
}

async function handleEnroll() {
  if (!session.isLoggedIn) {
    messageType.value = "error";
    message.value = "请先登录后再选课。";
    return;
  }
  enrolling.value = true;
  message.value = "";
  try {
    const result = await createCourseEnroll({ kechengId: Number(route.params.id) });
    if (result.code !== 0) {
      throw new Error(result.msg || "选课失败");
    }
    enrolled.value = true;
    messageType.value = "success";
    message.value = "选课成功，已加入我的课程。";
  } catch (error) {
    messageType.value = "error";
    message.value = error instanceof Error ? error.message : "选课失败";
  } finally {
    enrolling.value = false;
  }
}

async function markAsLearned(resource: CourseResourceItem) {
  if (!session.isLoggedIn) {
    messageType.value = "error";
    message.value = "请先登录后再记录学习进度。";
    return;
  }
  try {
    const result = await saveStudyProgress({
      resourceId: resource.id,
      studySeconds: resource.durationSeconds || 0,
      progressPercent: 100
    });
    if (result.code !== 0) {
      throw new Error(result.msg || "记录失败");
    }
    messageType.value = "success";
    message.value = `已记录《${resource.resourceName}》学习完成。`;
    await checkEnrollStatus();
  } catch (error) {
    messageType.value = "error";
    message.value = error instanceof Error ? error.message : "记录失败";
  }
}

async function loadPage() {
  const [course, chapterPage, resourcePage] = await Promise.all([
    fetchCourseDetail(route.params.id as string),
    fetchCourseChapterPage({ kechengId: route.params.id }),
    fetchCourseResourcePage({ kechengId: route.params.id })
  ]);
  detail.value = course;
  chapters.value = chapterPage.list;
  resources.value = resourcePage.list;
}

loadPage();

if (session.isLoggedIn) {
  checkEnrollStatus();
}
</script>
