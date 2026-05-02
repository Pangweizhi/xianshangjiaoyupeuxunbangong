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

@TableName("course_enroll")
public class CourseEnrollEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    @TableField(value = "id")
    private Integer id;
    @TableField(value = "kecheng_id")
    private Integer kechengId;
    @TableField(value = "yonghu_id")
    private Integer yonghuId;
    @TableField(value = "enroll_status")
    private String enrollStatus;
    @TableField(value = "progress_percent")
    private Double progressPercent;
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "enroll_time")
    private Date enrollTime;
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "finish_time")
    private Date finishTime;
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
    public Integer getYonghuId() { return yonghuId; }
    public void setYonghuId(Integer yonghuId) { this.yonghuId = yonghuId; }
    public String getEnrollStatus() { return enrollStatus; }
    public void setEnrollStatus(String enrollStatus) { this.enrollStatus = enrollStatus; }
    public Double getProgressPercent() { return progressPercent; }
    public void setProgressPercent(Double progressPercent) { this.progressPercent = progressPercent; }
    public Date getEnrollTime() { return enrollTime; }
    public void setEnrollTime(Date enrollTime) { this.enrollTime = enrollTime; }
    public Date getFinishTime() { return finishTime; }
    public void setFinishTime(Date finishTime) { this.finishTime = finishTime; }
    public Integer getIsDeleted() { return isDeleted; }
    public void setIsDeleted(Integer isDeleted) { this.isDeleted = isDeleted; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }
}

