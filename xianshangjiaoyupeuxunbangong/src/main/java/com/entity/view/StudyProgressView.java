package com.entity.view;

import com.baomidou.mybatisplus.annotations.TableName;
import com.entity.StudyProgressEntity;

import java.io.Serializable;

@TableName("study_progress")
public class StudyProgressView extends StudyProgressEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    private String kechengName;
    private String chapterName;
    private String resourceName;
    private String resourceType;
    private String yonghuName;

    public String getKechengName() { return kechengName; }
    public void setKechengName(String kechengName) { this.kechengName = kechengName; }
    public String getChapterName() { return chapterName; }
    public void setChapterName(String chapterName) { this.chapterName = chapterName; }
    public String getResourceName() { return resourceName; }
    public void setResourceName(String resourceName) { this.resourceName = resourceName; }
    public String getResourceType() { return resourceType; }
    public void setResourceType(String resourceType) { this.resourceType = resourceType; }
    public String getYonghuName() { return yonghuName; }
    public void setYonghuName(String yonghuName) { this.yonghuName = yonghuName; }
}

