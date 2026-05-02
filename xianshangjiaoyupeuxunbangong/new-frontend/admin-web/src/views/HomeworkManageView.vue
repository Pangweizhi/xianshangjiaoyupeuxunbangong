<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>作业管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="filters.zuoyeName" placeholder="搜索作业标题" clearable />
        <el-select v-model="filters.kechengId" placeholder="课程" clearable @change="handleCourseFilterChange">
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.chapterId" placeholder="章节" clearable>
          <el-option v-for="item in filterChapterOptions" :key="item.id" :label="item.chapterName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.publishStatus" placeholder="发布状态" clearable>
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="success" @click="openCreate">新增作业</el-button>
      </div>
    </div>

    <el-table :data="items" stripe empty-text="暂无作业数据">
      <el-table-column prop="zuoyeName" label="作业标题" min-width="220" />
      <el-table-column prop="kechengName" label="课程" min-width="180" />
      <el-table-column prop="chapterName" label="章节" min-width="180" />
      <el-table-column prop="zuoyeValue" label="作业类型" min-width="120" />
      <el-table-column prop="scoreTotal" label="总分" min-width="90" />
      <el-table-column prop="deadlineTime" label="截止时间" min-width="180" />
      <el-table-column prop="publishStatus" label="发布状态" min-width="120" />
      <el-table-column prop="jiaoshiName" label="教师" min-width="120" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.zuoyeFile" link type="primary" :href="downloadUrl(row.zuoyeFile)" target="_blank">查看附件</el-button>
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
        @current-change="loadItems"
        @size-change="handleSizeChange"
      />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑作业' : '新增作业'" width="780px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
      <el-form-item label="作业标题" prop="zuoyeName">
        <el-input v-model="form.zuoyeName" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="作业类型" prop="zuoyeTypes">
        <el-select v-model="form.zuoyeTypes" placeholder="请选择作业类型">
          <el-option v-for="item in typeOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="!isTeacher" label="教师" prop="jiaoshiId">
        <el-select v-model="form.jiaoshiId" placeholder="请选择教师">
          <el-option v-for="item in teacherOptions" :key="item.id" :label="item.jiaoshiName" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="所属课程" prop="kechengId">
        <el-select v-model="form.kechengId" placeholder="请选择课程" @change="handleFormCourseChange">
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="所属章节" prop="chapterId">
        <el-select v-model="form.chapterId" placeholder="可选关联章节" clearable>
          <el-option v-for="item in formChapterOptions" :key="item.id" :label="item.chapterName" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="截止时间" prop="deadlineTime">
        <el-date-picker
          v-model="form.deadlineTime"
          type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
          format="YYYY-MM-DD HH:mm:ss"
          placeholder="请选择截止时间"
        />
      </el-form-item>
      <el-form-item label="总分" prop="scoreTotal">
        <el-input-number v-model="form.scoreTotal" :min="1" :max="999" />
      </el-form-item>
      <el-form-item label="发布状态" prop="publishStatus">
        <el-select v-model="form.publishStatus" placeholder="请选择发布状态">
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
        </el-select>
      </el-form-item>
      <el-form-item label="作业图片">
        <input type="file" accept="image/*" @change="handleUpload($event, 'zuoyePhoto')" />
        <p class="upload-tip">{{ form.zuoyePhoto || "未上传" }}</p>
        <img v-if="assetUrl(form.zuoyePhoto)" class="upload-preview" :src="assetUrl(form.zuoyePhoto)" alt="作业图片预览" />
      </el-form-item>
      <el-form-item label="作业附件" prop="zuoyeFile">
        <input type="file" @change="handleUpload($event, 'zuoyeFile')" />
        <p class="upload-tip">{{ form.zuoyeFile || "未上传" }}</p>
        <a v-if="form.zuoyeFile" class="upload-link" :href="downloadUrl(form.zuoyeFile)" target="_blank">查看当前附件</a>
      </el-form-item>
      <el-form-item label="作业说明" prop="zuoyeContent">
        <el-input v-model="form.zuoyeContent" type="textarea" :rows="5" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitForm">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { DEFAULT_BASE_URL, createAssetUrl, createDownloadUrl, type HomeworkItem } from "@shared/index";
import { fetchHomeworks } from "@/api/dashboard";
import { deleteEntities, fetchCourseChaptersForSelect, fetchCoursesForSelect, fetchDictionaryOptions, fetchEntityDetail, fetchTeachersForSelect, saveEntity, uploadAdminFile } from "@/api/manage";
import { useAdminSessionStore } from "@/stores/session";

const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const formRef = ref<FormInstance>();
const items = ref<HomeworkItem[]>([]);
const teacherOptions = ref<Array<{ id: number; jiaoshiName: string }>>([]);
const typeOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]);
const courseOptions = ref<Array<{ id: number; kechengName: string }>>([]);
const filterChapterOptions = ref<Array<{ id: number; chapterName: string; kechengId: number }>>([]);
const formChapterOptions = ref<Array<{ id: number; chapterName: string; kechengId: number }>>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({
  zuoyeName: "",
  kechengId: undefined as number | undefined,
  chapterId: undefined as number | undefined,
  publishStatus: ""
});

const createForm = () => ({
  id: undefined as number | undefined,
  zuoyeName: "",
  zuoyePhoto: "",
  zuoyeTypes: undefined as number | undefined,
  zuoyeFile: "",
  jiaoshiId: isTeacher.value ? store.session?.userId : undefined,
  kechengId: undefined as number | undefined,
  chapterId: undefined as number | undefined,
  deadlineTime: "",
  scoreTotal: 100,
  publishStatus: "published",
  zuoyeContent: "",
  zuoyeDelete: 1
});
const form = reactive(createForm());

const rules: FormRules = {
  zuoyeName: [{ required: true, message: "请输入作业标题", trigger: "blur" }],
  zuoyeTypes: [{ required: true, message: "请选择作业类型", trigger: "change" }],
  jiaoshiId: [{ required: true, message: "请选择教师", trigger: "change" }],
  kechengId: [{ required: true, message: "请选择课程", trigger: "change" }],
  deadlineTime: [{ required: true, message: "请选择截止时间", trigger: "change" }],
  scoreTotal: [{ required: true, message: "请填写总分", trigger: "change" }],
  publishStatus: [{ required: true, message: "请选择发布状态", trigger: "change" }],
  zuoyeFile: [{ required: true, message: "请上传作业附件", trigger: "change" }],
  zuoyeContent: [{ required: true, message: "请输入作业说明", trigger: "blur" }]
};

function assetUrl(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path);
}

function downloadUrl(fileName?: string) {
  return createDownloadUrl(DEFAULT_BASE_URL, fileName);
}

async function loadOptions() {
  const [courses, teachers, types] = await Promise.all([
    fetchCoursesForSelect(),
    fetchTeachersForSelect(),
    fetchDictionaryOptions("zuoye_types")
  ]);
  courseOptions.value = courses;
  teacherOptions.value = teachers;
  typeOptions.value = types;
  filterChapterOptions.value = await fetchCourseChaptersForSelect(filters.kechengId);
}

async function loadItems() {
  loading.value = true;
  try {
    const page = await fetchHomeworks({
      page: pagination.page,
      limit: pagination.limit,
      zuoyeName: filters.zuoyeName || undefined,
      kechengId: filters.kechengId,
      chapterId: filters.chapterId,
      publishStatus: filters.publishStatus || undefined
    });
    items.value = page.list;
    pagination.total = page.totalCount;
  } finally {
    loading.value = false;
  }
}

async function handleCourseFilterChange() {
  filters.chapterId = undefined;
  filterChapterOptions.value = await fetchCourseChaptersForSelect(filters.kechengId);
}

function handleSearch() {
  pagination.page = 1;
  loadItems();
}

async function resetFilters() {
  filters.zuoyeName = "";
  filters.kechengId = undefined;
  filters.chapterId = undefined;
  filters.publishStatus = "";
  pagination.page = 1;
  await loadOptions();
  loadItems();
}

function handleSizeChange() {
  pagination.page = 1;
  loadItems();
}

function resetForm() {
  Object.assign(form, createForm());
  formChapterOptions.value = [];
}

async function openCreate() {
  resetForm();
  await loadOptions();
  if (form.kechengId) {
    formChapterOptions.value = await fetchCourseChaptersForSelect(form.kechengId);
  }
  dialogVisible.value = true;
}

async function openEdit(id: number) {
  resetForm();
  await loadOptions();
  Object.assign(form, await fetchEntityDetail("zuoye", id));
  if (!isTeacher.value && !form.jiaoshiId) {
    form.jiaoshiId = undefined;
  }
  formChapterOptions.value = await fetchCourseChaptersForSelect(form.kechengId);
  dialogVisible.value = true;
}

async function handleFormCourseChange() {
  form.chapterId = undefined;
  formChapterOptions.value = await fetchCourseChaptersForSelect(form.kechengId);
}

async function handleUpload(event: Event, field: "zuoyePhoto" | "zuoyeFile") {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) return;
  try {
    form[field] = await uploadAdminFile(file);
    ElMessage.success(field === "zuoyePhoto" ? "作业图片已上传" : "作业附件已上传");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "上传失败");
  }
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    await saveEntity("zuoye", form as unknown as Record<string, unknown>);
    ElMessage.success("作业已保存");
    dialogVisible.value = false;
    await loadItems();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  await deleteEntities("zuoye", [id]);
  ElMessage.success("作业已删除");
  await loadItems();
}

loadOptions();
loadItems();
</script>
