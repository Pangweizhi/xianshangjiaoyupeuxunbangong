package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.CourseCreditRecordEntity;
import com.utils.PageUtils;

import java.util.Map;

public interface CourseCreditRecordService extends IService<CourseCreditRecordEntity> {
    PageUtils queryPage(Map<String, Object> params);
}

