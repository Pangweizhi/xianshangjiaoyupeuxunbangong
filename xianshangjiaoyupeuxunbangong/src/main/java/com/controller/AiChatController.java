package com.controller;

import com.service.AiAssistantService;
import com.utils.PageUtils;
import com.utils.R;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.Map;

@RestController
@Controller
@RequestMapping("/aiChat")
public class AiChatController {

    @Autowired
    private AiAssistantService aiAssistantService;

    @RequestMapping("/session/page")
    public R sessionPage(HttpServletRequest request) {
        Integer userId = currentUserId(request);
        String userTable = currentUserTable(request);
        Map<String, Object> params = buildPageParams(request);
        PageUtils page = aiAssistantService.sessionPage(userId, userTable, params);
        return R.ok().put("data", page);
    }

    @RequestMapping("/session/create")
    public R createSession(@RequestBody Map<String, Object> params, HttpServletRequest request) {
        return R.ok().put("data", aiAssistantService.createSession(
            currentUserId(request),
            currentUserTable(request),
            currentRole(request),
            params
        ));
    }

    @RequestMapping("/session/delete")
    public R deleteSession(@RequestBody Map<String, Object> params, HttpServletRequest request) {
        aiAssistantService.deleteSession(
            currentUserId(request),
            currentUserTable(request),
            intValue(params.get("sessionId"))
        );
        return R.ok();
    }

    @RequestMapping("/message/page")
    public R messagePage(HttpServletRequest request) {
        Integer sessionId = intValue(request.getParameter("sessionId"));
        int page = intValue(request.getParameter("page")) == null ? 1 : intValue(request.getParameter("page"));
        int limit = intValue(request.getParameter("limit")) == null ? 100 : intValue(request.getParameter("limit"));
        PageUtils result = aiAssistantService.messagePage(currentUserId(request), currentUserTable(request), sessionId, page, limit);
        return R.ok().put("data", result);
    }

    @RequestMapping("/message/send")
    public R sendMessage(@RequestBody Map<String, Object> params, HttpServletRequest request) {
        try {
            return R.ok().put("data", aiAssistantService.sendMessage(
                currentUserId(request),
                currentUserTable(request),
                currentRole(request),
                params
            ));
        } catch (IllegalArgumentException e) {
            return R.error(511, e.getMessage());
        }
    }

    @RequestMapping("/recommendQuestions")
    public R recommendQuestions(HttpServletRequest request) {
        String bizScene = request.getParameter("bizScene");
        Integer courseId = intValue(request.getParameter("courseId"));
        Integer chapterId = intValue(request.getParameter("chapterId"));
        return R.ok().put("data", aiAssistantService.recommendQuestions(
            currentUserTable(request),
            bizScene,
            courseId,
            chapterId
        ));
    }

    private Integer currentUserId(HttpServletRequest request) {
        Object value = request.getSession().getAttribute("userId");
        return value == null ? null : Integer.valueOf(String.valueOf(value));
    }

    private String currentUserTable(HttpServletRequest request) {
        Object value = request.getSession().getAttribute("tableName");
        return value == null ? null : String.valueOf(value);
    }

    private String currentRole(HttpServletRequest request) {
        Object value = request.getSession().getAttribute("role");
        return value == null ? null : String.valueOf(value);
    }

    private Integer intValue(Object value) {
        if (value == null || String.valueOf(value).trim().length() == 0) {
            return null;
        }
        return Integer.valueOf(String.valueOf(value));
    }

    private Map<String, Object> buildPageParams(HttpServletRequest request) {
        Map<String, Object> params = new HashMap<String, Object>();
        params.put("page", request.getParameter("page") == null ? "1" : request.getParameter("page"));
        params.put("limit", request.getParameter("limit") == null ? "20" : request.getParameter("limit"));
        return params;
    }
}
