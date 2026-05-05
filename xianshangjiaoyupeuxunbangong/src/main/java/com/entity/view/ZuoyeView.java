package com.entity.view;

import com.annotation.ColumnInfo;
import com.baomidou.mybatisplus.annotations.TableName;
import com.entity.ZuoyeEntity;
import org.apache.commons.beanutils.BeanUtils;

import java.io.Serializable;
import java.lang.reflect.InvocationTargetException;

/**
 * 作业视图
 */
@TableName("zuoye")
public class ZuoyeView extends ZuoyeEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @ColumnInfo(comment = "作业类型值", type = "varchar(200)")
    private String zuoyeValue;

    @ColumnInfo(comment = "课程标题", type = "varchar(200)")
    private String kechengName;

    @ColumnInfo(comment = "章节标题", type = "varchar(200)")
    private String chapterName;

    @ColumnInfo(comment = "教师姓名", type = "varchar(200)")
    private String jiaoshiName;

    @ColumnInfo(comment = "教师头像", type = "varchar(200)")
    private String jiaoshiPhoto;

    @ColumnInfo(comment = "教师身份证号", type = "varchar(200)")
    private String jiaoshiIdNumber;

    @ColumnInfo(comment = "教师电话", type = "varchar(200)")
    private String jiaoshiPhone;

    @ColumnInfo(comment = "教师邮箱", type = "varchar(200)")
    private String jiaoshiEmail;

    @ColumnInfo(comment = "教师删除状态", type = "int(11)")
    private Integer jiaoshiDelete;

    public ZuoyeView() {
    }

    public ZuoyeView(ZuoyeEntity entity) {
        try {
            BeanUtils.copyProperties(this, entity);
        } catch (IllegalAccessException | InvocationTargetException e) {
            e.printStackTrace();
        }
    }

    public String getZuoyeValue() {
        return zuoyeValue;
    }

    public void setZuoyeValue(String zuoyeValue) {
        this.zuoyeValue = zuoyeValue;
    }

    public String getKechengName() {
        return kechengName;
    }

    public void setKechengName(String kechengName) {
        this.kechengName = kechengName;
    }

    public String getChapterName() {
        return chapterName;
    }

    public void setChapterName(String chapterName) {
        this.chapterName = chapterName;
    }

    public String getJiaoshiName() {
        return jiaoshiName;
    }

    public void setJiaoshiName(String jiaoshiName) {
        this.jiaoshiName = jiaoshiName;
    }

    public String getJiaoshiPhoto() {
        return jiaoshiPhoto;
    }

    public void setJiaoshiPhoto(String jiaoshiPhoto) {
        this.jiaoshiPhoto = jiaoshiPhoto;
    }

    public String getJiaoshiIdNumber() {
        return jiaoshiIdNumber;
    }

    public void setJiaoshiIdNumber(String jiaoshiIdNumber) {
        this.jiaoshiIdNumber = jiaoshiIdNumber;
    }

    public String getJiaoshiPhone() {
        return jiaoshiPhone;
    }

    public void setJiaoshiPhone(String jiaoshiPhone) {
        this.jiaoshiPhone = jiaoshiPhone;
    }

    public String getJiaoshiEmail() {
        return jiaoshiEmail;
    }

    public void setJiaoshiEmail(String jiaoshiEmail) {
        this.jiaoshiEmail = jiaoshiEmail;
    }

    public Integer getJiaoshiDelete() {
        return jiaoshiDelete;
    }

    public void setJiaoshiDelete(Integer jiaoshiDelete) {
        this.jiaoshiDelete = jiaoshiDelete;
    }
}
