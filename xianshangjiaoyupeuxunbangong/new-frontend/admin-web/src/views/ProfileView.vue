<template>
  <section class="admin-panel profile-manage" v-loading="loading">
    <div class="panel-header panel-header--spread">
      <div>
        <h2>个人中心</h2>
        <p class="panel-note">维护当前登录账号的基础资料。教师可更新个人信息，管理员可维护账号与密码。</p>
      </div>
      <el-button type="primary" :loading="saving" @click="submitProfile">保存信息</el-button>
    </div>

    <div class="profile-manage__layout">
      <aside class="profile-manage__summary">
        <div v-if="isTeacher" class="profile-manage__avatar-wrap">
          <img
            v-if="teacherForm.jiaoshiPhoto"
            :src="assetUrl(teacherForm.jiaoshiPhoto)"
            alt="教师头像"
            class="profile-manage__avatar"
          />
          <div v-else class="profile-manage__avatar profile-manage__avatar--placeholder">
            {{ teacherForm.jiaoshiName?.slice(0, 1) || "师" }}
          </div>
        </div>
        <strong>{{ isTeacher ? teacherForm.jiaoshiName || store.session?.username : adminForm.username || store.session?.username }}</strong>
        <span>{{ store.displayRole }}</span>
        <p>{{ isTeacher ? "建议保持联系方式和邮箱最新，方便课程和教学沟通。" : "管理员账号用于后台维护，修改密码后请使用新密码重新登录。" }}</p>
      </aside>

      <section class="profile-manage__form">
        <el-form
          v-if="isTeacher"
          ref="teacherFormRef"
          :model="teacherForm"
          :rules="teacherRules"
          label-width="96px"
        >
          <el-form-item label="账号" prop="username">
            <el-input v-model="teacherForm.username" />
          </el-form-item>
          <el-form-item label="教师姓名" prop="jiaoshiName">
            <el-input v-model="teacherForm.jiaoshiName" />
          </el-form-item>
          <el-form-item label="性别" prop="sexTypes">
            <el-select v-model="teacherForm.sexTypes" placeholder="请选择性别">
              <el-option v-for="item in sexOptions" :key="item.codeIndex" :label="item.indexName" :value="item.codeIndex" />
            </el-select>
          </el-form-item>
          <el-form-item label="头像">
            <label class="ghost-button upload-button">
              上传头像
              <input type="file" accept="image/*" hidden @change="handleTeacherUpload" />
            </label>
            <p class="upload-tip">{{ teacherForm.jiaoshiPhoto || "未上传头像" }}</p>
          </el-form-item>
          <el-form-item label="身份证号" prop="jiaoshiIdNumber">
            <el-input v-model="teacherForm.jiaoshiIdNumber" />
          </el-form-item>
          <el-form-item label="联系方式" prop="jiaoshiPhone">
            <el-input v-model="teacherForm.jiaoshiPhone" />
          </el-form-item>
          <el-form-item label="电子邮箱" prop="jiaoshiEmail">
            <el-input v-model="teacherForm.jiaoshiEmail" />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="teacherPassword" show-password placeholder="不填写则保持原密码" />
          </el-form-item>
        </el-form>

        <el-form
          v-else
          ref="adminFormRef"
          :model="adminForm"
          :rules="adminRules"
          label-width="96px"
        >
          <el-form-item label="账号" prop="username">
            <el-input v-model="adminForm.username" />
          </el-form-item>
          <el-form-item label="角色">
            <el-input :model-value="adminForm.role || store.displayRole" disabled />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="adminPassword" show-password placeholder="不填写则保持原密码" />
          </el-form-item>
        </el-form>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { DEFAULT_BASE_URL, createAssetUrl, type AdminUserItem, type TeacherItem } from "@shared/index";
import { fetchCurrentEntitySession, fetchDictionaryOptions, saveEntity, uploadAdminFile } from "@/api/manage";
import { useAdminSessionStore } from "@/stores/session";

const store = useAdminSessionStore();
const isTeacher = computed(() => store.session?.tableName === "jiaoshi");
const loading = ref(false);
const saving = ref(false);
const sexOptions = ref<Array<{ codeIndex: number; indexName: string }>>([]);
const teacherFormRef = ref<FormInstance>();
const adminFormRef = ref<FormInstance>();
const teacherPassword = ref("");
const adminPassword = ref("");

const teacherForm = reactive<TeacherItem & { password?: string; sexTypes?: number; jiaoshiIdNumber?: string; jiaoshiDelete?: number }>({
  id: 0,
  username: "",
  jiaoshiName: "",
  sexValue: "",
  jiaoshiPhoto: "",
  jiaoshiPhone: "",
  jiaoshiEmail: "",
  password: "",
  sexTypes: undefined,
  jiaoshiIdNumber: "",
  jiaoshiDelete: 1
});

const adminForm = reactive<AdminUserItem>({
  id: 0,
  username: "",
  password: "",
  role: ""
});

const teacherRules: FormRules = {
  username: [{ required: true, message: "请输入账号", trigger: "blur" }],
  jiaoshiName: [{ required: true, message: "请输入教师姓名", trigger: "blur" }],
  sexTypes: [{ required: true, message: "请选择性别", trigger: "change" }],
  jiaoshiPhone: [{ required: true, message: "请输入联系方式", trigger: "blur" }],
  jiaoshiEmail: [
    { required: true, message: "请输入电子邮箱", trigger: "blur" },
    { type: "email", message: "邮箱格式不正确", trigger: "blur" }
  ]
};

const adminRules: FormRules = {
  username: [{ required: true, message: "请输入账号", trigger: "blur" }]
};

function assetUrl(path?: string) {
  return createAssetUrl(DEFAULT_BASE_URL, path);
}

async function loadProfile() {
  loading.value = true;
  try {
    if (isTeacher.value) {
      const [profile, sexList] = await Promise.all([
        fetchCurrentEntitySession<TeacherItem & { password?: string; sexTypes?: number; jiaoshiIdNumber?: string; jiaoshiDelete?: number }>("jiaoshi"),
        fetchDictionaryOptions("sex_types")
      ]);
      Object.assign(teacherForm, profile);
      sexOptions.value = sexList;
      teacherPassword.value = "";
      return;
    }

    const profile = await fetchCurrentEntitySession<AdminUserItem>("users");
    Object.assign(adminForm, profile);
    adminPassword.value = "";
  } finally {
    loading.value = false;
  }
}

async function handleTeacherUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (!file) {
    return;
  }
  try {
    teacherForm.jiaoshiPhoto = await uploadAdminFile(file);
    ElMessage.success("头像上传成功");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "上传失败");
  } finally {
    (event.target as HTMLInputElement).value = "";
  }
}

async function submitProfile() {
  saving.value = true;
  try {
    if (isTeacher.value) {
      await teacherFormRef.value?.validate();
      await saveEntity("jiaoshi", {
        ...teacherForm,
        password: teacherPassword.value || teacherForm.password,
        jiaoshiDelete: teacherForm.jiaoshiDelete ?? 1
      });
    } else {
      await adminFormRef.value?.validate();
      await saveEntity("users", {
        ...adminForm,
        password: adminPassword.value || adminForm.password
      });
    }
    ElMessage.success("个人信息已保存");
    await loadProfile();
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "保存失败");
  } finally {
    saving.value = false;
  }
}

loadProfile();
</script>

<style scoped>
.profile-manage {
  padding: 24px;
}

.profile-manage__layout {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 20px;
}

.profile-manage__summary,
.profile-manage__form {
  border: 1px solid var(--admin-line);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.74);
}

.profile-manage__summary {
  padding: 24px;
  display: grid;
  align-content: start;
  gap: 12px;
  background:
    linear-gradient(135deg, rgba(255, 244, 231, 0.92), rgba(238, 245, 255, 0.96)),
    #fff;
}

.profile-manage__summary strong {
  font-size: 1.4rem;
  color: var(--admin-text);
}

.profile-manage__summary span,
.profile-manage__summary p {
  color: var(--admin-muted);
  line-height: 1.7;
  margin: 0;
}

.profile-manage__form {
  padding: 24px;
}

.profile-manage__avatar-wrap {
  margin-bottom: 6px;
}

.profile-manage__avatar {
  width: 116px;
  height: 116px;
  border-radius: 28px;
  object-fit: cover;
  border: 1px solid var(--admin-line);
  background: #fff;
}

.profile-manage__avatar--placeholder {
  display: grid;
  place-items: center;
  font-size: 2rem;
  font-weight: 700;
  color: var(--admin-accent);
  background:
    linear-gradient(135deg, rgba(255, 244, 231, 0.92), rgba(238, 245, 255, 0.96)),
    #fff;
}

.upload-button {
  cursor: pointer;
}

@media (max-width: 960px) {
  .profile-manage__layout {
    grid-template-columns: 1fr;
  }
}
</style>
