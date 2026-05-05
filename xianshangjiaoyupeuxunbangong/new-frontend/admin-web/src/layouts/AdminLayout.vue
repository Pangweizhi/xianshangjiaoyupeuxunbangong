<template>
  <div class="admin-shell">
    <aside class="admin-aside">
      <div class="admin-brand">
        <div class="admin-brand__mark"></div>
        <div>
          <p class="admin-brand__eyebrow">Creator Workspace</p>
          <strong>线上教育培训系统后台</strong>
        </div>
      </div>

      <div class="admin-aside__meta">
        <span class="admin-aside__pill">{{ store.displayRole }}</span>
      </div>

      <div v-for="group in visibleNavGroups" :key="group.label" class="admin-nav-group">
        <span class="admin-nav-group__label">{{ group.label }}</span>
        <RouterLink
          v-for="item in group.items"
          :key="item.to"
          :class="item.className"
          :to="item.to"
        >
          {{ item.label }}
        </RouterLink>
      </div>
    </aside>

    <div class="admin-main">
      <header class="admin-header">
        <div class="admin-header__intro">
          <p class="admin-header__eyebrow">{{ currentSection }}</p>
          <h1>{{ title }}</h1>
          <p>{{ subtitle }}</p>
        </div>
        <div class="admin-header__actions">
          <span class="admin-header__tag">{{ isTeacher ? "教师视角" : "平台视角" }}</span>
          <el-button plain @click="handleLogout">退出登录</el-button>
        </div>
      </header>

      <section class="admin-content">
        <RouterView :key="route.fullPath" />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";
import { useAdminSessionStore } from "@/stores/session";

type NavGroup = {
  label: string;
  items: Array<{
    label: string;
    to: string;
    className?: string;
    teacherOnly?: boolean;
    adminOnly?: boolean;
  }>;
};

const route = useRoute();
const router = useRouter();
const store = useAdminSessionStore();

const isTeacher = computed(() => store.session?.tableName === "jiaoshi");

const title = computed(() => {
  const titleMap: Record<string, string> = {
    dashboard: "仪表盘",
    profile: "个人中心",
    courses: "课程管理",
    "course-types": "课程类型管理",
    chapters: "章节与资源",
    resources: "资源管理",
    enrolls: "选课管理",
    progress: "学习进度",
    homeworks: "作业管理",
    "homework-types": "作业类型管理",
    exams: "考试管理",
    "exam-questions": "题库管理",
    "exam-records": "阅卷管理",
    submissions: "作业提交记录",
    notices: "公告管理",
    "notice-types": "公告类型管理",
    students: "学生管理",
    teachers: "教师管理",
    dictionary: "字典管理",
    config: "轮播图管理",
    forums: "论坛管理",
    materials: "备课管理",
    meetings: "会议管理"
  };
  return titleMap[String(route.name ?? "dashboard")] || "仪表盘";
});

const subtitleMap: Record<string, string> = {
  dashboard: "查看课程运行、学习进度和考试执行的整体面板。",
  profile: "维护登录账号与个人信息。",
  courses: "统一管理课程基础信息、封面与状态。",
  "course-types": "维护课程类型和分类字典。",
  chapters: "按课程管理章节结构，并紧邻处理配套资源。",
  enrolls: "查看学生选课情况与课程覆盖。",
  progress: "追踪视频学习、完成进度和学习记录。",
  homeworks: "发布与维护课程作业内容。",
  "homework-types": "维护作业类型分类。",
  exams: "按课程组织考试与选题。",
  "exam-questions": "题库默认按课程和题型分类浏览，并支持分页筛选。",
  "exam-records": "处理考试记录、得分和阅卷状态。",
  submissions: "查看学生作业提交、评分与反馈。",
  notices: "维护平台公告与对外通知。",
  "notice-types": "维护公告分类。",
  students: "查看学生账号与班级资料。",
  teachers: "查看教师账号与授课资料。",
  dictionary: "统一维护系统字典与枚举项。",
  config: "管理轮播图等平台展示配置。",
  forums: "维护论坛主题、回复与内容质量。",
  materials: "管理备课资料与教学素材。",
  meetings: "发布和维护会议通知。"
};

const subtitle = computed(() => subtitleMap[String(route.name ?? "dashboard")] || "统一管理后台业务内容。");

const navGroups: NavGroup[] = [
  {
    label: "总览",
    items: [
      { label: "仪表盘", to: "/dashboard" },
      { label: "个人中心", to: "/profile" }
    ]
  },
  {
    label: "课程与教学",
    items: [
      { label: "课程管理", to: "/courses" },
      { label: "课程类型管理", to: "/course-types", className: "admin-subnav__link" },
      { label: "章节与资源", to: "/chapters", teacherOnly: true },
      { label: "选课管理", to: "/enrolls" },
      { label: "学习进度", to: "/progress" },
      { label: "备课管理", to: "/materials" }
    ]
  },
  {
    label: "作业与考试",
    items: [
      { label: "作业管理", to: "/homeworks" },
      { label: "作业类型管理", to: "/homework-types", className: "admin-subnav__link" },
      { label: "考试管理", to: "/exams" },
      { label: "题库管理", to: "/exam-questions" },
      { label: "阅卷管理", to: "/exam-records" },
      { label: "作业提交记录", to: "/submissions" }
    ]
  },
  {
    label: "内容运营",
    items: [
      { label: "论坛管理", to: "/forums" },
      { label: "会议管理", to: "/meetings" },
      { label: "公告管理", to: "/notices", adminOnly: true },
      { label: "公告类型管理", to: "/notice-types", className: "admin-subnav__link", adminOnly: true }
    ]
  },
  {
    label: "平台治理",
    items: [
      { label: "学生管理", to: "/students", adminOnly: true },
      { label: "教师管理", to: "/teachers", adminOnly: true },
      { label: "字典管理", to: "/dictionary", adminOnly: true },
      { label: "轮播图管理", to: "/config", className: "admin-subnav__link", adminOnly: true }
    ]
  }
];

const visibleNavGroups = computed(() =>
  navGroups
    .map((group) => ({
      ...group,
      items: group.items.filter((item) => {
        if (item.teacherOnly) {
          return isTeacher.value;
        }
        if (item.adminOnly) {
          return !isTeacher.value;
        }
        return true;
      })
    }))
    .filter((group) => group.items.length)
);

const currentSection = computed(() => {
  const currentPath = route.path;
  const currentGroup = visibleNavGroups.value.find((group) => group.items.some((item) => currentPath.startsWith(item.to)));
  return currentGroup?.label || "总览";
});

function handleLogout() {
  store.logout();
  router.push({ name: "login" });
}
</script>

<style scoped>
.admin-brand {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 14px;
  align-items: center;
  margin-bottom: 8px;
}

.admin-brand__mark {
  width: 48px;
  height: 48px;
  border-radius: 18px;
  background:
    radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.78), transparent 36%),
    linear-gradient(145deg, #ff9d41, #ff7a1a 52%, #2f65d9 100%);
  box-shadow:
    0 14px 28px rgba(255, 122, 26, 0.24),
    inset 0 1px 0 rgba(255, 255, 255, 0.36);
}

.admin-brand__eyebrow {
  margin: 0 0 4px;
  color: rgba(89, 61, 31, 0.64);
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.admin-aside__meta {
  display: grid;
  gap: 10px;
  margin-bottom: 14px;
  padding: 16px 18px;
  border-radius: 22px;
  background: rgba(255, 250, 244, 0.74);
  border: 1px solid rgba(255, 255, 255, 0.56);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.52);
}

.admin-aside__pill,
.admin-header__tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
}

.admin-aside__pill {
  justify-self: start;
  background: rgba(47, 101, 217, 0.1);
  color: #2752ae;
}

.admin-aside__caption {
  color: rgba(90, 47, 8, 0.76);
  font-size: 0.9rem;
  line-height: 1.6;
}

.admin-header__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.admin-nav-group {
  margin-top: 4px;
  display: grid;
  gap: 8px;
  padding: 14px 12px 0;
  border-top: 1px solid rgba(111, 60, 11, 0.1);
}

.admin-nav-group__label {
  padding: 0 8px 2px;
  color: rgba(90, 47, 8, 0.58);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.admin-subnav__link {
  margin-left: 12px;
}

.admin-header__intro {
  display: grid;
  gap: 6px;
}

.admin-header__eyebrow {
  margin: 0;
  color: var(--admin-muted);
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.admin-header__intro h1 {
  margin: 0;
}

.admin-header__intro p {
  margin: 0;
}

.admin-header__tag {
  background: rgba(255, 122, 26, 0.12);
  color: #b95a16;
}

</style>
