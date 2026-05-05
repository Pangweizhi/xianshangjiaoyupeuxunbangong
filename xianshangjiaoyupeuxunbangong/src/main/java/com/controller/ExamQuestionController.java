package com.controller;

import com.annotation.IgnoreAuth;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.entity.ExamEntity;
import com.entity.ExamQuestionEntity;
import com.entity.view.ExamQuestionView;
import com.service.ExamQuestionService;
import com.service.ExamService;
import com.utils.CommonUtil;
import com.utils.PageUtils;
import com.utils.R;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.Set;

@RestController
@Controller
@RequestMapping("/examQuestion")
public class ExamQuestionController {

    @Autowired
    private ExamQuestionService examQuestionService;

    @Autowired
    private ExamService examService;

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        params.put("isDeleted", 1);
        CommonUtil.checkMap(params);
        PageUtils page = examQuestionService.queryPage(params);
        return R.ok().put("data", page);
    }

    @IgnoreAuth
    @RequestMapping("/list")
    public R list(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        params.put("isDeleted", 1);
        CommonUtil.checkMap(params);
        PageUtils page = examQuestionService.queryPage(params);

        String role = String.valueOf(request.getSession().getAttribute("role"));
        String tableName = String.valueOf(request.getSession().getAttribute("tableName"));
        if (!isTeacher(role, tableName) && !isStudent(role, tableName)) {
            hideAnswer(page);
        } else if (isStudent(role, tableName)) {
            hideAnswer(page);
        }
        return R.ok().put("data", page);
    }

    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id) {
        ExamQuestionEntity entity = examQuestionService.selectById(id);
        return entity == null ? R.error(511, "鏌ヨ涓嶅埌鏁版嵁") : R.ok().put("data", entity);
    }

    @RequestMapping("/save")
    public R save(@RequestBody ExamQuestionEntity entity) {
        ensureQuestionCourse(entity);
        entity.setQuestionType(normalizeQuestionType(entity.getQuestionType()));
        if (entity.getKechengId() == null || entity.getKechengId() <= 0) {
            return R.error(511, "璇烽€夋嫨璇剧▼");
        }
        if (entity.getExamId() == null) {
            entity.setExamId(0);
        }
        entity.setIsDeleted(1);
        entity.setCreateTime(new Date());
        if (entity.getSortNo() == null) {
            entity.setSortNo(1);
        }
        examQuestionService.insert(entity);
        refreshExamScore(entity.getExamId());
        return R.ok().put("data", entity);
    }

    @RequestMapping("/update")
    public R update(@RequestBody ExamQuestionEntity entity) {
        ensureQuestionCourse(entity);
        entity.setQuestionType(normalizeQuestionType(entity.getQuestionType()));
        if (entity.getKechengId() == null || entity.getKechengId() <= 0) {
            return R.error(511, "璇烽€夋嫨璇剧▼");
        }
        if (entity.getExamId() == null) {
            entity.setExamId(0);
        }
        examQuestionService.updateById(entity);
        refreshExamScore(entity.getExamId());
        return R.ok().put("data", entity);
    }

    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids) {
        Set<Integer> affectedExamIds = new java.util.HashSet<Integer>();
        for (Integer id : ids) {
            ExamQuestionEntity entity = examQuestionService.selectById(id);
            if (entity != null && entity.getExamId() != null && entity.getExamId() > 0) {
                affectedExamIds.add(entity.getExamId());
            }
            ExamQuestionEntity deleteEntity = new ExamQuestionEntity();
            deleteEntity.setId(id);
            deleteEntity.setIsDeleted(2);
            examQuestionService.updateById(deleteEntity);
        }
        for (Integer examId : affectedExamIds) {
            refreshExamScore(examId);
        }
        return R.ok();
    }

    @RequestMapping("/bindToExam")
    public R bindToExam(@RequestBody Map<String, Object> payload) {
        Integer examId = payload.get("examId") == null ? null : Integer.valueOf(String.valueOf(payload.get("examId")));
        if (examId == null || examId <= 0) {
            return R.error(511, "璇烽€夋嫨鑰冭瘯");
        }
        ExamEntity exam = examService.selectById(examId);
        if (exam == null) {
            return R.error(511, "考试不存在");
        }

        List<Integer> questionIds = new ArrayList<Integer>();
        Object rawIds = payload.get("questionIds");
        if (rawIds instanceof List) {
            for (Object item : (List<?>) rawIds) {
                if (item != null && !"".equals(String.valueOf(item).trim())) {
                    questionIds.add(Integer.valueOf(String.valueOf(item)));
                }
            }
        }

        List<ExamQuestionEntity> currentQuestions = examQuestionService.selectList(new EntityWrapper<ExamQuestionEntity>()
            .eq("exam_id", examId)
            .eq("is_deleted", 1));
        for (ExamQuestionEntity question : currentQuestions) {
            if (!questionIds.contains(question.getId())) {
                question.setExamId(0);
                examQuestionService.updateById(question);
            }
        }

        for (Integer questionId : questionIds) {
            ExamQuestionEntity question = examQuestionService.selectById(questionId);
            if (question == null || question.getIsDeleted() != null && question.getIsDeleted() != 1) {
                continue;
            }
            if (question.getKechengId() != null && !question.getKechengId().equals(exam.getKechengId())) {
                continue;
            }
            question.setExamId(examId);
            if (question.getSortNo() == null) {
                question.setSortNo(1);
            }
            examQuestionService.updateById(question);
        }

        refreshExamScore(examId);
        return R.ok();
    }

    private void ensureQuestionCourse(ExamQuestionEntity entity) {
        if (entity == null) {
            return;
        }
        if (entity.getKechengId() != null && entity.getKechengId() > 0) {
            return;
        }
        if (entity.getExamId() != null && entity.getExamId() > 0) {
            ExamEntity exam = examService.selectById(entity.getExamId());
            if (exam != null) {
                entity.setKechengId(exam.getKechengId());
            }
        }
    }

    private String normalizeQuestionType(String value) {
        if (value == null) {
            return null;
        }
        String text = value.trim();
        if (text.isEmpty()) {
            return text;
        }
        if (text.contains("判断") || text.contains("True")) {
            return "判断题";
        }
        if (text.contains("填空") || text.contains("Fill")) {
            return "填空题";
        }
        if (text.contains("简答") || text.contains("问答") || text.contains("Short")) {
            return "简答题";
        }
        return "选择题";
    }

    private void refreshExamScore(Integer examId) {
        if (examId == null || examId <= 0) {
            return;
        }
        ExamEntity exam = examService.selectById(examId);
        if (exam == null) {
            return;
        }
        List<ExamQuestionEntity> questions = examQuestionService.selectList(new EntityWrapper<ExamQuestionEntity>()
            .eq("exam_id", examId)
            .eq("is_deleted", 1));
        int total = 0;
        for (ExamQuestionEntity question : questions) {
            total += question.getQuestionScore() == null ? 0 : question.getQuestionScore();
        }
        exam.setTotalScore(total > 0 ? total : (exam.getTotalScore() == null ? 100 : exam.getTotalScore()));
        if (exam.getPassScore() == null) {
            exam.setPassScore(60);
        }
        examService.updateById(exam);
    }

    private void hideAnswer(PageUtils page) {
        if (page == null || page.getList() == null) {
            return;
        }
        for (Object item : page.getList()) {
            if (item instanceof ExamQuestionEntity) {
                ExamQuestionEntity question = (ExamQuestionEntity) item;
                question.setCorrectAnswer(null);
                question.setAnalysisText(null);
            } else if (item instanceof ExamQuestionView) {
                ExamQuestionView view = (ExamQuestionView) item;
                view.setCorrectAnswer(null);
                view.setAnalysisText(null);
            }
        }
    }

    private boolean isTeacher(String role, String tableName) {
        return "jiaoshi".equals(tableName) || "\u6559\u5e08".equals(role);
    }

    private boolean isStudent(String role, String tableName) {
        return "users".equals(tableName) || "\u5b66\u751f".equals(role);
    }
}
