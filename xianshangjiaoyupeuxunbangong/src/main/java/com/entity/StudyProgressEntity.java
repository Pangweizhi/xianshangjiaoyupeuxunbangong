package com.entity;

import com.baomidou.mybatisplus.annotations.TableField;
import com.baomidou.mybatisplus.annotations.TableId;
import com.baomidou.mybatisplus.annotations.TableName;
import com.baomidou.mybatisplus.enums.FieldFill;
import com.baomidou.mybatisplus.enums.IdType;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.springframework.format.annotation.DateTimeFormat;

import java.io.Serializable;
import java.util.Date;

@TableName("study_progress")
public class StudyProgressEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    @TableField(value = "id")
    private Integer id;
    @TableField(value = "kecheng_id")
    private Integer kechengId;
    @TableField(value = "chapter_id")
    private Integer chapterId;
    @TableField(value = "resource_id")
    private Integer resourceId;
    @TableField(value = "yonghu_id")
    private Integer yonghuId;
    @TableField(value = "study_seconds")
    private Integer studySeconds;
    @TableField(value = "progress_percent")
    private Double progressPercent;
    @TableField(value = "is_completed")
    private Integer isCompleted;
    @TableField(exist = false)
    private Integer forceCompleted;
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "last_study_time")
    private Date lastStudyTime;
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "create_time", fill = FieldFill.INSERT)
    private Date createTime;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public Integer getKechengId() { return kechengId; }
    public void setKechengId(Integer kechengId) { this.kechengId = kechengId; }
    public Integer getChapterId() { return chapterId; }
    public void setChapterId(Integer chapterId) { this.chapterId = chapterId; }
    public Integer getResourceId() { return resourceId; }
    public void setResourceId(Integer resourceId) { this.resourceId = resourceId; }
    public Integer getYonghuId() { return yonghuId; }
    public void setYonghuId(Integer yonghuId) { this.yonghuId = yonghuId; }
    public Integer getStudySeconds() { return studySeconds; }
    public void setStudySeconds(Integer studySeconds) { this.studySeconds = studySeconds; }
    public Double getProgressPercent() { return progressPercent; }
    public void setProgressPercent(Double progressPercent) { this.progressPercent = progressPercent; }
    public Integer getIsCompleted() { return isCompleted; }
    public void setIsCompleted(Integer isCompleted) { this.isCompleted = isCompleted; }
    public Integer getForceCompleted() { return forceCompleted; }
    public void setForceCompleted(Integer forceCompleted) { this.forceCompleted = forceCompleted; }
    public Date getLastStudyTime() { return lastStudyTime; }
    public void setLastStudyTime(Date lastStudyTime) { this.lastStudyTime = lastStudyTime; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }
}
