package com.controller;

import com.alibaba.fastjson.JSONObject;
import com.annotation.IgnoreAuth;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.entity.CourseChapterEntity;
import com.service.CourseChapterService;
import com.utils.CommonUtil;
import com.utils.PageUtils;
import com.utils.R;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.Arrays;
import java.util.Date;
import java.util.Map;

@RestController
@Controller
@RequestMapping("/courseChapter")
public class CourseChapterController {
    private static final Logger logger = LoggerFactory.getLogger(CourseChapterController.class);

    @Autowired
    private CourseChapterService courseChapterService;

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("教师".equals(role)) {
            params.put("jiaoshiId", request.getSession().getAttribute("userId"));
        }
        params.put("isDeleted", 1);
        CommonUtil.checkMap(params);
        PageUtils page = courseChapterService.queryPage(params);
        return R.ok().put("data", page);
    }

    @IgnoreAuth
    @RequestMapping("/list")
    public R list(@RequestParam Map<String, Object> params) {
        params.put("chapterStatus", "approved");
        params.put("isDeleted", 1);
        CommonUtil.checkMap(params);
        return R.ok().put("data", courseChapterService.queryPage(params));
    }

    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id) {
        CourseChapterEntity entity = courseChapterService.selectById(id);
        return entity == null ? R.error(511, "查不到数据") : R.ok().put("data", entity);
    }

    @RequestMapping("/save")
    public R save(@RequestBody CourseChapterEntity entity) {
        CourseChapterEntity old = courseChapterService.selectOne(new EntityWrapper<CourseChapterEntity>()
            .eq("kecheng_id", entity.getKechengId())
            .eq("chapter_sort", entity.getChapterSort())
            .eq("is_deleted", 1));
        if (old != null) {
            return R.error(511, "章节排序不能重复");
        }
        entity.setChapterStatus("pending_review");
        entity.setReviewRemark(null);
        entity.setReviewTime(null);
        entity.setReviewAdminId(null);
        entity.setIsDeleted(1);
        entity.setCreateTime(new Date());
        courseChapterService.insert(entity);
        return R.ok();
    }

    @RequestMapping("/update")
    public R update(@RequestBody CourseChapterEntity entity) {
        CourseChapterEntity old = courseChapterService.selectOne(new EntityWrapper<CourseChapterEntity>()
            .notIn("id", entity.getId())
            .eq("kecheng_id", entity.getKechengId())
            .eq("chapter_sort", entity.getChapterSort())
            .eq("is_deleted", 1));
        if (old != null) {
            return R.error(511, "章节排序不能重复");
        }
        entity.setChapterStatus("pending_review");
        entity.setReviewRemark(null);
        entity.setReviewTime(null);
        entity.setReviewAdminId(null);
        courseChapterService.updateById(entity);
        return R.ok();
    }

    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids) {
        for (Integer id : ids) {
            CourseChapterEntity entity = new CourseChapterEntity();
            entity.setId(id);
            entity.setIsDeleted(2);
            courseChapterService.updateById(entity);
        }
        return R.ok();
    }

    @RequestMapping("/review")
    public R review(@RequestBody CourseChapterEntity entity, HttpServletRequest request) {
        CourseChapterEntity old = courseChapterService.selectById(entity.getId());
        if (old == null) {
            return R.error(511, "查不到数据");
        }
        old.setChapterStatus(entity.getChapterStatus());
        old.setReviewRemark(entity.getReviewRemark());
        old.setReviewTime(new Date());
        Object userId = request.getSession().getAttribute("userId");
        old.setReviewAdminId(userId == null ? null : Long.valueOf(String.valueOf(userId)));
        courseChapterService.updateById(old);
        return R.ok();
    }
}

