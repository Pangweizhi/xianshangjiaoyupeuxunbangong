<template>
  <section class="admin-panel">
    <div class="panel-header panel-header--spread">
      <div>
        <h2>作业提交记录</h2>
        <p class="panel-note">支持按作业、学生、状态筛选，并直接完成评分、评语、退回重交和批量批改。</p>
      </div>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="filters.zuoyeName" placeholder="搜索作业标题" clearable />
        <el-input v-model="filters.yonghuName" placeholder="搜索学生姓名" clearable />
        <el-select v-model="filters.submitStatus" placeholder="提交状态" clearable>
          <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button :disabled="selectedRows.length === 0" @click="openBatchReview">批量批改</el-button>
        <el-button type="danger" plain :disabled="selectedRows.length === 0" @click="removeSelected">批量删除</el-button>
      </div>
    </div>

    <el-table :data="items" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="52" />
      <el-table-column prop="zuoyeName" label="作业" min-width="180" />
      <el-table-column prop="yonghuName" label="学生" min-width="120" />
      <el-table-column label="附件" min-width="180">
        <template #default="{ row }">
          <a
            v-if="row.submitFile"
            class="upload-link"
            :href="downloadUrl(row.submitFile)"
            target="_blank"
          >
            查看附件
          </a>
          <span v-else class="form-hint">未上传附件</span>
        </template>
      </el-table-column>
      <el-table-column prop="submitStatus" label="状态" min-width="120" />
      <el-table-column prop="submitScore" label="评分" min-width="100" />
      <el-table-column prop="checkTime" label="批改时间" min-width="180" />
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openReview(row.id)">批改</el-button>
          <el-button link type="warning" @click="quickReject(row)">退回重交</el-button>
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

  <el-dialog v-model="dialogVisible" title="批改单条提交记录" width="720px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="作业标题">
        <el-input v-model="form.zuoyeName" disabled />
      </el-form-item>
      <el-form-item label="学生姓名">
        <el-input v-model="form.yonghuName" disabled />
      </el-form-item>
      <el-form-item label="提交附件">
        <a
          v-if="form.submitFile"
          class="upload-link"
          :href="downloadUrl(form.submitFile)"
          target="_blank"
        >
          {{ form.submitFile }}
        </a>
        <span v-else class="form-hint">当前记录没有附件</span>
      </el-form-item>
      <el-form-item label="提交说明">
        <el-input v-model="form.submitContent" type="textarea" :rows="4" disabled />
      </el-form-item>
      <el-form-item label="提交状态" prop="submitStatus">
        <el-select v-model="form.submitStatus" placeholder="请选择状态">
          <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item label="评分">
        <el-input-number
          v-model="form.submitScore"
          :min="0"
          :max="100"
          :precision="1"
          :step="1"
        />
      </el-form-item>
      <el-form-item label="评语">
        <el-input
          v-model="form.submitRemark"
          type="textarea"
          :rows="5"
          placeholder="请输入批改意见或退回原因"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitSingleReview">保存批改</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="batchDialogVisible" title="批量批改提交记录" width="620px">
    <el-form ref="batchFormRef" :model="batchForm" :rules="rules" label-width="100px">
      <el-form-item label="选中数量">
        <el-input :model-value="String(selectedRows.length)" disabled />
      </el-form-item>
      <el-form-item label="提交状态" prop="submitStatus">
        <el-select v-model="batchForm.submitStatus" placeholder="请选择状态">
          <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item label="统一评分">
        <el-input-number
          v-model="batchForm.submitScore"
          :min="0"
          :max="100"
          :precision="1"
          :step="1"
        />
      </el-form-item>
      <el-form-item label="统一评语">
        <el-input
          v-model="batchForm.submitRemark"
          type="textarea"
          :rows="5"
          placeholder="请输入统一批改意见或退回原因"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="batchDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitBatchReview">执行批量批改</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { DEFAULT_BASE_URL, createDownloadUrl, type HomeworkSubmissionItem } from "@shared/index";
import { fetchHomeworkSubmissionPage } from "@/api/dashboard";
import { deleteEntities, fetchEntityDetail, saveEntity } from "@/api/manage";

const statusOptions = ["待批改", "已批改", "需重交"];
const filters = reactive({
  zuoyeName: "",
  yonghuName: "",
  submitStatus: ""
});
const items = ref<HomeworkSubmissionItem[]>([]);
const selectedRows = ref<HomeworkSubmissionItem[]>([]);
const dialogVisible = ref(false);
const batchDialogVisible = ref(false);
const saving = ref(false);
const formRef = ref<FormInstance>();
const batchFormRef = ref<FormInstance>();
const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0
});

const createForm = () => ({
  id: undefined as number | undefined,
  zuoyeId: undefined as number | undefined,
  yonghuId: undefined as number | undefined,
  submitDelete: 1,
  zuoyeName: "",
  yonghuName: "",
  submitFile: "",
  submitContent: "",
  submitStatus: "待批改",
  submitScore: null as number | null,
  submitRemark: ""
});

const createBatchForm = () => ({
  submitStatus: "已批改",
  submitScore: null as number | null,
  submitRemark: ""
});

const form = reactive(createForm());
const batchForm = reactive(createBatchForm());

const rules: FormRules = {
  submitStatus: [{ required: true, message: "请选择提交状态", trigger: "change" }]
};

function downloadUrl(fileName?: string) {
  return createDownloadUrl(DEFAULT_BASE_URL, fileName);
}

function resetForm() {
  Object.assign(form, createForm());
}

function resetBatchForm() {
  Object.assign(batchForm, createBatchForm());
}

function validateReviewPayload(status: string, score: number | null, remark: string) {
  if (status === "已批改" && (score === null || Number.isNaN(score))) {
    ElMessage.error("已批改状态必须填写评分");
    return false;
  }
  if (status !== "待批改" && !remark.trim()) {
    ElMessage.error("已批改或需重交状态必须填写评语");
    return false;
  }
  return true;
}

function buildPayload(
  source: HomeworkSubmissionItem,
  override?: { submitStatus: string; submitScore: number | null; submitRemark: string }
) {
  const status = override?.submitStatus ?? source.submitStatus ?? "待批改";
  return {
    id: source.id,
    zuoyeId: source.zuoyeId,
    yonghuId: source.yonghuId,
    submitFile: source.submitFile,
    submitContent: source.submitContent,
    submitStatus: status,
    submitScore: status === "已批改" ? (override?.submitScore ?? source.submitScore ?? null) : null,
    submitRemark: override?.submitRemark ?? source.submitRemark ?? "",
    submitDelete: source.submitDelete ?? 1
  };
}

async function loadItems() {
  const page = await fetchHomeworkSubmissionPage({
    page: pagination.page,
    limit: pagination.limit,
    zuoyeName: filters.zuoyeName || undefined,
    yonghuName: filters.yonghuName || undefined,
    submitStatus: filters.submitStatus || undefined
  });
  items.value = page.list;
  pagination.total = page.totalCount;
  selectedRows.value = [];
}

function handleSelectionChange(rows: HomeworkSubmissionItem[]) {
  selectedRows.value = rows;
}

function handleSearch() {
  pagination.page = 1;
  loadItems();
}

function resetFilters() {
  filters.zuoyeName = "";
  filters.yonghuName = "";
  filters.submitStatus = "";
  pagination.page = 1;
  loadItems();
}

function handleSizeChange() {
  pagination.page = 1;
  loadItems();
}

async function openReview(id: number) {
  resetForm();
  Object.assign(form, await fetchEntityDetail<HomeworkSubmissionItem>("zuoyeSubmit", id));
  dialogVisible.value = true;
}

function openBatchReview() {
  if (selectedRows.value.length === 0) {
    ElMessage.warning("请先选择要批改的提交记录");
    return;
  }
  resetBatchForm();
  batchDialogVisible.value = true;
}

async function submitSingleReview() {
  await formRef.value?.validate();
  if (!validateReviewPayload(form.submitStatus, form.submitScore, form.submitRemark)) {
    return;
  }
  saving.value = true;
  try {
    await saveEntity("zuoyeSubmit", buildPayload(form as unknown as HomeworkSubmissionItem));
    ElMessage.success("批改结果已保存");
    dialogVisible.value = false;
    await loadItems();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function submitBatchReview() {
  await batchFormRef.value?.validate();
  if (!validateReviewPayload(batchForm.submitStatus, batchForm.submitScore, batchForm.submitRemark)) {
    return;
  }
  saving.value = true;
  try {
    await Promise.all(
      selectedRows.value.map((item) =>
        saveEntity(
          "zuoyeSubmit",
          buildPayload(item, {
            submitStatus: batchForm.submitStatus,
            submitScore: batchForm.submitScore,
            submitRemark: batchForm.submitRemark
          })
        )
      )
    );
    ElMessage.success(`已完成 ${selectedRows.value.length} 条提交记录的批量批改`);
    batchDialogVisible.value = false;
    await loadItems();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "批量批改失败");
  } finally {
    saving.value = false;
  }
}

async function quickReject(row: HomeworkSubmissionItem) {
  saving.value = true;
  try {
    await saveEntity(
      "zuoyeSubmit",
      buildPayload(row, {
        submitStatus: "需重交",
        submitScore: null,
        submitRemark: row.submitRemark || "教师已退回，请根据要求修改后重新提交。"
      })
    );
    ElMessage.success("该提交已退回重交");
    await loadItems();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "退回失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  await deleteEntities("zuoyeSubmit", [id]);
  ElMessage.success("提交记录已删除");
  await loadItems();
}

async function removeSelected() {
  if (selectedRows.value.length === 0) {
    ElMessage.warning("请先选择要删除的提交记录");
    return;
  }
  await deleteEntities(
    "zuoyeSubmit",
    selectedRows.value.map((item) => item.id)
  );
  ElMessage.success(`已删除 ${selectedRows.value.length} 条提交记录`);
  await loadItems();
}

loadItems();
</script>
