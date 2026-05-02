package com.entity.view;

import com.baomidou.mybatisplus.annotations.TableName;
import com.entity.ExamRecordEntity;
import org.apache.commons.beanutils.BeanUtils;

import java.io.Serializable;
import java.lang.reflect.InvocationTargetException;

@TableName("exam_record")
public class ExamRecordView extends ExamRecordEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    private String examName;
    private String kechengName;
    private String yonghuName;
    private String jiaoshiName;

    public ExamRecordView() {
    }

    public ExamRecordView(ExamRecordEntity entity) {
        try {
            BeanUtils.copyProperties(this, entity);
        } catch (IllegalAccessException | InvocationTargetException e) {
            e.printStackTrace();
        }
    }

    public String getExamName() { return examName; }
    public void setExamName(String examName) { this.examName = examName; }
    public String getKechengName() { return kechengName; }
    public void setKechengName(String kechengName) { this.kechengName = kechengName; }
    public String getYonghuName() { return yonghuName; }
    public void setYonghuName(String yonghuName) { this.yonghuName = yonghuName; }
    public String getJiaoshiName() { return jiaoshiName; }
    public void setJiaoshiName(String jiaoshiName) { this.jiaoshiName = jiaoshiName; }
}
