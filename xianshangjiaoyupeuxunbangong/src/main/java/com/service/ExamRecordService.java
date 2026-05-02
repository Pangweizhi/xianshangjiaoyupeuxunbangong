package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.ExamRecordEntity;
import com.utils.PageUtils;

import java.util.Map;

public interface ExamRecordService extends IService<ExamRecordEntity> {
    PageUtils queryPage(Map<String, Object> params);
}
