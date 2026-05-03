<template>
  <section class="section section--tight">
    <div class="profile-shell center-grid">
      <aside class="profile-card">
        <img class="center-avatar" :src="avatarUrl" :alt="form.yonghuName || '学生头像'" />
        <h1>{{ form.yonghuName || session.session?.username || "未命名学生" }}</h1>
        <p>{{ session.displayRole }}</p>
        <div class="profile-card__meta">
          <span>账号 {{ form.username || "-" }}</span>
          <span>学号 {{ form.yonghuIdNumber || "-" }}</span>
          <span>班级 {{ rawProfile?.banjiValue || "-" }}</span>
        </div>
      </aside>

      <section class="profile-panel">
        <div class="panel-header">
          <div>
            <h2>个人信息</h2>
            <p>支持修改姓名、头像、手机号和邮箱。</p>
          </div>
          <button class="primary-button primary-button--compact" :disabled="saving" @click="submitProfile">
            {{ saving ? "保存中..." : "保存信息" }}
          </button>
        </div>

        <div class="filter-grid">
          <label class="field-wrap">
            <span>账号</span>
            <input v-model="form.username" class="field" disabled />
          </label>
          <label class="field-wrap">
            <span>姓名</span>
            <input v-model="form.yonghuName" class="field" placeholder="请输入姓名" />
          </label>
          <label class="field-wrap">
            <span>手机号</span>
            <input v-model="form.yonghuPhone" class="field" placeholder="请输入手机号" />
          </label>
          <label class="field-wrap">
            <span>邮箱</span>
            <input v-model="form.yonghuEmail" class="field" placeholder="请输入邮箱" />
          </label>
        </div>

        <div class="upload-row">
          <div class="avatar-status field-wrap--grow">
            <span>头像状态</span>
            <strong>{{ form.yonghuPhoto ? "已上传头像，可直接保存" : "未上传头像" }}</strong>
          </div>
          <label class="ghost-button upload-button">
            上传头像
            <input type="file" accept="image/*" hidden @change="handleAvatarUpload" />
          </label>
        </div>
      </section>
    </div>

    <section class="section">
      <div class="section__header section__header--stack">
        <div>
          <p class="eyebrow">学习概览</p>
          <h2>课程、作业、考试与学分统计</h2>
        </div>
      </div>

      <div class="dashboard-grid">
        <article v-for="card in cards" :key="card.label" class="dashboard-card">
          <span>{{ card.label }}</span>
          <strong>{{ card.value }}</strong>
          <p>{{ card.hint }}</p>
        </article>
      </div>

      <div class="mini-list">
        <article class="mini-list__row">
          <div>
            <strong>待学课程</strong>
            <p>尚未完成的课程会继续在我的课程和课程详情中推进学习。</p>
          </div>
          <div class="status-list">
            <span>{{ pendingCourseCount }} 门</span>
            <RouterLink class="text-link" to="/my-courses">查看课程</RouterLink>
          </div>
        </article>
        <article class="mini-list__row">
          <div>
            <strong>作业与考试</strong>
            <p>作业和考试都归属于课程，成绩也统一统计到考试记录中。</p>
          </div>
          <div class="status-list">
            <span>作业 {{ homeworkCount }} 份</span>
            <span>考试 {{ examCount }} 场</span>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { DEFAULT_BASE_URL, createAssetUrl, type StudentItem } from "@shared/index";
import {
  fetchHomeworkSubmissions,
  fetchMyCoursePage,
  fetchMyCreditPage,
  fetchMyCoursePerformanceSummary,
  fetchMyExamRecordPage,
  fetchStudentProfile,
  updateStudentProfile,
  uploadFile
} from "@/api/content";
import { showUiToast } from "@/composables/uiToast";
import { useSessionStore } from "@/stores/session";

const session = useSessionStore();
const rawProfile = ref<StudentItem | null>(null);
const saving = ref(false);
const avatarVersion = ref(0);

const form = reactive({
  id: 0,
  username: "",
  yonghuName: "",
  yonghuPhoto: "",
  yonghuPhone: "",
  yonghuEmail: "",
  yonghuIdNumber: ""
});

const stats = reactive({
  pendingCourseCount: 0,
  finishedCourseCount: 0,
  homeworkCount: 0,
  checkedHomeworkCount: 0,
  examCount: 0,
  passedExamCount: 0,
  creditScore: 0
});

const avatarUrl = computed(() => {
  const baseUrl = createAssetUrl(DEFAULT_BASE_URL, form.yonghuPhoto);
  if (!baseUrl) {
    return "https://dummyimage.com/240x240/f4e4d2/1c2430&text=Avatar";
  }
  const separator = baseUrl.includes("?") ? "&" : "?";
  return `${baseUrl}${separator}v=${avatarVersion.value}`;
});

const cards = computed(() => [
  { label: "待学课程", value: stats.pendingCourseCount, hint: "继续在课程详情中学习章节和资源。" },
  { label: "已学课程", value: stats.finishedCourseCount, hint: "已完成或已结课的课程数量。" },
  { label: "待批作业", value: Math.max(stats.homeworkCount - stats.checkedHomeworkCount, 0), hint: "已提交但尚未完成评阅的作业。" },
  { label: "通过考试", value: stats.passedExamCount, hint: "已通过的考试场次。" },
  { label: "累计学分", value: stats.creditScore, hint: "课程结算后的总学分。" },
  { label: "考试总数", value: stats.examCount, hint: "当前已产生记录的考试总数。" }
]);

const pendingCourseCount = computed(() => stats.pendingCourseCount);
const homeworkCount = computed(() => stats.homeworkCount);
const examCount = computed(() => stats.examCount);

function listOf<T>(value: { list?: T[] } | null | undefined) {
  return Array.isArray(value?.list) ? value.list : [];
}

function assignProfile(profile: StudentItem) {
  rawProfile.value = profile;
  form.id = profile.id;
  form.username = profile.username || "";
  form.yonghuName = profile.yonghuName || "";
  form.yonghuPhoto = profile.yonghuPhoto || "";
  form.yonghuPhone = profile.yonghuPhone || "";
  form.yonghuEmail = profile.yonghuEmail || "";
  form.yonghuIdNumber = profile.yonghuIdNumber || "";
  avatarVersion.value += 1;
}

async function loadPage() {
  const results = await Promise.allSettled([
    fetchStudentProfile(),
    fetchMyCoursePage({ limit: 100 }),
    fetchMyCreditPage({ limit: 100 }),
    fetchHomeworkSubmissions({ limit: 100 }),
    fetchMyExamRecordPage({ limit: 100 }),
    fetchMyCoursePerformanceSummary()
  ]);

  const profile = results[0].status === "fulfilled" ? results[0].value : null;
  const myCourses = results[1].status === "fulfilled" ? results[1].value : null;
  const credits = results[2].status === "fulfilled" ? results[2].value : null;
  const submissions = results[3].status === "fulfilled" ? results[3].value : null;
  const examRecords = results[4].status === "fulfilled" ? results[4].value : null;
  const summary = results[5].status === "fulfilled" ? results[5].value : null;

  if (profile) {
    assignProfile(profile);
  }

  const courseList = listOf(myCourses);
  const creditList = listOf(credits);
  const submissionList = listOf(submissions);
  const examRecordList = listOf(examRecords);

  stats.pendingCourseCount = courseList.filter((item) => (item.progressPercent || 0) < 100).length;
  stats.finishedCourseCount = courseList.filter((item) => (item.progressPercent || 0) >= 100 || item.finishTime).length;
  stats.homeworkCount = submissionList.length;
  stats.checkedHomeworkCount = submissionList.filter((item) => item.submitScore !== null && item.submitScore !== undefined).length;
  stats.examCount = examRecordList.length;
  stats.passedExamCount = examRecordList.filter((item) => item.passStatus === "通过").length;
  stats.creditScore = creditList.reduce((sum, item) => sum + Number(item.creditScore || 0), 0);

  const grantedCredit = Number(summary?.summary?.grantedCreditScore || 0);
  if (grantedCredit > 0 && stats.creditScore === 0) {
    stats.creditScore = grantedCredit;
  }
}

async function handleAvatarUpload(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) {
    return;
  }
  try {
    form.yonghuPhoto = await uploadFile(file, session.session?.token);
    avatarVersion.value += 1;
    showUiToast("头像上传成功");
  } catch (error) {
    showUiToast(error instanceof Error ? error.message : "头像上传失败", "error");
  } finally {
    input.value = "";
  }
}

async function submitProfile() {
  if (!rawProfile.value) {
    return;
  }
  saving.value = true;
  try {
    const result = await updateStudentProfile({
      ...rawProfile.value,
      yonghuName: form.yonghuName,
      yonghuPhoto: form.yonghuPhoto,
      yonghuPhone: form.yonghuPhone,
      yonghuEmail: form.yonghuEmail
    });
    if (result.code !== 0) {
      throw new Error(result.msg || "保存失败");
    }
    await loadPage();
    showUiToast("保存成功");
  } catch (error) {
    showUiToast(error instanceof Error ? error.message : "保存失败", "error");
  } finally {
    saving.value = false;
  }
}

loadPage();
</script>

<style scoped>
.center-grid {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 20px;
}

.center-avatar {
  width: 132px;
  height: 132px;
  border-radius: 28px;
  object-fit: cover;
  display: block;
  margin-bottom: 18px;
  border: 1px solid var(--line);
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.field-wrap {
  display: grid;
  gap: 8px;
}

.field-wrap span {
  color: var(--muted);
  font-size: 0.9rem;
}

.field-wrap--grow {
  flex: 1;
}

.avatar-status {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.avatar-status span {
  color: var(--muted);
  font-size: 0.9rem;
}

.avatar-status strong {
  color: var(--text);
  font-size: 1rem;
}

.upload-row {
  display: flex;
  align-items: end;
  gap: 14px;
  margin-top: 18px;
}

.upload-button {
  cursor: pointer;
  white-space: nowrap;
}

@media (max-width: 960px) {
  .center-grid,
  .filter-grid {
    grid-template-columns: 1fr;
  }

  .upload-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
