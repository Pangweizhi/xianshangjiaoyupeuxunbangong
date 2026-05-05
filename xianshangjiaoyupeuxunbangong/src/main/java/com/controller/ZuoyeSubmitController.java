package com.controller;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.annotation.IgnoreAuth;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.baomidou.mybatisplus.mapper.Wrapper;
import com.entity.CourseEnrollEntity;
import com.entity.ExamQuestionEntity;
import com.entity.ZuoyeEntity;
import com.entity.ZuoyeSubmitEntity;
import com.entity.view.ZuoyeSubmitView;
import com.service.CourseEnrollService;
import com.service.CourseSettlementService;
import com.service.ExamQuestionService;
import com.service.ZuoyeService;
import com.service.ZuoyeSubmitService;
import com.utils.CommonUtil;
import com.utils.PageUtils;
import com.utils.R;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Map;

@RestController
@Controller
@RequestMapping("/zuoyeSubmit")
public class ZuoyeSubmitController {
    private static final Logger logger = LoggerFactory.getLogger(ZuoyeSubmitController.class);

    private static final String STATUS_STARTED = "作答中";
    private static final String STATUS_PENDING = "待批改";
    private static final String STATUS_CHECKED = "已批改";
    private static final String STATUS_REDO = "需重交";

    @Autowired
    private ZuoyeSubmitService zuoyeSubmitService;
    @Autowired
    private ZuoyeService zuoyeService;
    @Autowired
    private ExamQuestionService examQuestionService;
    @Autowired
    private CourseEnrollService courseEnrollService;
    @Autowired
    private CourseSettlementService courseSettlementService;

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        logger.debug("page: {}", JSONObject.toJSONString(params));
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("学生".equals(role)) {
            params.put("yonghuId", request.getSession().getAttribute("userId"));
        } else if ("教师".equals(role)) {
            params.put("jiaoshiId", request.getSession().getAttribute("userId"));
        }
        params.put("submitDeleteStart", 1);
        params.put("submitDeleteEnd", 1);
        CommonUtil.checkMap(params);
        PageUtils page = zuoyeSubmitService.queryPage(params);
        return R.ok().put("data", page);
    }

    @RequestMapping("/myPage")
    public R myPage(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        params.put("yonghuId", request.getSession().getAttribute("userId"));
        params.put("submitDeleteStart", 1);
        params.put("submitDeleteEnd", 1);
        CommonUtil.checkMap(params);
        PageUtils page = zuoyeSubmitService.queryPage(params);
        return R.ok().put("data", page);
    }

    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id) {
        ZuoyeSubmitEntity entity = zuoyeSubmitService.selectById(id);
        if (entity == null) {
            return R.error(511, "查询不到数据");
        }
        ZuoyeSubmitView view = new ZuoyeSubmitView();
        BeanUtils.copyProperties(entity, view);
        return R.ok().put("data", view);
    }

    @RequestMapping("/start")
    public R start(@RequestBody ZuoyeSubmitEntity payload, HttpServletRequest request) {
        Integer yonghuId = resolveStudent(request);
        if (yonghuId == null) {
            return R.error(511, "仅学生可以开始作业");
        }
        ZuoyeEntity homework = zuoyeService.selectById(payload.getZuoyeId());
        if (homework == null || homework.getZuoyeDelete() == null || homework.getZuoyeDelete() != 1 || !"published".equals(homework.getPublishStatus())) {
            return R.error(511, "作业不存在或未发布");
        }
        if (homework.getDeadlineTime() != null && homework.getDeadlineTime().before(new Date())) {
            return R.error(511, "当前作业已截止");
        }
        if (homework.getKechengId() != null) {
            CourseEnrollEntity enroll = courseEnrollService.selectOne(new EntityWrapper<CourseEnrollEntity>()
                .eq("kecheng_id", homework.getKechengId())
                .eq("yonghu_id", yonghuId)
                .eq("is_deleted", 1));
            if (enroll == null) {
                return R.error(511, "请先选课后再完成作业");
            }
        }

        ZuoyeSubmitEntity started = zuoyeSubmitService.selectOne(new EntityWrapper<ZuoyeSubmitEntity>()
            .eq("zuoye_id", homework.getId())
            .eq("yonghu_id", yonghuId)
            .eq("submit_delete", 1)
            .eq("submit_status", STATUS_STARTED)
            .orderBy("id", false));
        if (started != null) {
            return R.ok().put("data", started);
        }

        ZuoyeSubmitEntity latest = zuoyeSubmitService.selectOne(new EntityWrapper<ZuoyeSubmitEntity>()
            .eq("zuoye_id", homework.getId())
            .eq("yonghu_id", yonghuId)
            .eq("submit_delete", 1)
            .orderBy("id", false));
        if (latest != null && !STATUS_REDO.equals(latest.getSubmitStatus())) {
            return R.error(511, "你已提交过本次作业，如需重做请联系教师退回");
        }

        ZuoyeSubmitEntity entity = new ZuoyeSubmitEntity();
        entity.setZuoyeId(homework.getId());
        entity.setYonghuId(yonghuId);
        entity.setSubmitStatus(STATUS_STARTED);
        entity.setSubmitScore(null);
        entity.setAutoScore(null);
        entity.setSubmitRemark(null);
        entity.setSubmitDelete(1);
        entity.setCheckTime(null);
        entity.setInsertTime(new Date());
        entity.setCreateTime(new Date());
        if (latest != null && latest.getAnswerSnapshot() != null) {
            entity.setAnswerSnapshot(latest.getAnswerSnapshot());
        }
        zuoyeSubmitService.insert(entity);
        return R.ok().put("data", entity);
    }

    @RequestMapping("/submit")
    public R submit(@RequestBody ZuoyeSubmitEntity payload, HttpServletRequest request) {
        Integer yonghuId = resolveStudent(request);
        if (yonghuId == null) {
            return R.error(511, "仅学生可以提交作业");
        }
        ZuoyeSubmitEntity record = zuoyeSubmitService.selectById(payload.getId());
        if (record == null || !yonghuId.equals(record.getYonghuId())) {
            return R.error(511, "作业记录不存在");
        }
        if (!STATUS_STARTED.equals(record.getSubmitStatus()) && !STATUS_REDO.equals(record.getSubmitStatus())) {
            return R.error(511, "当前作业记录不可提交");
        }

        ZuoyeEntity homework = zuoyeService.selectById(record.getZuoyeId());
        if (homework == null || homework.getZuoyeDelete() == null || homework.getZuoyeDelete() != 1) {
            return R.error(511, "作业不存在");
        }
        if (homework.getDeadlineTime() != null && homework.getDeadlineTime().before(new Date())) {
            return R.error(511, "当前作业已截止");
        }

        List<ExamQuestionEntity> questions = loadHomeworkQuestions(homework);
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
            boolean correct = !subjective && isAnswerCorrect(question, answer);
            item.put("isSubjective", subjective);
            item.put("autoCorrect", correct);
            questionSnapshot.add(item);
            if (subjective) {
                requiresManualCheck = true;
            } else if (correct) {
                autoScore += question.getQuestionScore() == null ? 0D : question.getQuestionScore();
            }
        }

        record.setSubmitContent(payload.getSubmitContent());
        record.setSubmitFile(payload.getSubmitFile());
        record.setAnswerSnapshot(answerJson.toJSONString());
        record.setQuestionSnapshot(questionSnapshot.toJSONString());
        record.setAutoScore(autoScore);
        record.setSubmitScore(autoScore);
        record.setSubmitStatus(requiresManualCheck ? STATUS_PENDING : STATUS_CHECKED);
        record.setCheckTime(requiresManualCheck ? null : new Date());
        record.setInsertTime(new Date());
        zuoyeSubmitService.updateById(record);
        if (!requiresManualCheck && homework.getKechengId() != null) {
            courseSettlementService.refreshCourseCompletion(homework.getKechengId(), yonghuId);
        }
        return R.ok().put("data", record);
    }

    @RequestMapping("/check")
    public R check(@RequestBody ZuoyeSubmitEntity payload) {
        ZuoyeSubmitEntity record = zuoyeSubmitService.selectById(payload.getId());
        if (record == null) {
            return R.error(511, "查询不到数据");
        }
        record.setSubmitStatus(STATUS_CHECKED);
        record.setSubmitScore(payload.getSubmitScore() == null ? (record.getAutoScore() == null ? 0D : record.getAutoScore()) : payload.getSubmitScore());
        record.setSubmitRemark(payload.getSubmitRemark());
        record.setCheckTime(new Date());
        zuoyeSubmitService.updateById(record);

        ZuoyeEntity homework = zuoyeService.selectById(record.getZuoyeId());
        if (homework != null && homework.getKechengId() != null) {
            courseSettlementService.refreshCourseCompletion(homework.getKechengId(), record.getYonghuId());
        }
        return R.ok();
    }

    @RequestMapping("/update")
    public R update(@RequestBody ZuoyeSubmitEntity zuoyeSubmit) {
        if ("".equals(zuoyeSubmit.getSubmitFile()) || "null".equals(zuoyeSubmit.getSubmitFile())) {
            zuoyeSubmit.setSubmitFile(null);
        }
        if (zuoyeSubmit.getSubmitStatus() == null || "".equals(zuoyeSubmit.getSubmitStatus().trim())) {
            zuoyeSubmit.setSubmitStatus(STATUS_PENDING);
        }
        if (STATUS_STARTED.equals(zuoyeSubmit.getSubmitStatus())) {
            zuoyeSubmit.setSubmitScore(null);
            zuoyeSubmit.setCheckTime(null);
        } else if (STATUS_PENDING.equals(zuoyeSubmit.getSubmitStatus())) {
            zuoyeSubmit.setCheckTime(null);
        } else {
            zuoyeSubmit.setCheckTime(new Date());
        }
        zuoyeSubmitService.updateById(zuoyeSubmit);
        if (zuoyeSubmit.getSubmitScore() != null) {
            ZuoyeEntity homework = zuoyeService.selectById(zuoyeSubmit.getZuoyeId());
            if (homework != null && homework.getKechengId() != null) {
                courseSettlementService.refreshCourseCompletion(homework.getKechengId(), zuoyeSubmit.getYonghuId());
            }
        }
        return R.ok();
    }

    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids) {
        ArrayList<ZuoyeSubmitEntity> list = new ArrayList<ZuoyeSubmitEntity>();
        for (Integer id : ids) {
            ZuoyeSubmitEntity entity = new ZuoyeSubmitEntity();
            entity.setId(id);
            entity.setSubmitDelete(2);
            list.add(entity);
        }
        if (!list.isEmpty()) {
            zuoyeSubmitService.updateBatchById(list);
        }
        return R.ok();
    }

    @IgnoreAuth
    @RequestMapping("/list")
    public R list(@RequestParam Map<String, Object> params) {
        CommonUtil.checkMap(params);
        PageUtils page = zuoyeSubmitService.queryPage(params);
        return R.ok().put("data", page);
    }

    @RequestMapping("/detail/{id}")
    public R detail(@PathVariable("id") Long id) {
        return info(id);
    }

    @RequestMapping("/save")
    public R save(@RequestBody ZuoyeSubmitEntity zuoyeSubmit, HttpServletRequest request) {
        Integer yonghuId = resolveStudent(request);
        if (yonghuId == null) {
            return R.error(511, "仅学生可以保存作业");
        }
        zuoyeSubmit.setYonghuId(yonghuId);
        if (zuoyeSubmit.getId() != null) {
            return submit(zuoyeSubmit, request);
        }
        return start(zuoyeSubmit, request);
    }

    @RequestMapping("/add")
    public R add(@RequestBody ZuoyeSubmitEntity zuoyeSubmit, HttpServletRequest request) {
        return save(zuoyeSubmit, request);
    }

    private Integer resolveStudent(HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if (!"学生".equals(role)) {
            return null;
        }
        return Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId")));
    }

    private List<ExamQuestionEntity> loadHomeworkQuestions(ZuoyeEntity homework) {
        List<ExamQuestionEntity> questions = new ArrayList<ExamQuestionEntity>();
        if (homework.getQuestionIds() == null || "".equals(homework.getQuestionIds().trim())) {
            return questions;
        }
        String[] parts = homework.getQuestionIds().split(",");
        for (String part : parts) {
            if (part == null || "".equals(part.trim())) {
                continue;
            }
            ExamQuestionEntity question = examQuestionService.selectById(Integer.valueOf(part.trim()));
            if (question == null || question.getIsDeleted() == null || question.getIsDeleted() != 1) {
                continue;
            }
            questions.add(question);
        }
        return questions;
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
}
