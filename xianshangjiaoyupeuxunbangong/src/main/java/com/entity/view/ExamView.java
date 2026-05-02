package com.entity.view;

import com.baomidou.mybatisplus.annotations.TableName;
import com.entity.ExamEntity;
import org.apache.commons.beanutils.BeanUtils;

import java.io.Serializable;
import java.lang.reflect.InvocationTargetException;

@TableName("exam")
public class ExamView extends ExamEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    private String kechengName;
    private String chapterName;
    private String jiaoshiName;

    public ExamView() {
    }

    public ExamView(ExamEntity entity) {
        try {
            BeanUtils.copyProperties(this, entity);
        } catch (IllegalAccessException | InvocationTargetException e) {
            e.printStackTrace();
        }
    }

    public String getKechengName() { return kechengName; }
    public void setKechengName(String kechengName) { this.kechengName = kechengName; }
    public String getChapterName() { return chapterName; }
    public void setChapterName(String chapterName) { this.chapterName = chapterName; }
    public String getJiaoshiName() { return jiaoshiName; }
    public void setJiaoshiName(String jiaoshiName) { this.jiaoshiName = jiaoshiName; }
}
