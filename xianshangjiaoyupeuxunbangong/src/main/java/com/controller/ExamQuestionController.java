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
import java.util.stream.Collectors;

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
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("教师".equals(role)) {
            params.put("jiaoshiId", request.getSession().getAttribute("userId"));
        }
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
        if (!"users".equals(request.getSession().getAttribute("tableName")) && !"jiaoshi".equals(request.getSession().getAttribute("tableName")) && !"教师".equals(role)) {
            hideAnswer(page);
        } else if ("学生".equals(role)) {
            hideAnswer(page);
        }
        return R.ok().put("data", page);
    }

    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id) {
        ExamQuestionEntity entity = examQuestionService.selectById(id);
        return entity == null ? R.error(511, "查不到数据") : R.ok().put("data", entity);
    }

    @RequestMapping("/save")
    public R save(@RequestBody ExamQuestionEntity entity) {
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
            return R.error(511, "请选择考试");
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
            question.setExamId(examId);
            if (question.getSortNo() == null) {
                question.setSortNo(1);
            }
            examQuestionService.updateById(question);
        }

        refreshExamScore(examId);
        return R.ok();
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
        List<ExamQuestionView> list = (List<ExamQuestionView>) page.getList();
        for (ExamQuestionView item : list) {
            item.setCorrectAnswer(null);
            item.setAnalysisText(null);
        }
    }
}
