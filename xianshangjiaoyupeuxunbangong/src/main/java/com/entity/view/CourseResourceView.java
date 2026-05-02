package com.entity.view;

import com.baomidou.mybatisplus.annotations.TableName;
import com.entity.CourseResourceEntity;

import java.io.Serializable;

@TableName("course_resource")
public class CourseResourceView extends CourseResourceEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    private String kechengName;
    private String chapterName;
    private String jiaoshiName;

    public String getKechengName() { return kechengName; }
    public void setKechengName(String kechengName) { this.kechengName = kechengName; }
    public String getChapterName() { return chapterName; }
    public void setChapterName(String chapterName) { this.chapterName = chapterName; }
    public String getJiaoshiName() { return jiaoshiName; }
    public void setJiaoshiName(String jiaoshiName) { this.jiaoshiName = jiaoshiName; }
}

