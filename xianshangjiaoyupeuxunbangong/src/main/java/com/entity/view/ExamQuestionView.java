package com.entity.view;

import com.baomidou.mybatisplus.annotations.TableName;
import com.entity.ExamQuestionEntity;
import org.apache.commons.beanutils.BeanUtils;

import java.io.Serializable;
import java.lang.reflect.InvocationTargetException;

@TableName("exam_question")
public class ExamQuestionView extends ExamQuestionEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    private String examName;
    private String kechengName;

    public ExamQuestionView() {
    }

    public ExamQuestionView(ExamQuestionEntity entity) {
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
}
