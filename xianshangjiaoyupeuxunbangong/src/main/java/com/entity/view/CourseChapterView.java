package com.entity.view;

import com.baomidou.mybatisplus.annotations.TableName;
import com.entity.CourseChapterEntity;

import java.io.Serializable;

@TableName("course_chapter")
public class CourseChapterView extends CourseChapterEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    private String kechengName;
    private String jiaoshiName;

    public String getKechengName() { return kechengName; }
    public void setKechengName(String kechengName) { this.kechengName = kechengName; }
    public String getJiaoshiName() { return jiaoshiName; }
    public void setJiaoshiName(String jiaoshiName) { this.jiaoshiName = jiaoshiName; }
}

