package com.controller;

import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.entity.CourseEnrollEntity;
import com.entity.KechengEntity;
import com.service.CourseEnrollService;
import com.service.KechengService;
import com.utils.CommonUtil;
import com.utils.PageUtils;
import com.utils.R;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.Date;
import java.util.Map;

@RestController
@Controller
@RequestMapping("/courseEnroll")
public class CourseEnrollController {

    @Autowired
    private CourseEnrollService courseEnrollService;
    @Autowired
    private KechengService kechengService;

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("学生".equals(role)) {
            params.put("yonghuId", request.getSession().getAttribute("userId"));
        } else if ("教师".equals(role)) {
            params.put("jiaoshiId", request.getSession().getAttribute("userId"));
        }
        params.put("isDeleted", 1);
        CommonUtil.checkMap(params);
        PageUtils page = courseEnrollService.queryPage(params);
        return R.ok().put("data", page);
    }

    @RequestMapping("/myCourses")
    public R myCourses(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        params.put("yonghuId", request.getSession().getAttribute("userId"));
        params.put("isDeleted", 1);
        CommonUtil.checkMap(params);
        return R.ok().put("data", courseEnrollService.queryPage(params));
    }

    @RequestMapping("/save")
    public R save(@RequestBody CourseEnrollEntity entity, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if (!"学生".equals(role)) {
            return R.error(511, "仅学生可以选课");
        }
        entity.setYonghuId(Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId"))));
        KechengEntity course = kechengService.selectById(entity.getKechengId());
        if (course == null || !"approved".equals(course.getCourseStatus())) {
            return R.error(511, "仅允许选修已审核通过的课程");
        }
        CourseEnrollEntity old = courseEnrollService.selectOne(new EntityWrapper<CourseEnrollEntity>()
            .eq("kecheng_id", entity.getKechengId())
            .eq("yonghu_id", entity.getYonghuId())
            .eq("is_deleted", 1));
        if (old != null) {
            return R.error(511, "请勿重复选课");
        }
        entity.setEnrollStatus("已选课");
        entity.setProgressPercent(0D);
        entity.setEnrollTime(new Date());
        entity.setIsDeleted(1);
        entity.setCreateTime(new Date());
        courseEnrollService.insert(entity);
        return R.ok();
    }
}
