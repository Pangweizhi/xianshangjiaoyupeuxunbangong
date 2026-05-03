<template>
  <section class="admin-panel">
    <div class="panel-header panel-header--spread">
      <h2>轮播图管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索配置名称" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="success" @click="openCreate">新增轮播图</el-button>
      </div>
    </div>

    <div class="admin-list">
      <article v-for="item in displayConfigs" :key="item.id">
        <div class="config-card__content">
          <img v-if="assetUrl(item.value)" class="upload-preview" :src="assetUrl(item.value)" alt="轮播图预览" />
          <div>
            <strong>{{ item.name }}</strong>
            <p>{{ item.value }}</p>
          </div>
        </div>
        <div class="table-actions">
          <span>轮播项</span>
          <el-button link type="primary" @click="openEdit(item.id)">编辑</el-button>
          <el-button link type="danger" @click="removeItem(item.id)">删除</el-button>
        </div>
      </article>
    </div>

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        background
        layout="total, sizes, prev, pager, next"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        @current-change="loadConfig"
        @size-change="handleSizeChange"
      />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑轮播图' : '新增轮播图'" width="680px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="图片路径" prop="value">
        <el-input v-model="form.value" />
      </el-form-item>
      <el-form-item label="上传图片">
        <input type="file" accept="image/*" @change="handleUpload" />
        <img v-if="assetUrl(form.value)" class="upload-preview" :src="assetUrl(form.value)" alt="轮播图预览" />
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
import { DEFAULT_BASE_URL, createAssetUrl, type ConfigItem } from "@shared/index";
import { fetchConfig } from "@/api/dashboard";
import { deleteEntities, fetchEntityDetail, saveEntity, uploadAdminFile } from "@/api/manage";

const keyword = ref("");
const configs = ref<ConfigItem[]>([]);
const dialogVisible = ref(false);
const saving = ref(false);
const formRef = ref<FormInstance>();
const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0
});

const createForm = () => ({
  id: undefined as number | undefined,
  name: "轮播图",
  value: ""
});

const form = reactive(createForm());

const rules: FormRules = {
  name: [{ required: true, message: "请输入名称", trigger: "blur" }],
  value: [{ required: true, message: "请上传轮播图", trigger: "blur" }]
};

const displayConfigs = computed(() =>
  configs.value.filter((item) => !keyword.value || item.name.includes(keyword.value) || item.value.includes(keyword.value))
);

function assetUrl(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path);
}

async function loadConfig() {
  const page = await fetchConfig({
    page: pagination.page,
    limit: pagination.limit
  });
  configs.value = page.list;
  pagination.total = page.totalCount;
}

function resetForm() {
  Object.assign(form, createForm());
}

function handleSearch() {
  pagination.page = 1;
  loadConfig();
}

function resetFilters() {
  keyword.value = "";
  pagination.page = 1;
  loadConfig();
}

function handleSizeChange() {
  pagination.page = 1;
  loadConfig();
}

function openCreate() {
  resetForm();
  dialogVisible.value = true;
}

async function openEdit(id: number) {
  resetForm();
  Object.assign(form, await fetchEntityDetail("config", id));
  dialogVisible.value = true;
}

async function handleUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) {
    return;
  }
  try {
    form.value = await uploadAdminFile(file);
    ElMessage.success("轮播图已上传");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "上传失败");
  }
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    await saveEntity("config", form as unknown as Record<string, unknown>);
    ElMessage.success("轮播图已保存");
    dialogVisible.value = false;
    await loadConfig();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  await deleteEntities("config", [id]);
  ElMessage.success("轮播图已删除");
  await loadConfig();
}

loadConfig();
</script>

<style scoped>
.config-card__content {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
