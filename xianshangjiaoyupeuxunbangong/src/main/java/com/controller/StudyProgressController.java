package com.controller;

import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.entity.CourseResourceEntity;
import com.entity.StudyProgressEntity;
import com.service.CourseResourceService;
import com.service.CourseSettlementService;
import com.service.StudyProgressService;
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
@RequestMapping("/studyProgress")
public class StudyProgressController {

    @Autowired
    private StudyProgressService studyProgressService;
    @Autowired
    private CourseResourceService courseResourceService;
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
        PageUtils page = studyProgressService.queryPage(params);
        return R.ok().put("data", page);
    }

    @RequestMapping("/saveOrUpdate")
    public R saveOrUpdate(@RequestBody StudyProgressEntity entity, HttpServletRequest request) {
        String role = String.valueOf(request.getSession().getAttribute("role"));
        if (!"学生".equals(role)) {
            return R.error(511, "Only students can record study progress.");
        }

        Integer yonghuId = Integer.valueOf(String.valueOf(request.getSession().getAttribute("userId")));
        entity.setYonghuId(yonghuId);

        CourseResourceEntity resource = courseResourceService.selectById(entity.getResourceId());
        if (resource == null) {
            return R.error(511, "Study resource not found.");
        }
        if (!isVideoResource(resource)) {
            return R.ok();
        }

        entity.setKechengId(resource.getKechengId());
        entity.setChapterId(resource.getChapterId());
        if (entity.getStudySeconds() == null) {
            entity.setStudySeconds(0);
        }

        boolean forceCompleted = entity.getForceCompleted() != null && entity.getForceCompleted() == 1;
        double percent = entity.getProgressPercent() == null ? 0D : entity.getProgressPercent();
        Integer durationSeconds = resource.getDurationSeconds();
        if (durationSeconds != null && durationSeconds > 0) {
            double calculated = entity.getStudySeconds() * 100D / durationSeconds;
            if (forceCompleted || calculated >= 99.5D || entity.getStudySeconds() >= durationSeconds) {
                percent = 100D;
            } else {
                percent = Math.max(percent, Math.min(99.5D, calculated));
            }
        } else if (forceCompleted) {
            percent = 100D;
        }

        entity.setProgressPercent(percent);
        entity.setIsCompleted(percent >= 100D ? 1 : 0);
        entity.setLastStudyTime(new Date());

        StudyProgressEntity old = studyProgressService.selectOne(new EntityWrapper<StudyProgressEntity>()
            .eq("resource_id", entity.getResourceId())
            .eq("yonghu_id", yonghuId));
        if (old == null) {
            entity.setCreateTime(new Date());
            studyProgressService.insert(entity);
        } else {
            old.setStudySeconds(Math.max(old.getStudySeconds() == null ? 0 : old.getStudySeconds(), entity.getStudySeconds()));
            old.setProgressPercent(Math.max(old.getProgressPercent() == null ? 0D : old.getProgressPercent(), entity.getProgressPercent()));
            boolean completed = (old.getProgressPercent() != null && old.getProgressPercent() >= 100D)
                || (entity.getProgressPercent() != null && entity.getProgressPercent() >= 100D);
            old.setIsCompleted(completed ? 1 : entity.getIsCompleted());
            old.setLastStudyTime(entity.getLastStudyTime());
            studyProgressService.updateById(old);
        }

        courseSettlementService.refreshCourseCompletion(entity.getKechengId(), yonghuId);
        return R.ok();
    }

    private boolean isVideoResource(CourseResourceEntity resource) {
        String type = resource.getResourceType() == null ? "" : resource.getResourceType();
        String url = resource.getResourceUrl() == null ? "" : resource.getResourceUrl();
        return type.contains("视频") || url.matches("(?i).*(mp4|m3u8|webm|mov)$");
    }
}
