<template>
  <section class="admin-panel" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <h2>{{ isTeacher ? "选课情况" : "选课管理" }}</h2>
      <div class="toolbar toolbar--wrap">
        <el-select v-model="filters.kechengId" placeholder="课程" clearable>
          <el-option v-for="item in courseOptions" :key="item.id" :label="item.kechengName" :value="item.id" />
        </el-select>
        <el-select v-model="filters.enrollStatus" placeholder="状态" clearable>
          <el-option label="已选课" value="已选课" />
          <el-option label="学习中" value="学习中" />
          <el-option label="已结课" value="已结课" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </div>

    <el-table :data="rows" stripe empty-text="暂无选课记录">
      <el-table-column prop="kechengName" label="课程" min-width="200" />
      <el-table-column prop="yonghuName" label="学生" min-width="120" />
      <el-table-column prop="jiaoshiName" label="教师" min-width="120" />
      <el-table-column prop="enrollStatus" label="状态" min-width="120" />
      <el-table-column label="进度" min-width="140">
        <template #default="{ row }">
          <el-progress :percentage="Math.round(row.progressPercent || 0)" :stroke-width="10" />
        </template>
      </el-table-column>
      <el-table-column prop="enrollTime" label="选课时间" min-width="180" />
      <el-table-column prop="finishTime" label="结课时间" min-width="180" />
      <el-table-column prop="creditScore" label="课程学分" min-width="100" />
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
import type { CourseEnrollItem } from "@shared/index";
import { useAdminSessionStore } from "@/stores/session";
import { fetchCourseEnrollPage } from "@/api/dashboard";
import { fetchCoursesForSelect } from "@/api/manage";

const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");
const loading = ref(false);
const rows = ref<CourseEnrollItem[]>([]);
const courseOptions = ref<Array<{ id: number; kechengName: string }>>([]);
const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive({ kechengId: undefined as number | undefined, enrollStatus: "" });

async function loadOptions() {
  courseOptions.value = await fetchCoursesForSelect();
}

async function loadRows() {
  loading.value = true;
  try {
    const page = await fetchCourseEnrollPage({
      page: pagination.page,
      limit: pagination.limit,
      kechengId: filters.kechengId,
      enrollStatus: filters.enrollStatus || undefined
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
  filters.enrollStatus = "";
  pagination.page = 1;
  loadRows();
}

function handleSizeChange() {
  pagination.page = 1;
  loadRows();
}

loadOptions();
loadRows();
</script>

