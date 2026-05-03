<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>章节与资源</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="filters.chapterName" placeholder="搜索章节名称" clearable />
        <el-select v-model="filters.kechengId" placeholder="课程" clearable>
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="success" @click="openCreate">新增章节</el-button>
      </div>
    </div>

    <el-table :data="rows" stripe empty-text="暂无章节数据">
      <el-table-column prop="kechengName" label="课程" min-width="180" />
      <el-table-column prop="chapterName" label="章节名称" min-width="220" />
      <el-table-column prop="chapterSort" label="排序" min-width="90" />
      <el-table-column prop="jiaoshiName" label="教师" min-width="120" />
      <el-table-column label="学习资源" min-width="320">
        <template #default="{ row }">
          <div class="resource-tags">
            <span v-for="resource in resourcesByChapter[row.id] || []" :key="resource.id" class="resource-tag">
              {{ resource.resourceName }}
            </span>
            <span v-if="!(resourcesByChapter[row.id] || []).length" class="panel-note">暂无资源</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row.id)">编辑</el-button>
          <el-button link type="danger" @click="removeItem(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        background
        layout="total, sizes, prev, pager, next"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        @current-change="loadRows"
        @size-change="handleSizeChange"
      />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑章节' : '新增章节'" width="980px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="所属课程" prop="kechengId">
        <el-select v-model="form.kechengId" placeholder="请选择课程">
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="章节名称" prop="chapterName">
        <el-input v-model="form.chapterName" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="章节排序" prop="chapterSort">
        <el-input-number v-model="form.chapterSort" :min="1" :max="999" />
      </el-form-item>
      <el-form-item label="章节简介" prop="chapterSummary">
        <el-input v-model="form.chapterSummary" type="textarea" :rows="4" />
      </el-form-item>
    </el-form>

    <div class="resource-editor">
      <div class="panel-header panel-header--spread">
        <h3>本章节资源</h3>
        <el-button type="primary" plain @click="addResourceDraft">新增资源</el-button>
      </div>

      <div v-if="resourceDrafts.length" class="resource-editor__list">
        <article v-for="(draft, index) in resourceDrafts" :key="draft.localKey" class="resource-editor__card">
          <div class="panel-header panel-header--spread">
            <strong>资源 {{ index + 1 }}</strong>
            <el-button link type="danger" @click="removeResourceDraft(index)">删除</el-button>
          </div>
          <div class="resource-editor__grid">
            <el-input v-model="draft.resourceName" placeholder="资源名称" />
            <el-select v-model="draft.resourceType" placeholder="资源类型">
              <el-option label="视频" value="视频" />
              <el-option label="PPT" value="PPT" />
              <el-option label="文档" value="文档" />
              <el-option label="压缩包" value="压缩包" />
            </el-select>
            <el-input-number v-model="draft.durationSeconds" :min="0" :max="99999" />
            <label class="resource-upload">
              <span>上传资源文件</span>
              <input type="file" @change="handleResourceUpload($event, draft, 'resourceUrl')" />
            </label>
            <label class="resource-upload">
              <span>上传封面图片</span>
              <input type="file" accept="image/*" @change="handleResourceUpload($event, draft, 'coverUrl')" />
            </label>
            <img v-if="assetUrl(draft.coverUrl)" class="upload-preview" :src="assetUrl(draft.coverUrl)" alt="资源封面" />
          </div>
          <p class="upload-tip">{{ draft.resourceUrl || "未上传资源文件" }}</p>
        </article>
      </div>
      <el-empty v-else description="当前还没有资源，可直接新增" />
    </div>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitForm">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { DEFAULT_BASE_URL, createAssetUrl, type CourseChapterItem, type CourseResourceItem } from "@shared/index";
import { fetchCourseChapterPage, fetchCourseResourcePage } from "@/api/dashboard";
import {
  deleteEntities,
  fetchCoursesForSelect,
  fetchEntityDetail,
  saveEntity,
  uploadAdminFile
} from "@/api/manage";

type ResourceDraft = {
  id?: number;
  localKey: string;
  resourceName: string;
  resourceType: string;
  resourceUrl: string;
  coverUrl: string;
  durationSeconds: number;
};

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const formRef = ref<FormInstance>();
const rows = ref<CourseChapterItem[]>([]);
const resources = ref<CourseResourceItem[]>([]);
const courseOptions = ref<Array<{ id: number; kechengName: string }>>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ chapterName: "", kechengId: undefined as number | undefined });
const deletedResourceIds = ref<number[]>([]);

const createForm = () => ({
  id: undefined as number | undefined,
  kechengId: undefined as number | undefined,
  chapterName: "",
  chapterSort: 1,
  chapterSummary: ""
});
const form = reactive(createForm());
const resourceDrafts = ref<ResourceDraft[]>([]);

const rules: FormRules = {
  kechengId: [{ required: true, message: "请选择课程", trigger: "change" }],
  chapterName: [{ required: true, message: "请输入章节名称", trigger: "blur" }],
  chapterSort: [{ required: true, message: "请输入排序", trigger: "change" }]
};

const resourcesByChapter = computed(() => {
  const map: Record<number, CourseResourceItem[]> = {};
  resources.value.forEach((item) => {
    if (!map[item.chapterId]) {
      map[item.chapterId] = [];
    }
    map[item.chapterId].push(item);
  });
  return map;
});

function assetUrl(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path);
}

function createDraft(): ResourceDraft {
  return {
    localKey: `${Date.now()}-${Math.random()}`,
    resourceName: "",
    resourceType: "",
    resourceUrl: "",
    coverUrl: "",
    durationSeconds: 0
  };
}

async function loadOptions() {
  courseOptions.value = await fetchCoursesForSelect();
}

async function loadRows() {
  loading.value = true;
  try {
    const [chapterPage, resourcePage] = await Promise.all([
      fetchCourseChapterPage({
        page: pagination.page,
        limit: pagination.limit,
        chapterName: filters.chapterName || undefined,
        kechengId: filters.kechengId
      }),
      fetchCourseResourcePage({
        limit: 200,
        kechengId: filters.kechengId
      })
    ]);
    rows.value = chapterPage.list;
    resources.value = resourcePage.list;
    pagination.total = chapterPage.totalCount;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  loadRows();
}

function resetFilters() {
  filters.chapterName = "";
  filters.kechengId = undefined;
  pagination.page = 1;
  loadRows();
}

function handleSizeChange() {
  pagination.page = 1;
  loadRows();
}

function resetForm() {
  Object.assign(form, createForm());
  resourceDrafts.value = [];
  deletedResourceIds.value = [];
}

function addResourceDraft() {
  resourceDrafts.value.push(createDraft());
}

async function openCreate() {
  resetForm();
  try {
    await loadOptions();
    addResourceDraft();
    dialogVisible.value = true;
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "加载章节表单失败");
  }
}

async function openEdit(id: number) {
  resetForm();
  try {
    await loadOptions();
    Object.assign(form, await fetchEntityDetail("courseChapter", id));
    const resourcePage = await fetchCourseResourcePage({ chapterId: id, limit: 100 });
    resourceDrafts.value = resourcePage.list.map((item) => ({
      id: item.id,
      localKey: `resource-${item.id}`,
      resourceName: item.resourceName,
      resourceType: item.resourceType || "",
      resourceUrl: item.resourceUrl || "",
      coverUrl: item.coverUrl || "",
      durationSeconds: item.durationSeconds || 0
    }));
    dialogVisible.value = true;
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "加载章节详情失败");
  }
}

function removeResourceDraft(index: number) {
  const target = resourceDrafts.value[index];
  if (target?.id) {
    deletedResourceIds.value.push(target.id);
  }
  resourceDrafts.value.splice(index, 1);
}

async function handleResourceUpload(event: Event, draft: ResourceDraft, field: "resourceUrl" | "coverUrl") {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) {
    return;
  }
  try {
    draft[field] = await uploadAdminFile(file);
    ElMessage.success(field === "coverUrl" ? "封面已上传" : "资源文件已上传");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "上传失败");
  }
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    const response = await saveEntity("courseChapter", form as unknown as Record<string, unknown>);
    const chapterId = Number(response.data?.id || form.id);
    for (const draft of resourceDrafts.value) {
      if (!draft.resourceName || !draft.resourceType) {
        continue;
      }
      await saveEntity("courseResource", {
        id: draft.id,
        kechengId: form.kechengId,
        chapterId,
        resourceName: draft.resourceName,
        resourceType: draft.resourceType,
        resourceUrl: draft.resourceUrl,
        coverUrl: draft.coverUrl,
        durationSeconds: draft.durationSeconds
      });
    }
    if (deletedResourceIds.value.length) {
      await deleteEntities("courseResource", deletedResourceIds.value);
    }
    ElMessage.success("章节与资源已保存");
    dialogVisible.value = false;
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  const related = resourcesByChapter.value[id] || [];
  if (related.length) {
    await deleteEntities("courseResource", related.map((item) => item.id));
  }
  await deleteEntities("courseChapter", [id]);
  ElMessage.success("章节已删除");
  await loadRows();
}

loadOptions();
loadRows();
</script>

<style scoped>
.resource-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.resource-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(19, 71, 201, 0.08);
  color: #1347c9;
  font-size: 12px;
}

.resource-editor {
  margin-top: 18px;
  border-top: 1px solid var(--admin-line);
  padding-top: 18px;
}

.resource-editor__list {
  display: grid;
  gap: 16px;
}

.resource-editor__card {
  border: 1px solid var(--admin-line);
  border-radius: 18px;
  padding: 16px;
}

.resource-editor__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.resource-upload {
  display: grid;
  gap: 8px;
  align-content: start;
  color: var(--admin-muted);
}

@media (max-width: 1080px) {
  .resource-editor__grid {
    grid-template-columns: 1fr;
  }
}
</style>
