import { createRouter, createWebHistory } from "vue-router";
import PublicLayout from "@/layouts/PublicLayout.vue";
import HomeView from "@/views/HomeView.vue";
import LoginView from "@/views/LoginView.vue";
import CoursesView from "@/views/CoursesView.vue";
import CourseDetailView from "@/views/CourseDetailView.vue";
import CourseVideoView from "@/views/CourseVideoView.vue";
import NoticesView from "@/views/NoticesView.vue";
import HomeworksView from "@/views/HomeworksView.vue";
import ExamsView from "@/views/ExamsView.vue";
import ExamDetailView from "@/views/ExamDetailView.vue";
import MyScoresView from "@/views/MyScoresView.vue";
import ForumView from "@/views/ForumView.vue";
import MeetingsView from "@/views/MeetingsView.vue";
import HomeworkDetailView from "@/views/HomeworkDetailView.vue";
import ForumDetailView from "@/views/ForumDetailView.vue";
import MeetingDetailView from "@/views/MeetingDetailView.vue";
import CenterView from "@/views/CenterView.vue";
import MyCoursesView from "@/views/MyCoursesView.vue";
import AiChatView from "@/views/AiChatView.vue";
import { useSessionStore } from "@/stores/session";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: PublicLayout,
      children: [
        { path: "", name: "home", component: HomeView },
        { path: "courses", name: "courses", component: CoursesView },
        { path: "courses/:id", name: "course-detail", component: CourseDetailView, meta: { requiresAuth: true } },
        { path: "courses/:courseId/video/:resourceId", name: "course-video", component: CourseVideoView, meta: { requiresAuth: true } },
        { path: "my-courses", name: "my-courses", component: MyCoursesView, meta: { requiresAuth: true } },
        { path: "notices", name: "notices", component: NoticesView },
        { path: "homeworks", name: "homeworks", component: HomeworksView },
        { path: "homeworks/:id", name: "homework-detail", component: HomeworkDetailView, meta: { requiresAuth: true } },
        { path: "exams", name: "exams", component: ExamsView },
        { path: "exams/:id", name: "exam-detail", component: ExamDetailView, meta: { requiresAuth: true } },
        { path: "my-scores", name: "my-scores", component: MyScoresView, meta: { requiresAuth: true } },
        { path: "forum", name: "forum", component: ForumView },
        { path: "forum/:id", name: "forum-detail", component: ForumDetailView, meta: { requiresAuth: true } },
        { path: "meetings", name: "meetings", component: MeetingsView },
        { path: "meetings/:id", name: "meeting-detail", component: MeetingDetailView, meta: { requiresAuth: true } },
        {
          path: "center",
          name: "center",
          component: CenterView,
          meta: { requiresAuth: true }
        },
        { path: "ai-chat", name: "ai-chat", component: AiChatView, meta: { requiresAuth: true } }
      ]
    },
    { path: "/login", name: "login", component: LoginView }
  ]
});

router.beforeEach(async (to) => {
  const session = useSessionStore();
  if (session.session) {
    await session.ensureSessionValid();
  }
  if (to.meta.requiresAuth && !session.isLoggedIn) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.name === "login" && session.isLoggedIn) {
    return { name: "center" };
  }
  return true;
});

export default router;
