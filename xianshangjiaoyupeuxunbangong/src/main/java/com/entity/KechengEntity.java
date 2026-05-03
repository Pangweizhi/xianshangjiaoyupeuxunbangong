package com.entity;

import com.annotation.ColumnInfo;
import javax.validation.constraints.*;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.lang.reflect.InvocationTargetException;
import java.io.Serializable;
import java.util.*;
import org.apache.tools.ant.util.DateUtils;
import org.springframework.format.annotation.DateTimeFormat;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.commons.beanutils.BeanUtils;
import com.baomidou.mybatisplus.annotations.TableField;
import com.baomidou.mybatisplus.annotations.TableId;
import com.baomidou.mybatisplus.annotations.TableName;
import com.baomidou.mybatisplus.enums.IdType;
import com.baomidou.mybatisplus.enums.FieldFill;
import com.utils.DateUtil;


/**
 * 课程信息
 *
 * @author 
 * @email
 */
@TableName("kecheng")
public class KechengEntity<T> implements Serializable {
    private static final long serialVersionUID = 1L;


	public KechengEntity() {

	}

	public KechengEntity(T t) {
		try {
			BeanUtils.copyProperties(this, t);
		} catch (IllegalAccessException | InvocationTargetException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}


    /**
     * 主键
     */
    @TableId(type = IdType.AUTO)
    @ColumnInfo(comment="主键",type="int(11)")
    @TableField(value = "id")

    private Integer id;


    /**
     * 课程标题
     */
    @ColumnInfo(comment="课程标题",type="varchar(200)")
    @TableField(value = "kecheng_name")

    private String kechengName;


    /**
     * 课程照片
     */
    @ColumnInfo(comment="课程照片",type="varchar(200)")
    @TableField(value = "kecheng_photo")

    private String kechengPhoto;


    /**
     * 课程类型
     */
    @ColumnInfo(comment="课程类型",type="int(11)")
    @TableField(value = "kecheng_types")

    private Integer kechengTypes;


    /**
     * 课程时长
     */
    @ColumnInfo(comment="课程时长",type="int(11)")
    @TableField(value = "kecheng_shichang")

    private Integer kechengShichang;


    /**
     * 开始时间
     */
    @JsonFormat(locale="zh", timezone="GMT+8", pattern="yyyy-MM-dd HH:mm:ss")
	@DateTimeFormat
    @ColumnInfo(comment="开始时间",type="timestamp")
    @TableField(value = "kecheng_time")

    private Date kechengTime;


    /**
     * 缁撴潫鏃堕棿
     */
    @JsonFormat(locale="zh", timezone="GMT+8", pattern="yyyy-MM-dd HH:mm:ss")
	@DateTimeFormat
    @ColumnInfo(comment="缁撴潫鏃堕棿",type="timestamp")
    @TableField(value = "kecheng_end_time")

    private Date kechengEndTime;


    /**
     * 班级
     */
    @ColumnInfo(comment="班级",type="int(11)")
    @TableField(value = "banji_types")

    private Integer banjiTypes;


    /**
     * 教师
     */
    @ColumnInfo(comment="教师",type="int(11)")
    @TableField(value = "jiaoshi_id")

    private Integer jiaoshiId;

    /**
     * 课程审核状态
     */
    @ColumnInfo(comment="课程审核状态",type="varchar(50)")
    @TableField(value = "course_status")
    private String courseStatus;

    /**
     * 课程学分
     */
    @ColumnInfo(comment="课程学分",type="int(11)")
    @TableField(value = "credit_score")
    private Integer creditScore;

    /**
     * 审核备注
     */
    @ColumnInfo(comment="审核备注",type="varchar(255)")
    @TableField(value = "review_remark")
    private String reviewRemark;

    /**
     * 审核时间
     */
    @JsonFormat(locale="zh", timezone="GMT+8", pattern="yyyy-MM-dd HH:mm:ss")
	@DateTimeFormat
    @ColumnInfo(comment="审核时间",type="timestamp")
    @TableField(value = "review_time")
    private Date reviewTime;

    /**
     * 审核管理员
     */
    @ColumnInfo(comment="审核管理员",type="bigint(20)")
    @TableField(value = "review_admin_id")
    private Long reviewAdminId;


    /**
     * 逻辑删除
     */
    @ColumnInfo(comment="逻辑删除",type="int(11)")
    @TableField(value = "kecheng_delete")

    private Integer kechengDelete;


    /**
     * 课程详情
     */
    @ColumnInfo(comment="课程详情",type="text")
    @TableField(value = "kecheng_content")

    private String kechengContent;


    /**
     * 创建时间
     */
    @JsonFormat(locale="zh", timezone="GMT+8", pattern="yyyy-MM-dd HH:mm:ss")
	@DateTimeFormat
    @ColumnInfo(comment="创建时间",type="timestamp")
    @TableField(value = "create_time",fill = FieldFill.INSERT)

    private Date createTime;


    /**
	 * 获取：主键
	 */
    public Integer getId() {
        return id;
    }
    /**
	 * 设置：主键
	 */

    public void setId(Integer id) {
        this.id = id;
    }
    /**
	 * 获取：课程标题
	 */
    public String getKechengName() {
        return kechengName;
    }
    /**
	 * 设置：课程标题
	 */

    public void setKechengName(String kechengName) {
        this.kechengName = kechengName;
    }
    /**
	 * 获取：课程照片
	 */
    public String getKechengPhoto() {
        return kechengPhoto;
    }
    /**
	 * 设置：课程照片
	 */

    public void setKechengPhoto(String kechengPhoto) {
        this.kechengPhoto = kechengPhoto;
    }
    /**
	 * 获取：课程类型
	 */
    public Integer getKechengTypes() {
        return kechengTypes;
    }
    /**
	 * 设置：课程类型
	 */

    public void setKechengTypes(Integer kechengTypes) {
        this.kechengTypes = kechengTypes;
    }
    /**
	 * 获取：课程时长
	 */
    public Integer getKechengShichang() {
        return kechengShichang;
    }
    /**
	 * 设置：课程时长
	 */

    public void setKechengShichang(Integer kechengShichang) {
        this.kechengShichang = kechengShichang;
    }
    /**
	 * 获取：开始时间
	 */
    public Date getKechengTime() {
        return kechengTime;
    }
    /**
	 * 设置：开始时间
	 */

    public void setKechengTime(Date kechengTime) {
        this.kechengTime = kechengTime;
    }
    /**
	 * 鑾峰彇锛氱粨鏉熸椂闂?
	 */
    public Date getKechengEndTime() {
        return kechengEndTime;
    }
    /**
	 * 璁剧疆锛氱粨鏉熸椂闂?
	 */

    public void setKechengEndTime(Date kechengEndTime) {
        this.kechengEndTime = kechengEndTime;
    }
    /**
	 * 获取：班级
	 */
    public Integer getBanjiTypes() {
        return banjiTypes;
    }
    /**
	 * 设置：班级
	 */

    public void setBanjiTypes(Integer banjiTypes) {
        this.banjiTypes = banjiTypes;
    }
    /**
	 * 获取：教师
	 */
    public Integer getJiaoshiId() {
        return jiaoshiId;
    }
    /**
	 * 设置：教师
	 */

    public void setJiaoshiId(Integer jiaoshiId) {
        this.jiaoshiId = jiaoshiId;
    }
    /**
	 * 获取：课程审核状态
	 */
    public String getCourseStatus() {
        return courseStatus;
    }
    /**
	 * 设置：课程审核状态
	 */
    public void setCourseStatus(String courseStatus) {
        this.courseStatus = courseStatus;
    }
    /**
	 * 获取：课程学分
	 */
    public Integer getCreditScore() {
        return creditScore;
    }
    /**
	 * 设置：课程学分
	 */
    public void setCreditScore(Integer creditScore) {
        this.creditScore = creditScore;
    }
    /**
	 * 获取：审核备注
	 */
    public String getReviewRemark() {
        return reviewRemark;
    }
    /**
	 * 设置：审核备注
	 */
    public void setReviewRemark(String reviewRemark) {
        this.reviewRemark = reviewRemark;
    }
    /**
	 * 获取：审核时间
	 */
    public Date getReviewTime() {
        return reviewTime;
    }
    /**
	 * 设置：审核时间
	 */
    public void setReviewTime(Date reviewTime) {
        this.reviewTime = reviewTime;
    }
    /**
	 * 获取：审核管理员
	 */
    public Long getReviewAdminId() {
        return reviewAdminId;
    }
    /**
	 * 设置：审核管理员
	 */
    public void setReviewAdminId(Long reviewAdminId) {
        this.reviewAdminId = reviewAdminId;
    }
    /**
	 * 获取：逻辑删除
	 */
    public Integer getKechengDelete() {
        return kechengDelete;
    }
    /**
	 * 设置：逻辑删除
	 */

    public void setKechengDelete(Integer kechengDelete) {
        this.kechengDelete = kechengDelete;
    }
    /**
	 * 获取：课程详情
	 */
    public String getKechengContent() {
        return kechengContent;
    }
    /**
	 * 设置：课程详情
	 */

    public void setKechengContent(String kechengContent) {
        this.kechengContent = kechengContent;
    }
    /**
	 * 获取：创建时间
	 */
    public Date getCreateTime() {
        return createTime;
    }
    /**
	 * 设置：创建时间
	 */

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }

    @Override
    public String toString() {
        return "Kecheng{" +
            ", id=" + id +
            ", kechengName=" + kechengName +
            ", kechengPhoto=" + kechengPhoto +
            ", kechengTypes=" + kechengTypes +
            ", kechengShichang=" + kechengShichang +
            ", kechengTime=" + DateUtil.convertString(kechengTime,"yyyy-MM-dd") +
            ", kechengEndTime=" + DateUtil.convertString(kechengEndTime,"yyyy-MM-dd") +
            ", banjiTypes=" + banjiTypes +
            ", jiaoshiId=" + jiaoshiId +
            ", courseStatus=" + courseStatus +
            ", creditScore=" + creditScore +
            ", reviewRemark=" + reviewRemark +
            ", reviewTime=" + DateUtil.convertString(reviewTime,"yyyy-MM-dd") +
            ", reviewAdminId=" + reviewAdminId +
            ", kechengDelete=" + kechengDelete +
            ", kechengContent=" + kechengContent +
            ", createTime=" + DateUtil.convertString(createTime,"yyyy-MM-dd") +
        "}";
    }
}
