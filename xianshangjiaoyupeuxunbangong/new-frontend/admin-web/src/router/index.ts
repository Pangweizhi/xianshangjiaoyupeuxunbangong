import { createRouter, createWebHistory } from "vue-router";
import AdminLayout from "@/layouts/AdminLayout.vue";
import LoginView from "@/views/LoginView.vue";
import DashboardView from "@/views/DashboardView.vue";
import CourseManageView from "@/views/CourseManageView.vue";
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
        { path: "courses", name: "courses", component: CourseManageView },
        { path: "notices", name: "notices", component: NoticeManageView },
        { path: "students", name: "students", component: StudentsManageView },
        { path: "teachers", name: "teachers", component: TeachersManageView },
        { path: "dictionary", name: "dictionary", component: DictionaryManageView },
        { path: "config", name: "config", component: ConfigManageView },
        { path: "homeworks", name: "homeworks", component: HomeworkManageView },
        { path: "forums", name: "forums", component: ForumManageView },
        { path: "materials", name: "materials", component: MaterialManageView },
        { path: "meetings", name: "meetings", component: MeetingManageView },
        { path: "submissions", name: "submissions", component: HomeworkSubmissionManageView }
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
