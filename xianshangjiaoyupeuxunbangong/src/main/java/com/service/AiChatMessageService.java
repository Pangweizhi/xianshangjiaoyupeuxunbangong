package com.service;

import com.baomidou.mybatisplus.service.IService;
import com.entity.AiChatMessageEntity;
import com.utils.PageUtils;

public interface AiChatMessageService extends IService<AiChatMessageEntity> {
    PageUtils querySessionPage(Integer sessionId, Integer userId, String userTable, int page, int limit);
}
