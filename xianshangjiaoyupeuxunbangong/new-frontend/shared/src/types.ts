export type UserTable = "users" | "jiaoshi" | "yonghu";

export interface AuthSession {
  token: string;
  userId: number;
  role: string;
  tableName: UserTable;
  username?: string;
}

export interface ApiResponse<T> {
  code: number;
  msg: string;
  data: T;
  token?: string;
  role?: string;
  userId?: number;
  tableName?: UserTable;
}

export interface PagePayload<T> {
  totalCount: number;
  pageSize: number;
  totalPage: number;
  currPage: number;
  list: T[];
}

export interface CourseItem {
  id: number;
  kechengName: string;
  kechengPhoto?: string;
  kechengValue?: string;
  kechengTypes?: number;
  kechengShichang?: number;
  kechengTime?: string;
  banjiValue?: string;
  jiaoshiName?: string;
  kechengContent?: string;
}

export interface NoticeItem {
  id: number;
  newsName: string;
  newsPhoto?: string;
  newsValue?: string;
  newsTypes?: number;
  insertTime?: string;
  newsContent?: string;
}

export interface HomeworkItem {
  id: number;
  zuoyeName: string;
  zuoyePhoto?: string;
  zuoyeValue?: string;
  zuoyeTypes?: number;
  zuoyeFile?: string;
  jiaoshiName?: string;
  zuoyeContent?: string;
  insertTime?: string;
}

export interface LessonMaterialItem {
  id: number;
  jiaoxueshipinName: string;
  jiaoxueshipinPhoto?: string;
  jiaoxueshipinFile?: string;
  jiaoxueshipinValue?: string;
  jiaoshiName?: string;
  jiaoxueshipinTime?: string;
  jiaoxueshipinContent?: string;
}

export interface MeetingItem {
  id: number;
  kaihuitongzhiName: string;
  kaihuitongzhiValue?: string;
  kaihuitongzhiContent?: string;
  insertTime?: string;
}

export interface HomeworkSubmissionItem {
  id: number;
  zuoyeId: number;
  yonghuId: number;
  submitFile?: string;
  submitContent?: string;
  submitStatus?: string;
  submitScore?: number | null;
  submitRemark?: string;
  submitDelete?: number;
  checkTime?: string;
  insertTime?: string;
  createTime?: string;
  zuoyeName?: string;
  yonghuName?: string;
  yonghuPhoto?: string;
  jiaoshiName?: string;
  jiaoshiUuidNumber?: string;
}

export interface ForumItem {
  id: number;
  forumName: string;
  forumContent?: string;
  forumStateValue?: string;
  yonghuName?: string;
  jiaoshiName?: string;
  uusername?: string;
  insertTime?: string;
  updateTime?: string;
}

export interface StudentItem {
  id: number;
  username: string;
  yonghuName: string;
  sexValue?: string;
  yonghuPhoto?: string;
  yonghuPhone?: string;
  yonghuEmail?: string;
  banjiValue?: string;
  createTime?: string;
}

export interface TeacherItem {
  id: number;
  username: string;
  jiaoshiName: string;
  sexValue?: string;
  jiaoshiPhoto?: string;
  jiaoshiPhone?: string;
  jiaoshiEmail?: string;
  createTime?: string;
}

export interface DictionaryItem {
  id: number;
  dicCode: string;
  dicName: string;
  codeIndex: number;
  indexName: string;
  superId?: number;
  beizhu?: string;
  createTime?: string;
}

export interface ConfigItem {
  id: number;
  name: string;
  value: string;
}

export interface DashboardCard {
  label: string;
  value: number;
  hint: string;
}
