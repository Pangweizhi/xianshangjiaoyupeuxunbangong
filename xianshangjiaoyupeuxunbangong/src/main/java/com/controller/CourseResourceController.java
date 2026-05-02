package com.controller;

import com.annotation.IgnoreAuth;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.entity.CourseResourceEntity;
import com.service.CourseResourceService;
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
@RequestMapping("/courseResource")
public class CourseResourceController {

    @Autowired
    private CourseResourceService courseResourceService;

    @RequestMapping("/page")
    public R page(@RequestParam Map<String, Object> params, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if ("教师".equals(role)) {
            params.put("jiaoshiId", request.getSession().getAttribute("userId"));
        }
        params.put("isDeleted", 1);
        CommonUtil.checkMap(params);
        PageUtils page = courseResourceService.queryPage(params);
        return R.ok().put("data", page);
    }

    @IgnoreAuth
    @RequestMapping("/list")
    public R list(@RequestParam Map<String, Object> params) {
        params.put("resourceStatus", "approved");
        params.put("isDeleted", 1);
        CommonUtil.checkMap(params);
        return R.ok().put("data", courseResourceService.queryPage(params));
    }

    @RequestMapping("/info/{id}")
    public R info(@PathVariable("id") Long id) {
        CourseResourceEntity entity = courseResourceService.selectById(id);
        return entity == null ? R.error(511, "查不到数据") : R.ok().put("data", entity);
    }

    @RequestMapping("/save")
    public R save(@RequestBody CourseResourceEntity entity) {
        entity.setResourceStatus("pending_review");
        entity.setReviewRemark(null);
        entity.setReviewTime(null);
        entity.setReviewAdminId(null);
        entity.setIsDeleted(1);
        entity.setCreateTime(new Date());
        courseResourceService.insert(entity);
        return R.ok();
    }

    @RequestMapping("/update")
    public R update(@RequestBody CourseResourceEntity entity) {
        entity.setResourceStatus("pending_review");
        entity.setReviewRemark(null);
        entity.setReviewTime(null);
        entity.setReviewAdminId(null);
        courseResourceService.updateById(entity);
        return R.ok();
    }

    @RequestMapping("/delete")
    public R delete(@RequestBody Integer[] ids) {
        for (Integer id : ids) {
            CourseResourceEntity entity = new CourseResourceEntity();
            entity.setId(id);
            entity.setIsDeleted(2);
            courseResourceService.updateById(entity);
        }
        return R.ok();
    }

    @RequestMapping("/review")
    public R review(@RequestBody CourseResourceEntity entity, HttpServletRequest request) {
        CourseResourceEntity old = courseResourceService.selectById(entity.getId());
        if (old == null) {
            return R.error(511, "查不到数据");
        }
        old.setResourceStatus(entity.getResourceStatus());
        old.setReviewRemark(entity.getReviewRemark());
        old.setReviewTime(new Date());
        Object userId = request.getSession().getAttribute("userId");
        old.setReviewAdminId(userId == null ? null : Long.valueOf(String.valueOf(userId)));
        courseResourceService.updateById(old);
        return R.ok();
    }
}

