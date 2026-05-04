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
              <p>{{ chapter.chapterSummary || "暂无章节说明。" }}</p>
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

    <section v-if="activeVideo" class="section">
      <div class="section__header section__header--stack">
        <div>
          <p class="eyebrow">视频学习</p>
          <h2>{{ activeVideo.resourceName }}</h2>
          <p class="section__summary">视频在站内播放，并按播放进度自动记录学习进度。</p>
        </div>
      </div>

      <article class="detail-article video-panel">
        <video
          v-if="activeVideoUrl"
          :key="`${activeVideo.id}-${activeVideoSourceIndex}`"
          ref="videoRef"
          class="video-player"
          controls
          playsinline
          preload="metadata"
          :src="activeVideoUrl"
          @loadedmetadata="restoreVideoProgress"
          @timeupdate="handleVideoProgress"
          @pause="handleVideoPause"
          @ended="handleVideoEnded"
          @error="handleVideoError"
        ></video>
        <p v-else class="field-help">当前资源缺少可播放地址。</p>
        <div class="status-list">
          <span>当前进度：{{ formatProgress(activeVideo.id) }}</span>
          <span>章节：{{ chapterNameMap[activeVideo.chapterId] || "未归类" }}</span>
          <span>时长：{{ activeVideo.durationSeconds || 0 }} 秒</span>
        </div>
      </article>
    </section>

    <section v-if="resources.length" class="section">
      <div class="section__header section__header--stack">
        <div>
          <p class="eyebrow">学习资源</p>
          <h2>课程资源按章节归类</h2>
          <p class="section__summary">PPT、文档、压缩包直接下载并记为已学习，视频则在站内播放并记录进度。</p>
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
import { computed, nextTick, onBeforeUnmount, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
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
  fetchStudyProgressPage,
  saveStudyProgress
} from "@/api/content";
import { showUiToast } from "@/composables/uiToast";
import { useSessionStore } from "@/stores/session";

const route = useRoute();
const session = useSessionStore();
const detail = ref<CourseItem | null>(null);
const chapters = ref<CourseChapterItem[]>([]);
const resources = ref<CourseResourceItem[]>([]);
const progresses = ref<StudyProgressItem[]>([]);
const activeVideo = ref<CourseResourceItem | null>(null);
const activeVideoSourceIndex = ref(0);
const videoRef = ref<HTMLVideoElement | null>(null);
const enrolling = ref(false);
const enrolled = ref(false);
const lastSavedSecondsByResource: Record<number, number> = {};

const activeVideoSourceCandidates = computed(() => buildMediaCandidates(activeVideo.value?.resourceUrl));
const activeVideoUrl = computed(() => activeVideoSourceCandidates.value[activeVideoSourceIndex.value] || "");
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
  return value?.replace(/<[^>]+>/g, "").trim() || "暂无课程介绍。";
}

function isVideoResource(resource: CourseResourceItem) {
  const type = resource.resourceType || "";
  const url = resource.resourceUrl || "";
  return /视频|mp4|m3u8|webm|mov/i.test(type) || /\.(mp4|m3u8|webm|mov)$/i.test(url);
}

function formatProgress(resourceId: number) {
  const progress = progressMap.value[resourceId];
  return `${Math.round(progress?.progressPercent || 0)}%`;
}

function buildMediaCandidates(path?: string) {
  if (!path) {
    return [];
  }
  let decodedPath = path;
  try {
    decodedPath = decodeURIComponent(path);
  } catch {
    decodedPath = path;
  }
  const normalized = decodedPath.replace(/\\/g, "/").trim();
  if (!normalized) {
    return [];
  }
  if (/^https?:\/\//i.test(normalized)) {
    return [encodeURI(normalized)];
  }

  const value = normalized.replace(/^\/+/, "").replace(/^\.\//, "");
  const contextFreeValue = value.replace(/^xianshangjiaoyupeuxunbangong\//, "");
  const fileName = contextFreeValue.split("/").filter(Boolean).pop() || "";
  const candidates = new Set<string>();

  if (/^file\/download/i.test(contextFreeValue)) {
    candidates.add(encodeURI(`${DEFAULT_BASE_URL}/${contextFreeValue}`));
  } else if (/^[A-Za-z]:\//.test(contextFreeValue)) {
    if (fileName) {
      candidates.add(downloadUrl(fileName));
    }
  } else {
    if (contextFreeValue.startsWith("upload/")) {
      candidates.add(encodeURI(`${DEFAULT_BASE_URL}/${contextFreeValue}`));
    } else if (contextFreeValue.startsWith("static/upload/")) {
      candidates.add(encodeURI(`${DEFAULT_BASE_URL}/${contextFreeValue.replace(/^static\//, "")}`));
    } else if (!contextFreeValue.includes("/")) {
      candidates.add(encodeURI(`${DEFAULT_BASE_URL}/upload/${contextFreeValue}`));
    } else {
      candidates.add(encodeURI(`${DEFAULT_BASE_URL}/${contextFreeValue}`));
    }
    if (fileName) {
      candidates.add(downloadUrl(fileName));
    }
  }

  candidates.add(createAssetUrl(DEFAULT_BASE_URL, normalized));
  candidates.add(createAssetUrl(DEFAULT_BASE_URL, contextFreeValue));
  candidates.add(downloadUrl(normalized));
  if (fileName && fileName !== normalized) {
    candidates.add(downloadUrl(fileName));
  }

  return Array.from(candidates).filter(Boolean);
}

function buildProgressPayload(resource: CourseResourceItem, studySeconds: number, progressPercent?: number) {
  let percent = progressPercent ?? 0;
  if (resource.durationSeconds && resource.durationSeconds > 0) {
    percent = Math.max(percent, Math.min(100, (studySeconds * 100) / resource.durationSeconds));
  }
  return {
    resourceId: resource.id,
    studySeconds,
    progressPercent: Number(percent.toFixed(2))
  };
}

function syncLocalProgress(resource: CourseResourceItem, studySeconds: number, progressPercent?: number) {
  const payload = buildProgressPayload(resource, studySeconds, progressPercent);
  const current = progresses.value.find((item) => item.resourceId === resource.id);
  if (current) {
    current.studySeconds = Math.max(current.studySeconds || 0, payload.studySeconds);
    current.progressPercent = Math.max(current.progressPercent || 0, payload.progressPercent);
    current.isCompleted = (current.progressPercent || 0) >= 90 ? 1 : 0;
    return;
  }
  progresses.value = [
    {
      id: 0,
      kechengId: resource.kechengId,
      chapterId: resource.chapterId,
      resourceId: resource.id,
      yonghuId: session.session?.userId || 0,
      studySeconds: payload.studySeconds,
      progressPercent: payload.progressPercent,
      isCompleted: payload.progressPercent >= 90 ? 1 : 0
    },
    ...progresses.value
  ];
}

async function refreshProgress() {
  if (!session.isLoggedIn) {
    progresses.value = [];
    return;
  }
  const progressPage = await fetchStudyProgressPage({ kechengId: route.params.id, limit: 100 });
  progresses.value = listOf(progressPage);
  Object.keys(lastSavedSecondsByResource).forEach((key) => {
    delete lastSavedSecondsByResource[Number(key)];
  });
  progresses.value.forEach((item) => {
    if (item.resourceId) {
      lastSavedSecondsByResource[item.resourceId] = item.studySeconds || 0;
    }
  });
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
    showUiToast("请先登录后再选课。", "error");
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

async function persistStudyProgress(
  resource: CourseResourceItem,
  studySeconds: number,
  progressPercent?: number,
  options?: { refresh?: boolean }
) {
  syncLocalProgress(resource, studySeconds, progressPercent);
  const payload = buildProgressPayload(resource, studySeconds, progressPercent);
  const result = await saveStudyProgress(payload);
  if (result.code !== 0) {
    throw new Error(result.msg || "记录学习进度失败");
  }
  lastSavedSecondsByResource[resource.id] = Math.max(lastSavedSecondsByResource[resource.id] || 0, payload.studySeconds);
  if (options?.refresh) {
    await refreshProgress();
  }
}

async function handleResourceAction(resource: CourseResourceItem) {
  if (!session.isLoggedIn) {
    showUiToast("请先登录后再开始学习。", "error");
    return;
  }

  if (isVideoResource(resource)) {
    await flushActiveVideoProgress();
    activeVideo.value = resource;
    activeVideoSourceIndex.value = 0;
    await nextTick();
    videoRef.value?.load();
    const playTask = videoRef.value?.play();
    if (playTask) {
      playTask.catch(() => {
        showUiToast("视频已切换，点击播放器上的播放按钮即可开始学习。");
      });
    }
    return;
  }

  try {
    await persistStudyProgress(resource, resource.durationSeconds || 0, 100, { refresh: true });
    window.open(downloadUrl(resource.resourceUrl), "_blank");
    showUiToast(`已记录《${resource.resourceName}》学习完成`);
  } catch (error) {
    showUiToast(error instanceof Error ? error.message : "记录学习失败", "error");
  }
}

async function flushActiveVideoProgress(force = false) {
  if (!activeVideo.value || !videoRef.value || !session.isLoggedIn) {
    return;
  }
  const currentTime = Math.floor(videoRef.value.currentTime || 0);
  if (currentTime <= 0) {
    return;
  }
  const lastSaved = lastSavedSecondsByResource[activeVideo.value.id] || 0;
  if (!force && currentTime <= lastSaved) {
    return;
  }
  try {
    await persistStudyProgress(activeVideo.value, currentTime);
  } catch {
    // Ignore pause/unload save failures to keep playback flow stable.
  }
}

function restoreVideoProgress() {
  if (!activeVideo.value || !videoRef.value) {
    return;
  }
  const progress = progressMap.value[activeVideo.value.id];
  if (progress?.studySeconds) {
    videoRef.value.currentTime = progress.studySeconds;
  }
}

async function handleVideoProgress() {
  if (!activeVideo.value || !videoRef.value || !session.isLoggedIn) {
    return;
  }
  const currentTime = Math.floor(videoRef.value.currentTime || 0);
  if (currentTime <= 0) {
    return;
  }
  const lastSaved = lastSavedSecondsByResource[activeVideo.value.id] || 0;
  if (currentTime - lastSaved < 10) {
    return;
  }
  try {
    await persistStudyProgress(activeVideo.value, currentTime);
  } catch {
    // Do not interrupt playback because of a transient save failure.
  }
}

function handleVideoPause() {
  void flushActiveVideoProgress(true);
}

async function handleVideoEnded() {
  if (!activeVideo.value) {
    return;
  }
  try {
    const finishedSeconds = activeVideo.value.durationSeconds || Math.floor(videoRef.value?.duration || 0);
    await persistStudyProgress(activeVideo.value, finishedSeconds, 100, { refresh: true });
    showUiToast(`已完成《${activeVideo.value.resourceName}》学习`);
  } catch (error) {
    showUiToast(error instanceof Error ? error.message : "记录学习失败", "error");
  }
}

async function handleVideoError() {
  if (!activeVideo.value) {
    return;
  }
  if (activeVideoSourceIndex.value < activeVideoSourceCandidates.value.length - 1) {
    activeVideoSourceIndex.value += 1;
    await nextTick();
    videoRef.value?.load();
    return;
  }
  showUiToast("当前视频地址无法播放，请检查资源文件路径。", "error");
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
  await refreshProgress();
  await checkEnrollStatus();
}

onBeforeUnmount(() => {
  void flushActiveVideoProgress(true);
});

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

.video-panel {
  padding: 24px;
}

.video-player {
  width: 100%;
  max-height: 540px;
  border-radius: 24px;
  background: #000;
  margin-bottom: 16px;
}
</style>
