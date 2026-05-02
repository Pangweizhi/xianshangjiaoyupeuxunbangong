package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.StudyProgressEntity;
import com.utils.PageUtils;

import java.util.Map;

public interface StudyProgressService extends IService<StudyProgressEntity> {
    PageUtils queryPage(Map<String, Object> params);
}

