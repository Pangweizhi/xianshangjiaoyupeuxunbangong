package com.controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.entity.CourseEnrollEntity;
import com.entity.ExamEntity;
import com.entity.ExamQuestionEntity;
import com.entity.ExamRecordEntity;
import com.service.CourseEnrollService;
import com.service.CourseSettlementService;
import com.service.ExamQuestionService;
import com.service.ExamRecordService;
import com.service.ExamService;
import com.utils.CommonUtil;
import com.utils.PageUtils;
import com.utils.R;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Map;

@RestController
@Controller
@RequestMapping("/examRecord")
public class ExamRecordController {

    @Autowired
    private ExamRecordService examRecordService;
    @Autowired
    private ExamService examService;
    @Autowired
    private ExamQuestionService examQuestionService;
    @Autowired
    private CourseEnrollService courseEnrollService;
    @Autowired
    private CourseSettlementService courseSettlementService;

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("学生".equals(role)) {
            params.put("yonghuId", request.getSession().getAttribute("userId"));
        } else if ("教师".equals(role)) {
            params.put("jiaoshiId", request.getSession().getAttribute("userId"));
        }
        CommonUtil.checkMap(params);
        PageUtils page = examRecordService.queryPage(params);
        return R.ok().put("data", page);
    }

    @RequestMapping("/myPage")
    public R myPage(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        params.put("yonghuId", request.getSession().getAttribute("userId"));
        CommonUtil.checkMap(params);
        PageUtils page = examRecordService.queryPage(params);
        return R.ok().put("data", page);
    }

    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id) {
        ExamRecordEntity entity = examRecordService.selectById(id);
        return entity == null ? R.error(511, "查不到数据") : R.ok().put("data", entity);
    }

    @RequestMapping("/start")
    public R start(@RequestBody ExamRecordEntity entity, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if (!"学生".equals(role)) {
            return R.error(511, "仅学生可以开始考试");
        }
        Integer yonghuId = Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId")));
        ExamEntity exam = examService.selectById(entity.getExamId());
        if (exam == null || exam.getIsDeleted() == null || exam.getIsDeleted() != 1 || !"published".equals(exam.getExamStatus())) {
            return R.error(511, "考试不存在或未发布");
        }
        Date now = new Date();
        if (exam.getStartTime() != null && now.before(exam.getStartTime())) {
            return R.error(511, "考试尚未开始");
        }
        if (exam.getEndTime() != null && now.after(exam.getEndTime())) {
            return R.error(511, "考试已结束");
        }
        CourseEnrollEntity enroll = courseEnrollService.selectOne(new EntityWrapper<CourseEnrollEntity>()
            .eq("kecheng_id", exam.getKechengId())
            .eq("yonghu_id", yonghuId)
            .eq("is_deleted", 1));
        if (enroll == null) {
            return R.error(511, "请先选课后再参加考试");
        }

        int finishedAttemptCount = examRecordService.selectCount(new EntityWrapper<ExamRecordEntity>()
            .eq("exam_id", exam.getId())
            .eq("yonghu_id", yonghuId)
            .notIn("record_status", Arrays.asList("started", "reset", "voided")));
        ExamRecordEntity pending = examRecordService.selectOne(new EntityWrapper<ExamRecordEntity>()
            .eq("exam_id", exam.getId())
            .eq("yonghu_id", yonghuId)
            .eq("record_status", "started")
            .orderBy("id", false));
        if (pending != null) {
            if (exam.getAllowResume() != null && exam.getAllowResume() == 0) {
                return R.error(511, "当前考试不允许退出后恢复作答");
            }
            return R.ok().put("data", pending);
        }

        if ((exam.getAllowRetake() == null || exam.getAllowRetake() == 0) && finishedAttemptCount > 0) {
            return R.error(511, "当前考试不允许重复参加");
        }
        int maxAttemptCount = exam.getMaxAttemptCount() == null || exam.getMaxAttemptCount() <= 0 ? 1 : exam.getMaxAttemptCount();
        if (finishedAttemptCount >= maxAttemptCount) {
            return R.error(511, "已达到本场考试最大作答次数");
        }

        int attemptNo = examRecordService.selectCount(new EntityWrapper<ExamRecordEntity>()
            .eq("exam_id", exam.getId())
            .eq("yonghu_id", yonghuId)) + 1;
        entity.setKechengId(exam.getKechengId());
        entity.setYonghuId(yonghuId);
        entity.setRecordStatus("started");
        entity.setPassStatus("pending");
        entity.setAttemptNo(attemptNo);
        entity.setStartTime(now);
        entity.setCreateTime(now);
        examRecordService.insert(entity);
        return R.ok().put("data", entity);
    }

    @RequestMapping("/submit")
    public R submit(@RequestBody ExamRecordEntity payload, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if (!"学生".equals(role)) {
            return R.error(511, "仅学生可以提交考试");
        }
        Integer yonghuId = Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId")));
        ExamRecordEntity record = examRecordService.selectById(payload.getId());
        if (record == null || !yonghuId.equals(record.getYonghuId())) {
            return R.error(511, "考试记录不存在");
        }
        ExamEntity exam = examService.selectById(record.getExamId());
        if (exam == null) {
            return R.error(511, "考试不存在");
        }
        Date now = new Date();
        if (exam.getEndTime() != null && now.after(exam.getEndTime())) {
            return R.error(511, "考试已结束");
        }

        List<ExamQuestionEntity> questions = examQuestionService.selectList(new EntityWrapper<ExamQuestionEntity>()
            .eq("exam_id", exam.getId())
            .eq("is_deleted", 1)
            .orderBy("sort_no", true)
            .orderBy("id", true));
        JSONObject answerJson = toJson(payload.getAnswerSnapshot());
        JSONArray questionSnapshot = new JSONArray();
        double autoScore = 0D;
        boolean requiresManualCheck = false;
        for (ExamQuestionEntity question : questions) {
            String answer = answerJson.getString(String.valueOf(question.getId()));
            JSONObject item = new JSONObject();
            item.put("id", question.getId());
            item.put("type", question.getQuestionType());
            item.put("title", question.getQuestionTitle());
            item.put("score", question.getQuestionScore());
            item.put("options", question.getOptionJson());
            item.put("correctAnswer", question.getCorrectAnswer());
            item.put("analysisText", question.getAnalysisText());
            item.put("answer", answer);
            boolean subjective = isSubjective(question.getQuestionType());
            item.put("isSubjective", subjective);
            boolean correct = !subjective && isAnswerCorrect(question, answer);
            item.put("autoCorrect", correct);
            questionSnapshot.add(item);
            if (subjective) {
                requiresManualCheck = true;
                continue;
            }
            if (correct) {
                autoScore += question.getQuestionScore() == null ? 0D : question.getQuestionScore();
            }
        }

        record.setAnswerSnapshot(answerJson.toJSONString());
        record.setQuestionSnapshot(questionSnapshot.toJSONString());
        record.setAutoScore(autoScore);
        record.setManualScore(requiresManualCheck ? null : 0D);
        record.setFinalScore(autoScore);
        record.setSubmitTime(now);
        record.setRecordStatus(requiresManualCheck ? "pending_check" : "checked");
        record.setCheckTime(requiresManualCheck ? null : now);
        double passLine = exam.getPassScore() == null ? 60D : exam.getPassScore();
        record.setPassStatus(record.getFinalScore() != null && record.getFinalScore() >= passLine ? "passed" : "failed");
        examRecordService.updateById(record);
        if (!requiresManualCheck) {
            courseSettlementService.refreshCourseCompletion(record.getKechengId(), yonghuId);
        }
        return R.ok().put("data", record);
    }

    @RequestMapping("/check")
    public R check(@RequestBody ExamRecordEntity payload) {
        ExamRecordEntity record = examRecordService.selectById(payload.getId());
        if (record == null) {
            return R.error(511, "查不到数据");
        }
        ExamEntity exam = examService.selectById(record.getExamId());
        if (exam == null) {
            return R.error(511, "考试不存在");
        }
        record.setManualScore(payload.getManualScore() == null ? 0D : payload.getManualScore());
        double finalScore = (record.getAutoScore() == null ? 0D : record.getAutoScore()) + (record.getManualScore() == null ? 0D : record.getManualScore());
        record.setFinalScore(finalScore);
        record.setRecordStatus("checked");
        record.setCheckRemark(payload.getCheckRemark());
        record.setCheckTime(new Date());
        double passLine = exam.getPassScore() == null ? 60D : exam.getPassScore();
        record.setPassStatus(finalScore >= passLine ? "passed" : "failed");
        examRecordService.updateById(record);
        courseSettlementService.refreshCourseCompletion(record.getKechengId(), record.getYonghuId());
        return R.ok();
    }

    @RequestMapping("/reset")
    public R reset(@RequestBody ExamRecordEntity payload) {
        ExamRecordEntity record = examRecordService.selectById(payload.getId());
        if (record == null) {
            return R.error(511, "查不到数据");
        }
        if (!"started".equals(record.getRecordStatus())) {
            return R.error(511, "仅未提交的作答记录可以重置");
        }
        record.setRecordStatus("reset");
        record.setPassStatus("reset");
        record.setCheckRemark(buildActionRemark(record.getCheckRemark(), payload.getCheckRemark(), "教师重置作答记录"));
        record.setCheckTime(new Date());
        examRecordService.updateById(record);
        return R.ok();
    }

    @RequestMapping("/voidRecord")
    public R voidRecord(@RequestBody ExamRecordEntity payload) {
        ExamRecordEntity record = examRecordService.selectById(payload.getId());
        if (record == null) {
            return R.error(511, "查不到数据");
        }
        if ("voided".equals(record.getRecordStatus())) {
            return R.error(511, "该记录已作废");
        }
        record.setRecordStatus("voided");
        record.setPassStatus("voided");
        record.setCheckRemark(buildActionRemark(record.getCheckRemark(), payload.getCheckRemark(), "教师作废考试记录"));
        record.setCheckTime(new Date());
        examRecordService.updateById(record);
        return R.ok();
    }

    private JSONObject toJson(String answerSnapshot) {
        if (answerSnapshot == null || "".equals(answerSnapshot.trim())) {
            return new JSONObject();
        }
        return JSON.parseObject(answerSnapshot);
    }

    private boolean isAnswerCorrect(ExamQuestionEntity question, String answer) {
        if (answer == null) {
            return false;
        }
        String correct = question.getCorrectAnswer();
        if (correct == null) {
            return false;
        }
        if (isMultiChoice(question.getQuestionType())) {
            return normalizeMulti(answer).equals(normalizeMulti(correct));
        }
        return normalizeText(answer).equals(normalizeText(correct));
    }

    private boolean isSubjective(String questionType) {
        return "简答题".equals(questionType) || "简答".equals(questionType) || "问答".equals(questionType);
    }

    private boolean isMultiChoice(String questionType) {
        return "多选".equals(questionType) || "多选题".equals(questionType);
    }

    private String normalizeMulti(String value) {
        String[] parts = value.replace(" ", "").split(",");
        Arrays.sort(parts);
        return String.join(",", parts);
    }

    private String normalizeText(String value) {
        return value == null ? "" : value.trim().replace(" ", "").replace("，", ",").toLowerCase();
    }

    private String buildActionRemark(String oldRemark, String inputRemark, String fallbackAction) {
        StringBuilder builder = new StringBuilder();
        if (oldRemark != null && !"".equals(oldRemark.trim())) {
            builder.append(oldRemark.trim()).append(" | ");
        }
        if (inputRemark != null && !"".equals(inputRemark.trim())) {
            builder.append(inputRemark.trim());
        } else {
            builder.append(fallbackAction);
        }
        return builder.toString();
    }
}
