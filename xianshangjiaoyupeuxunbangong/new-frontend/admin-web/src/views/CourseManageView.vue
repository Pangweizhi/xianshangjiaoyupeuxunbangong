<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <div>
        <h2>{{ isTeacher ? "课程管理" : "课程审核" }}</h2>
        <p class="panel-note">{{ isTeacher ? "课程图片、时间和内容统一在这里维护。" : "管理员在这里完成课程审核。" }}</p>
      </div>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索课程标题" clearable />
        <el-select v-model="statusFilter" placeholder="审核状态" clearable>
          <el-option label="待审核" value="pending_review" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button v-if="isTeacher" type="success" @click="openCreate">新增课程</el-button>
      </div>
    </div>

    <el-table :data="courses" stripe empty-text="暂无课程数据">
      <el-table-column prop="kechengName" label="课程标题" min-width="180" show-overflow-tooltip />
      <el-table-column prop="kechengValue" label="类型" min-width="100" />
      <el-table-column prop="jiaoshiName" label="教师" min-width="100" />
      <el-table-column prop="banjiValue" label="班级" min-width="100" />
      <el-table-column prop="creditScore" label="学分" width="74" />
      <el-table-column prop="kechengShichang" label="时长" width="82" />
      <el-table-column prop="courseStatus" label="状态" min-width="100" />
      <el-table-column prop="kechengTime" label="开始时间" min-width="132" />
      <el-table-column prop="kechengEndTime" label="结束时间" min-width="132" />
      <el-table-column prop="reviewRemark" label="审核备注" min-width="160" show-overflow-tooltip />
      <el-table-column label="操作" width="170">
        <template #default="{ row }">
          <div class="table-actions table-actions--wrap">
            <el-button v-if="isTeacher" link type="primary" @click="openEdit(row.id)">编辑</el-button>
            <el-button v-if="isTeacher" link type="danger" @click="removeItem(row.id)">删除</el-button>
            <el-button
              v-if="isTeacher && row.courseStatus === 'rejected'"
              link
              type="warning"
              @click="submitReview(row.id)"
            >
              重新提交
            </el-button>
            <el-button v-if="!isTeacher" link type="success" @click="openReview(row, 'approved')">通过</el-button>
            <el-button v-if="!isTeacher" link type="danger" @click="openReview(row, 'rejected')">驳回</el-button>
          </div>
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
        @current-change="loadCourses"
        @size-change="handleSizeChange"
      />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑课程' : '新增课程'" width="760px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
      <el-form-item label="课程标题" prop="kechengName">
        <el-input v-model="form.kechengName" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="课程类型" prop="kechengTypes">
        <el-select v-model="form.kechengTypes" placeholder="请选择课程类型">
          <el-option v-for="item in courseTypeOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" />
        </el-select>
      </el-form-item>
      <el-form-item label="课程时长" prop="kechengShichang">
        <el-input-number v-model="form.kechengShichang" :min="1" :max="999" />
      </el-form-item>
      <el-form-item label="课程学分" prop="creditScore">
        <el-input-number v-model="form.creditScore" :min="0" :max="99" />
      </el-form-item>
      <el-form-item label="班级" prop="banjiTypes">
        <el-select v-model="form.banjiTypes" placeholder="请选择班级">
          <el-option v-for="item in banjiOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="!isTeacher" label="教师" prop="jiaoshiId">
        <el-select v-model="form.jiaoshiId" placeholder="请选择教师">
          <el-option v-for="item in teacherOptions" :key="item.id" :label="item.jiaoshiName" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="开始时间" prop="kechengTime">
        <el-date-picker
          v-model="form.kechengTime"
          type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
          placeholder="请选择开始时间"
        />
      </el-form-item>
      <el-form-item label="结束时间" prop="kechengEndTime">
        <el-date-picker
          v-model="form.kechengEndTime"
          type="datetime"
          value-format="YYYY-MM-DD HH:mm:ss"
          placeholder="请选择结束时间"
        />
      </el-form-item>
      <el-form-item label="课程图片">
        <label class="ghost-button upload-button">
          上传图片
          <input type="file" accept="image/*" hidden @change="handleUpload" />
        </label>
        <p class="upload-tip">{{ form.kechengPhoto || "未上传课程图片" }}</p>
        <img v-if="assetUrl(form.kechengPhoto)" class="upload-preview upload-preview--large" :src="assetUrl(form.kechengPhoto)" alt="课程图片预览" />
      </el-form-item>
      <el-form-item label="课程详情" prop="kechengContent">
        <el-input v-model="form.kechengContent" type="textarea" :rows="5" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitForm">提交</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="reviewVisible" :title="reviewForm.courseStatus === 'approved' ? '通过课程' : '驳回课程'" width="560px">
    <el-form :model="reviewForm" label-width="88px">
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
import { DEFAULT_BASE_URL, createAssetUrl, type CourseItem } from "@shared/index";
import { fetchAdminCourses } from "@/api/dashboard";
import {
  deleteEntities,
  fetchDictionaryOptions,
  fetchEntityDetail,
  fetchTeachersForSelect,
  postModuleAction,
  saveEntity,
  uploadAdminFile
} from "@/api/manage";
import { useAdminSessionStore } from "@/stores/session";

const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");
const keyword = ref("");
const statusFilter = ref("");
const courses = ref<CourseItem[]>([]);
const dialogVisible = ref(false);
const reviewVisible = ref(false);
const saving = ref(false);
const loading = ref(false);
const formRef = ref<FormInstance>();
const teacherOptions = ref<Array<{ id: number; jiaoshiName: string }>>([]);
const courseTypeOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]);
const banjiOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const reviewForm = reactive({ id: undefined as number | undefined, courseStatus: "approved", reviewRemark: "" });

const createForm = () => ({
  id: undefined as number | undefined,
  kechengName: "",
  kechengPhoto: "",
  kechengTypes: undefined as number | undefined,
  kechengShichang: undefined as number | undefined,
  creditScore: 0,
  kechengTime: "",
  kechengEndTime: "",
  banjiTypes: undefined as number | undefined,
  jiaoshiId: undefined as number | undefined,
  kechengContent: "",
  kechengDelete: 1
});
const form = reactive(createForm());

const rules: FormRules = {
  kechengName: [{ required: true, message: "请输入课程标题", trigger: "blur" }],
  kechengTypes: [{ required: true, message: "请选择课程类型", trigger: "change" }],
  kechengShichang: [{ required: true, message: "请输入课程时长", trigger: "change" }],
  kechengTime: [{ required: true, message: "请选择开始时间", trigger: "change" }],
  kechengEndTime: [{ required: true, message: "请选择结束时间", trigger: "change" }],
  banjiTypes: [{ required: true, message: "请选择班级", trigger: "change" }],
  jiaoshiId: [{ required: true, message: "请选择教师", trigger: "change" }],
  kechengContent: [{ required: true, message: "请输入课程详情", trigger: "blur" }]
};

function assetUrl(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path);
}

async function loadCourses() {
  loading.value = true;
  try {
    const page = await fetchAdminCourses({
      page: pagination.page,
      limit: pagination.limit,
      kechengName: keyword.value || undefined,
      courseStatus: statusFilter.value || undefined
    });
    courses.value = page.list;
    pagination.total = page.totalCount;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  loadCourses();
}

function resetFilters() {
  keyword.value = "";
  statusFilter.value = "";
  pagination.page = 1;
  loadCourses();
}

function handleSizeChange() {
  pagination.page = 1;
  loadCourses();
}

function resetForm() {
  Object.assign(form, createForm());
}

async function prepareOptions() {
  const tasks: Array<Promise<unknown>> = [
    fetchDictionaryOptions("kecheng_types"),
    fetchDictionaryOptions("banji_types")
  ];
  if (isTeacher.value) {
    tasks.unshift(Promise.resolve([{ id: store.session?.userId ?? 0, jiaoshiName: store.session?.username || "当前教师" }]));
  } else {
    tasks.unshift(fetchTeachersForSelect());
  }
  const [teachers, courseTypes, banjiTypes] = await Promise.all(tasks);
  teacherOptions.value = teachers as Array<{ id: number; jiaoshiName: string }>;
  courseTypeOptions.value = courseTypes as Array<{ codeIndex: number; indexName: string }>;
  banjiOptions.value = banjiTypes as Array<{ codeIndex: number; indexName: string }>;
}

async function openCreate() {
  resetForm();
  await prepareOptions();
  dialogVisible.value = true;
}

async function openEdit(id: number) {
  resetForm();
  await prepareOptions();
  Object.assign(form, await fetchEntityDetail("kecheng", id));
  dialogVisible.value = true;
}

async function handleUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) {
    return;
  }
  try {
    form.kechengPhoto = await uploadAdminFile(file);
    ElMessage.success("课程图片上传成功");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "上传失败");
  } finally {
    (event.target as HTMLInputElement).value = "";
  }
}

async function submitForm() {
  await formRef.value?.validate();
  if (form.kechengEndTime <= form.kechengTime) {
    ElMessage.error("结束时间必须晚于开始时间");
    return;
  }
  saving.value = true;
  try {
    await saveEntity("kecheng", form as unknown as Record<string, unknown>);
    ElMessage.success("课程已保存");
    dialogVisible.value = false;
    await loadCourses();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  await deleteEntities("kecheng", [id]);
  ElMessage.success("课程已删除");
  await loadCourses();
}

function openReview(row: CourseItem, status: "approved" | "rejected") {
  reviewForm.id = row.id;
  reviewForm.courseStatus = status;
  reviewForm.reviewRemark = row.reviewRemark || "";
  reviewVisible.value = true;
}

async function submitReviewAction() {
  if (!reviewForm.id) {
    return;
  }
  await postModuleAction("kecheng", "review", reviewForm as unknown as Record<string, unknown>);
  ElMessage.success("审核结果已提交");
  reviewVisible.value = false;
  await loadCourses();
}

async function submitReview(id: number) {
  await postModuleAction("kecheng", "submitReview", { id });
  ElMessage.success("已重新提交审核");
  await loadCourses();
}

prepareOptions();
loadCourses();
</script>

<style scoped>
.upload-button {
  cursor: pointer;
}

.upload-preview--large {
  width: 220px;
  height: 132px;
}

.table-actions--wrap {
  flex-wrap: wrap;
}
</style>
