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

@TableName("course_resource")
public class CourseResourceEntity<T> implements Serializable {
    private static final long serialVersionUID = 1L;

    public CourseResourceEntity() {
    }

    public CourseResourceEntity(T t) {
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
    @TableField(value = "resource_name")
    private String resourceName;
    @TableField(value = "resource_type")
    private String resourceType;
    @TableField(value = "resource_url")
    private String resourceUrl;
    @TableField(value = "cover_url")
    private String coverUrl;
    @TableField(value = "duration_seconds")
    private Integer durationSeconds;
    @TableField(value = "resource_status")
    private String resourceStatus;
    @TableField(value = "review_remark")
    private String reviewRemark;
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "review_time")
    private Date reviewTime;
    @TableField(value = "review_admin_id")
    private Long reviewAdminId;
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
    public String getResourceName() { return resourceName; }
    public void setResourceName(String resourceName) { this.resourceName = resourceName; }
    public String getResourceType() { return resourceType; }
    public void setResourceType(String resourceType) { this.resourceType = resourceType; }
    public String getResourceUrl() { return resourceUrl; }
    public void setResourceUrl(String resourceUrl) { this.resourceUrl = resourceUrl; }
    public String getCoverUrl() { return coverUrl; }
    public void setCoverUrl(String coverUrl) { this.coverUrl = coverUrl; }
    public Integer getDurationSeconds() { return durationSeconds; }
    public void setDurationSeconds(Integer durationSeconds) { this.durationSeconds = durationSeconds; }
    public String getResourceStatus() { return resourceStatus; }
    public void setResourceStatus(String resourceStatus) { this.resourceStatus = resourceStatus; }
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

