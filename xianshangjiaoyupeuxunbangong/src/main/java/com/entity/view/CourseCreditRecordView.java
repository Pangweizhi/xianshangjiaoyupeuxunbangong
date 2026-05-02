package com.entity.view;

import com.baomidou.mybatisplus.annotations.TableName;
import com.entity.CourseCreditRecordEntity;

import java.io.Serializable;

@TableName("course_credit_record")
public class CourseCreditRecordView extends CourseCreditRecordEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    private String kechengName;
    private String yonghuName;

    public String getKechengName() { return kechengName; }
    public void setKechengName(String kechengName) { this.kechengName = kechengName; }
    public String getYonghuName() { return yonghuName; }
    public void setYonghuName(String yonghuName) { this.yonghuName = yonghuName; }
}
