package com.service.impl;

import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.entity.*;
import com.service.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Service("courseSettlementService")
@Transactional
public class CourseSettlementServiceImpl implements CourseSettlementService {

    @Autowired
    private CourseEnrollService courseEnrollService;
    @Autowired
    private CourseResourceService courseResourceService;
    @Autowired
    private StudyProgressService studyProgressService;
    @Autowired
    private ZuoyeService zuoyeService;
    @Autowired
    private ZuoyeSubmitService zuoyeSubmitService;
    @Autowired
    private CourseCreditRecordService courseCreditRecordService;
    @Autowired
    private KechengService kechengService;

    @Override
    public void refreshCourseCompletion(Integer kechengId, Integer yonghuId) {
        if (kechengId == null || yonghuId == null) {
            return;
        }
        CourseEnrollEntity enroll = courseEnrollService.selectOne(new EntityWrapper<CourseEnrollEntity>()
            .eq("kecheng_id", kechengId)
            .eq("yonghu_id", yonghuId)
            .eq("is_deleted", 1));
        if (enroll == null) {
            return;
        }

        List<CourseResourceEntity> resources = courseResourceService.selectList(new EntityWrapper<CourseResourceEntity>()
            .eq("kecheng_id", kechengId)
            .eq("resource_status", "approved")
            .eq("is_deleted", 1));
        int totalResources = resources.size();
        Set<Integer> resourceIds = new HashSet<Integer>();
        for (CourseResourceEntity resource : resources) {
            resourceIds.add(resource.getId());
        }

        List<StudyProgressEntity> progressList = studyProgressService.selectList(new EntityWrapper<StudyProgressEntity>()
            .eq("kecheng_id", kechengId)
            .eq("yonghu_id", yonghuId)
            .eq("is_completed", 1));
        int completedCount = 0;
        for (StudyProgressEntity progress : progressList) {
            if (progress.getResourceId() != null && resourceIds.contains(progress.getResourceId())) {
                completedCount++;
            }
        }

        double progressPercent = totalResources == 0 ? 0D : (completedCount * 100D / totalResources);
        enroll.setProgressPercent(progressPercent);

        boolean homeworkPassed = isHomeworkPassed(kechengId, yonghuId);
        if (progressPercent >= 90D && homeworkPassed) {
            enroll.setEnrollStatus("已结课");
            enroll.setFinishTime(new Date());
            grantCredit(kechengId, yonghuId, progressPercent);
        } else if (progressPercent > 0D) {
            enroll.setEnrollStatus("学习中");
        } else if (enroll.getEnrollStatus() == null) {
            enroll.setEnrollStatus("已选课");
        }
        courseEnrollService.updateById(enroll);
    }

    private boolean isHomeworkPassed(Integer kechengId, Integer yonghuId) {
        List<ZuoyeEntity> homeworks = zuoyeService.selectList(new EntityWrapper<ZuoyeEntity>()
            .eq("kecheng_id", kechengId)
            .eq("zuoye_delete", 1)
            .eq("publish_status", "published"));
        if (homeworks == null || homeworks.isEmpty()) {
            return true;
        }
        Set<Integer> passedHomeworkIds = new HashSet<Integer>();
        List<ZuoyeSubmitEntity> submits = zuoyeSubmitService.selectList(new EntityWrapper<ZuoyeSubmitEntity>()
            .eq("yonghu_id", yonghuId)
            .eq("submit_delete", 1));
        for (ZuoyeSubmitEntity submit : submits) {
            if (submit.getZuoyeId() != null && submit.getSubmitScore() != null && submit.getSubmitScore() >= 60D) {
                passedHomeworkIds.add(submit.getZuoyeId());
            }
        }
        for (ZuoyeEntity homework : homeworks) {
            if (!passedHomeworkIds.contains(homework.getId())) {
                return false;
            }
        }
        return true;
    }

    private void grantCredit(Integer kechengId, Integer yonghuId, double progressPercent) {
        KechengEntity course = kechengService.selectById(kechengId);
        if (course == null || course.getCreditScore() == null || course.getCreditScore() <= 0) {
            return;
        }
        CourseCreditRecordEntity record = courseCreditRecordService.selectOne(new EntityWrapper<CourseCreditRecordEntity>()
            .eq("kecheng_id", kechengId)
            .eq("yonghu_id", yonghuId));
        if (record == null) {
            record = new CourseCreditRecordEntity();
            record.setKechengId(kechengId);
            record.setYonghuId(yonghuId);
            record.setCreateTime(new Date());
        }
        record.setCreditScore(course.getCreditScore());
        record.setGrantStatus("已发放");
        record.setGrantTime(new Date());
        record.setGrantRemark("系统自动发放");
        record.setSourceRuleSnapshot("progress>=" + progressPercent + ",homework>=60");
        if (record.getId() == null) {
            courseCreditRecordService.insert(record);
        } else {
            courseCreditRecordService.updateById(record);
        }
    }
}
