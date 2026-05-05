<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>{{ isTeacher ? "学习进度" : "学习进度管理" }}</h2>
      <div class="toolbar toolbar--wrap">
        <el-select v-model="filters.kechengId" placeholder="课程" clearable>
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.yonghuId" placeholder="学生" clearable>
          <el-option v-for="item in studentOptions" :key="item.id" :label="item.yonghuName" :value="item.id" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>

    <el-table :data="rows" stripe empty-text="暂无学习进度">
      <el-table-column prop="kechengName" label="课程" min-width="180" />
      <el-table-column prop="chapterName" label="章节" min-width="180" />
      <el-table-column prop="resourceName" label="资源" min-width="220" />
      <el-table-column prop="resourceType" label="类型" min-width="120" />
      <el-table-column prop="yonghuName" label="学生" min-width="120" />
      <el-table-column prop="studySeconds" label="学习秒数" min-width="100" />
      <el-table-column label="进度" min-width="140">
        <template #default="{ row }">
          <el-progress :percentage="progressDisplay(row)" :stroke-width="10" />
        </template>
      </el-table-column>
      <el-table-column label="完成状态" min-width="120">
        <template #default="{ row }">
          <span>{{ row.isCompleted === 1 ? "已完成" : "学习中" }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="lastStudyTime" label="最近学习时间" min-width="180" />
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
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import type { StudyProgressItem } from "@shared/index";
import { useAdminSessionStore } from "@/stores/session";
import { fetchStudyProgressPage } from "@/api/dashboard";
import { fetchCoursesForSelect, fetchStudentsForSelect } from "@/api/manage";

const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");
const loading = ref(false);
const rows = ref<StudyProgressItem[]>([]);
const courseOptions = ref<Array<{ id: number; kechengName: string }>>([]);
const studentOptions = ref<Array<{ id: number; yonghuName: string }>>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ kechengId: undefined as number | undefined, yonghuId: undefined as number | undefined });

async function loadOptions() {
  const [courses, students] = await Promise.all([fetchCoursesForSelect(), fetchStudentsForSelect()]);
  courseOptions.value = courses;
  studentOptions.value = students;
}

async function loadRows() {
  loading.value = true;
  try {
    const page = await fetchStudyProgressPage({
      page: pagination.page,
      limit: pagination.limit,
      kechengId: filters.kechengId,
      yonghuId: filters.yonghuId
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
  filters.kechengId = undefined;
  filters.yonghuId = undefined;
  pagination.page = 1;
  loadRows();
}

function progressDisplay(row: StudyProgressItem) {
  if (row.isCompleted === 1 || (row.progressPercent || 0) >= 100) {
    return 100;
  }
  return Math.min(99, Math.floor(row.progressPercent || 0));
}

function handleSizeChange() {
  pagination.page = 1;
  loadRows();
}

loadOptions();
loadRows();
</script>
