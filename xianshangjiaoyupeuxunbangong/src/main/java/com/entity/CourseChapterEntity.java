package com.entity;

import com.annotation.ColumnInfo;
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

@TableName("course_chapter")
public class CourseChapterEntity<T> implements Serializable {
    private static final long serialVersionUID = 1L;

    public CourseChapterEntity() {
    }

    public CourseChapterEntity(T t) {
        try {
            BeanUtils.copyProperties(this, t);
        } catch (IllegalAccessException | InvocationTargetException e) {
            e.printStackTrace();
        }
    }

    @TableId(type = IdType.AUTO)
    @TableField(value = "id")
    @ColumnInfo(comment = "主键", type = "int(11)")
    private Integer id;

    @TableField(value = "kecheng_id")
    @ColumnInfo(comment = "课程", type = "int(11)")
    private Integer kechengId;

    @TableField(value = "chapter_name")
    @ColumnInfo(comment = "章节名称", type = "varchar(200)")
    private String chapterName;

    @TableField(value = "chapter_sort")
    @ColumnInfo(comment = "章节排序", type = "int(11)")
    private Integer chapterSort;

    @TableField(value = "chapter_summary")
    @ColumnInfo(comment = "章节简介", type = "text")
    private String chapterSummary;

    @TableField(value = "chapter_status")
    @ColumnInfo(comment = "章节状态", type = "varchar(50)")
    private String chapterStatus;

    @TableField(value = "review_remark")
    @ColumnInfo(comment = "审核备注", type = "varchar(255)")
    private String reviewRemark;

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "review_time")
    @ColumnInfo(comment = "审核时间", type = "timestamp")
    private Date reviewTime;

    @TableField(value = "review_admin_id")
    @ColumnInfo(comment = "审核管理员", type = "bigint(20)")
    private Long reviewAdminId;

    @TableField(value = "is_deleted")
    @ColumnInfo(comment = "逻辑删除", type = "int(11)")
    private Integer isDeleted;

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "create_time", fill = FieldFill.INSERT)
    @ColumnInfo(comment = "创建时间", type = "timestamp")
    private Date createTime;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public Integer getKechengId() { return kechengId; }
    public void setKechengId(Integer kechengId) { this.kechengId = kechengId; }
    public String getChapterName() { return chapterName; }
    public void setChapterName(String chapterName) { this.chapterName = chapterName; }
    public Integer getChapterSort() { return chapterSort; }
    public void setChapterSort(Integer chapterSort) { this.chapterSort = chapterSort; }
    public String getChapterSummary() { return chapterSummary; }
    public void setChapterSummary(String chapterSummary) { this.chapterSummary = chapterSummary; }
    public String getChapterStatus() { return chapterStatus; }
    public void setChapterStatus(String chapterStatus) { this.chapterStatus = chapterStatus; }
    public String getReviewRemark() { return reviewRemark; }
    public void setReviewRemark(String reviewRemark) { this.reviewRemark = reviewRemark; }
    public Date getReviewTime() { return reviewTime; }
    public void setReviewTime(Date reviewTime) { this.reviewTime = reviewTime; }
    public Long getReviewAdminId() { return reviewAdminId; }
    public void setReviewAdminId(Long reviewAdminId) { this.reviewAdminId = reviewAdminId; }
    public Integer getIsDeleted() { return isDeleted; }
    public void setIsDeleted(Integer isDeleted) { this.isDeleted = isDeleted; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }
}

