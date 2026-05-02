package com.entity.view;

import com.baomidou.mybatisplus.annotations.TableName;
import com.entity.CourseEnrollEntity;

import java.io.Serializable;

@TableName("course_enroll")
public class CourseEnrollView extends CourseEnrollEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    private String kechengName;
    private String kechengPhoto;
    private String courseStatus;
    private Integer creditScore;
    private String jiaoshiName;
    private String yonghuName;

    public String getKechengName() { return kechengName; }
    public void setKechengName(String kechengName) { this.kechengName = kechengName; }
    public String getKechengPhoto() { return kechengPhoto; }
    public void setKechengPhoto(String kechengPhoto) { this.kechengPhoto = kechengPhoto; }
    public String getCourseStatus() { return courseStatus; }
    public void setCourseStatus(String courseStatus) { this.courseStatus = courseStatus; }
    public Integer getCreditScore() { return creditScore; }
    public void setCreditScore(Integer creditScore) { this.creditScore = creditScore; }
    public String getJiaoshiName() { return jiaoshiName; }
    public void setJiaoshiName(String jiaoshiName) { this.jiaoshiName = jiaoshiName; }
    public String getYonghuName() { return yonghuName; }
    public void setYonghuName(String yonghuName) { this.yonghuName = yonghuName; }
}

