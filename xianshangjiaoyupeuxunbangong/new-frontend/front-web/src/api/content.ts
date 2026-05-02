import type {
  CourseItem,
  CourseChapterItem,
  CourseEnrollItem,
  CourseResourceItem,
  CreditRecordItem,
  ApiResponse,
  ForumItem,
  HomeworkItem,
  HomeworkSubmissionItem,
  LessonMaterialItem,
  MeetingItem,
  NoticeItem,
  PagePayload
} from "@shared/index";
import { DEFAULT_BASE_URL, unwrap } from "@shared/index";
import { useHttp } from "./client";
import axios from "axios";

export async function fetchCoursePage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/kecheng/list", {
    params: { page: 1, limit: 8, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<CourseItem>>(data);
}

export async function fetchCourseDetail(id: number | string) {
  const http = useHttp();
  const { data } = await http.get(`/kecheng/detail/${id}`);
  return unwrap<CourseItem>(data);
}

export async function fetchCourseChapterPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/courseChapter/list", {
    params: { page: 1, limit: 50, sort: "chapterSort", order: "asc", ...params }
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

export async function fetchMyCreditPage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/courseCreditRecord/myPage", {
    params: { page: 1, limit: 20, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<CreditRecordItem>>(data);
}

export async function fetchNoticePage(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/news/list", {
    params: { page: 1, limit: 6, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<NoticeItem>>(data);
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
    params: { page: 1, limit: 8, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<MeetingItem>>(data);
}

export async function fetchHomeworkDetail(id: number | string) {
  const http = useHttp();
  const { data } = await http.get(`/zuoye/detail/${id}`);
  return unwrap<HomeworkItem>(data);
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

export async function fetchHomeworkSubmissions(params?: Record<string, unknown>) {
  const http = useHttp();
  const { data } = await http.get("/zuoyeSubmit/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<HomeworkSubmissionItem>>(data);
}
