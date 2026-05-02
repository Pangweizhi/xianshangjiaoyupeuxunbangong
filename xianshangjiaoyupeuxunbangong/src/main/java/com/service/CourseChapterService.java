package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.CourseChapterEntity;
import com.utils.PageUtils;

import java.util.Map;

public interface CourseChapterService extends IService<CourseChapterEntity> {
    PageUtils queryPage(Map<String, Object> params);
}

