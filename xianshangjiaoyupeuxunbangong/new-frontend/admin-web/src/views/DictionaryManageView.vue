<template>
  <section class="admin-panel">
    <div class="panel-header panel-header--spread">
      <h2>字典管理</h2>
      <div class="toolbar toolbar--wrap">
        <el-input v-model="keyword" placeholder="搜索字段名" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置筛选</el-button>
        <el-button type="success" @click="openCreate">新增字典</el-button>
      </div>
    </div>

    <el-table :data="dictionary" stripe>
      <el-table-column prop="dicCode" label="字段" min-width="160" />
      <el-table-column prop="dicName" label="字段名" min-width="160" />
      <el-table-column prop="codeIndex" label="编码" min-width="100" />
      <el-table-column prop="indexName" label="编码名称" min-width="180" />
      <el-table-column prop="beizhu" label="备注" min-width="200" />
      <el-table-column label="操作" width="180" fixed="right">
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
        @current-change="loadDictionary"
        @size-change="handleSizeChange"
      />
    </div>
  </section>

  <el-dialog v-model="dialogVisible" :title="form.id ? '编辑字典' : '新增字典'" width="720px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="字段" prop="dicCode"><el-input v-model="form.dicCode" /></el-form-item>
      <el-form-item label="字段名" prop="dicName"><el-input v-model="form.dicName" /></el-form-item>
      <el-form-item label="编码" prop="codeIndex"><el-input-number v-model="form.codeIndex" :min="0" :max="999999" /></el-form-item>
      <el-form-item label="编码名称" prop="indexName"><el-input v-model="form.indexName" /></el-form-item>
      <el-form-item label="父字段 ID"><el-input-number v-model="form.superId" :min="0" :max="999999" /></el-form-item>
      <el-form-item label="备注"><el-input v-model="form.beizhu" type="textarea" :rows="4" /></el-form-item>
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
import type { DictionaryItem } from "@shared/index";
import { fetchDictionary } from "@/api/dashboard";
import { deleteEntities, fetchEntityDetail, saveEntity } from "@/api/manage";

const keyword = ref("");
const dictionary = ref<DictionaryItem[]>([]);
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
  dicCode: "",
  dicName: "",
  codeIndex: undefined as number | undefined,
  indexName: "",
  superId: 0,
  beizhu: ""
});

const form = reactive(createForm());

const rules: FormRules = {
  dicCode: [{ required: true, message: "请输入字段", trigger: "blur" }],
  dicName: [{ required: true, message: "请输入字段名", trigger: "blur" }],
  codeIndex: [{ required: true, message: "请输入编码", trigger: "change" }],
  indexName: [{ required: true, message: "请输入编码名称", trigger: "blur" }]
};

async function loadDictionary() {
  const page = await fetchDictionary({
    page: pagination.page,
    limit: pagination.limit,
    dicName: keyword.value || undefined
  });
  dictionary.value = page.list;
  pagination.total = page.totalCount;
}

function resetForm() {
  Object.assign(form, createForm());
}

function handleSearch() {
  pagination.page = 1;
  loadDictionary();
}

function resetFilters() {
  keyword.value = "";
  pagination.page = 1;
  loadDictionary();
}

function handleSizeChange() {
  pagination.page = 1;
  loadDictionary();
}

function openCreate() {
  resetForm();
  dialogVisible.value = true;
}

async function openEdit(id: number) {
  resetForm();
  Object.assign(form, await fetchEntityDetail("dictionary", id));
  dialogVisible.value = true;
}

async function submitForm() {
  await formRef.value?.validate();
  saving.value = true;
  try {
    await saveEntity("dictionary", form as unknown as Record<string, unknown>);
    ElMessage.success("字典项已保存");
    dialogVisible.value = false;
    await loadDictionary();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

async function removeItem(id: number) {
  await deleteEntities("dictionary", [id]);
  ElMessage.success("字典项已删除");
  await loadDictionary();
}

loadDictionary();
</script>
