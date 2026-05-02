package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.CourseResourceEntity;
import com.utils.PageUtils;

import java.util.Map;

public interface CourseResourceService extends IService<CourseResourceEntity> {
    PageUtils queryPage(Map<String, Object> params);
}

