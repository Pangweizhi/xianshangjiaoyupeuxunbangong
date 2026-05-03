package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.AiChatSessionEntity;
import com.utils.PageUtils;

import java.util.Map;

public interface AiChatSessionService extends IService<AiChatSessionEntity> {
    PageUtils queryUserPage(Map<String, Object> params, Integer userId, String userTable);
}
