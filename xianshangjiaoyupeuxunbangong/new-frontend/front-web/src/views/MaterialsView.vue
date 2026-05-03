<template>
  <section class="section section--tight">
    <div class="filter-bar filter-bar--surface filter-grid">
      <input v-model="filters.keyword" class="field" placeholder="搜索资源标题" />
      <select v-model="filters.teacher" class="field">
        <option value="">全部教师</option>
        <option v-for="item in teacherOptions" :key="item" :value="item">{{ item }}</option>
      </select>
      <select v-model="filters.type" class="field">
        <option value="">全部类型</option>
        <option v-for="item in typeOptions" :key="item" :value="item">{{ item }}</option>
      </select>
      <button class="primary-button" @click="loadMaterials">查询</button>
    </div>

    <div class="content-grid">
      <article v-for="item in materials" :key="item.id" class="feature-card feature-card--compact">
        <img :src="toAsset(item.jiaoxueshipinPhoto)" :alt="item.jiaoxueshipinName" />
        <div>
          <div class="stack-inline">
            <span class="tag">{{ item.jiaoxueshipinValue || "备课" }}</span>
            <span class="meta">{{ item.jiaoshiName || "教师待补充" }}</span>
          </div>
          <h3>{{ item.jiaoxueshipinName }}</h3>
          <p>{{ stripHtml(item.jiaoxueshipinContent) }}</p>
          <div class="status-list">
            <span>{{ item.jiaoxueshipinTime?.slice(0, 10) || "时间待定" }}</span>
            <span>{{ item.jiaoxueshipinFile ? "含附件" : "无附件" }}</span>
          </div>
          <RouterLink class="text-link" :to="`/materials/${item.id}`">查看详情</RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { RouterLink } from "vue-router";
import { DEFAULT_BASE_URL, createAssetUrl, type LessonMaterialItem } from "@shared/index";
import { fetchMaterialPage } from "@/api/content";

const filters = reactive({
  keyword: "",
  teacher: "",
  type: ""
});
const materials = ref<LessonMaterialItem[]>([]);

const teacherOptions = computed(() =>
  Array.from(new Set(materials.value.map((item) => item.jiaoshiName).filter(Boolean) as string[]))
);
const typeOptions = computed(() =>
  Array.from(new Set(materials.value.map((item) => item.jiaoxueshipinValue).filter(Boolean) as string[]))
);

function toAsset(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path) || "https://dummyimage.com/600x400/e6efe4/21393b&text=Lesson";
}

function stripHtml(value?: string) {
  return value?.replace(/<[^>]+>/g, "").slice(0, 100) || "暂无备课内容。";
}

async function loadMaterials() {
  const page = await fetchMaterialPage({ limit: 100, jiaoxueshipinName: filters.keyword || undefined });
  materials.value = page.list.filter((item) => {
    const matchTeacher = !filters.teacher || item.jiaoshiName === filters.teacher;
    const matchType = !filters.type || item.jiaoxueshipinValue === filters.type;
    return matchTeacher && matchType;
  });
}

loadMaterials();
</script>

<style scoped>
.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 960px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
