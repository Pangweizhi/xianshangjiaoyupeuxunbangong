package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.ExamEntity;
import com.utils.PageUtils;

import java.util.Map;

public interface ExamService extends IService<ExamEntity> {
    PageUtils queryPage(Map<String, Object> params);
}
