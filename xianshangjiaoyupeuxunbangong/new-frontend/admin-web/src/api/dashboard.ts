import type {
  ConfigItem,
  CourseItem,
  CourseChapterItem,
  CourseEnrollItem,
  CourseResourceItem,
  CreditRecordItem,
  DictionaryItem,
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
  StudentItem,
  TeacherItem
} from "@shared/index";
import { unwrap } from "@shared/index";
import { useAdminHttp } from "./client";

export async function fetchAdminCourses(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/kecheng/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<CourseItem>>(data);
}

export async function fetchAdminNotices(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/news/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<NoticeItem>>(data);
}

export async function fetchAdminSummary() {
  const [courses, notices] = await Promise.all([
    fetchAdminCourses({ limit: 4 }),
    fetchAdminNotices({ limit: 6 })
  ]);
  return {
    courses,
    notices
  };
}

export async function fetchStudents(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/yonghu/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<StudentItem>>(data);
}

export async function fetchTeachers(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/jiaoshi/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<TeacherItem>>(data);
}

export async function fetchDictionary(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/dictionary/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<DictionaryItem>>(data);
}

export async function fetchConfig(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/config/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<ConfigItem>>(data);
}

export async function fetchHomeworks(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/zuoye/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<HomeworkItem>>(data);
}

export async function fetchForums(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/forum/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<ForumItem>>(data);
}

export async function fetchMaterials(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/jiaoxueshipin/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<LessonMaterialItem>>(data);
}

export async function fetchMeetings(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/kaihuitongzhi/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<MeetingItem>>(data);
}

export async function fetchHomeworkSubmissionPage(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/zuoyeSubmit/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<HomeworkSubmissionItem>>(data);
}

export async function fetchCourseChapterPage(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/courseChapter/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<CourseChapterItem>>(data);
}

export async function fetchCourseResourcePage(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/courseResource/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<CourseResourceItem>>(data);
}

export async function fetchCourseEnrollPage(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/courseEnroll/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<CourseEnrollItem>>(data);
}

export async function fetchStudyProgressPage(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/studyProgress/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<StudyProgressItem>>(data);
}

export async function fetchCreditRecordPage(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/courseCreditRecord/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<CreditRecordItem>>(data);
}

export async function fetchExamPage(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/exam/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<ExamItem>>(data);
}

export async function fetchExamQuestionPage(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/examQuestion/page", {
    params: { page: 1, limit: 10, sort: "sort_no", order: "asc", ...params }
  });
  return unwrap<PagePayload<ExamQuestionItem>>(data);
}

export async function fetchExamRecordPage(params?: Record<string, unknown>) {
  const http = useAdminHttp();
  const { data } = await http.get("/examRecord/page", {
    params: { page: 1, limit: 10, sort: "id", order: "desc", ...params }
  });
  return unwrap<PagePayload<ExamRecordItem>>(data);
}
