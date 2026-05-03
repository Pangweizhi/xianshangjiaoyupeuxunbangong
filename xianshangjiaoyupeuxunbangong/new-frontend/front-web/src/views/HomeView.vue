<template>
  <section class="home-banner" v-if="bannerImages.length">
    <div class="home-banner__viewport">
      <img
        v-for="(image, index) in bannerImages"
        :key="`${image}-${index}`"
        :src="toAsset(image, '轮播图')"
        :class="['home-banner__image', { 'is-active': index === activeBanner }]"
        :alt="`轮播图 ${index + 1}`"
      />
    </div>
    <div class="home-banner__dots">
      <button
        v-for="(_, index) in bannerImages"
        :key="index"
        :class="['home-banner__dot', { 'is-active': index === activeBanner }]"
        @click="activeBanner = index"
      />
    </div>
  </section>

  <section class="hero">
    <div class="hero__copy">
      <h1>课程、公告、作业和论坛，在一个首页里顺序展开。</h1>
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
      </div>
      <div class="hero__panel-card">
        <div class="metric-card">
          <strong>{{ notices.length }}</strong>
          <span>最新公告</span>
        </div>
        <div class="metric-card">
          <strong>{{ materials.length }}</strong>
          <span>备课资料</span>
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
        <h2>公共入口与学习入口分开展示</h2>
      </div>
    </div>
    <div class="shortcut-columns">
      <section class="shortcut-panel">
        <div class="shortcut-panel__head">
          <span class="tag">公共功能</span>
        </div>
        <div class="shortcut-grid shortcut-grid--dual">
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
          <RouterLink class="shortcut-card" to="/materials">
            <strong>备课</strong>
          </RouterLink>
        </div>
      </section>

      <section class="shortcut-panel">
        <div class="shortcut-panel__head">
          <span class="tag">我的学习</span>
        </div>
        <div class="shortcut-grid shortcut-grid--dual">
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
        <img :src="toAsset(highlightCourse.kechengPhoto, '课程') " :alt="highlightCourse.kechengName" />
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
  type LessonMaterialItem,
  type MeetingItem,
  type NoticeItem
} from "@shared/index";
import {
  fetchConfigList,
  fetchCoursePage,
  fetchForumPage,
  fetchHomeworkPage,
  fetchMaterialPage,
  fetchMeetingPage,
  fetchNoticePage
} from "@/api/content";

const courses = ref<CourseItem[]>([]);
const notices = ref<NoticeItem[]>([]);
const homeworks = ref<HomeworkItem[]>([]);
const forums = ref<ForumItem[]>([]);
const materials = ref<LessonMaterialItem[]>([]);
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

onMounted(async () => {
  try {
    const [configPage, coursePage, noticePage, homeworkPage, forumPage, materialPage, meetingPage] =
      await Promise.all([
        fetchConfigList(),
        fetchCoursePage(),
        fetchNoticePage(),
        fetchHomeworkPage(),
        fetchForumPage(),
        fetchMaterialPage(),
        fetchMeetingPage()
      ]);

    parseBannerImages(configPage.list);
    courses.value = coursePage.list;
    notices.value = noticePage.list;
    homeworks.value = homeworkPage.list;
    forums.value = forumPage.list;
    materials.value = materialPage.list;
    meetings.value = meetingPage.list;
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
}

.home-banner__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.home-banner__image.is-active {
  opacity: 1;
}

.home-banner__dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 16px;
}

.home-banner__dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(22, 32, 51, 0.18);
}

.home-banner__dot.is-active {
  background: var(--primary);
}

.shortcut-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.shortcut-panel {
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: var(--surface);
  box-shadow: var(--shadow-soft);
  padding: 20px;
}

.shortcut-panel__head {
  margin-bottom: 14px;
}

.shortcut-grid--dual {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (max-width: 1120px) {
  .shortcut-columns,
  .shortcut-grid--dual {
    grid-template-columns: 1fr;
  }
}
</style>
