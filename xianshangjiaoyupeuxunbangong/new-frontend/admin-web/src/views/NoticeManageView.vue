<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>公告管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索公告标题" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button type="success" @click="openCreate">新增公告</el-button>
      </div>
    </div>

    <div v-if="notices.length > 0" class="admin-list">
      <article v-for="notice in notices" :key="notice.id">
        <div>
          <strong>{{ notice.newsName }}</strong>
          <p>{{ stripHtml(notice.newsContent) }}</p>
        </div>
        <div class="table-actions">
          <span>{{ notice.insertTime?.slice(0, 10) || "待更新" }}</span>
          <el-button link type="primary" @click="openEdit(notice.id)">编辑</el-button>
          <el-button link type="danger" @click="removeItem(notice.id)">删除</el-button>
        </div>
      </article>
    </div>

    <el-empty v-else description="暂无公告数据" />

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        background
        layout="total, sizes, prev, pager, next"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        @current-change="loadNotices"
        @size-change="handleSizeChange"
      />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑公告' : '新增公告'" width="720px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="公告标题" prop="newsName">
        <el-input v-model="form.newsName" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="公告类型" prop="newsTypes">
        <el-select v-model="form.newsTypes" placeholder="请选择">
          <el-option v-for="item in newsTypeOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" />
        </el-select>
      </el-form-item>
      <el-form-item label="公告图片">
        <input type="file" accept="image/*" @change="handleUpload" />
        <p class="upload-tip">{{ form.newsPhoto || "未上传" }}</p>
        <img v-if="assetUrl(form.newsPhoto)" class="upload-preview" :src="assetUrl(form.newsPhoto)" alt="公告图片预览" />
      </el-form-item>
      <el-form-item label="公告详情" prop="newsContent">
        <el-input v-model="form.newsContent" type="textarea" :rows="6" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitForm">提交</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { DEFAULT_BASE_URL, createAssetUrl, type NoticeItem } from "@shared/index";
import { fetchAdminNotices } from "@/api/dashboard";
import { deleteEntities, fetchDictionaryOptions, fetchEntityDetail, saveEntity, uploadAdminFile } from "@/api/manage";

const keyword = ref("");
const notices = ref<NoticeItem[]>([]);
const dialogVisible = ref(false);
const saving = ref(false);
const loading = ref(false);
const formRef = ref<FormInstance>();
const newsTypeOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });

const createForm = () => ({
  id: undefined as number | undefined,
  newsName: "",
  newsTypes: undefined as number | undefined,
  newsPhoto: "",
  newsContent: ""
});
const form = reactive(createForm());

const rules: FormRules = {
  newsName: [{ required: true, message: "请输入公告标题", trigger: "blur" }],
  newsTypes: [{ required: true, message: "请选择公告类型", trigger: "change" }],
  newsContent: [{ required: true, message: "请输入公告详情", trigger: "blur" }]
};

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 100) || "暂无公告内容";
}

function assetUrl(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path);
}

async function loadNotices() {
  loading.value = true;
  try {
    const page = await fetchAdminNotices({
      page: pagination.page,
      limit: pagination.limit,
      newsName: keyword.value || undefined
    });
    notices.value = page.list;
    pagination.total = page.totalCount;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  loadNotices();
}

function resetFilters() {
  keyword.value = "";
  pagination.page = 1;
  loadNotices();
}

function handleSizeChange() {
  pagination.page = 1;
  loadNotices();
}

function resetForm() {
  Object.assign(form, createForm());
}

async function loadNewsTypes() {
  newsTypeOptions.value = await fetchDictionaryOptions("news_types");
}

async function openCreate() {
  resetForm();
  await loadNewsTypes();
  dialogVisible.value = true;
}

async function openEdit(id: number) {
  resetForm();
  await loadNewsTypes();
  Object.assign(form, await fetchEntityDetail("news", id));
  form.id = id;
  dialogVisible.value = true;
}

async function handleUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) {
    return;
  }
  try {
    form.newsPhoto = await uploadAdminFile(file);
    ElMessage.success("公告图片已上传");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "上传失败");
  }
}

async function submitForm() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) {
    return;
  }

  saving.value = true;
  try {
    await saveEntity("news", { ...form, id: form.id } as unknown as Record<string, unknown>);
    ElMessage.success("公告已保存");
    dialogVisible.value = false;
    await loadNotices();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  await deleteEntities("news", [id]);
  ElMessage.success("公告已删除");
  await loadNotices();
}

loadNotices();
</script>
