<template>
  <section class="hero">
    <div class="hero__copy">
      <p class="eyebrow">学习门户</p>
      <h1>把课程、作业、公告与交流整合进一个清晰高效的学习入口。</h1>
      <p class="hero__lead">
        首页聚焦教学信息分发、学习任务追踪和师生互动，帮助学生快速进入学习状态，也方便教师统一组织教学内容。
      </p>
      <div class="hero__actions">
        <RouterLink class="primary-button" to="/courses">浏览课程</RouterLink>
        <RouterLink class="ghost-button" to="/forum">进入论坛</RouterLink>
      </div>

      <div class="hero__signals">
        <article class="signal-card">
          <span>课程更新</span>
          <strong>{{ courses.length }}</strong>
          <small>最新课程内容</small>
        </article>
        <article class="signal-card">
          <span>学习任务</span>
          <strong>{{ homeworks.length }}</strong>
          <small>待查看作业</small>
        </article>
        <article class="signal-card">
          <span>讨论主题</span>
          <strong>{{ forums.length }}</strong>
          <small>交流与答疑</small>
        </article>
      </div>
    </div>

    <aside class="hero__panel">
      <div class="hero__panel-card hero__panel-card--accent">
        <span class="meta-label">今日导览</span>
        <h2>从课程、公告到会议通知，重要信息优先展示。</h2>
        <p>首屏保留最关键的学习入口，减少无关说明和冗余跳转。</p>
      </div>
      <div class="hero__panel-card">
        <div class="metric-card">
          <strong>{{ notices.length }}</strong>
          <span>最新公告</span>
        </div>
        <div class="metric-card">
          <strong>{{ materials.length }}</strong>
          <span>备课资源</span>
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
        <h2>围绕系统核心模块组织学习与办公流程</h2>
      </div>
    </div>
    <div class="shortcut-grid">
      <RouterLink class="shortcut-card" to="/courses">
        <strong>课程中心</strong>
        <p>查看课程安排、授课教师和学习内容。</p>
      </RouterLink>
      <RouterLink class="shortcut-card" to="/homeworks">
        <strong>作业任务</strong>
        <p>快速进入提交入口，跟踪最新批改记录。</p>
      </RouterLink>
      <RouterLink class="shortcut-card" to="/notices">
        <strong>公告通知</strong>
        <p>集中浏览教学公告与校内信息更新。</p>
      </RouterLink>
      <RouterLink class="shortcut-card" to="/materials">
        <strong>备课资源</strong>
        <p>查阅教师上传的资料、附件与课程配套内容。</p>
      </RouterLink>
      <RouterLink class="shortcut-card" to="/meetings">
        <strong>会议日程</strong>
        <p>了解线上会议、教务通知和安排节奏。</p>
      </RouterLink>
      <RouterLink class="shortcut-card" to="/forum">
        <strong>讨论交流</strong>
        <p>围绕课程、作业和问题展开讨论与回复。</p>
      </RouterLink>
    </div>
  </section>

  <section class="section">
    <div class="section__header">
      <div>
        <p class="eyebrow">重点内容</p>
        <h2>课程推荐与最新公告并排呈现</h2>
      </div>
      <RouterLink class="text-link" to="/notices">查看全部公告</RouterLink>
    </div>

    <div class="spotlight-grid">
      <article class="spotlight-card" v-if="highlightCourse">
        <img :src="toAsset(highlightCourse.kechengPhoto, 'Course')" :alt="highlightCourse.kechengName" />
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

  <section class="section">
    <div class="section__header">
      <div>
        <p class="eyebrow">学习动态</p>
        <h2>任务、资料、会议与讨论统一进入信息流</h2>
      </div>
    </div>

    <div class="dashboard-grid">
      <article class="dashboard-card">
        <div class="panel-header">
          <h3>最新作业</h3>
          <RouterLink class="text-link" to="/homeworks">更多</RouterLink>
        </div>
        <div class="mini-list">
          <RouterLink
            v-for="item in homeworks.slice(0, 3)"
            :key="item.id"
            class="mini-list__row"
            :to="`/homeworks/${item.id}`"
          >
            <div>
              <strong>{{ item.zuoyeName }}</strong>
              <p>{{ stripHtml(item.zuoyeContent, 60, "暂无作业说明") }}</p>
            </div>
            <span>{{ formatDate(item.insertTime) }}</span>
          </RouterLink>
        </div>
      </article>

      <article class="dashboard-card">
        <div class="panel-header">
          <h3>备课资料</h3>
          <RouterLink class="text-link" to="/materials">更多</RouterLink>
        </div>
        <div class="mini-list">
          <RouterLink
            v-for="item in materials.slice(0, 3)"
            :key="item.id"
            class="mini-list__row"
            :to="`/materials/${item.id}`"
          >
            <div>
              <strong>{{ item.jiaoxueshipinName }}</strong>
              <p>{{ item.jiaoshiName || "教师发布" }}</p>
            </div>
            <span>{{ formatDate(item.jiaoxueshipinTime) }}</span>
          </RouterLink>
        </div>
      </article>

      <article class="dashboard-card">
        <div class="panel-header">
          <h3>论坛热帖</h3>
          <RouterLink class="text-link" to="/forum">更多</RouterLink>
        </div>
        <div class="mini-list">
          <RouterLink
            v-for="item in forums.slice(0, 3)"
            :key="item.id"
            class="mini-list__row"
            :to="`/forum/${item.id}`"
          >
            <div>
              <strong>{{ item.forumName }}</strong>
              <p>{{ resolveAuthor(item) }}</p>
            </div>
            <span>{{ formatDate(item.insertTime) }}</span>
          </RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import {
  DEFAULT_BASE_URL,
  createAssetUrl,
  type CourseItem,
  type ForumItem,
  type HomeworkItem,
  type LessonMaterialItem,
  type MeetingItem,
  type NoticeItem
} from "@shared/index";
import {
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

const highlightCourse = computed(() => courses.value[0] || null);

function toAsset(path?: string, text = "Course") {
  return createAssetUrl(DEFAULT_BASE_URL, path) || `https://dummyimage.com/800x520/f4e4d2/1c2430&text=${text}`;
}

function stripHtml(value: string | undefined, limit: number, fallback: string) {
  return value?.replace(/<[^>]+>/g, "").trim().slice(0, limit) || fallback;
}

function formatDate(value?: string) {
  return value?.slice(0, 10) || "待更新";
}

function resolveAuthor(item: ForumItem) {
  return item.yonghuName || item.jiaoshiName || item.uusername || "匿名发布";
}

onMounted(async () => {
  try {
    const [coursePage, noticePage, homeworkPage, forumPage, materialPage, meetingPage] =
      await Promise.all([
        fetchCoursePage(),
        fetchNoticePage(),
        fetchHomeworkPage(),
        fetchForumPage(),
        fetchMaterialPage(),
        fetchMeetingPage()
      ]);

    courses.value = coursePage.list;
    notices.value = noticePage.list;
    homeworks.value = homeworkPage.list;
    forums.value = forumPage.list;
    materials.value = materialPage.list;
    meetings.value = meetingPage.list;
  } catch (error) {
    console.error(error);
  }
});
</script>
