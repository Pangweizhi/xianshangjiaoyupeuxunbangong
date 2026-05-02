package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.ZuoyeSubmitEntity;
import com.utils.PageUtils;

import java.util.Map;

/**
 * 作业提交 服务类
 */
public interface ZuoyeSubmitService extends IService<ZuoyeSubmitEntity> {

    PageUtils queryPage(Map<String, Object> params);
}
