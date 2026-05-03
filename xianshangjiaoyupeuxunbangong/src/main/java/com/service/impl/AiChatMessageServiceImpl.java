package com.service.impl;

import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.AiChatMessageDao;
import com.entity.AiChatMessageEntity;
import com.entity.AiChatSessionEntity;
import com.service.AiChatMessageService;
import com.service.AiChatSessionService;
import com.utils.PageUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;

@Service("aiChatMessageService")
@Transactional
public class AiChatMessageServiceImpl extends ServiceImpl<AiChatMessageDao, AiChatMessageEntity> implements AiChatMessageService {

    @Autowired
    private AiChatSessionService aiChatSessionService;

    @Override
    public PageUtils querySessionPage(Integer sessionId, Integer userId, String userTable, int page, int limit) {
        AiChatSessionEntity session = aiChatSessionService.selectOne(new EntityWrapper<AiChatSessionEntity>()
            .eq("id", sessionId)
            .eq("user_id", userId)
            .eq("user_table", userTable)
            .ne("status", "deleted"));
        if (session == null) {
            return new PageUtils(Collections.emptyList(), 0, limit, page);
        }
        int totalCount = this.selectCount(new EntityWrapper<AiChatMessageEntity>().eq("session_id", sessionId));
        List<AiChatMessageEntity> list = this.selectList(new EntityWrapper<AiChatMessageEntity>()
            .eq("session_id", sessionId)
            .orderBy("sort_no", true)
            .last("limit " + ((page - 1) * limit) + "," + limit));
        return new PageUtils(list, totalCount, limit, page);
    }
}
