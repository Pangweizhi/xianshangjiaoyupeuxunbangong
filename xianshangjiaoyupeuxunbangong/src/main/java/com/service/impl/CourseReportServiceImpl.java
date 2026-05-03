package com.service.impl;

import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.entity.CourseCreditRecordEntity;
import com.entity.CourseEnrollEntity;
import com.entity.ExamEntity;
import com.entity.ExamRecordEntity;
import com.entity.JiaoshiEntity;
import com.entity.KechengEntity;
import com.entity.ZuoyeEntity;
import com.entity.ZuoyeSubmitEntity;
import com.service.CourseCreditRecordService;
import com.service.CourseEnrollService;
import com.service.CourseReportService;
import com.service.ExamRecordService;
import com.service.ExamService;
import com.service.JiaoshiService;
import com.service.KechengService;
import com.service.ZuoyeService;
import com.service.ZuoyeSubmitService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Service("courseReportService")
@Transactional(readOnly = true)
public class CourseReportServiceImpl implements CourseReportService {

    @Autowired
    private KechengService kechengService;
    @Autowired
    private JiaoshiService jiaoshiService;
    @Autowired
    private CourseEnrollService courseEnrollService;
    @Autowired
    private CourseCreditRecordService courseCreditRecordService;
    @Autowired
    private ZuoyeService zuoyeService;
    @Autowired
    private ZuoyeSubmitService zuoyeSubmitService;
    @Autowired
    private ExamService examService;
    @Autowired
    private ExamRecordService examRecordService;

    @Override
    public Map<String, Object> buildOverview(String role, Integer userId) {
        List<KechengEntity> courses = loadScopedCourses(role, userId);
        Map<Integer, String> teacherNameMap = loadTeacherNameMap(courses);

        Map<String, Object> result = new LinkedHashMap<String, Object>();
        if (courses.isEmpty()) {
            result.put("summary", buildEmptyOverviewSummary());
            result.put("courseStats", Collections.emptyList());
            return result;
        }

        List<Integer> courseIds = new ArrayList<Integer>();
        for (KechengEntity course : courses) {
            courseIds.add(course.getId());
        }

        List<CourseEnrollEntity> enrolls = courseEnrollService.selectList(new EntityWrapper<CourseEnrollEntity>()
            .in("kecheng_id", courseIds)
            .eq("is_deleted", 1));
        List<CourseCreditRecordEntity> creditRecords = courseCreditRecordService.selectList(new EntityWrapper<CourseCreditRecordEntity>()
            .in("kecheng_id", courseIds));
        List<ZuoyeEntity> homeworks = zuoyeService.selectList(new EntityWrapper<ZuoyeEntity>()
            .in("kecheng_id", courseIds)
            .eq("zuoye_delete", 1)
            .eq("publish_status", "published"));
        List<ExamEntity> exams = examService.selectList(new EntityWrapper<ExamEntity>()
            .in("kecheng_id", courseIds)
            .eq("is_deleted", 1)
            .eq("exam_status", "published"));

        Map<Integer, Integer> homeworkCourseMap = new HashMap<Integer, Integer>();
        List<Integer> homeworkIds = new ArrayList<Integer>();
        for (ZuoyeEntity homework : homeworks) {
            homeworkIds.add(homework.getId());
            homeworkCourseMap.put(homework.getId(), homework.getKechengId());
        }

        Map<Integer, Integer> examCourseMap = new HashMap<Integer, Integer>();
        List<Integer> examIds = new ArrayList<Integer>();
        for (ExamEntity exam : exams) {
            examIds.add(exam.getId());
            examCourseMap.put(exam.getId(), exam.getKechengId());
        }

        List<ZuoyeSubmitEntity> submissions = homeworkIds.isEmpty()
            ? Collections.<ZuoyeSubmitEntity>emptyList()
            : zuoyeSubmitService.selectList(new EntityWrapper<ZuoyeSubmitEntity>()
                .in("zuoye_id", homeworkIds)
                .eq("submit_delete", 1));

        List<ExamRecordEntity> examRecords = examIds.isEmpty()
            ? Collections.<ExamRecordEntity>emptyList()
            : examRecordService.selectList(new EntityWrapper<ExamRecordEntity>()
                .in("exam_id", examIds)
                .notIn("record_status", Arrays.asList("reset", "voided")));

        Map<Integer, CourseStatsAccumulator> courseStatsMap = new LinkedHashMap<Integer, CourseStatsAccumulator>();
        for (KechengEntity course : courses) {
            courseStatsMap.put(course.getId(), new CourseStatsAccumulator(course));
        }

        for (CourseEnrollEntity enroll : enrolls) {
            CourseStatsAccumulator accumulator = courseStatsMap.get(enroll.getKechengId());
            if (accumulator == null) {
                continue;
            }
            accumulator.enrollCount++;
            accumulator.progressSum += safeDouble(enroll.getProgressPercent());
            if ("已结课".equals(enroll.getEnrollStatus())) {
                accumulator.finishedCount++;
            }
        }

        for (CourseCreditRecordEntity record : creditRecords) {
            CourseStatsAccumulator accumulator = courseStatsMap.get(record.getKechengId());
            if (accumulator == null) {
                continue;
            }
            if ("已发放".equals(record.getGrantStatus())) {
                accumulator.creditGrantedCount++;
                accumulator.creditGrantedScore += safeInt(record.getCreditScore());
            }
        }

        for (ZuoyeEntity homework : homeworks) {
            CourseStatsAccumulator accumulator = courseStatsMap.get(homework.getKechengId());
            if (accumulator != null) {
                accumulator.homeworkCount++;
            }
        }

        for (ZuoyeSubmitEntity submission : submissions) {
            Integer courseId = homeworkCourseMap.get(submission.getZuoyeId());
            CourseStatsAccumulator accumulator = courseStatsMap.get(courseId);
            if (accumulator == null || submission.getSubmitScore() == null) {
                continue;
            }
            accumulator.reviewedHomeworkCount++;
            accumulator.homeworkScoreSum += submission.getSubmitScore();
            if (submission.getSubmitScore() >= 60D) {
                accumulator.passedHomeworkCount++;
            }
        }

        for (ExamEntity exam : exams) {
            CourseStatsAccumulator accumulator = courseStatsMap.get(exam.getKechengId());
            if (accumulator != null) {
                accumulator.examCount++;
            }
        }

        for (ExamRecordEntity record : examRecords) {
            Integer courseId = examCourseMap.get(record.getExamId());
            CourseStatsAccumulator accumulator = courseStatsMap.get(courseId);
            if (accumulator == null) {
                continue;
            }
            if (record.getFinalScore() != null) {
                accumulator.checkedExamCount++;
                accumulator.examScoreSum += record.getFinalScore();
            }
            if ("passed".equals(record.getPassStatus())) {
                accumulator.passedExamCount++;
            }
        }

        Map<String, Object> summary = new LinkedHashMap<String, Object>();
        summary.put("courseCount", courses.size());
        summary.put("enrollCount", sumCourseStats(courseStatsMap.values(), "enrollCount"));
        summary.put("finishedCount", sumCourseStats(courseStatsMap.values(), "finishedCount"));
        summary.put("creditGrantedCount", sumCourseStats(courseStatsMap.values(), "creditGrantedCount"));
        summary.put("creditGrantedScore", sumCourseStats(courseStatsMap.values(), "creditGrantedScore"));
        summary.put("homeworkCount", sumCourseStats(courseStatsMap.values(), "homeworkCount"));
        summary.put("reviewedHomeworkCount", sumCourseStats(courseStatsMap.values(), "reviewedHomeworkCount"));
        summary.put("passedHomeworkCount", sumCourseStats(courseStatsMap.values(), "passedHomeworkCount"));
        summary.put("examCount", sumCourseStats(courseStatsMap.values(), "examCount"));
        summary.put("checkedExamCount", sumCourseStats(courseStatsMap.values(), "checkedExamCount"));
        summary.put("passedExamCount", sumCourseStats(courseStatsMap.values(), "passedExamCount"));
        summary.put("averageHomeworkScore", average(
            sumCourseStatsDouble(courseStatsMap.values(), "homeworkScoreSum"),
            sumCourseStats(courseStatsMap.values(), "reviewedHomeworkCount")
        ));
        summary.put("averageExamScore", average(
            sumCourseStatsDouble(courseStatsMap.values(), "examScoreSum"),
            sumCourseStats(courseStatsMap.values(), "checkedExamCount")
        ));
        summary.put("averageProgressPercent", average(
            sumCourseStatsDouble(courseStatsMap.values(), "progressSum"),
            sumCourseStats(courseStatsMap.values(), "enrollCount")
        ));

        List<Map<String, Object>> courseStats = new ArrayList<Map<String, Object>>();
        for (CourseStatsAccumulator accumulator : courseStatsMap.values()) {
            courseStats.add(accumulator.toMap(teacherNameMap.get(accumulator.course.getJiaoshiId())));
        }

        result.put("summary", summary);
        result.put("courseStats", courseStats);
        return result;
    }

    @Override
    public Map<String, Object> buildStudentSummary(Integer yonghuId) {
        Map<String, Object> result = new LinkedHashMap<String, Object>();
        if (yonghuId == null) {
            result.put("summary", buildEmptyStudentSummary());
            result.put("courseSummaries", Collections.emptyList());
            return result;
        }

        List<CourseEnrollEntity> enrolls = courseEnrollService.selectList(new EntityWrapper<CourseEnrollEntity>()
            .eq("yonghu_id", yonghuId)
            .eq("is_deleted", 1)
            .orderBy("id", false));
        if (enrolls.isEmpty()) {
            result.put("summary", buildEmptyStudentSummary());
            result.put("courseSummaries", Collections.emptyList());
            return result;
        }

        List<Integer> courseIds = new ArrayList<Integer>();
        for (CourseEnrollEntity enroll : enrolls) {
            courseIds.add(enroll.getKechengId());
        }

        List<KechengEntity> courses = kechengService.selectBatchIds(courseIds);
        Map<Integer, KechengEntity> courseMap = new HashMap<Integer, KechengEntity>();
        for (KechengEntity course : courses) {
            courseMap.put(course.getId(), course);
        }
        Map<Integer, String> teacherNameMap = loadTeacherNameMap(courses);

        List<CourseCreditRecordEntity> creditRecords = courseCreditRecordService.selectList(new EntityWrapper<CourseCreditRecordEntity>()
            .eq("yonghu_id", yonghuId)
            .in("kecheng_id", courseIds));
        Map<Integer, CourseCreditRecordEntity> creditMap = new HashMap<Integer, CourseCreditRecordEntity>();
        for (CourseCreditRecordEntity record : creditRecords) {
            creditMap.put(record.getKechengId(), record);
        }

        List<ZuoyeEntity> homeworks = zuoyeService.selectList(new EntityWrapper<ZuoyeEntity>()
            .in("kecheng_id", courseIds)
            .eq("zuoye_delete", 1)
            .eq("publish_status", "published"));
        Map<Integer, List<ZuoyeEntity>> homeworksByCourse = new HashMap<Integer, List<ZuoyeEntity>>();
        List<Integer> homeworkIds = new ArrayList<Integer>();
        for (ZuoyeEntity homework : homeworks) {
            homeworkIds.add(homework.getId());
            append(homeworksByCourse, homework.getKechengId(), homework);
        }

        List<ZuoyeSubmitEntity> submissions = homeworkIds.isEmpty()
            ? Collections.<ZuoyeSubmitEntity>emptyList()
            : zuoyeSubmitService.selectList(new EntityWrapper<ZuoyeSubmitEntity>()
                .eq("yonghu_id", yonghuId)
                .eq("submit_delete", 1)
                .in("zuoye_id", homeworkIds));
        Map<Integer, ZuoyeSubmitEntity> bestSubmissionByHomework = new HashMap<Integer, ZuoyeSubmitEntity>();
        for (ZuoyeSubmitEntity submission : submissions) {
            if (submission.getSubmitScore() == null) {
                continue;
            }
            ZuoyeSubmitEntity current = bestSubmissionByHomework.get(submission.getZuoyeId());
            if (current == null || safeDouble(submission.getSubmitScore()) > safeDouble(current.getSubmitScore())) {
                bestSubmissionByHomework.put(submission.getZuoyeId(), submission);
            }
        }

        List<ExamEntity> exams = examService.selectList(new EntityWrapper<ExamEntity>()
            .in("kecheng_id", courseIds)
            .eq("is_deleted", 1)
            .eq("exam_status", "published"));
        Map<Integer, List<ExamEntity>> examsByCourse = new HashMap<Integer, List<ExamEntity>>();
        List<Integer> examIds = new ArrayList<Integer>();
        for (ExamEntity exam : exams) {
            examIds.add(exam.getId());
            append(examsByCourse, exam.getKechengId(), exam);
        }

        List<ExamRecordEntity> examRecords = examIds.isEmpty()
            ? Collections.<ExamRecordEntity>emptyList()
            : examRecordService.selectList(new EntityWrapper<ExamRecordEntity>()
                .eq("yonghu_id", yonghuId)
                .in("exam_id", examIds)
                .notIn("record_status", Arrays.asList("reset", "voided")));
        Map<Integer, ExamRecordEntity> bestRecordByExam = new HashMap<Integer, ExamRecordEntity>();
        for (ExamRecordEntity record : examRecords) {
            if (record.getFinalScore() == null) {
                continue;
            }
            ExamRecordEntity current = bestRecordByExam.get(record.getExamId());
            if (current == null || safeDouble(record.getFinalScore()) > safeDouble(current.getFinalScore())) {
                bestRecordByExam.put(record.getExamId(), record);
            }
        }

        List<Map<String, Object>> courseSummaries = new ArrayList<Map<String, Object>>();
        int finishedCount = 0;
        int grantedCreditCount = 0;
        double creditScoreSum = 0D;
        double progressSum = 0D;
        int homeworkReviewedCount = 0;
        double homeworkScoreSum = 0D;
        int examCheckedCount = 0;
        double examScoreSum = 0D;

        for (CourseEnrollEntity enroll : enrolls) {
            Integer courseId = enroll.getKechengId();
            KechengEntity course = courseMap.get(courseId);
            CourseCreditRecordEntity creditRecord = creditMap.get(courseId);
            List<ZuoyeEntity> courseHomeworks = homeworksByCourse.get(courseId);
            List<ExamEntity> courseExams = examsByCourse.get(courseId);

            int homeworkTotal = courseHomeworks == null ? 0 : courseHomeworks.size();
            int reviewedHomeworkCountPerCourse = 0;
            int passedHomeworkCount = 0;
            double homeworkScoreSumPerCourse = 0D;
            if (courseHomeworks != null) {
                for (ZuoyeEntity homework : courseHomeworks) {
                    ZuoyeSubmitEntity bestSubmission = bestSubmissionByHomework.get(homework.getId());
                    if (bestSubmission == null || bestSubmission.getSubmitScore() == null) {
                        continue;
                    }
                    reviewedHomeworkCountPerCourse++;
                    homeworkReviewedCount++;
                    homeworkScoreSumPerCourse += bestSubmission.getSubmitScore();
                    homeworkScoreSum += bestSubmission.getSubmitScore();
                    if (bestSubmission.getSubmitScore() >= 60D) {
                        passedHomeworkCount++;
                    }
                }
            }

            int examTotal = courseExams == null ? 0 : courseExams.size();
            int checkedExamCountPerCourse = 0;
            int passedExamCount = 0;
            double examScoreSumPerCourse = 0D;
            double bestExamScore = 0D;
            if (courseExams != null) {
                for (ExamEntity exam : courseExams) {
                    ExamRecordEntity bestRecord = bestRecordByExam.get(exam.getId());
                    if (bestRecord == null || bestRecord.getFinalScore() == null) {
                        continue;
                    }
                    checkedExamCountPerCourse++;
                    examCheckedCount++;
                    examScoreSumPerCourse += bestRecord.getFinalScore();
                    examScoreSum += bestRecord.getFinalScore();
                    bestExamScore = Math.max(bestExamScore, bestRecord.getFinalScore());
                    if ("passed".equals(bestRecord.getPassStatus())) {
                        passedExamCount++;
                    }
                }
            }

            if ("已结课".equals(enroll.getEnrollStatus())) {
                finishedCount++;
            }
            progressSum += safeDouble(enroll.getProgressPercent());
            if (creditRecord != null && "已发放".equals(creditRecord.getGrantStatus())) {
                grantedCreditCount++;
                creditScoreSum += safeDouble(creditRecord.getCreditScore());
            }

            Map<String, Object> item = new LinkedHashMap<String, Object>();
            item.put("courseId", courseId);
            item.put("courseName", course == null ? "" : course.getKechengName());
            item.put("teacherName", course == null ? "" : teacherNameMap.get(course.getJiaoshiId()));
            item.put("creditScore", course == null ? 0 : safeInt(course.getCreditScore()));
            item.put("progressPercent", safeDouble(enroll.getProgressPercent()));
            item.put("enrollStatus", enroll.getEnrollStatus());
            item.put("finishTime", enroll.getFinishTime());
            item.put("homeworkTotal", homeworkTotal);
            item.put("reviewedHomeworkCount", reviewedHomeworkCountPerCourse);
            item.put("passedHomeworkCount", passedHomeworkCount);
            item.put("averageHomeworkScore", average(homeworkScoreSumPerCourse, reviewedHomeworkCountPerCourse));
            item.put("examTotal", examTotal);
            item.put("checkedExamCount", checkedExamCountPerCourse);
            item.put("passedExamCount", passedExamCount);
            item.put("averageExamScore", average(examScoreSumPerCourse, checkedExamCountPerCourse));
            item.put("bestExamScore", round(bestExamScore));
            item.put("grantStatus", creditRecord == null ? "未发放" : creditRecord.getGrantStatus());
            item.put("grantedCreditScore", creditRecord == null ? 0 : safeInt(creditRecord.getCreditScore()));
            item.put("grantTime", creditRecord == null ? null : creditRecord.getGrantTime());
            item.put("grantRemark", creditRecord == null ? null : creditRecord.getGrantRemark());
            courseSummaries.add(item);
        }

        Map<String, Object> summary = new LinkedHashMap<String, Object>();
        summary.put("courseCount", enrolls.size());
        summary.put("finishedCount", finishedCount);
        summary.put("grantedCreditCount", grantedCreditCount);
        summary.put("grantedCreditScore", round(creditScoreSum));
        summary.put("averageProgressPercent", average(progressSum, enrolls.size()));
        summary.put("reviewedHomeworkCount", homeworkReviewedCount);
        summary.put("averageHomeworkScore", average(homeworkScoreSum, homeworkReviewedCount));
        summary.put("checkedExamCount", examCheckedCount);
        summary.put("averageExamScore", average(examScoreSum, examCheckedCount));

        result.put("summary", summary);
        result.put("courseSummaries", courseSummaries);
        return result;
    }

    private List<KechengEntity> loadScopedCourses(String role, Integer userId) {
        EntityWrapper<KechengEntity> wrapper = new EntityWrapper<KechengEntity>();
        wrapper.eq("kecheng_delete", 1);
        if ("教师".equals(role) && userId != null) {
            wrapper.eq("jiaoshi_id", userId);
        }
        return kechengService.selectList(wrapper);
    }

    private Map<Integer, String> loadTeacherNameMap(List<KechengEntity> courses) {
        Set<Integer> teacherIds = new HashSet<Integer>();
        for (KechengEntity course : courses) {
            if (course.getJiaoshiId() != null) {
                teacherIds.add(course.getJiaoshiId());
            }
        }
        if (teacherIds.isEmpty()) {
            return Collections.emptyMap();
        }
        List<JiaoshiEntity> teachers = jiaoshiService.selectBatchIds(teacherIds);
        Map<Integer, String> teacherNameMap = new HashMap<Integer, String>();
        for (JiaoshiEntity teacher : teachers) {
            teacherNameMap.put(teacher.getId(), teacher.getJiaoshiName());
        }
        return teacherNameMap;
    }

    private Map<String, Object> buildEmptyOverviewSummary() {
        Map<String, Object> summary = new LinkedHashMap<String, Object>();
        summary.put("courseCount", 0);
        summary.put("enrollCount", 0);
        summary.put("finishedCount", 0);
        summary.put("creditGrantedCount", 0);
        summary.put("creditGrantedScore", 0);
        summary.put("homeworkCount", 0);
        summary.put("reviewedHomeworkCount", 0);
        summary.put("passedHomeworkCount", 0);
        summary.put("examCount", 0);
        summary.put("checkedExamCount", 0);
        summary.put("passedExamCount", 0);
        summary.put("averageHomeworkScore", 0D);
        summary.put("averageExamScore", 0D);
        summary.put("averageProgressPercent", 0D);
        return summary;
    }

    private Map<String, Object> buildEmptyStudentSummary() {
        Map<String, Object> summary = new LinkedHashMap<String, Object>();
        summary.put("courseCount", 0);
        summary.put("finishedCount", 0);
        summary.put("grantedCreditCount", 0);
        summary.put("grantedCreditScore", 0D);
        summary.put("averageProgressPercent", 0D);
        summary.put("reviewedHomeworkCount", 0);
        summary.put("averageHomeworkScore", 0D);
        summary.put("checkedExamCount", 0);
        summary.put("averageExamScore", 0D);
        return summary;
    }

    private int sumCourseStats(Collection<CourseStatsAccumulator> values, String field) {
        int sum = 0;
        for (CourseStatsAccumulator value : values) {
            if ("enrollCount".equals(field)) {
                sum += value.enrollCount;
            } else if ("finishedCount".equals(field)) {
                sum += value.finishedCount;
            } else if ("creditGrantedCount".equals(field)) {
                sum += value.creditGrantedCount;
            } else if ("creditGrantedScore".equals(field)) {
                sum += value.creditGrantedScore;
            } else if ("homeworkCount".equals(field)) {
                sum += value.homeworkCount;
            } else if ("reviewedHomeworkCount".equals(field)) {
                sum += value.reviewedHomeworkCount;
            } else if ("passedHomeworkCount".equals(field)) {
                sum += value.passedHomeworkCount;
            } else if ("examCount".equals(field)) {
                sum += value.examCount;
            } else if ("checkedExamCount".equals(field)) {
                sum += value.checkedExamCount;
            } else if ("passedExamCount".equals(field)) {
                sum += value.passedExamCount;
            }
        }
        return sum;
    }

    private double sumCourseStatsDouble(Collection<CourseStatsAccumulator> values, String field) {
        double sum = 0D;
        for (CourseStatsAccumulator value : values) {
            if ("progressSum".equals(field)) {
                sum += value.progressSum;
            } else if ("homeworkScoreSum".equals(field)) {
                sum += value.homeworkScoreSum;
            } else if ("examScoreSum".equals(field)) {
                sum += value.examScoreSum;
            }
        }
        return sum;
    }

    private double average(double total, int count) {
        if (count <= 0) {
            return 0D;
        }
        return round(total / count);
    }

    private double round(double value) {
        return Math.round(value * 10D) / 10D;
    }

    private int safeInt(Integer value) {
        return value == null ? 0 : value;
    }

    private double safeDouble(Number value) {
        return value == null ? 0D : value.doubleValue();
    }

    private <T> void append(Map<Integer, List<T>> container, Integer key, T value) {
        List<T> list = container.get(key);
        if (list == null) {
            list = new ArrayList<T>();
            container.put(key, list);
        }
        list.add(value);
    }

    private static class CourseStatsAccumulator {
        private final KechengEntity course;
        private int enrollCount;
        private int finishedCount;
        private double progressSum;
        private int creditGrantedCount;
        private int creditGrantedScore;
        private int homeworkCount;
        private int reviewedHomeworkCount;
        private int passedHomeworkCount;
        private double homeworkScoreSum;
        private int examCount;
        private int checkedExamCount;
        private int passedExamCount;
        private double examScoreSum;

        private CourseStatsAccumulator(KechengEntity course) {
            this.course = course;
        }

        private Map<String, Object> toMap(String teacherName) {
            Map<String, Object> item = new LinkedHashMap<String, Object>();
            item.put("courseId", course.getId());
            item.put("courseName", course.getKechengName());
            item.put("teacherName", teacherName);
            item.put("creditScore", course.getCreditScore() == null ? 0 : course.getCreditScore());
            item.put("enrollCount", enrollCount);
            item.put("finishedCount", finishedCount);
            item.put("averageProgressPercent", enrollCount <= 0 ? 0D : Math.round(progressSum * 10D / enrollCount) / 10D);
            item.put("creditGrantedCount", creditGrantedCount);
            item.put("creditGrantedScore", creditGrantedScore);
            item.put("homeworkCount", homeworkCount);
            item.put("reviewedHomeworkCount", reviewedHomeworkCount);
            item.put("passedHomeworkCount", passedHomeworkCount);
            item.put("averageHomeworkScore", reviewedHomeworkCount <= 0 ? 0D : Math.round(homeworkScoreSum * 10D / reviewedHomeworkCount) / 10D);
            item.put("examCount", examCount);
            item.put("checkedExamCount", checkedExamCount);
            item.put("passedExamCount", passedExamCount);
            item.put("averageExamScore", checkedExamCount <= 0 ? 0D : Math.round(examScoreSum * 10D / checkedExamCount) / 10D);
            return item;
        }
    }
}
