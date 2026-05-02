package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.ExamQuestionEntity;
import com.utils.PageUtils;

import java.util.Map;

public interface ExamQuestionService extends IService<ExamQuestionEntity> {
    PageUtils queryPage(Map<String, Object> params);
}
