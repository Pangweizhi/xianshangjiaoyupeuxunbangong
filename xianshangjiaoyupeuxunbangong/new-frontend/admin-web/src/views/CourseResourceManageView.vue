<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>{{ isTeacher ? "资源管理" : "资源审核" }}</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="filters.resourceName" placeholder="搜索资源名称" clearable />
        <el-select v-model="filters.kechengId" placeholder="课程" clearable @change="handleCourseFilterChange">
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.chapterId" placeholder="章节" clearable>
          <el-option v-for="item in chapterOptions" :key="item.id" :label="item.chapterName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.resourceStatus" placeholder="状态" clearable>
          <el-option label="待审核" value="pending_review" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button v-if="isTeacher" type="success" @click="openCreate">新增资源</el-button>
      </div>
    </div>

    <el-table :data="rows" stripe empty-text="暂无资源数据">
      <el-table-column prop="kechengName" label="课程" min-width="180" />
      <el-table-column prop="chapterName" label="章节" min-width="180" />
      <el-table-column prop="resourceName" label="资源名称" min-width="220" />
      <el-table-column prop="resourceType" label="类型" min-width="120" />
      <el-table-column prop="durationSeconds" label="时长(秒)" min-width="100" />
      <el-table-column prop="resourceStatus" label="状态" min-width="120" />
      <el-table-column prop="reviewRemark" label="审核备注" min-width="180" show-overflow-tooltip />
      <el-table-column label="操作" min-width="260" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.resourceUrl" link type="primary" :href="assetUrl(row.resourceUrl)" target="_blank">查看资源</el-button>
          <el-button v-if="isTeacher" link type="primary" @click="openEdit(row.id)">编辑</el-button>
          <el-button v-if="isTeacher" link type="danger" @click="removeItem(row.id)">删除</el-button>
          <el-button v-if="!isTeacher" link type="success" @click="openReview(row, 'approved')">通过</el-button>
          <el-button v-if="!isTeacher" link type="danger" @click="openReview(row, 'rejected')">驳回</el-button>
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

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑资源' : '新增资源'" width="760px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="所属课程" prop="kechengId">
        <el-select v-model="form.kechengId" placeholder="请选择课程" @change="handleFormCourseChange">
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="所属章节" prop="chapterId">
        <el-select v-model="form.chapterId" placeholder="请选择章节">
          <el-option v-for="item in formChapterOptions" :key="item.id" :label="item.chapterName" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="资源名称" prop="resourceName">
        <el-input v-model="form.resourceName" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="资源类型" prop="resourceType">
        <el-select v-model="form.resourceType" placeholder="请选择类型">
          <el-option label="视频" value="视频" />
          <el-option label="PPT" value="PPT" />
          <el-option label="文档" value="文档" />
          <el-option label="压缩包" value="压缩包" />
        </el-select>
      </el-form-item>
      <el-form-item label="资源文件">
        <input type="file" @change="handleUpload($event, 'resourceUrl')" />
        <p class="upload-tip">{{ form.resourceUrl || "未上传" }}</p>
      </el-form-item>
      <el-form-item label="封面图片">
        <input type="file" accept="image/*" @change="handleUpload($event, 'coverUrl')" />
        <p class="upload-tip">{{ form.coverUrl || "未上传" }}</p>
        <img v-if="assetUrl(form.coverUrl)" class="upload-preview" :src="assetUrl(form.coverUrl)" alt="资源封面预览" />
      </el-form-item>
      <el-form-item label="时长(秒)" prop="durationSeconds">
        <el-input-number v-model="form.durationSeconds" :min="0" :max="99999" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitForm">提交</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="reviewVisible" :title="reviewForm.resourceStatus === 'approved' ? '通过资源' : '驳回资源'" width="620px">
    <el-form :model="reviewForm" label-width="100px">
      <el-form-item label="审核备注">
        <el-input v-model="reviewForm.reviewRemark" type="textarea" :rows="4" placeholder="填写审核意见" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="reviewVisible = false">取消</el-button>
      <el-button type="primary" @click="submitReviewAction">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { DEFAULT_BASE_URL, createAssetUrl, type CourseResourceItem } from "@shared/index";
import { useAdminSessionStore } from "@/stores/session";
import { fetchCourseResourcePage } from "@/api/dashboard";
import { deleteEntities, fetchCourseChaptersForSelect, fetchCoursesForSelect, fetchEntityDetail, postModuleAction, saveEntity, uploadAdminFile } from "@/api/manage";

const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const reviewVisible = ref(false);
const formRef = ref<FormInstance>();
const rows = ref<CourseResourceItem[]>([]);
const courseOptions = ref<Array<{ id: number; kechengName: string }>>([]);
const chapterOptions = ref<Array<{ id: number; chapterName: string; kechengId: number }>>([]);
const formChapterOptions = ref<Array<{ id: number; chapterName: string; kechengId: number }>>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({
  resourceName: "",
  kechengId: undefined as number | undefined,
  chapterId: undefined as number | undefined,
  resourceStatus: ""
});

const createForm = () => ({
  id: undefined as number | undefined,
  kechengId: undefined as number | undefined,
  chapterId: undefined as number | undefined,
  resourceName: "",
  resourceType: "",
  resourceUrl: "",
  coverUrl: "",
  durationSeconds: 0
});
const form = reactive(createForm());
const reviewForm = reactive({ id: undefined as number | undefined, resourceStatus: "approved", reviewRemark: "" });

const rules: FormRules = {
  kechengId: [{ required: true, message: "请选择课程", trigger: "change" }],
  chapterId: [{ required: true, message: "请选择章节", trigger: "change" }],
  resourceName: [{ required: true, message: "请输入资源名称", trigger: "blur" }],
  resourceType: [{ required: true, message: "请选择资源类型", trigger: "change" }]
};

function assetUrl(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path);
}

async function loadOptions() {
  courseOptions.value = await fetchCoursesForSelect();
  chapterOptions.value = await fetchCourseChaptersForSelect(filters.kechengId);
}

async function loadRows() {
  loading.value = true;
  try {
    const page = await fetchCourseResourcePage({
      page: pagination.page,
      limit: pagination.limit,
      resourceName: filters.resourceName || undefined,
      kechengId: filters.kechengId,
      chapterId: filters.chapterId,
      resourceStatus: filters.resourceStatus || undefined
    });
    rows.value = page.list;
    pagination.total = page.totalCount;
  } finally {
    loading.value = false;
  }
}

async function handleCourseFilterChange() {
  filters.chapterId = undefined;
  chapterOptions.value = await fetchCourseChaptersForSelect(filters.kechengId);
}

function handleSearch() {
  pagination.page = 1;
  loadRows();
}

async function resetFilters() {
  filters.resourceName = "";
  filters.kechengId = undefined;
  filters.chapterId = undefined;
  filters.resourceStatus = "";
  pagination.page = 1;
  await loadOptions();
  loadRows();
}

function handleSizeChange() {
  pagination.page = 1;
  loadRows();
}

function resetForm() {
  Object.assign(form, createForm());
  formChapterOptions.value = [];
}

async function openCreate() {
  resetForm();
  try {
    await loadOptions();
    dialogVisible.value = true;
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "加载资源表单失败");
  }
}

async function openEdit(id: number) {
  resetForm();
  try {
    await loadOptions();
    Object.assign(form, await fetchEntityDetail("courseResource", id));
    formChapterOptions.value = await fetchCourseChaptersForSelect(form.kechengId);
    dialogVisible.value = true;
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "加载资源详情失败");
  }
}

async function handleFormCourseChange() {
  form.chapterId = undefined;
  formChapterOptions.value = await fetchCourseChaptersForSelect(form.kechengId);
}

async function handleUpload(event: Event, field: "resourceUrl" | "coverUrl") {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  try {
    form[field] = await uploadAdminFile(file);
    ElMessage.success(field === "coverUrl" ? "封面已上传" : "资源文件已上传");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "上传失败");
  }
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    await saveEntity("courseResource", form as unknown as Record<string, unknown>);
    ElMessage.success("资源已保存");
    dialogVisible.value = false;
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  await deleteEntities("courseResource", [id]);
  ElMessage.success("资源已删除");
  await loadRows();
}

function openReview(row: CourseResourceItem, status: "approved" | "rejected") {
  reviewForm.id = row.id;
  reviewForm.resourceStatus = status;
  reviewForm.reviewRemark = row.reviewRemark || "";
  reviewVisible.value = true;
}

async function submitReviewAction() {
  if (!reviewForm.id) return;
  try {
    await postModuleAction("courseResource", "review", reviewForm as unknown as Record<string, unknown>);
    ElMessage.success("审核结果已提交");
    reviewVisible.value = false;
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "审核失败");
  }
}

loadOptions();
loadRows();
</script>
