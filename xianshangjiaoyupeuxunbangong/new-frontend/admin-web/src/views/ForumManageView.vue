<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <div>
        <h2>论坛管理</h2>
        <p class="panel-note">按前台阅读逻辑展示主题帖与回复帖，便于教师直接跟帖处理交流内容。</p>
      </div>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索帖子标题" clearable />
        <el-select v-model="authorFilter" placeholder="发布身份" clearable>
          <el-option label="学生" value="student" />
          <el-option label="教师" value="teacher" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-select v-model="typeFilter" placeholder="帖子类型" clearable>
          <el-option label="主题帖" value="topic" />
          <el-option label="回复帖" value="reply" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="success" @click="openCreate">新增帖子</el-button>
      </div>
    </div>

    <el-table :data="displayItems" stripe empty-text="暂无帖子数据">
      <el-table-column prop="forumName" label="标题" min-width="180" show-overflow-tooltip />
      <el-table-column label="类型" width="82">
        <template #default="{ row }">{{ row.superIds ? "回复帖" : "主题帖" }}</template>
      </el-table-column>
      <el-table-column prop="forumStateValue" label="状态" min-width="96" />
      <el-table-column label="发布者" min-width="110">
        <template #default="{ row }">{{ resolveAuthor(row) }}</template>
      </el-table-column>
      <el-table-column label="身份" width="74">
        <template #default="{ row }">{{ resolveAuthorType(row) }}</template>
      </el-table-column>
      <el-table-column label="所属主题" min-width="170" show-overflow-tooltip>
        <template #default="{ row }">{{ resolveParentName(row) }}</template>
      </el-table-column>
      <el-table-column prop="insertTime" label="发布时间" min-width="126" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <div class="table-actions table-actions--wrap">
            <el-button link type="success" @click="openReply(row)">回复</el-button>
            <el-button link type="primary" @click="openEdit(row.id)">编辑</el-button>
            <el-button link type="danger" @click="removeItem(row.id)">删除</el-button>
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
        @current-change="loadItems"
        @size-change="handleSizeChange"
      />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="760px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
      <el-form-item label="帖子标题" prop="forumName">
        <el-input v-model="form.forumName" />
      </el-form-item>
      <el-form-item label="所属主题">
        <el-select v-model="form.superIds" clearable placeholder="不选则为主题帖">
          <el-option v-for="item in topicOptions" :key="item.id" :label="item.forumName" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="帖子状态" prop="forumStateTypes">
        <el-select v-model="form.forumStateTypes">
          <el-option v-for="item in stateOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" />
        </el-select>
      </el-form-item>
      <el-form-item label="发布内容" prop="forumContent">
        <el-input v-model="form.forumContent" type="textarea" :rows="6" />
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
import type { ForumItem } from "@shared/index";
import { fetchForums } from "@/api/dashboard";
import { deleteEntities, fetchDictionaryOptions, fetchEntityDetail, saveEntity } from "@/api/manage";

const keyword = ref("");
const authorFilter = ref("");
const typeFilter = ref("");
const items = ref<ForumItem[]>([]);
const topicOptions = ref<ForumItem[]>([]);
const dialogVisible = ref(false);
const saving = ref(false);
const loading = ref(false);
const formRef = ref<FormInstance>();
const stateOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const dialogTitle = ref("新增帖子");

const createForm = () => ({
  id: undefined as number | undefined,
  forumName: "",
  forumContent: "",
  superIds: undefined as number | undefined,
  forumStateTypes: undefined as number | undefined
});
const form = reactive(createForm());

const rules: FormRules = {
  forumName: [{ required: true, message: "请输入帖子标题", trigger: "blur" }],
  forumStateTypes: [{ required: true, message: "请选择帖子状态", trigger: "change" }],
  forumContent: [{ required: true, message: "请输入发布内容", trigger: "blur" }]
};

const displayItems = computed(() =>
  items.value.filter((item) => {
    if (authorFilter.value === "student" && !item.yonghuName) return false;
    if (authorFilter.value === "teacher" && !item.jiaoshiName) return false;
    if (authorFilter.value === "admin" && !item.uusername) return false;
    if (typeFilter.value === "topic" && item.superIds) return false;
    if (typeFilter.value === "reply" && !item.superIds) return false;
    return true;
  })
);

function resolveAuthor(item: ForumItem) {
  return item.yonghuName || item.jiaoshiName || item.uusername || "-";
}

function resolveAuthorType(item: ForumItem) {
  if (item.yonghuName) return "学生";
  if (item.jiaoshiName) return "教师";
  if (item.uusername) return "管理员";
  return "-";
}

function resolveParentName(item: ForumItem) {
  if (!item.superIds) {
    return "当前就是主题帖";
  }
  return topicOptions.value.find((topic) => topic.id === item.superIds)?.forumName || `主题帖 #${item.superIds}`;
}

async function loadItems() {
  loading.value = true;
  try {
    const page = await fetchForums({
      page: pagination.page,
      limit: pagination.limit,
      forumName: keyword.value || undefined
    });
    items.value = page.list;
    topicOptions.value = page.list.filter((item) => !item.superIds);
    pagination.total = page.totalCount;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  loadItems();
}

function resetFilters() {
  keyword.value = "";
  authorFilter.value = "";
  typeFilter.value = "";
  pagination.page = 1;
  loadItems();
}

function handleSizeChange() {
  pagination.page = 1;
  loadItems();
}

function resetForm() {
  Object.assign(form, createForm());
}

async function prepareDialog() {
  stateOptions.value = await fetchDictionaryOptions("forum_state_types");
  if (!topicOptions.value.length) {
    const page = await fetchForums({ page: 1, limit: 100 });
    topicOptions.value = page.list.filter((item) => !item.superIds);
  }
}

async function openCreate() {
  resetForm();
  dialogTitle.value = "新增帖子";
  await prepareDialog();
  dialogVisible.value = true;
}

async function openReply(row: ForumItem) {
  resetForm();
  dialogTitle.value = `回复：${row.forumName}`;
  await prepareDialog();
  form.superIds = row.superIds || row.id;
  form.forumName = `回复：${row.forumName}`;
  form.forumStateTypes = 2;
  dialogVisible.value = true;
}

async function openEdit(id: number) {
  resetForm();
  dialogTitle.value = "编辑帖子";
  await prepareDialog();
  Object.assign(form, await fetchEntityDetail("forum", id));
  dialogVisible.value = true;
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    await saveEntity("forum", form as unknown as Record<string, unknown>);
    ElMessage.success("帖子已保存");
    dialogVisible.value = false;
    await loadItems();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  await deleteEntities("forum", [id]);
  ElMessage.success("帖子已删除");
  await loadItems();
}

loadItems();
</script>

<style scoped>
.table-actions--wrap {
  flex-wrap: wrap;
}
</style>
