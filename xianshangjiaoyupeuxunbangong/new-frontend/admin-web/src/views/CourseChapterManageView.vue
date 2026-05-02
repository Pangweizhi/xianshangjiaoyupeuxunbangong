<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>{{ isTeacher ? "章节管理" : "章节审核" }}</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="filters.chapterName" placeholder="搜索章节名称" clearable />
        <el-select v-model="filters.kechengId" placeholder="课程" clearable>
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.chapterStatus" placeholder="状态" clearable>
          <el-option label="待审核" value="pending_review" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button v-if="isTeacher" type="success" @click="openCreate">新增章节</el-button>
      </div>
    </div>

    <el-table :data="rows" stripe empty-text="暂无章节数据">
      <el-table-column prop="kechengName" label="课程" min-width="180" />
      <el-table-column prop="chapterName" label="章节名称" min-width="220" />
      <el-table-column prop="chapterSort" label="排序" min-width="90" />
      <el-table-column prop="jiaoshiName" label="教师" min-width="120" />
      <el-table-column prop="chapterStatus" label="状态" min-width="120" />
      <el-table-column prop="reviewRemark" label="审核备注" min-width="180" show-overflow-tooltip />
      <el-table-column label="操作" min-width="240" fixed="right">
        <template #default="{ row }">
          <el-button v-if="isTeacher" link type="primary" @click="openEdit(row.id)">编辑</el-button>
          <el-button v-if="isTeacher" link type="danger" @click="removeItem(row.id)">删除</el-button>
          <el-button v-if="isTeacher && row.chapterStatus === 'rejected'" link type="warning" @click="submitReview(row.id)">重新提审</el-button>
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

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑章节' : '新增章节'" width="720px">
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
        <el-input v-model="form.chapterSummary" type="textarea" :rows="5" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitForm">提交</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="reviewVisible" :title="reviewForm.chapterStatus === 'approved' ? '通过章节' : '驳回章节'" width="620px">
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
import type { CourseChapterItem } from "@shared/index";
import { useAdminSessionStore } from "@/stores/session";
import { fetchCourseChapterPage } from "@/api/dashboard";
import { deleteEntities, fetchCoursesForSelect, fetchEntityDetail, postModuleAction, saveEntity } from "@/api/manage";

const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");
const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const reviewVisible = ref(false);
const formRef = ref<FormInstance>();
const rows = ref<CourseChapterItem[]>([]);
const courseOptions = ref<Array<{ id: number; kechengName: string }>>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ chapterName: "", kechengId: undefined as number | undefined, chapterStatus: "" });

const createForm = () => ({
  id: undefined as number | undefined,
  kechengId: undefined as number | undefined,
  chapterName: "",
  chapterSort: 1,
  chapterSummary: ""
});
const form = reactive(createForm());
const reviewForm = reactive({ id: undefined as number | undefined, chapterStatus: "approved", reviewRemark: "" });

const rules: FormRules = {
  kechengId: [{ required: true, message: "请选择课程", trigger: "change" }],
  chapterName: [{ required: true, message: "请输入章节名称", trigger: "blur" }],
  chapterSort: [{ required: true, message: "请输入排序", trigger: "change" }]
};

async function loadOptions() {
  courseOptions.value = await fetchCoursesForSelect();
}

async function loadRows() {
  loading.value = true;
  try {
    const page = await fetchCourseChapterPage({
      page: pagination.page,
      limit: pagination.limit,
      chapterName: filters.chapterName || undefined,
      kechengId: filters.kechengId,
      chapterStatus: filters.chapterStatus || undefined
    });
    rows.value = page.list;
    pagination.total = page.totalCount;
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
  filters.chapterStatus = "";
  pagination.page = 1;
  loadRows();
}

function handleSizeChange() {
  pagination.page = 1;
  loadRows();
}

function resetForm() {
  Object.assign(form, createForm());
}

async function openCreate() {
  resetForm();
  await loadOptions();
  dialogVisible.value = true;
}

async function openEdit(id: number) {
  resetForm();
  await loadOptions();
  Object.assign(form, await fetchEntityDetail("courseChapter", id));
  dialogVisible.value = true;
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    await saveEntity("courseChapter", form as unknown as Record<string, unknown>);
    ElMessage.success("章节已保存");
    dialogVisible.value = false;
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  await deleteEntities("courseChapter", [id]);
  ElMessage.success("章节已删除");
  await loadRows();
}

function openReview(row: CourseChapterItem, status: "approved" | "rejected") {
  reviewForm.id = row.id;
  reviewForm.chapterStatus = status;
  reviewForm.reviewRemark = row.reviewRemark || "";
  reviewVisible.value = true;
}

async function submitReviewAction() {
  if (!reviewForm.id) return;
  try {
    await postModuleAction("courseChapter", "review", reviewForm as unknown as Record<string, unknown>);
    ElMessage.success("审核结果已提交");
    reviewVisible.value = false;
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "审核失败");
  }
}

async function submitReview(id: number) {
  try {
    await postModuleAction("courseChapter", "review", { id, chapterStatus: "pending_review", reviewRemark: "" });
    ElMessage.success("已重新提交审核");
    await loadRows();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "提交失败");
  }
}

loadOptions();
loadRows();
</script>

