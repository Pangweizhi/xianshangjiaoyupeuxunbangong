import type {
  ConfigItem,
  CourseItem,
  CourseChapterItem,
  CourseEnrollItem,
  StudentCoursePerformanceResponse,
  CourseResourceItem,
  CreditRecordItem,
  ApiResponse,
  ExamItem,
  ExamQuestionItem,
  ExamRecordItem,
  ForumItem,
  HomeworkItem,
  HomeworkSubmissionItem,
  LessonMaterialItem,
  MeetingItem,
  NoticeItem,
  PagePayload,
  StudyProgressItem,
  StudentItem
} from "@shared/index";
import { DEFAULT_BASE_URL, unwrap } from "@shared/index";
import { useHttp } from "./client";
import axios from "axios";

export async function fetchCoursePage(params?: Record<string, unknown>) {
  const http = useHttp();
  const requestParams = { page: 1, limit: 8, sort: "id", order: "desc", ...params };
  const { data } = await http.get("/kecheng/list", { params: requestParams });
  const page = unwrap<PagePayload<CourseItem>>(data);
  if (Array.isArray(page.list) && page.list.length > 0) {
    return page;
  }
  try {
    const fallback = await http.get("/kecheng/page", { params: requestParams });
    return unwrap<PagePayload<CourseItem>>(fallback.data);
  } catch {
    return page;
  }
}

export async function fetchCourseDetail(id: number | string) {
  const http = useHttp();
  const { data } = await http.get(`/kecheng/detail/${id}`);
  return unwrap<CourseItem>(data);
}

export async function fetchCourseChapterPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/courseChapter/list", {
    params: { page: 1, limit: 50, sort: "chapter_sort", order: "asc", ...params }
  });
  return unwrap<PagePayload<CourseChapterItem>>(data);
}

export async function fetchCourseResourcePage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/courseResource/list", {
    params: { page: 1, limit: 100, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<CourseResourceItem>>(data);
}

export async function fetchCourseResourceDetail(id: number | string) {
  const http = useHttp();
  const { data } = await http.get(`/courseResource/info/${id}`);
  return unwrap<CourseResourceItem>(data);
}

export async function createCourseEnroll(payload: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.post("/courseEnroll/save", payload);
  return data as ApiResponse<unknown>;
}

export async function fetchMyCoursePage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/courseEnroll/myCourses", {
    params: { page: 1, limit: 20, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<CourseEnrollItem>>(data);
}

export async function saveStudyProgress(payload: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.post("/studyProgress/saveOrUpdate", payload);
  return data as ApiResponse<unknown>;
}

export async function fetchStudyProgressPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/studyProgress/page", {
    params: { page: 1, limit: 100, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<StudyProgressItem>>(data);
}

export async function fetchMyCreditPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/courseCreditRecord/myPage", {
    params: { page: 1, limit: 20, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<CreditRecordItem>>(data);
}

export async function fetchExamPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/exam/list", {
    params: { page: 1, limit: 8, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<ExamItem>>(data);
}

export async function fetchExamDetail(id: number | string) {
  const http = useHttp();
  const { data } = await http.get(`/exam/detail/${id}`);
  return unwrap<ExamItem>(data);
}

export async function fetchExamQuestionPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/examQuestion/list", {
    params: { page: 1, limit: 100, sort: "sort_no", order: "asc", ...params }
  });
  return unwrap<PagePayload<ExamQuestionItem>>(data);
}

export async function startExam(payload: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.post("/examRecord/start", payload);
  return data as ApiResponse<ExamRecordItem>;
}

export async function submitExam(payload: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.post("/examRecord/submit", payload);
  return data as ApiResponse<ExamRecordItem>;
}

export async function fetchMyExamRecordPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/examRecord/myPage", {
    params: { page: 1, limit: 20, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<ExamRecordItem>>(data);
}

export async function fetchMyCoursePerformanceSummary() {
  const http = useHttp();
  const { data } = await http.get("/courseReport/mySummary");
  return unwrap<StudentCoursePerformanceResponse>(data);
}

export async function fetchNoticePage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/news/list", {
    params: { page: 1, limit: 6, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<NoticeItem>>(data);
}

export async function fetchConfigList(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/config/list", {
    params: { page: 1, limit: 50, sort: "id", order: "asc", ...params }
  });
  return unwrap<PagePayload<ConfigItem>>(data);
}

export async function fetchHomeworkPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/zuoye/list", {
    params: { page: 1, limit: 8, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<HomeworkItem>>(data);
}

export async function fetchForumPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/forum/list", {
    params: { page: 1, limit: 8, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<ForumItem>>(data);
}

export async function fetchMaterialPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/jiaoxueshipin/list", {
    params: { page: 1, limit: 8, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<LessonMaterialItem>>(data);
}

export async function fetchMeetingPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/kaihuitongzhi/list", {
    params: {
      page: 1,
      limit: 8,
      sort: "id",
      order: "desc",
      kaihuitongzhiDeleteStart: 1,
      kaihuitongzhiDeleteEnd: 1,
      ...params
    }
  });
  const page = unwrap<PagePayload<MeetingItem>>(data);
  return {
    totalCount: Number(page?.totalCount || 0),
    pageSize: Number(page?.pageSize || 0),
    totalPage: Number(page?.totalPage || 0),
    currPage: Number(page?.currPage || 1),
    list: Array.isArray(page?.list) ? page.list : []
  };
}

export async function fetchHomeworkDetail(id: number | string) {
  const http = useHttp();
  const { data } = await http.get(`/zuoye/detail/${id}`);
  return unwrap<HomeworkItem>(data);
}

export async function fetchHomeworkQuestions(id: number | string) {
  const http = useHttp();
  const { data } = await http.get(`/zuoye/questionList/${id}`);
  return unwrap<ExamQuestionItem[]>(data);
}

export async function fetchForumDetail(id: number | string) {
  const http = useHttp();
  const { data } = await http.get(`/forum/detail/${id}`);
  return unwrap<ForumItem>(data);
}

export async function fetchMaterialDetail(id: number | string) {
  const http = useHttp();
  const { data } = await http.get(`/jiaoxueshipin/detail/${id}`);
  return unwrap<LessonMaterialItem>(data);
}

export async function fetchMeetingDetail(id: number | string) {
  const http = useHttp();
  const { data } = await http.get(`/kaihuitongzhi/detail/${id}`);
  return unwrap<MeetingItem>(data);
}

export async function createForumPost(payload: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.post("/forum/save", payload);
  return data as ApiResponse<unknown>;
}

export async function uploadFile(
  file: File,
  token?: string | null
) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await axios.post(`${DEFAULT_BASE_URL}/file/upload`, formData, {
    headers: token ? { Token: token } : undefined,
    withCredentials: true
  });
  return data.file as string;
}

export async function createHomeworkSubmission(payload: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.post("/zuoyeSubmit/save", payload);
  return data as ApiResponse<unknown>;
}

export async function startHomework(payload: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.post("/zuoyeSubmit/start", payload);
  return data as ApiResponse<HomeworkSubmissionItem>;
}

export async function submitHomework(payload: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.post("/zuoyeSubmit/submit", payload);
  return data as ApiResponse<HomeworkSubmissionItem>;
}

export async function fetchHomeworkSubmissions(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/zuoyeSubmit/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<HomeworkSubmissionItem>>(data);
}

export async function fetchMyHomeworkSubmissions(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/zuoyeSubmit/myPage", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  const page = unwrap<PagePayload<HomeworkSubmissionItem>>(data);
  return {
    totalCount: Number(page?.totalCount || 0),
    pageSize: Number(page?.pageSize || 0),
    totalPage: Number(page?.totalPage || 0),
    currPage: Number(page?.currPage || 1),
    list: Array.isArray(page?.list) ? page.list : []
  };
}

export async function fetchStudentProfile() {
  const http = useHttp();
  const { data } = await http.get("/yonghu/session");
  return unwrap<StudentItem>(data);
}

export async function updateStudentProfile(payload: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.post("/yonghu/update", payload);
  return data as ApiResponse<unknown>;
}
