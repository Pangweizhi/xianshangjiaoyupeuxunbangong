package com.entity;

import com.annotation.ColumnInfo;
import com.baomidou.mybatisplus.annotations.TableField;
import com.baomidou.mybatisplus.annotations.TableId;
import com.baomidou.mybatisplus.annotations.TableName;
import com.baomidou.mybatisplus.enums.FieldFill;
import com.baomidou.mybatisplus.enums.IdType;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.utils.DateUtil;
import org.apache.commons.beanutils.BeanUtils;
import org.springframework.format.annotation.DateTimeFormat;

import java.io.Serializable;
import java.lang.reflect.InvocationTargetException;
import java.util.Date;

/**
 * 作业
 */
@TableName("zuoye")
public class ZuoyeEntity<T> implements Serializable {
    private static final long serialVersionUID = 1L;

    public ZuoyeEntity() {
    }

    public ZuoyeEntity(T t) {
        try {
            BeanUtils.copyProperties(this, t);
        } catch (IllegalAccessException | InvocationTargetException e) {
            e.printStackTrace();
        }
    }

    @TableId(type = IdType.AUTO)
    @ColumnInfo(comment = "主键", type = "int(11)")
    @TableField(value = "id")
    private Integer id;

    @ColumnInfo(comment = "作业标题", type = "varchar(200)")
    @TableField(value = "zuoye_name")
    private String zuoyeName;

    @ColumnInfo(comment = "作业图片", type = "varchar(200)")
    @TableField(value = "zuoye_photo")
    private String zuoyePhoto;

    @ColumnInfo(comment = "作业类型", type = "int(11)")
    @TableField(value = "zuoye_types")
    private Integer zuoyeTypes;

    @ColumnInfo(comment = "作业附件", type = "varchar(200)")
    @TableField(value = "zuoye_file")
    private String zuoyeFile;

    @ColumnInfo(comment = "教师", type = "int(11)")
    @TableField(value = "jiaoshi_id")
    private Integer jiaoshiId;

    @ColumnInfo(comment = "课程", type = "int(11)")
    @TableField(value = "kecheng_id")
    private Integer kechengId;

    @ColumnInfo(comment = "章节", type = "int(11)")
    @TableField(value = "chapter_id")
    private Integer chapterId;

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @ColumnInfo(comment = "截止时间", type = "timestamp")
    @TableField(value = "deadline_time")
    private Date deadlineTime;

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @ColumnInfo(comment = "开始时间", type = "timestamp")
    @TableField(value = "start_time")
    private Date startTime;

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @ColumnInfo(comment = "结束时间", type = "timestamp")
    @TableField(value = "end_time")
    private Date endTime;

    @ColumnInfo(comment = "总分", type = "int(11)")
    @TableField(value = "score_total")
    private Integer scoreTotal;

    @ColumnInfo(comment = "发布状态", type = "varchar(50)")
    @TableField(value = "publish_status")
    private String publishStatus;

    @ColumnInfo(comment = "题目ID集合", type = "text")
    @TableField(value = "question_ids")
    private String questionIds;

    @ColumnInfo(comment = "作业说明", type = "text")
    @TableField(value = "zuoye_content")
    private String zuoyeContent;

    @ColumnInfo(comment = "逻辑删除", type = "int(11)")
    @TableField(value = "zuoye_delete")
    private Integer zuoyeDelete;

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @ColumnInfo(comment = "添加时间", type = "timestamp")
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

    public String getZuoyeName() {
        return zuoyeName;
    }

    public void setZuoyeName(String zuoyeName) {
        this.zuoyeName = zuoyeName;
    }

    public String getZuoyePhoto() {
        return zuoyePhoto;
    }

    public void setZuoyePhoto(String zuoyePhoto) {
        this.zuoyePhoto = zuoyePhoto;
    }

    public Integer getZuoyeTypes() {
        return zuoyeTypes;
    }

    public void setZuoyeTypes(Integer zuoyeTypes) {
        this.zuoyeTypes = zuoyeTypes;
    }

    public String getZuoyeFile() {
        return zuoyeFile;
    }

    public void setZuoyeFile(String zuoyeFile) {
        this.zuoyeFile = zuoyeFile;
    }

    public Integer getJiaoshiId() {
        return jiaoshiId;
    }

    public void setJiaoshiId(Integer jiaoshiId) {
        this.jiaoshiId = jiaoshiId;
    }

    public Integer getKechengId() {
        return kechengId;
    }

    public void setKechengId(Integer kechengId) {
        this.kechengId = kechengId;
    }

    public Integer getChapterId() {
        return chapterId;
    }

    public void setChapterId(Integer chapterId) {
        this.chapterId = chapterId;
    }

    public Date getDeadlineTime() {
        return deadlineTime;
    }

    public void setDeadlineTime(Date deadlineTime) {
        this.deadlineTime = deadlineTime;
    }

    public Date getStartTime() {
        return startTime;
    }

    public void setStartTime(Date startTime) {
        this.startTime = startTime;
    }

    public Date getEndTime() {
        return endTime;
    }

    public void setEndTime(Date endTime) {
        this.endTime = endTime;
    }

    public Integer getScoreTotal() {
        return scoreTotal;
    }

    public void setScoreTotal(Integer scoreTotal) {
        this.scoreTotal = scoreTotal;
    }

    public String getPublishStatus() {
        return publishStatus;
    }

    public void setPublishStatus(String publishStatus) {
        this.publishStatus = publishStatus;
    }

    public String getQuestionIds() {
        return questionIds;
    }

    public void setQuestionIds(String questionIds) {
        this.questionIds = questionIds;
    }

    public String getZuoyeContent() {
        return zuoyeContent;
    }

    public void setZuoyeContent(String zuoyeContent) {
        this.zuoyeContent = zuoyeContent;
    }

    public Integer getZuoyeDelete() {
        return zuoyeDelete;
    }

    public void setZuoyeDelete(Integer zuoyeDelete) {
        this.zuoyeDelete = zuoyeDelete;
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

    @Override
    public String toString() {
        return "Zuoye{" +
            "id=" + id +
            ", zuoyeName='" + zuoyeName + '\'' +
            ", zuoyePhoto='" + zuoyePhoto + '\'' +
            ", zuoyeTypes=" + zuoyeTypes +
            ", zuoyeFile='" + zuoyeFile + '\'' +
            ", jiaoshiId=" + jiaoshiId +
            ", kechengId=" + kechengId +
            ", chapterId=" + chapterId +
            ", deadlineTime=" + DateUtil.convertString(deadlineTime, "yyyy-MM-dd HH:mm:ss") +
            ", startTime=" + DateUtil.convertString(startTime, "yyyy-MM-dd HH:mm:ss") +
            ", endTime=" + DateUtil.convertString(endTime, "yyyy-MM-dd HH:mm:ss") +
            ", scoreTotal=" + scoreTotal +
            ", publishStatus='" + publishStatus + '\'' +
            ", questionIds='" + questionIds + '\'' +
            ", zuoyeContent='" + zuoyeContent + '\'' +
            ", zuoyeDelete=" + zuoyeDelete +
            ", insertTime=" + DateUtil.convertString(insertTime, "yyyy-MM-dd HH:mm:ss") +
            ", createTime=" + DateUtil.convertString(createTime, "yyyy-MM-dd HH:mm:ss") +
            '}';
    }
}
