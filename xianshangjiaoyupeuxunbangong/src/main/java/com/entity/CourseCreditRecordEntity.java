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

@TableName("course_credit_record")
public class CourseCreditRecordEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    @TableField(value = "id")
    private Integer id;
    @TableField(value = "kecheng_id")
    private Integer kechengId;
    @TableField(value = "yonghu_id")
    private Integer yonghuId;
    @TableField(value = "credit_score")
    private Integer creditScore;
    @TableField(value = "grant_status")
    private String grantStatus;
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "grant_time")
    private Date grantTime;
    @TableField(value = "grant_remark")
    private String grantRemark;
    @TableField(value = "source_rule_snapshot")
    private String sourceRuleSnapshot;
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
    public Integer getCreditScore() { return creditScore; }
    public void setCreditScore(Integer creditScore) { this.creditScore = creditScore; }
    public String getGrantStatus() { return grantStatus; }
    public void setGrantStatus(String grantStatus) { this.grantStatus = grantStatus; }
    public Date getGrantTime() { return grantTime; }
    public void setGrantTime(Date grantTime) { this.grantTime = grantTime; }
    public String getGrantRemark() { return grantRemark; }
    public void setGrantRemark(String grantRemark) { this.grantRemark = grantRemark; }
    public String getSourceRuleSnapshot() { return sourceRuleSnapshot; }
    public void setSourceRuleSnapshot(String sourceRuleSnapshot) { this.sourceRuleSnapshot = sourceRuleSnapshot; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }
}

