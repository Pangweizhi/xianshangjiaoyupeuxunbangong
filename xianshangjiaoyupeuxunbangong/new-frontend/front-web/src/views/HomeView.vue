<template>
  <section class="home-banner" v-if="bannerImages.length">
    <div class="home-banner__viewport">
      <button
        v-if="bannerImages.length > 1"
        class="home-banner__arrow home-banner__arrow--left"
        type="button"
        aria-label="上一张轮播图"
        @click="prevBanner"
      >
        <span>‹</span>
      </button>

      <img
        v-for="(image, index) in bannerImages"
        :key="`${image}-${index}`"
        :src="toAsset(image, '轮播图')"
        :class="['home-banner__image', 'media-fit-contain', { 'is-active': index === activeBanner }]"
        :alt="`轮播图 ${index + 1}`"
      />

      <button
        v-if="bannerImages.length > 1"
        class="home-banner__arrow home-banner__arrow--right"
        type="button"
        aria-label="下一张轮播图"
        @click="nextBanner"
      >
        <span>›</span>
      </button>
    </div>

    <div class="home-banner__dots">
      <button
        v-for="(_, index) in bannerImages"
        :key="index"
        :class="['home-banner__dot', { 'is-active': index === activeBanner }]"
        @click="activeBanner = index"
        :aria-label="`切换到第 ${index + 1} 张轮播图`"
      />
    </div>
  </section>

  <section class="hero">
    <div class="hero__copy">
      <h1>学习内容一屏聚合</h1>
      <div class="hero__actions">
        <RouterLink class="primary-button" to="/courses">进入课程</RouterLink>
        <RouterLink class="ghost-button" to="/my-courses">进入我的课程</RouterLink>
      </div>

      <div class="hero__signals">
        <article class="signal-card">
          <span>课程更新</span>
          <strong>{{ courses.length }}</strong>
          <small>当前可浏览课程</small>
        </article>
        <article class="signal-card">
          <span>作业任务</span>
          <strong>{{ homeworks.length }}</strong>
          <small>已发布作业</small>
        </article>
        <article class="signal-card">
          <span>论坛主题</span>
          <strong>{{ forums.length }}</strong>
          <small>最近讨论</small>
        </article>
      </div>
    </div>

    <aside class="hero__panel">
      <div class="hero__panel-card hero__panel-card--accent">
        <span class="meta-label">今日导览</span>
        <h2>先看课程，再看公告和作业。</h2>
        <p>首页信息压缩到更短的链路，减少视觉拖沓，保留必要入口。</p>
      </div>
        <div class="hero__panel-card">
          <div class="metric-card">
            <strong>{{ notices.length }}</strong>
            <span>最新公告</span>
          </div>
          <div class="metric-card">
            <strong>{{ meetings.length }}</strong>
            <span>会议通知</span>
          </div>
      </div>
    </aside>
  </section>

  <section class="section section--flush">
    <div class="section__header">
      <div>
        <p class="eyebrow">快捷入口</p>
        <h2>公共入口与学习入口分组展示</h2>
      </div>
    </div>
    <div class="shortcut-columns">
      <section class="shortcut-panel">
        <div class="shortcut-panel__head">
          <span class="tag">公共服务</span>
        </div>
        <div class="shortcut-grid shortcut-grid--dual shortcut-grid--compact">
          <RouterLink class="shortcut-card" to="/">
            <strong>首页</strong>
          </RouterLink>
          <RouterLink class="shortcut-card" to="/courses">
            <strong>课程</strong>
          </RouterLink>
          <RouterLink class="shortcut-card" to="/notices">
            <strong>公告</strong>
          </RouterLink>
          <RouterLink class="shortcut-card" to="/forum">
            <strong>论坛</strong>
          </RouterLink>
        </div>
      </section>

      <section class="shortcut-panel shortcut-panel--study">
        <div class="shortcut-panel__head">
          <span class="tag">我的学习</span>
        </div>
        <div class="shortcut-grid shortcut-grid--dual shortcut-grid--compact">
          <RouterLink class="shortcut-card" to="/my-courses">
            <strong>我的课程</strong>
            <p>章节和学习资源都在课程详情里查看。</p>
          </RouterLink>
          <RouterLink class="shortcut-card" to="/homeworks">
            <strong>作业</strong>
            <p>按课程查看待完成任务。</p>
          </RouterLink>
          <RouterLink class="shortcut-card" to="/exams">
            <strong>考试</strong>
            <p>成绩归集在考试结果中查看。</p>
          </RouterLink>
          <RouterLink class="shortcut-card" to="/meetings">
            <strong>会议</strong>
          </RouterLink>
          <RouterLink class="shortcut-card" to="/center">
            <strong>个人中心</strong>
          </RouterLink>
        </div>
      </section>
    </div>
  </section>

  <section class="section">
    <div class="section__header">
      <div>
        <p class="eyebrow">重点内容</p>
        <h2>课程推荐与最新公告</h2>
      </div>
      <RouterLink class="text-link" to="/notices">查看全部公告</RouterLink>
    </div>

    <div class="spotlight-grid">
      <article class="spotlight-card" v-if="highlightCourse">
        <img
          :src="toAsset(highlightCourse.kechengPhoto, '课程')"
          :alt="highlightCourse.kechengName"
          class="media-fit-contain media-fit-contain--course"
        />
        <div class="spotlight-card__body">
          <div class="stack-inline">
            <span class="tag">{{ highlightCourse.kechengValue || "课程" }}</span>
            <span class="meta">{{ highlightCourse.jiaoshiName || "课程讲师" }}</span>
          </div>
          <h3>{{ highlightCourse.kechengName }}</h3>
          <p>{{ stripHtml(highlightCourse.kechengContent, 110, "课程详情待补充") }}</p>
          <div class="stack-inline">
            <span class="meta">时长 {{ highlightCourse.kechengShichang || 0 }} 分钟</span>
            <span class="meta">{{ formatDate(highlightCourse.kechengTime) }}</span>
          </div>
        </div>
      </article>

      <div class="stream-panel">
        <article v-for="notice in notices.slice(0, 4)" :key="notice.id" class="stream-row">
          <div>
            <div class="stack-inline">
              <span class="tag">{{ notice.newsValue || "公告" }}</span>
              <span class="meta">{{ formatDate(notice.insertTime) }}</span>
            </div>
            <h3>{{ notice.newsName }}</h3>
            <p>{{ stripHtml(notice.newsContent, 72, "暂无公告摘要") }}</p>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import {
  DEFAULT_BASE_URL,
  createAssetUrl,
  type ConfigItem,
  type CourseItem,
  type ForumItem,
  type HomeworkItem,
  type MeetingItem,
  type NoticeItem
} from "@shared/index";
import {
  fetchConfigList,
  fetchCoursePage,
  fetchForumPage,
  fetchHomeworkPage,
  fetchMeetingPage,
  fetchNoticePage
} from "@/api/content";

const courses = ref<CourseItem[]>([]);
const notices = ref<NoticeItem[]>([]);
const homeworks = ref<HomeworkItem[]>([]);
const forums = ref<ForumItem[]>([]);
const meetings = ref<MeetingItem[]>([]);
const bannerImages = ref<string[]>([]);
const activeBanner = ref(0);

const highlightCourse = computed(() => courses.value[0] || null);

let timer: number | undefined;

function toAsset(path?: string, text = "Course") {
  return createAssetUrl(DEFAULT_BASE_URL, path) || `https://dummyimage.com/1200x420/f4e4d2/1c2430&text=${encodeURIComponent(text)}`;
}

function stripHtml(value: string | undefined, limit: number, fallback: string) {
  return value?.replace(/<[^>]+>/g, "").trim().slice(0, limit) || fallback;
}

function formatDate(value?: string) {
  return value?.slice(0, 10) || "待更新";
}

function parseBannerImages(configs: ConfigItem[]) {
  const images = configs.flatMap((item) =>
    item.value
      .split(/[\n,，]/)
      .map((entry) => entry.trim())
      .filter((entry) => /\.(png|jpe?g|gif|webp|bmp)$/i.test(entry))
  );
  bannerImages.value = [...new Set(images)];
}

function startBannerLoop() {
  if (timer || bannerImages.value.length <= 1) {
    return;
  }
  timer = window.setInterval(() => {
    activeBanner.value = (activeBanner.value + 1) % bannerImages.value.length;
  }, 3600);
}

function prevBanner() {
  if (!bannerImages.value.length) {
    return;
  }
  activeBanner.value =
    (activeBanner.value - 1 + bannerImages.value.length) % bannerImages.value.length;
}

function nextBanner() {
  if (!bannerImages.value.length) {
    return;
  }
  activeBanner.value = (activeBanner.value + 1) % bannerImages.value.length;
}

onMounted(async () => {
  try {
    const [configPage, coursePage, noticePage, homeworkPage, forumPage, meetingPage] =
      await Promise.all([
        fetchConfigList(),
        fetchCoursePage(),
        fetchNoticePage(),
        fetchHomeworkPage(),
        fetchForumPage(),
        fetchMeetingPage()
      ]);

    parseBannerImages(configPage.list);
    courses.value = coursePage.list;
    notices.value = noticePage.list;
    homeworks.value = homeworkPage.list;
    forums.value = forumPage.list;
    meetings.value = Array.isArray(meetingPage?.list) ? meetingPage.list : [];
    startBannerLoop();
  } catch (error) {
    console.error(error);
  }
});

onBeforeUnmount(() => {
  if (timer) {
    window.clearInterval(timer);
  }
});
</script>

<style scoped>
.home-banner {
  margin-top: 28px;
  border-radius: 32px;
  overflow: hidden;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: var(--shadow-soft);
}

.home-banner__viewport {
  position: relative;
  min-height: 340px;
  background:
    radial-gradient(circle at top left, rgba(255, 122, 26, 0.16), transparent 28%),
    radial-gradient(circle at top right, rgba(26, 78, 216, 0.14), transparent 26%),
    linear-gradient(135deg, rgba(255, 248, 240, 0.9), rgba(238, 245, 255, 0.94));
}

.home-banner__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.home-banner__image.is-active {
  opacity: 1;
}

.home-banner__arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.82);
  color: var(--primary-deep);
  font-size: 1.9rem;
  line-height: 1;
  box-shadow: 0 12px 28px rgba(31, 41, 55, 0.16);
  cursor: pointer;
  backdrop-filter: blur(12px);
  transition:
    transform 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
}

.home-banner__arrow:hover {
  transform: translateY(-50%) scale(1.04);
  background: #ffffff;
  box-shadow: 0 14px 32px rgba(31, 41, 55, 0.18);
}

.home-banner__arrow--left {
  left: 18px;
}

.home-banner__arrow--right {
  right: 18px;
}

.home-banner__dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 12px 16px 14px;
}

.home-banner__dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: rgba(22, 32, 51, 0.18);
}

.home-banner__dot.is-active {
  background: var(--primary);
}

.shortcut-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.shortcut-panel {
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: var(--surface);
  box-shadow: var(--shadow-soft);
  padding: 18px;
}

.shortcut-panel__head {
  margin-bottom: 10px;
}

.shortcut-panel--study .shortcut-panel__head {
  margin-top: -6px;
}

.shortcut-grid--dual {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.shortcut-grid--compact {
  gap: 12px;
}

.shortcut-grid--compact .shortcut-card {
  padding: 18px;
}

.shortcut-grid--compact .shortcut-card p {
  margin-top: 8px;
}

.hero {
  gap: 18px;
}

.hero__copy {
  padding: 40px 38px 30px;
}

.hero__signals {
  margin-top: 18px;
  gap: 12px;
}

.hero__signals .signal-card {
  padding: 16px 16px 14px;
}

.hero__panel-card {
  padding: 20px;
}

.hero__panel {
  gap: 14px;
}

@media (max-width: 1120px) {
  .shortcut-columns,
  .shortcut-grid--dual {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .home-banner__arrow {
    width: 40px;
    height: 40px;
    font-size: 1.7rem;
  }

  .home-banner__arrow--left {
    left: 12px;
  }

  .home-banner__arrow--right {
    right: 12px;
  }
}
</style>
