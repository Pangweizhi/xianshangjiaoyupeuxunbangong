<template>
  <section class="video-course-page section section--tight">
    <RouterLink class="text-link" :to="`/courses/${route.params.courseId}`">返回课程详情</RouterLink>

    <div v-if="course && resource" class="video-course-layout">
      <article class="video-stage">
        <div class="video-player-shell">
          <video
            v-if="activeVideoUrl"
            :key="`${resource.id}-${sourceIndex}`"
            ref="videoRef"
            class="video-player"
            controls
            playsinline
            preload="metadata"
            :src="activeVideoUrl"
            @loadedmetadata="handleLoadedMetadata"
            @timeupdate="handleTimeUpdate"
            @pause="handlePause"
            @play="handlePlay"
            @ended="handleEnded"
            @error="handleError"
          ></video>
          <p v-else class="field-help">当前视频资源缺少可播放地址。</p>

          <div v-if="showCompletedOverlay" class="video-overlay">
            <div class="video-overlay__card">
              <p class="eyebrow">学习完成</p>
              <h3>您已完成{{ resource.resourceName }}的学习</h3>
              <p>您已完成{{ resource.resourceName }}的学习，可以继续播放视频，也不会影响学习进度。</p>
              <button class="primary-button primary-button--compact" @click="resumePlayback">点击播放视频</button>
            </div>
          </div>
        </div>
      </article>

      <aside class="video-sidebar">
        <section class="sidebar-card sidebar-card--summary">
          <p class="eyebrow">视频播放</p>
          <h1>{{ resource.resourceName }}</h1>
          <p class="sidebar-card__subtitle">{{ course.kechengName }}</p>
          <div class="stack-inline">
            <span class="tag">{{ resource.resourceType || "视频" }}</span>
            <span class="meta">{{ chapterNameMap[resource.chapterId] || "章节" }}</span>
          </div>
          <div class="status-list status-list--compact">
            <span>当前进度：{{ displayProgressText }}</span>
            <span>章节：{{ chapterNameMap[resource.chapterId] || "Uncategorized" }}</span>
            <span>课时：{{ resource.durationSeconds || 0 }} 秒</span>
          </div>
        </section>

        <section class="sidebar-card">
          <p class="eyebrow">课程信息</p>
          <h2>{{ course.kechengName }}</h2>
          <p>{{ stripHtml(course.kechengContent) }}</p>
          <div class="status-list">
            <span>学分 {{ course.creditScore ?? 0 }}</span>
            <span>教师 {{ course.jiaoshiName || "Teacher pending" }}</span>
          </div>
        </section>

        <section class="sidebar-card">
          <p class="eyebrow">学习说明</p>
          <ul class="info-list">
            <li>视频播放过程中会自动记录学习进度。</li>
            <li>播放完成后再次进入会默认暂停并提示已完成。</li>
            <li>压缩包资源仅支持下载，不影响学习进度。</li>
          </ul>
        </section>

        <section class="sidebar-card">
          <p class="eyebrow">相关资源</p>
          <div class="mini-list mini-list--dense">
            <article v-for="item in relatedResources" :key="item.id" class="mini-list__row">
              <div>
                <strong>{{ item.resourceName }}</strong>
                <p>{{ chapterNameMap[item.chapterId] || "章节" }}</p>
              </div>
              <button class="ghost-button ghost-button--compact" @click="jumpToResource(item.id)">
                {{ item.id === resource.id ? "当前播放" : isVideoResource(item) ? "切换播放" : "下载" }}
              </button>
            </article>
          </div>
        </section>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
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
  fetchCourseChapterPage,
  fetchCourseDetail,
  fetchCourseResourceDetail,
  fetchCourseResourcePage,
  fetchStudyProgressPage,
  saveStudyProgress
} from "@/api/content";
import { showUiToast } from "@/composables/uiToast";
import { useSessionStore } from "@/stores/session";

const route = useRoute();
const router = useRouter();
const session = useSessionStore();
const course = ref<CourseItem | null>(null);
const resource = ref<CourseResourceItem | null>(null);
const chapters = ref<CourseChapterItem[]>([]);
const resources = ref<CourseResourceItem[]>([]);
const progress = ref<StudyProgressItem | null>(null);
const videoRef = ref<HTMLVideoElement | null>(null);
const sourceIndex = ref(0);
const lastSavedSeconds = ref(0);
const overlayDismissed = ref(false);
const pendingSeekSeconds = ref(0);
const saving = ref(false);

const chapterNameMap = computed(() => Object.fromEntries(chapters.value.map((item) => [item.id, item.chapterName])));
const relatedResources = computed(() => resources.value.filter((item) => item.chapterId === resource.value?.chapterId));
const sourceCandidates = computed(() => buildMediaCandidates(resource.value?.resourceUrl));
const activeVideoUrl = computed(() => sourceCandidates.value[sourceIndex.value] || "");
const storedProgressPercent = computed(() => {
  if (progress.value?.isCompleted === 1) {
    return 100;
  }
  const studySeconds = Number(progress.value?.studySeconds || 0);
  const durationSeconds = Number(resource.value?.durationSeconds || 0);
  if (durationSeconds > 0 && studySeconds > 0) {
    return Math.min(100, (studySeconds * 100) / durationSeconds);
  }
  return Math.max(0, Number(progress.value?.progressPercent || 0));
});
const completedMode = computed(() => Boolean(progress.value?.isCompleted === 1 || storedProgressPercent.value >= 100));
const showCompletedOverlay = computed(() => completedMode.value && !overlayDismissed.value);
const currentProgressPercent = computed(() => {
  if (completedMode.value) {
    return 100;
  }
  const mediaDuration = Number(resource.value?.durationSeconds || videoRef.value?.duration || 0);
  const storedPercent = Math.floor(storedProgressPercent.value || 0);
  if (mediaDuration > 0 && videoRef.value) {
    const currentTime = Number(videoRef.value.currentTime || 0);
    const livePercent = Math.floor((currentTime * 100) / mediaDuration);
    if (videoRef.value.ended || currentTime >= Math.max(0, mediaDuration - 0.25) || livePercent >= 100) {
      return 100;
    }
    return Math.max(storedPercent, Math.min(99, livePercent));
  }
  return Math.min(99, storedPercent);
});
const displayProgressText = computed(() => `${currentProgressPercent.value}%`);

function listOf<T>(value: { list?: T[] } | null | undefined) {
  return Array.isArray(value?.list) ? value.list : [];
}

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/800x480/f3d8c5/1c2430&text=Video";
}

function downloadUrl(fileName?: string) {
  return createDownloadUrl(DEFAULT_BASE_URL, fileName);
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").trim() || "暂无课程介绍";
}

function isVideoResource(item: CourseResourceItem) {
  const type = item.resourceType || "";
  const url = item.resourceUrl || "";
  return type.includes("视频") || /\.(mp4|m3u8|webm|mov)$/i.test(url);
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

  const assetCandidate = createAssetUrl(DEFAULT_BASE_URL, normalized);
  const contextCandidate = createAssetUrl(DEFAULT_BASE_URL, contextFreeValue);
  if (assetCandidate) {
    candidates.add(assetCandidate);
  }
  if (contextCandidate) {
    candidates.add(contextCandidate);
  }
  candidates.add(downloadUrl(normalized));
  if (fileName && fileName !== normalized) {
    candidates.add(downloadUrl(fileName));
  }

  return Array.from(candidates).filter(Boolean);
}

async function loadPage() {
  window.scrollTo({ top: 0, behavior: "auto" });
  sourceIndex.value = 0;
  overlayDismissed.value = false;
  pendingSeekSeconds.value = 0;
  progress.value = null;
  const [coursePage, chapterPage, resourcePage, progressPage] = await Promise.all([
    fetchCourseDetail(route.params.courseId as string),
    fetchCourseChapterPage({ kechengId: route.params.courseId }),
    fetchCourseResourcePage({ kechengId: route.params.courseId }),
    fetchStudyProgressPage({ kechengId: route.params.courseId, resourceId: route.params.resourceId })
  ]);
  course.value = coursePage;
  chapters.value = listOf(chapterPage);
  resources.value = listOf(resourcePage);
  progress.value = listOf(progressPage)[0] || null;
  resource.value = await fetchCourseResourceDetail(route.params.resourceId as string);
  pendingSeekSeconds.value = progress.value?.isCompleted === 1 ? 0 : Math.max(0, Math.floor(progress.value?.studySeconds || 0));
  lastSavedSeconds.value = pendingSeekSeconds.value;
  overlayDismissed.value = completedMode.value;
  await nextTick();
  applyVideoState();
}

function applyVideoState() {
  if (!videoRef.value) {
    return;
  }
  if (completedMode.value) {
    videoRef.value.pause();
    try {
      videoRef.value.currentTime = 0;
    } catch {
      // ignore seek failure
    }
    return;
  }
  try {
    videoRef.value.currentTime = pendingSeekSeconds.value;
  } catch {
    // metadata may not be ready yet
  }
  void videoRef.value.play().catch(() => {
    // autoplay may be blocked; the user can press play manually
  });
}

async function ensureSaved(forceCompleted = false) {
  if (!session.isLoggedIn || !resource.value || completedMode.value) {
    return;
  }
  if (!videoRef.value) {
    return;
  }
  const currentSeconds = Math.floor(videoRef.value.currentTime || 0);
  const studySeconds = Math.max(lastSavedSeconds.value, currentSeconds);
  if (!forceCompleted && studySeconds <= lastSavedSeconds.value) {
    return;
  }
  saving.value = true;
  try {
    const payload: Record<string, unknown> = {
      resourceId: resource.value.id,
      studySeconds: forceCompleted ? Math.floor(videoRef.value.duration || resource.value.durationSeconds || studySeconds) : studySeconds,
      progressPercent: forceCompleted ? 100 : undefined,
      forceCompleted: forceCompleted ? 1 : 0
    };
    const result = await saveStudyProgress(payload);
    if (result.code !== 0) {
      throw new Error(result.msg || "记录学习进度失败");
    }
    lastSavedSeconds.value = studySeconds;
    progress.value = {
      ...(progress.value || {}),
      resourceId: resource.value.id,
      studySeconds: studySeconds,
      progressPercent: forceCompleted ? 100 : Math.min(99.5, Math.max(storedProgressPercent.value, (studySeconds * 100) / Math.max(1, resource.value.durationSeconds || 1))),
      isCompleted: forceCompleted ? 1 : 0
    } as StudyProgressItem;
  } finally {
    saving.value = false;
  }
}

async function handleLoadedMetadata() {
  if (!videoRef.value) {
    return;
  }
  if (completedMode.value) {
    videoRef.value.pause();
    overlayDismissed.value = false;
    try {
      videoRef.value.currentTime = 0;
    } catch {
      // ignore
    }
    return;
  }
  try {
    videoRef.value.currentTime = pendingSeekSeconds.value;
  } catch {
    // wait for the browser to finish seeking
  }
  await nextTick();
  void videoRef.value.play().catch(() => {
    // leave the player ready for manual play
  });
}

function handlePlay() {
  overlayDismissed.value = true;
}

async function handleTimeUpdate() {
  if (completedMode.value || !videoRef.value) {
    return;
  }
  const currentSeconds = Math.floor(videoRef.value.currentTime || 0);
  const mediaDuration = Number(videoRef.value.duration || resource.value?.durationSeconds || 0);
  if (mediaDuration > 0 && (videoRef.value.ended || videoRef.value.currentTime >= Math.max(0, mediaDuration - 0.25))) {
    await handleEnded();
    return;
  }
  if (currentSeconds - lastSavedSeconds.value < 5) {
    return;
  }
  pendingSeekSeconds.value = currentSeconds;
  await ensureSaved(false);
}

async function handlePause() {
  await ensureSaved(false);
}

async function handleEnded() {
  if (!resource.value) {
    return;
  }
  pendingSeekSeconds.value = 0;
  await ensureSaved(true);
  overlayDismissed.value = false;
}

async function handleError() {
  if (!resource.value) {
    return;
  }
  if (sourceIndex.value < sourceCandidates.value.length - 1) {
    sourceIndex.value += 1;
    await nextTick();
    applyVideoState();
    return;
  }
  showUiToast("Current video URL cannot be played. Please check the resource path.", "error");
}

function resumePlayback() {
  overlayDismissed.value = true;
  void videoRef.value?.play().catch(() => {
    // manual play is available
  });
}

function jumpToResource(resourceId: number) {
  if (!resource.value) {
    return;
  }
  const target = resources.value.find((item) => item.id === resourceId);
  if (!target) {
    return;
  }
  if (isVideoResource(target)) {
    if (target.id === resource.value.id) {
      return;
    }
    router.push({
      name: "course-video",
      params: { courseId: route.params.courseId, resourceId: target.id }
    });
    return;
  }
  window.open(downloadUrl(target.resourceUrl), "_blank");
}

onBeforeUnmount(() => {
  void ensureSaved(completedMode.value);
});

onMounted(() => {
  window.scrollTo({ top: 0, behavior: "auto" });
});

watch(
  () => [route.params.courseId, route.params.resourceId],
  async () => {
    await ensureSaved(false);
    await loadPage();
  }
);

loadPage();
</script>

<style scoped>
.video-course-page {
  display: grid;
  gap: 18px;
}

.video-course-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(340px, 0.8fr);
  gap: 18px;
  align-items: stretch;
}

.video-stage,
.video-sidebar {
  display: grid;
  gap: 12px;
}

.video-stage {
  padding: 0;
  border-radius: 28px;
  background: transparent;
  box-shadow: none;
}

.video-player-shell {
  position: relative;
  border-radius: 28px;
  overflow: hidden;
  background: #0c1117;
  min-height: 420px;
  height: 100%;
}

.video-player {
  width: 100%;
  height: 100%;
  min-height: 420px;
  object-fit: contain;
  background: #000;
}

.video-overlay {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(8, 11, 16, 0.42);
  backdrop-filter: blur(3px);
}

.video-overlay__card {
  max-width: 420px;
  width: 100%;
  padding: 28px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.25);
  text-align: center;
}

.video-sidebar {
  align-self: stretch;
  height: 100%;
  grid-template-rows: auto auto auto minmax(0, 1fr);
}

.sidebar-card {
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 50px rgba(24, 27, 34, 0.1);
}

.sidebar-card--summary {
  display: grid;
  gap: 8px;
}

.sidebar-card__subtitle {
  margin: 0;
  color: var(--muted-strong);
}

.sidebar-card h1,
.sidebar-card h2 {
  margin-bottom: 8px;
}

.sidebar-card p {
  margin: 0;
}

.status-list {
  gap: 8px;
}

.status-list--compact {
  gap: 6px;
}

.info-list {
  margin: 0;
  padding-left: 18px;
  color: var(--muted);
}

.info-list li + li {
  margin-top: 6px;
}

.mini-list--dense {
  gap: 8px;
}

.mini-list__row p {
  margin-top: 4px;
}

.video-sidebar .sidebar-card:last-child {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
}

.video-sidebar .sidebar-card:last-child .mini-list {
  align-content: start;
}

@media (max-width: 1024px) {
  .video-course-layout {
    grid-template-columns: 1fr;
  }

  .video-sidebar {
    height: auto;
    grid-template-rows: none;
  }
}
</style>
