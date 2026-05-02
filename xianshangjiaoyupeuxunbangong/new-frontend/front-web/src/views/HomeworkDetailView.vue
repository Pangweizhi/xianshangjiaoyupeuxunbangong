<template>
  <section class="section section--tight">
    <RouterLink class="text-link" to="/homeworks">返回作业列表</RouterLink>
    <div v-if="detail" class="detail-shell">
      <article class="detail-card">
        <img :src="toAsset(detail.zuoyePhoto)" :alt="detail.zuoyeName" />
        <div class="detail-card__body">
          <div class="stack-inline">
            <span class="tag">{{ detail.zuoyeValue || "作业" }}</span>
            <span class="meta">{{ detail.kechengName || "未关联课程" }}</span>
            <span class="meta">{{ detail.chapterName || "未指定章节" }}</span>
          </div>
          <h1>{{ detail.zuoyeName }}</h1>
          <p>{{ stripHtml(detail.zuoyeContent) }}</p>
          <div class="status-list">
            <span>授课教师：{{ detail.jiaoshiName || "待补充" }}</span>
            <span>截止时间：{{ detail.deadlineTime || "未设置" }}</span>
            <span>总分：{{ detail.scoreTotal ?? 100 }}</span>
            <span>{{ expired ? "当前已截止" : "当前可提交" }}</span>
          </div>
          <a
            v-if="detail.zuoyeFile"
            class="primary-button"
            :href="downloadUrl(detail.zuoyeFile)"
            target="_blank"
          >
            下载作业附件
          </a>
        </div>
      </article>

      <aside class="action-panel">
        <p class="eyebrow">作业提交</p>
        <h2>上传附件并补充说明</h2>
        <p class="hero__lead">
          提交后可在下方查看最近一次提交记录，包括状态、评分、批改时间和教师评语。
        </p>
        <p v-if="expired" class="field-error">该作业已超过截止时间，系统将拒绝新的提交。</p>
        <p v-if="!session.isLoggedIn" class="field-error">请先登录后再提交作业。</p>
        <input type="file" class="field field--file" :disabled="expired" @change="handleFileChange" />
        <p v-if="selectedFile" class="field-help">已选择文件：{{ selectedFile.name }}</p>
        <textarea
          v-model="submissionContent"
          class="field field--textarea"
          placeholder="补充本次提交说明"
          :disabled="expired"
        ></textarea>
        <button
          class="primary-button primary-button--full"
          :disabled="!selectedFile || uploading || expired"
          @click="submitHomework"
        >
          {{ uploading ? "提交中..." : "上传并提交" }}
        </button>
        <p v-if="submissionMessage" :class="submissionMessageType === 'error' ? 'field-error' : 'field-help'">
          {{ submissionMessage }}
        </p>
        <div v-if="submissionRecord" class="note-card">
          <strong>最近一次提交</strong>
          <div class="status-list">
            <span>提交时间：{{ submissionRecord.insertTime || "-" }}</span>
            <span>当前状态：{{ submissionRecord.submitStatus || "待批改" }}</span>
            <span>评分：{{ submissionRecord.submitScore ?? "待评分" }}</span>
            <span>批改时间：{{ submissionRecord.checkTime || "未批改" }}</span>
          </div>
          <p v-if="submissionRecord.submitRemark">评语：{{ submissionRecord.submitRemark }}</p>
          <a
            v-if="submissionRecord.submitFile"
            class="upload-link"
            :href="downloadUrl(submissionRecord.submitFile)"
            target="_blank"
          >
            查看已提交附件
          </a>
        </div>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";
import {
  DEFAULT_BASE_URL,
  createAssetUrl,
  createDownloadUrl,
  type HomeworkItem,
  type HomeworkSubmissionItem
} from "@shared/index";
import {
  createHomeworkSubmission,
  fetchHomeworkDetail,
  fetchHomeworkSubmissions,
  uploadFile
} from "@/api/content";
import { useSessionStore } from "@/stores/session";

const route = useRoute();
const session = useSessionStore();
const detail = ref<HomeworkItem | null>(null);
const selectedFile = ref<File | null>(null);
const uploading = ref(false);
const submissionMessage = ref("");
const submissionMessageType = ref<"success" | "error">("success");
const submissionContent = ref("");
const submissionRecord = ref<HomeworkSubmissionItem | null>(null);

const expired = computed(() => {
  if (!detail.value?.deadlineTime) return false;
  return new Date(detail.value.deadlineTime).getTime() < Date.now();
});

function toAsset(path?: string) {
  return (
    createAssetUrl(DEFAULT_BASE_URL, path) ||
    "https://dummyimage.com/800x480/f3d8c5/1c2430&text=Homework"
  );
}

function downloadUrl(fileName?: string) {
  return createDownloadUrl(DEFAULT_BASE_URL, fileName);
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").trim() || "暂无作业详情";
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  selectedFile.value = target.files?.[0] || null;
}

async function loadSubmission() {
  if (!session.isLoggedIn) {
    submissionRecord.value = null;
    return;
  }
  const page = await fetchHomeworkSubmissions({
    zuoyeId: route.params.id,
    limit: 1
  });
  submissionRecord.value = page.list[0] || null;
}

async function submitHomework() {
  if (expired.value) {
    submissionMessageType.value = "error";
    submissionMessage.value = "该作业已截止，不能继续提交。";
    return;
  }
  if (!selectedFile.value) {
    submissionMessageType.value = "error";
    submissionMessage.value = "请先选择要提交的附件。";
    return;
  }
  if (!session.isLoggedIn) {
    submissionMessageType.value = "error";
    submissionMessage.value = "请先登录后再提交作业。";
    return;
  }
  uploading.value = true;
  submissionMessage.value = "";
  try {
    const fileName = await uploadFile(selectedFile.value, session.session?.token);
    const result = await createHomeworkSubmission({
      zuoyeId: Number(route.params.id),
      submitFile: fileName,
      submitContent: submissionContent.value.trim()
    });
    if (result.code !== 0) {
      throw new Error(result.msg || "提交失败");
    }
    submissionMessageType.value = "success";
    submissionMessage.value = "提交成功。";
    selectedFile.value = null;
    submissionContent.value = "";
    await loadSubmission();
  } catch (error) {
    submissionMessageType.value = "error";
    submissionMessage.value =
      error instanceof Error ? error.message : "上传失败，请稍后重试";
  } finally {
    uploading.value = false;
  }
}

fetchHomeworkDetail(route.params.id as string).then((data) => {
  detail.value = data;
});

if (session.isLoggedIn) {
  loadSubmission();
}
</script>
