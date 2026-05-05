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
  kechengEndTime?: string;
  banjiValue?: string;
  jiaoshiName?: string;
  kechengContent?: string;
  courseStatus?: string;
  creditScore?: number;
  reviewRemark?: string;
}

export interface CourseChapterItem {
  id: number;
  kechengId: number;
  chapterName: string;
  chapterSort?: number;
  chapterSummary?: string;
  chapterStatus?: string;
  reviewRemark?: string;
  kechengName?: string;
  jiaoshiName?: string;
}

export interface CourseResourceItem {
  id: number;
  kechengId: number;
  chapterId: number;
  resourceName: string;
  resourceType?: string;
  resourceUrl?: string;
  coverUrl?: string;
  durationSeconds?: number;
  resourceStatus?: string;
  reviewRemark?: string;
  kechengName?: string;
  chapterName?: string;
  jiaoshiName?: string;
}

export interface CourseEnrollItem {
  id: number;
  kechengId: number;
  yonghuId: number;
  enrollStatus?: string;
  progressPercent?: number;
  enrollTime?: string;
  finishTime?: string;
  kechengName?: string;
  kechengPhoto?: string;
  jiaoshiName?: string;
  courseStatus?: string;
  creditScore?: number;
}

export interface CreditRecordItem {
  id: number;
  kechengId: number;
  yonghuId: number;
  creditScore?: number;
  grantStatus?: string;
  grantTime?: string;
  grantRemark?: string;
  kechengName?: string;
}

export interface ExamItem {
  id: number;
  kechengId: number;
  chapterId?: number;
  jiaoshiId?: number;
  examName: string;
  examSummary?: string;
  durationMinutes?: number;
  totalScore?: number;
  passScore?: number;
  startTime?: string;
  endTime?: string;
  examStatus?: string;
  allowRetake?: number;
  maxAttemptCount?: number;
  allowResume?: number;
  publishTime?: string;
  kechengName?: string;
  chapterName?: string;
  jiaoshiName?: string;
}

export interface ExamQuestionItem {
  id: number;
  kechengId?: number;
  examId: number;
  questionType?: string;
  questionTitle: string;
  optionJson?: string;
  correctAnswer?: string;
  questionScore?: number;
  sortNo?: number;
  analysisText?: string;
  examName?: string;
  kechengName?: string;
}

export interface ExamRecordItem {
  id: number;
  examId: number;
  kechengId?: number;
  yonghuId?: number;
  answerSnapshot?: string;
  questionSnapshot?: string;
  autoScore?: number;
  manualScore?: number;
  finalScore?: number;
  passStatus?: string;
  recordStatus?: string;
  startTime?: string;
  submitTime?: string;
  checkTime?: string;
  checkRemark?: string;
  attemptNo?: number;
  examName?: string;
  kechengName?: string;
  yonghuName?: string;
  jiaoshiName?: string;
}

export interface StudyProgressItem {
  id: number;
  kechengId: number;
  chapterId: number;
  resourceId: number;
  yonghuId: number;
  studySeconds?: number;
  progressPercent?: number;
  isCompleted?: number;
  lastStudyTime?: string;
  kechengName?: string;
  chapterName?: string;
  resourceName?: string;
  resourceType?: string;
  yonghuName?: string;
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
  jiaoshiId?: number;
  kechengId?: number;
  chapterId?: number;
  deadlineTime?: string;
  scoreTotal?: number;
  publishStatus?: string;
  jiaoshiName?: string;
  kechengName?: string;
  chapterName?: string;
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
  superIds?: number;
  insertTime?: string;
  updateTime?: string;
}

export interface StudentItem {
  id: number;
  username: string;
  yonghuName: string;
  password?: string;
  sexTypes?: number;
  sexValue?: string;
  yonghuPhoto?: string;
  yonghuIdNumber?: string;
  yonghuPhone?: string;
  yonghuEmail?: string;
  banjiTypes?: number;
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

export interface AdminUserItem {
  id: number;
  username: string;
  password?: string;
  role?: string;
  addtime?: string;
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

export interface CourseReportSummary {
  courseCount: number;
  enrollCount?: number;
  finishedCount: number;
  creditGrantedCount?: number;
  creditGrantedScore?: number;
  homeworkCount?: number;
  reviewedHomeworkCount: number;
  passedHomeworkCount?: number;
  examCount?: number;
  checkedExamCount: number;
  passedExamCount?: number;
  averageHomeworkScore: number;
  averageExamScore: number;
  averageProgressPercent: number;
  grantedCreditCount?: number;
  grantedCreditScore?: number;
}

export interface CourseReportCourseItem {
  courseId: number;
  courseName: string;
  teacherName?: string;
  creditScore?: number;
  enrollCount?: number;
  finishedCount?: number;
  averageProgressPercent?: number;
  creditGrantedCount?: number;
  creditGrantedScore?: number;
  homeworkCount?: number;
  reviewedHomeworkCount?: number;
  passedHomeworkCount?: number;
  averageHomeworkScore?: number;
  examCount?: number;
  checkedExamCount?: number;
  passedExamCount?: number;
  averageExamScore?: number;
}

export interface StudentCoursePerformanceItem {
  courseId: number;
  courseName: string;
  teacherName?: string;
  creditScore?: number;
  progressPercent?: number;
  enrollStatus?: string;
  finishTime?: string;
  homeworkTotal?: number;
  reviewedHomeworkCount?: number;
  passedHomeworkCount?: number;
  averageHomeworkScore?: number;
  examTotal?: number;
  checkedExamCount?: number;
  passedExamCount?: number;
  averageExamScore?: number;
  bestExamScore?: number;
  grantStatus?: string;
  grantedCreditScore?: number;
  grantTime?: string;
  grantRemark?: string;
}

export interface CourseReportOverview {
  summary: CourseReportSummary;
  courseStats: CourseReportCourseItem[];
}

export interface StudentCoursePerformanceResponse {
  summary: CourseReportSummary;
  courseSummaries: StudentCoursePerformanceItem[];
}

export interface AiChatSessionItem {
  id: number;
  userId: number;
  userTable: UserTable;
  roleType?: string;
  sessionTitle: string;
  bizScene?: string;
  courseId?: number;
  chapterId?: number;
  resourceId?: number;
  messageCount?: number;
  lastMessageAt?: string;
  status?: string;
  createTime?: string;
  updateTime?: string;
}

export interface AiChatMessageItem {
  id: number;
  sessionId: number;
  userId: number;
  roleType?: string;
  messageRole: "user" | "assistant" | "system" | "tool";
  messageType?: string;
  content: string;
  toolName?: string;
  toolRequestJson?: string;
  toolResponseJson?: string;
  contextJson?: string;
  tokenEstimate?: number;
  sortNo?: number;
  createTime?: string;
}

export interface AiChatSessionCreateResponse {
  session: AiChatSessionItem;
  recommendQuestions: string[];
}

export interface AiChatSendResponse {
  session: AiChatSessionItem;
  userMessage: AiChatMessageItem;
  assistantMessage: AiChatMessageItem;
  recommendQuestions: string[];
}
