package com.controller;

import com.annotation.IgnoreAuth;
import com.entity.ExamQuestionEntity;
import com.entity.view.ExamQuestionView;
import com.service.ExamQuestionService;
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
@RequestMapping("/examQuestion")
public class ExamQuestionController {

    @Autowired
    private ExamQuestionService examQuestionService;

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("鏁欏笀".equals(role)) {
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
        if (!"users".equals(request.getSession().getAttribute("tableName")) && !"jiaoshi".equals(request.getSession().getAttribute("tableName")) && !"鏁欏笀".equals(role)) {
            hideAnswer(page);
        } else if ("瀛︾敓".equals(role)) {
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
        entity.setIsDeleted(1);
        entity.setCreateTime(new Date());
        if (entity.getSortNo() == null) {
            entity.setSortNo(1);
        }
        examQuestionService.insert(entity);
        return R.ok();
    }

    @RequestMapping("/update")
    public R update(@RequestBody ExamQuestionEntity entity) {
        examQuestionService.updateById(entity);
        return R.ok();
    }

    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids) {
        for (Integer id : ids) {
            ExamQuestionEntity entity = new ExamQuestionEntity();
            entity.setId(id);
            entity.setIsDeleted(2);
            examQuestionService.updateById(entity);
        }
        return R.ok();
    }

    private void hideAnswer(PageUtils page) {
        List<ExamQuestionView> list = (List<ExamQuestionView>) page.getList();
        for (ExamQuestionView item : list) {
            item.setCorrectAnswer(null);
            item.setAnalysisText(null);
        }
    }
}
