package com.controller;

import com.annotation.IgnoreAuth;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.entity.ExamEntity;
import com.entity.ExamQuestionEntity;
import com.service.ExamQuestionService;
import com.service.ExamService;
import com.utils.CommonUtil;
import com.utils.PageUtils;
import com.utils.R;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.Date;
import java.util.List;
import java.util.Map;

@RestController
@Controller
@RequestMapping("/exam")
public class ExamController {

    @Autowired
    private ExamService examService;
    @Autowired
    private ExamQuestionService examQuestionService;

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("教师".equals(role)) {
            params.put("jiaoshiId", request.getSession().getAttribute("userId"));
        }
        params.put("isDeleted", 1);
        CommonUtil.checkMap(params);
        PageUtils page = examService.queryPage(params);
        return R.ok().put("data", page);
    }

    @IgnoreAuth
    @RequestMapping("/list")
    public R list(@RequestParam Map<String, Object> params) {
        params.put("examStatus", "published");
        params.put("isDeleted", 1);
        CommonUtil.checkMap(params);
        PageUtils page = examService.queryPage(params);
        return R.ok().put("data", page);
    }

    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id) {
        ExamEntity entity = examService.selectById(id);
        return entity == null ? R.error(511, "查不到数据") : R.ok().put("data", entity);
    }

    @RequestMapping("/detail/{id}")
    public R detail(@PathVariable("id") Long id) {
        ExamEntity entity = examService.selectById(id);
        if (entity == null || entity.getIsDeleted() == null || entity.getIsDeleted() != 1 || !"published".equals(entity.getExamStatus())) {
            return R.error(511, "查不到数据");
        }
        return R.ok().put("data", entity);
    }

    @RequestMapping("/save")
    public R save(@RequestBody ExamEntity entity, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("教师".equals(role)) {
            entity.setJiaoshiId(Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId"))));
        }
        fillRuleDefaults(entity);
        entity.setExamStatus("draft");
        entity.setPublishTime(null);
        entity.setIsDeleted(1);
        entity.setCreateTime(new Date());
        syncExamScore(entity);
        examService.insert(entity);
        return R.ok().put("data", entity);
    }

    @RequestMapping("/update")
    public R update(@RequestBody ExamEntity entity, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("教师".equals(role)) {
            entity.setJiaoshiId(Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId"))));
        }
        ExamEntity old = examService.selectById(entity.getId());
        if (old == null) {
            return R.error(511, "查不到数据");
        }
        fillRuleDefaults(entity);
        if (old.getPublishTime() != null && "published".equals(old.getExamStatus())) {
            entity.setPublishTime(old.getPublishTime());
            entity.setExamStatus(old.getExamStatus());
        } else {
            entity.setExamStatus("draft");
            entity.setPublishTime(null);
        }
        syncExamScore(entity);
        examService.updateById(entity);
        return R.ok().put("data", entity);
    }

    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids) {
        for (Integer id : ids) {
            ExamEntity entity = new ExamEntity();
            entity.setId(id);
            entity.setIsDeleted(2);
            examService.updateById(entity);
        }
        return R.ok();
    }

    @RequestMapping("/publish")
    public R publish(@RequestBody ExamEntity entity) {
        ExamEntity old = examService.selectById(entity.getId());
        if (old == null) {
            return R.error(511, "查不到数据");
        }
        fillRuleDefaults(old);
        syncExamScore(old);
        old.setExamStatus("published");
        old.setPublishTime(new Date());
        examService.updateById(old);
        return R.ok().put("data", old);
    }

    private void fillRuleDefaults(ExamEntity entity) {
        if (entity.getAllowRetake() == null) {
            entity.setAllowRetake(0);
        }
        if (entity.getMaxAttemptCount() == null || entity.getMaxAttemptCount() <= 0) {
            entity.setMaxAttemptCount(1);
        }
        if (entity.getAllowResume() == null) {
            entity.setAllowResume(1);
        }
    }

    private void syncExamScore(ExamEntity entity) {
        if (entity.getId() == null) {
            if (entity.getTotalScore() == null) {
                entity.setTotalScore(100);
            }
            if (entity.getPassScore() == null) {
                entity.setPassScore(60);
            }
            return;
        }
        List<ExamQuestionEntity> questions = examQuestionService.selectList(new EntityWrapper<ExamQuestionEntity>()
            .eq("exam_id", entity.getId())
            .eq("is_deleted", 1));
        int total = 0;
        for (ExamQuestionEntity question : questions) {
            total += question.getQuestionScore() == null ? 0 : question.getQuestionScore();
        }
        entity.setTotalScore(total > 0 ? total : (entity.getTotalScore() == null ? 100 : entity.getTotalScore()));
        if (entity.getPassScore() == null) {
            entity.setPassScore(60);
        }
    }
}
