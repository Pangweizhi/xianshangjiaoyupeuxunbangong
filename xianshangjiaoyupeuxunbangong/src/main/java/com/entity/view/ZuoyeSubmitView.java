package com.entity.view;

import com.annotation.ColumnInfo;
import com.baomidou.mybatisplus.annotations.TableName;
import com.entity.ZuoyeSubmitEntity;

import java.io.Serializable;

/**
 * 作业提交视图
 */
@TableName("zuoye_submit")
public class ZuoyeSubmitView extends ZuoyeSubmitEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @ColumnInfo(comment="作业标题",type="varchar(200)")
    private String zuoyeName;

    @ColumnInfo(comment="学生姓名",type="varchar(200)")
    private String yonghuName;

    @ColumnInfo(comment="学生头像",type="varchar(200)")
    private String yonghuPhoto;

    @ColumnInfo(comment="教师姓名",type="varchar(200)")
    private String jiaoshiName;

    @ColumnInfo(comment="教师账号",type="varchar(200)")
    private String jiaoshiUuidNumber;

    public String getZuoyeName() {
        return zuoyeName;
    }

    public void setZuoyeName(String zuoyeName) {
        this.zuoyeName = zuoyeName;
    }

    public String getYonghuName() {
        return yonghuName;
    }

    public void setYonghuName(String yonghuName) {
        this.yonghuName = yonghuName;
    }

    public String getYonghuPhoto() {
        return yonghuPhoto;
    }

    public void setYonghuPhoto(String yonghuPhoto) {
        this.yonghuPhoto = yonghuPhoto;
    }

    public String getJiaoshiName() {
        return jiaoshiName;
    }

    public void setJiaoshiName(String jiaoshiName) {
        this.jiaoshiName = jiaoshiName;
    }

    public String getJiaoshiUuidNumber() {
        return jiaoshiUuidNumber;
    }

    public void setJiaoshiUuidNumber(String jiaoshiUuidNumber) {
        this.jiaoshiUuidNumber = jiaoshiUuidNumber;
    }
}
