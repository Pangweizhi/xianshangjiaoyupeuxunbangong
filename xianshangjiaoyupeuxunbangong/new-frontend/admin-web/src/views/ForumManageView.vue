<template>
  <section class="admin-panel forum-manage" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <div>
        <h2>论坛管理</h2>
        <p class="panel-note">按前台讨论流组织主题和回复，教师在后台可以沿着完整上下文处理交流内容。</p>
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

    <div class="forum-manage__layout">
      <section class="forum-stream">
        <article
          v-for="topic in topicThreads"
          :key="topic.id"
          :class="['forum-thread-card', { 'is-active': selectedThreadId === topic.id }]"
          @click="selectThread(topic.id)"
        >
          <div class="forum-thread-card__meta">
            <span class="tag">主题帖</span>
            <span class="meta">{{ resolveAuthorType(topic) }}</span>
            <span class="meta">{{ resolveAuthor(topic) }}</span>
            <span class="meta">{{ topic.forumStateValue || "讨论中" }}</span>
          </div>
          <h3>{{ topic.forumName }}</h3>
          <p>{{ summarize(topic.forumContent) }}</p>
          <div v-if="replyMap[topic.id]?.length" class="forum-thread-card__glance">
            <div v-for="reply in replyMap[topic.id].slice(0, 2)" :key="reply.id" class="forum-thread-card__reply">
              <strong>{{ resolveAuthor(reply) }}</strong>
              <p>{{ summarize(reply.forumContent, 56) }}</p>
            </div>
          </div>
          <div class="forum-thread-card__footer">
            <span class="forum-count">{{ replyMap[topic.id]?.length || 0 }} 条回复</span>
            <span class="forum-soft-tag">{{ topic.insertTime?.slice(0, 16) || "待更新" }}</span>
          </div>
        </article>

        <article
          v-for="reply in standaloneReplies"
          :key="reply.id"
          :class="['forum-thread-card', { 'is-active': selectedReplyId === reply.id }]"
          @click="selectReply(reply.id)"
        >
          <div class="forum-thread-card__meta">
            <span class="tag">回复帖</span>
            <span class="meta">{{ resolveAuthorType(reply) }}</span>
            <span class="meta">{{ resolveAuthor(reply) }}</span>
            <span class="meta">{{ reply.forumStateValue || "讨论中" }}</span>
          </div>
          <h3>{{ reply.forumName }}</h3>
          <p>{{ summarize(reply.forumContent) }}</p>
          <div class="forum-thread-card__footer">
            <span class="forum-soft-tag">所属主题：{{ resolveParentName(reply) }}</span>
            <span class="forum-soft-tag">{{ reply.insertTime?.slice(0, 16) || "待更新" }}</span>
          </div>
        </article>

        <div v-if="!topicThreads.length && !standaloneReplies.length" class="forum-empty">
          <strong>当前没有符合条件的讨论内容</strong>
          <p>可以调整筛选条件，或者直接新增一个主题帖。</p>
        </div>
      </section>

      <section v-if="selectedTopic" class="forum-detail">
        <article class="forum-detail__hero">
          <div class="forum-detail__meta">
            <span class="tag">{{ selectedTopic.forumStateValue || "讨论中" }}</span>
            <span class="meta">{{ resolveAuthorType(selectedTopic) }}</span>
            <span class="meta">{{ resolveAuthor(selectedTopic) }}</span>
            <span class="meta">{{ selectedTopic.insertTime?.slice(0, 16) || "待更新" }}</span>
          </div>
          <h3>{{ selectedTopic.forumName }}</h3>
          <p class="forum-detail__content">{{ summarize(selectedTopic.forumContent, 400) }}</p>
        </article>

        <div class="forum-detail__actions">
          <el-button type="primary" @click="openReply(selectedTopic)">回复主题</el-button>
          <el-button @click="openEdit(selectedTopic.id)">编辑主题</el-button>
          <el-button type="danger" plain @click="removeItem(selectedTopic.id)">删除主题</el-button>
        </div>

        <div class="panel-header">
          <div>
            <h3>讨论回复</h3>
            <p class="panel-note">保持和前台一致的阅读顺序，先看上下文再处理具体回复。</p>
          </div>
          <span class="forum-count">{{ selectedReplies.length }} 条回复</span>
        </div>

        <div v-if="selectedReplies.length" class="forum-detail__replies">
          <article v-for="reply in selectedReplies" :key="reply.id" class="forum-reply">
            <div class="forum-reply__meta">
              <div class="forum-detail__meta">
                <span class="tag">回复帖</span>
                <span class="meta">{{ resolveAuthorType(reply) }}</span>
                <span class="meta">{{ resolveAuthor(reply) }}</span>
              </div>
              <span class="forum-soft-tag">{{ reply.insertTime?.slice(0, 16) || "待更新" }}</span>
            </div>
            <h4>{{ reply.forumName }}</h4>
            <p>{{ summarize(reply.forumContent, 220) }}</p>
            <div class="table-actions">
              <el-button link type="success" @click="openReply(reply)">继续回复</el-button>
              <el-button link type="primary" @click="openEdit(reply.id)">编辑</el-button>
              <el-button link type="danger" @click="removeItem(reply.id)">删除</el-button>
            </div>
          </article>
        </div>
        <div v-else class="forum-empty">
          <strong>这个主题还没有回复</strong>
          <p>可以直接从右侧发起第一条回复。</p>
        </div>
      </section>

      <section v-else-if="selectedReply" class="forum-detail">
        <article class="forum-detail__hero">
          <div class="forum-detail__meta">
            <span class="tag">回复帖</span>
            <span class="meta">{{ resolveAuthorType(selectedReply) }}</span>
            <span class="meta">{{ resolveAuthor(selectedReply) }}</span>
            <span class="meta">{{ selectedReply.insertTime?.slice(0, 16) || "待更新" }}</span>
          </div>
          <h3>{{ selectedReply.forumName }}</h3>
          <p class="forum-detail__content">{{ summarize(selectedReply.forumContent, 400) }}</p>
        </article>

        <div class="forum-detail__actions">
          <el-button type="primary" @click="openReply(selectedReply)">继续回复</el-button>
          <el-button @click="openEdit(selectedReply.id)">编辑回复</el-button>
          <el-button type="danger" plain @click="removeItem(selectedReply.id)">删除回复</el-button>
        </div>

        <article class="forum-reply">
          <div class="forum-detail__meta">
            <span class="tag">所属主题</span>
            <span class="meta">{{ resolveParentName(selectedReply) }}</span>
          </div>
          <p>{{ selectedReply.superIds ? "这条回复未出现在当前页的主题列表中，因此单独展示。" : "当前帖子没有父主题。" }}</p>
        </article>
      </section>

      <section v-else class="forum-detail forum-empty">
        <strong>请选择一个讨论线程查看完整内容</strong>
        <p>左侧列表会按主题聚合帖子，便于教师按讨论线程处理内容。</p>
      </section>
    </div>

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
        <el-select v-model="form.superIds" clearable placeholder="不选择则为主题帖">
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
const selectedThreadId = ref<number | null>(null);
const selectedReplyId = ref<number | null>(null);

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

const topicThreads = computed(() => displayItems.value.filter((item) => !item.superIds));
const standaloneReplies = computed(() =>
  displayItems.value.filter((item) => item.superIds && !topicThreads.value.some((topic) => topic.id === item.superIds))
);
const replyMap = computed(() => {
  const map: Record<number, ForumItem[]> = {};
  displayItems.value
    .filter((item) => item.superIds)
    .forEach((item) => {
      if (!item.superIds) {
        return;
      }
      if (!map[item.superIds]) {
        map[item.superIds] = [];
      }
      map[item.superIds].push(item);
    });
  return map;
});
const selectedTopic = computed(() => {
  if (!selectedThreadId.value) {
    return topicThreads.value[0] || null;
  }
  return topicThreads.value.find((item) => item.id === selectedThreadId.value) || topicThreads.value[0] || null;
});
const selectedReplies = computed(() => (selectedTopic.value ? replyMap.value[selectedTopic.value.id] || [] : []));
const selectedReply = computed(() => {
  if (!selectedReplyId.value) {
    return null;
  }
  return displayItems.value.find((item) => item.id === selectedReplyId.value && item.superIds) || null;
});

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

function summarize(content?: string, limit = 96) {
  return content?.replace(/<[^>]+>/g, "").trim().slice(0, limit) || "暂无帖子内容。";
}

function selectThread(id: number) {
  selectedThreadId.value = id;
  selectedReplyId.value = null;
}

function selectReply(id: number) {
  selectedReplyId.value = id;
  selectedThreadId.value = null;
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

    if (selectedThreadId.value && !topicOptions.value.some((item) => item.id === selectedThreadId.value)) {
      selectedThreadId.value = topicOptions.value[0]?.id ?? null;
    }
    if (selectedReplyId.value && !items.value.some((item) => item.id === selectedReplyId.value)) {
      selectedReplyId.value = null;
    }
    if (!selectedThreadId.value && !selectedReplyId.value) {
      selectedThreadId.value = topicOptions.value[0]?.id ?? null;
    }
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  selectedThreadId.value = null;
  selectedReplyId.value = null;
  loadItems();
}

function resetFilters() {
  keyword.value = "";
  authorFilter.value = "";
  typeFilter.value = "";
  pagination.page = 1;
  selectedThreadId.value = null;
  selectedReplyId.value = null;
  loadItems();
}

function handleSizeChange() {
  pagination.page = 1;
  selectedThreadId.value = null;
  selectedReplyId.value = null;
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
  if (selectedThreadId.value === id) {
    selectedThreadId.value = null;
  }
  if (selectedReplyId.value === id) {
    selectedReplyId.value = null;
  }
  await loadItems();
}

loadItems();
</script>
