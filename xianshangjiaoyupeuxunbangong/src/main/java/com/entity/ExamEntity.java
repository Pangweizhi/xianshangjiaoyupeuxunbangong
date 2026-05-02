package com.entity;

import com.baomidou.mybatisplus.annotations.TableField;
import com.baomidou.mybatisplus.annotations.TableId;
import com.baomidou.mybatisplus.annotations.TableName;
import com.baomidou.mybatisplus.enums.FieldFill;
import com.baomidou.mybatisplus.enums.IdType;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.commons.beanutils.BeanUtils;
import org.springframework.format.annotation.DateTimeFormat;

import java.io.Serializable;
import java.lang.reflect.InvocationTargetException;
import java.util.Date;

@TableName("exam")
public class ExamEntity<T> implements Serializable {
    private static final long serialVersionUID = 1L;

    public ExamEntity() {
    }

    public ExamEntity(T t) {
        try {
            BeanUtils.copyProperties(this, t);
        } catch (IllegalAccessException | InvocationTargetException e) {
            e.printStackTrace();
        }
    }

    @TableId(type = IdType.AUTO)
    @TableField(value = "id")
    private Integer id;
    @TableField(value = "kecheng_id")
    private Integer kechengId;
    @TableField(value = "chapter_id")
    private Integer chapterId;
    @TableField(value = "jiaoshi_id")
    private Integer jiaoshiId;
    @TableField(value = "exam_name")
    private String examName;
    @TableField(value = "exam_summary")
    private String examSummary;
    @TableField(value = "duration_minutes")
    private Integer durationMinutes;
    @TableField(value = "total_score")
    private Integer totalScore;
    @TableField(value = "pass_score")
    private Integer passScore;
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "start_time")
    private Date startTime;
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "end_time")
    private Date endTime;
    @TableField(value = "exam_status")
    private String examStatus;
    @TableField(value = "allow_retake")
    private Integer allowRetake;
    @TableField(value = "max_attempt_count")
    private Integer maxAttemptCount;
    @TableField(value = "allow_resume")
    private Integer allowResume;
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "publish_time")
    private Date publishTime;
    @TableField(value = "is_deleted")
    private Integer isDeleted;
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
    public Integer getJiaoshiId() { return jiaoshiId; }
    public void setJiaoshiId(Integer jiaoshiId) { this.jiaoshiId = jiaoshiId; }
    public String getExamName() { return examName; }
    public void setExamName(String examName) { this.examName = examName; }
    public String getExamSummary() { return examSummary; }
    public void setExamSummary(String examSummary) { this.examSummary = examSummary; }
    public Integer getDurationMinutes() { return durationMinutes; }
    public void setDurationMinutes(Integer durationMinutes) { this.durationMinutes = durationMinutes; }
    public Integer getTotalScore() { return totalScore; }
    public void setTotalScore(Integer totalScore) { this.totalScore = totalScore; }
    public Integer getPassScore() { return passScore; }
    public void setPassScore(Integer passScore) { this.passScore = passScore; }
    public Date getStartTime() { return startTime; }
    public void setStartTime(Date startTime) { this.startTime = startTime; }
    public Date getEndTime() { return endTime; }
    public void setEndTime(Date endTime) { this.endTime = endTime; }
    public String getExamStatus() { return examStatus; }
    public void setExamStatus(String examStatus) { this.examStatus = examStatus; }
    public Integer getAllowRetake() { return allowRetake; }
    public void setAllowRetake(Integer allowRetake) { this.allowRetake = allowRetake; }
    public Integer getMaxAttemptCount() { return maxAttemptCount; }
    public void setMaxAttemptCount(Integer maxAttemptCount) { this.maxAttemptCount = maxAttemptCount; }
    public Integer getAllowResume() { return allowResume; }
    public void setAllowResume(Integer allowResume) { this.allowResume = allowResume; }
    public Date getPublishTime() { return publishTime; }
    public void setPublishTime(Date publishTime) { this.publishTime = publishTime; }
    public Integer getIsDeleted() { return isDeleted; }
    public void setIsDeleted(Integer isDeleted) { this.isDeleted = isDeleted; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }
}
