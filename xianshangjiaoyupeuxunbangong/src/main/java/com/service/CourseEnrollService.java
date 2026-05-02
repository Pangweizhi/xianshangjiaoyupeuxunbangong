package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.CourseEnrollEntity;
import com.utils.PageUtils;

import java.util.Map;

public interface CourseEnrollService extends IService<CourseEnrollEntity> {
    PageUtils queryPage(Map<String, Object> params);
}

