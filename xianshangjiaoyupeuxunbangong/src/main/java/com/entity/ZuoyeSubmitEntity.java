package com.entity;

import com.annotation.ColumnInfo;
import com.baomidou.mybatisplus.annotations.TableField;
import com.baomidou.mybatisplus.annotations.TableId;
import com.baomidou.mybatisplus.annotations.TableName;
import com.baomidou.mybatisplus.enums.FieldFill;
import com.baomidou.mybatisplus.enums.IdType;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.springframework.format.annotation.DateTimeFormat;

import java.io.Serializable;
import java.util.Date;

/**
 * 作业提交
 */
@TableName("zuoye_submit")
public class ZuoyeSubmitEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    @ColumnInfo(comment = "主键", type = "int(11)")
    @TableField(value = "id")
    private Integer id;

    @ColumnInfo(comment = "作业", type = "int(11)")
    @TableField(value = "zuoye_id")
    private Integer zuoyeId;

    @ColumnInfo(comment = "学生", type = "int(11)")
    @TableField(value = "yonghu_id")
    private Integer yonghuId;

    @ColumnInfo(comment = "提交附件", type = "varchar(255)")
    @TableField(value = "submit_file")
    private String submitFile;

    @ColumnInfo(comment = "提交说明", type = "text")
    @TableField(value = "submit_content")
    private String submitContent;

    @ColumnInfo(comment = "提交状态", type = "varchar(50)")
    @TableField(value = "submit_status")
    private String submitStatus;

    @ColumnInfo(comment = "答案快照", type = "longtext")
    @TableField(value = "answer_snapshot")
    private String answerSnapshot;

    @ColumnInfo(comment = "题目快照", type = "longtext")
    @TableField(value = "question_snapshot")
    private String questionSnapshot;

    @ColumnInfo(comment = "自动评分", type = "decimal(10,2)")
    @TableField(value = "auto_score")
    private Double autoScore;

    @ColumnInfo(comment = "最终评分", type = "decimal(10,2)")
    @TableField(value = "submit_score")
    private Double submitScore;

    @ColumnInfo(comment = "评语", type = "text")
    @TableField(value = "submit_remark")
    private String submitRemark;

    @ColumnInfo(comment = "逻辑删除", type = "int(11)")
    @TableField(value = "submit_delete")
    private Integer submitDelete;

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @ColumnInfo(comment = "批改时间", type = "timestamp")
    @TableField(value = "check_time")
    private Date checkTime;

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @ColumnInfo(comment = "提交时间", type = "timestamp")
    @TableField(value = "insert_time", fill = FieldFill.INSERT)
    private Date insertTime;

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @ColumnInfo(comment = "创建时间", type = "timestamp")
    @TableField(value = "create_time", fill = FieldFill.INSERT)
    private Date createTime;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getZuoyeId() {
        return zuoyeId;
    }

    public void setZuoyeId(Integer zuoyeId) {
        this.zuoyeId = zuoyeId;
    }

    public Integer getYonghuId() {
        return yonghuId;
    }

    public void setYonghuId(Integer yonghuId) {
        this.yonghuId = yonghuId;
    }

    public String getSubmitFile() {
        return submitFile;
    }

    public void setSubmitFile(String submitFile) {
        this.submitFile = submitFile;
    }

    public String getSubmitContent() {
        return submitContent;
    }

    public void setSubmitContent(String submitContent) {
        this.submitContent = submitContent;
    }

    public String getSubmitStatus() {
        return submitStatus;
    }

    public void setSubmitStatus(String submitStatus) {
        this.submitStatus = submitStatus;
    }

    public String getAnswerSnapshot() {
        return answerSnapshot;
    }

    public void setAnswerSnapshot(String answerSnapshot) {
        this.answerSnapshot = answerSnapshot;
    }

    public String getQuestionSnapshot() {
        return questionSnapshot;
    }

    public void setQuestionSnapshot(String questionSnapshot) {
        this.questionSnapshot = questionSnapshot;
    }

    public Double getAutoScore() {
        return autoScore;
    }

    public void setAutoScore(Double autoScore) {
        this.autoScore = autoScore;
    }

    public Double getSubmitScore() {
        return submitScore;
    }

    public void setSubmitScore(Double submitScore) {
        this.submitScore = submitScore;
    }

    public String getSubmitRemark() {
        return submitRemark;
    }

    public void setSubmitRemark(String submitRemark) {
        this.submitRemark = submitRemark;
    }

    public Integer getSubmitDelete() {
        return submitDelete;
    }

    public void setSubmitDelete(Integer submitDelete) {
        this.submitDelete = submitDelete;
    }

    public Date getCheckTime() {
        return checkTime;
    }

    public void setCheckTime(Date checkTime) {
        this.checkTime = checkTime;
    }

    public Date getInsertTime() {
        return insertTime;
    }

    public void setInsertTime(Date insertTime) {
        this.insertTime = insertTime;
    }

    public Date getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }
}
