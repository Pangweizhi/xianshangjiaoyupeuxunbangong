package com.service.impl;

import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.baomidou.mybatisplus.mapper.Wrapper;
import com.baomidou.mybatisplus.plugins.Page;
import com.baomidou.mybatisplus.service.impl.ServiceImpl;
import com.dao.AiChatSessionDao;
import com.entity.AiChatSessionEntity;
import com.service.AiChatSessionService;
import com.utils.PageUtils;
import com.utils.Query;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service("aiChatSessionService")
@Transactional
public class AiChatSessionServiceImpl extends ServiceImpl<AiChatSessionDao, AiChatSessionEntity> implements AiChatSessionService {
    @Override
    public PageUtils queryUserPage(Map<String, Object> params, Integer userId, String userTable) {
        Page<AiChatSessionEntity> page = new Query<AiChatSessionEntity>(params).getPage();
        Wrapper<AiChatSessionEntity> wrapper = new EntityWrapper<AiChatSessionEntity>()
            .eq("user_id", userId)
            .eq("user_table", userTable)
            .ne("status", "deleted");
        wrapper.orderBy("last_message_at", false);
        wrapper.orderBy("id", false);
        Page<AiChatSessionEntity> result = this.selectPage(page, wrapper);
        return new PageUtils(result);
    }
}
