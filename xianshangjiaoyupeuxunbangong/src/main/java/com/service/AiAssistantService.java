package com.service;

import com.utils.PageUtils;

import java.util.List;
import java.util.Map;

public interface AiAssistantService {
    Map<String, Object> createSession(Integer userId, String userTable, String role, Map<String, Object> params);
    PageUtils sessionPage(Integer userId, String userTable, Map<String, Object> params);
    PageUtils messagePage(Integer userId, String userTable, Integer sessionId, int page, int limit);
    Map<String, Object> sendMessage(Integer userId, String userTable, String role, Map<String, Object> params);
    List<String> recommendQuestions(String userTable, String bizScene, Integer courseId, Integer chapterId);
    void deleteSession(Integer userId, String userTable, Integer sessionId);
}
