import { createRouter, createWebHistory } from "vue-router";
import AdminLayout from "@/layouts/AdminLayout.vue";
import LoginView from "@/views/LoginView.vue";
import DashboardView from "@/views/DashboardView.vue";
import CourseManageView from "@/views/CourseManageView.vue";
import CourseChapterManageView from "@/views/CourseChapterManageView.vue";
import CourseResourceManageView from "@/views/CourseResourceManageView.vue";
import CourseEnrollManageView from "@/views/CourseEnrollManageView.vue";
import StudyProgressManageView from "@/views/StudyProgressManageView.vue";
import ExamManageView from "@/views/ExamManageView.vue";
import ExamQuestionManageView from "@/views/ExamQuestionManageView.vue";
import ExamRecordManageView from "@/views/ExamRecordManageView.vue";
import NoticeManageView from "@/views/NoticeManageView.vue";
import StudentsManageView from "@/views/StudentsManageView.vue";
import TeachersManageView from "@/views/TeachersManageView.vue";
import DictionaryManageView from "@/views/DictionaryManageView.vue";
import ConfigManageView from "@/views/ConfigManageView.vue";
import HomeworkManageView from "@/views/HomeworkManageView.vue";
import ForumManageView from "@/views/ForumManageView.vue";
import MaterialManageView from "@/views/MaterialManageView.vue";
import MeetingManageView from "@/views/MeetingManageView.vue";
import HomeworkSubmissionManageView from "@/views/HomeworkSubmissionManageView.vue";
import AiChatView from "@/views/AiChatView.vue";
import ProfileView from "@/views/ProfileView.vue";
import { useAdminSessionStore } from "@/stores/session";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView },
    {
      path: "/",
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        { path: "", redirect: "/dashboard" },
        { path: "dashboard", name: "dashboard", component: DashboardView },
        { path: "profile", name: "profile", component: ProfileView },
        { path: "courses", name: "courses", component: CourseManageView },
        { path: "chapters", name: "chapters", component: CourseChapterManageView },
        { path: "resources", name: "resources", component: CourseResourceManageView },
        { path: "enrolls", name: "enrolls", component: CourseEnrollManageView },
        { path: "progress", name: "progress", component: StudyProgressManageView },
        { path: "exams", name: "exams", component: ExamManageView },
        { path: "exam-questions", name: "exam-questions", component: ExamQuestionManageView },
        { path: "exam-records", name: "exam-records", component: ExamRecordManageView },
        { path: "notices", name: "notices", component: NoticeManageView },
        { path: "students", name: "students", component: StudentsManageView },
        { path: "teachers", name: "teachers", component: TeachersManageView },
        { path: "dictionary", name: "dictionary", component: DictionaryManageView },
        { path: "config", name: "config", component: ConfigManageView },
        { path: "homeworks", name: "homeworks", component: HomeworkManageView },
        { path: "forums", name: "forums", component: ForumManageView },
        { path: "materials", name: "materials", component: MaterialManageView },
        { path: "meetings", name: "meetings", component: MeetingManageView },
        { path: "submissions", name: "submissions", component: HomeworkSubmissionManageView },
        { path: "ai-chat", name: "ai-chat", component: AiChatView }
      ]
    }
  ]
});

router.beforeEach((to) => {
  const session = useAdminSessionStore();
  if (to.meta.requiresAuth && !session.isLoggedIn) {
    return { name: "login" };
  }
  if (to.name === "login" && session.isLoggedIn) {
    return { name: "dashboard" };
  }
  return true;
});

export default router;
