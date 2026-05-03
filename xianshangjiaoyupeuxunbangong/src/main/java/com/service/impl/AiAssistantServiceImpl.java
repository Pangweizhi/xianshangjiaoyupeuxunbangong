package com.service.impl;

import com.alibaba.fastjson.JSONObject;
import com.baomidou.mybatisplus.mapper.EntityWrapper;
import com.baomidou.mybatisplus.mapper.Wrapper;
import com.entity.AiChatMessageEntity;
import com.entity.AiChatSessionEntity;
import com.entity.CourseChapterEntity;
import com.entity.ExamEntity;
import com.entity.ExamRecordEntity;
import com.entity.JiaoshiEntity;
import com.entity.KechengEntity;
import com.entity.YonghuEntity;
import com.entity.ZuoyeEntity;
import com.entity.ZuoyeSubmitEntity;
import com.service.AiAssistantService;
import com.service.AiChatMessageService;
import com.service.AiChatSessionService;
import com.service.AiModelGatewayService;
import com.service.CourseChapterService;
import com.service.CourseReportService;
import com.service.ExamRecordService;
import com.service.ExamService;
import com.service.JiaoshiService;
import com.service.KechengService;
import com.service.YonghuService;
import com.service.ZuoyeService;
import com.service.ZuoyeSubmitService;
import com.utils.PageUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service("aiAssistantService")
@Transactional
public class AiAssistantServiceImpl implements AiAssistantService {

    private static final int MAX_SESSION_COUNT = 50;
    private static final int MAX_MESSAGE_COUNT = 100;
    private static final int MAX_MODEL_HISTORY = 12;

    @Autowired
    private AiChatSessionService aiChatSessionService;
    @Autowired
    private AiChatMessageService aiChatMessageService;
    @Autowired
    private AiModelGatewayService aiModelGatewayService;
    @Autowired
    private KechengService kechengService;
    @Autowired
    private CourseChapterService courseChapterService;
    @Autowired
    private ZuoyeService zuoyeService;
    @Autowired
    private ZuoyeSubmitService zuoyeSubmitService;
    @Autowired
    private ExamService examService;
    @Autowired
    private ExamRecordService examRecordService;
    @Autowired
    private CourseReportService courseReportService;
    @Autowired
    private JiaoshiService jiaoshiService;
    @Autowired
    private YonghuService yonghuService;

    @Override
    public Map<String, Object> createSession(Integer userId, String userTable, String role, Map<String, Object> params) {
        AiChatSessionEntity session = new AiChatSessionEntity();
        Date now = new Date();
        session.setUserId(userId);
        session.setUserTable(userTable);
        session.setRoleType(role);
        session.setSessionTitle(defaultSessionTitle(stringValue(params.get("bizScene"))));
        session.setBizScene(stringValue(params.get("bizScene")));
        session.setCourseId(intValue(params.get("courseId")));
        session.setChapterId(intValue(params.get("chapterId")));
        session.setResourceId(intValue(params.get("resourceId")));
        session.setMessageCount(0);
        session.setLastMessageAt(now);
        session.setStatus("active");
        session.setCreateTime(now);
        session.setUpdateTime(now);
        aiChatSessionService.insert(session);
        trimSessions(userId, userTable);

        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("session", session);
        result.put("recommendQuestions", recommendQuestions(userTable, session.getBizScene(), session.getCourseId(), session.getChapterId()));
        return result;
    }

    @Override
    public PageUtils sessionPage(Integer userId, String userTable, Map<String, Object> params) {
        return aiChatSessionService.queryUserPage(params, userId, userTable);
    }

    @Override
    public PageUtils messagePage(Integer userId, String userTable, Integer sessionId, int page, int limit) {
        return aiChatMessageService.querySessionPage(sessionId, userId, userTable, page, limit);
    }

    @Override
    public Map<String, Object> sendMessage(Integer userId, String userTable, String role, Map<String, Object> params) {
        String content = stringValue(params.get("content"));
        if (StringUtils.isBlank(content)) {
            throw new IllegalArgumentException("请输入问题内容");
        }

        AiChatSessionEntity session = resolveSession(userId, userTable, role, params);
        Date now = new Date();
        String contextJson = buildContextJson(params, session);

        AiChatMessageEntity userMessage = buildMessage(session.getId(), userId, role, "user", "text", content, contextJson, nextSortNo(session.getId()), now);
        aiChatMessageService.insert(userMessage);

        String answer = buildAssistantReply(userId, userTable, role, session, content);
        AiChatMessageEntity assistantMessage = buildMessage(session.getId(), userId, role, "assistant", "text", answer, contextJson, nextSortNo(session.getId()), now);
        aiChatMessageService.insert(assistantMessage);

        if (StringUtils.startsWith(session.getSessionTitle(), "新会话")) {
            session.setSessionTitle(buildTitleFromContent(content));
        }
        session.setLastMessageAt(now);
        session.setUpdateTime(now);
        session.setMessageCount(aiChatMessageService.selectCount(new EntityWrapper<AiChatMessageEntity>().eq("session_id", session.getId())));
        aiChatSessionService.updateById(session);

        trimMessages(session.getId());
        trimSessions(userId, userTable);

        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("session", session);
        result.put("userMessage", userMessage);
        result.put("assistantMessage", assistantMessage);
        result.put("recommendQuestions", recommendQuestions(userTable, session.getBizScene(), session.getCourseId(), session.getChapterId()));
        return result;
    }

    @Override
    public List<String> recommendQuestions(String userTable, String bizScene, Integer courseId, Integer chapterId) {
        if ("jiaoshi".equals(userTable) || "users".equals(userTable)) {
            if ("course_manage".equals(bizScene)) {
                return Arrays.asList("如何给当前课程新增章节？", "如何为当前课程发布作业或考试？");
            }
            return Arrays.asList("我现在应该从哪里新增课程？", "如何查看本人的课程、作业和考试进度？");
        }
        if (courseId != null || chapterId != null || "course_learning".equals(bizScene)) {
            return Arrays.asList("帮我总结这一节内容", "这个章节的重点是什么？");
        }
        return Arrays.asList("作业在哪里查看？", "考试入口在哪？");
    }

    @Override
    public void deleteSession(Integer userId, String userTable, Integer sessionId) {
        AiChatSessionEntity session = aiChatSessionService.selectOne(new EntityWrapper<AiChatSessionEntity>()
            .eq("id", sessionId)
            .eq("user_id", userId)
            .eq("user_table", userTable)
            .ne("status", "deleted"));
        if (session == null) {
            return;
        }
        session.setStatus("deleted");
        session.setUpdateTime(new Date());
        aiChatSessionService.updateById(session);
    }

    private AiChatSessionEntity resolveSession(Integer userId, String userTable, String role, Map<String, Object> params) {
        Integer sessionId = intValue(params.get("sessionId"));
        if (sessionId == null) {
            return (AiChatSessionEntity) createSession(userId, userTable, role, params).get("session");
        }
        AiChatSessionEntity session = aiChatSessionService.selectOne(new EntityWrapper<AiChatSessionEntity>()
            .eq("id", sessionId)
            .eq("user_id", userId)
            .eq("user_table", userTable)
            .ne("status", "deleted"));
        if (session == null) {
            throw new IllegalArgumentException("会话不存在或无权访问");
        }
        return session;
    }

    private AiChatMessageEntity buildMessage(Integer sessionId, Integer userId, String role, String messageRole, String messageType, String content, String contextJson, Integer sortNo, Date now) {
        AiChatMessageEntity entity = new AiChatMessageEntity();
        entity.setSessionId(sessionId);
        entity.setUserId(userId);
        entity.setRoleType(role);
        entity.setMessageRole(messageRole);
        entity.setMessageType(messageType);
        entity.setContent(content);
        entity.setContextJson(contextJson);
        entity.setTokenEstimate(estimateTokens(content));
        entity.setSortNo(sortNo);
        entity.setCreateTime(now);
        return entity;
    }

    private Integer nextSortNo(Integer sessionId) {
        AiChatMessageEntity lastMessage = aiChatMessageService.selectOne(new EntityWrapper<AiChatMessageEntity>()
            .eq("session_id", sessionId)
            .orderBy("sort_no", false)
            .last("limit 1"));
        return lastMessage == null || lastMessage.getSortNo() == null ? 1 : lastMessage.getSortNo() + 1;
    }

    private void trimSessions(Integer userId, String userTable) {
        List<AiChatSessionEntity> sessions = aiChatSessionService.selectList(new EntityWrapper<AiChatSessionEntity>()
            .eq("user_id", userId)
            .eq("user_table", userTable)
            .ne("status", "deleted")
            .orderBy("last_message_at", false)
            .orderBy("id", false));
        if (sessions.size() <= MAX_SESSION_COUNT) {
            return;
        }
        for (int i = MAX_SESSION_COUNT; i < sessions.size(); i++) {
            AiChatSessionEntity session = sessions.get(i);
            session.setStatus("deleted");
            session.setUpdateTime(new Date());
            aiChatSessionService.updateById(session);
        }
    }

    private void trimMessages(Integer sessionId) {
        List<AiChatMessageEntity> messages = aiChatMessageService.selectList(new EntityWrapper<AiChatMessageEntity>()
            .eq("session_id", sessionId)
            .orderBy("sort_no", false));
        if (messages.size() <= MAX_MESSAGE_COUNT) {
            return;
        }
        List<Integer> deleteIds = new ArrayList<Integer>();
        for (int i = MAX_MESSAGE_COUNT; i < messages.size(); i++) {
            deleteIds.add(messages.get(i).getId());
        }
        if (!deleteIds.isEmpty()) {
            aiChatMessageService.deleteBatchIds(deleteIds);
        }
    }

    private String buildAssistantReply(Integer userId, String userTable, String role, AiChatSessionEntity session, String content) {
        String normalized = content == null ? "" : content.trim();
        if (!isRelevantQuestion(normalized, session)) {
            return "我当前只负责本系统内的课程学习、作业、考试、成绩和操作导航问题。你可以继续问我“作业在哪里查看”或“帮我总结当前课程重点”。";
        }

        String modelReply = buildModelReply(userId, userTable, role, session, normalized);
        if (StringUtils.isNotBlank(modelReply)) {
            return modelReply;
        }

        if (containsAny(normalized, "作业", "作业在哪", "作业入口")) {
            return buildHomeworkAnswer(userId, userTable, session);
        }
        if (containsAny(normalized, "考试", "考试入口", "试卷")) {
            return buildExamAnswer(userId, userTable, session);
        }
        if (containsAny(normalized, "成绩", "学分", "结课")) {
            return buildScoreAnswer(userId, userTable);
        }
        if (containsAny(normalized, "课程", "章节", "重点", "总结", "概念", "例子", "学习")) {
            return buildCourseAnswer(userId, userTable, session, normalized);
        }
        if (containsAny(normalized, "怎么", "哪里", "入口", "查看", "下载", "新增", "发布")) {
            return buildNavigationAnswer(userTable, session, normalized);
        }
        return buildGenericAnswer(userId, userTable, session);
    }

    private String buildModelReply(Integer userId, String userTable, String role, AiChatSessionEntity session, String content) {
        if (!aiModelGatewayService.isEnabled()) {
            return null;
        }
        List<Map<String, String>> messages = new ArrayList<Map<String, String>>();
        messages.add(chatMessage("system", buildSystemPrompt(userTable, role, session)));
        messages.add(chatMessage("system", buildBusinessContext(userId, userTable, session)));

        List<AiChatMessageEntity> history = aiChatMessageService.selectList(new EntityWrapper<AiChatMessageEntity>()
            .eq("session_id", session.getId())
            .orderBy("sort_no", false)
            .last("limit " + MAX_MODEL_HISTORY));
        Collections.reverse(history);
        for (AiChatMessageEntity item : history) {
            if (!"user".equals(item.getMessageRole()) && !"assistant".equals(item.getMessageRole())) {
                continue;
            }
            if (StringUtils.isBlank(item.getContent())) {
                continue;
            }
            messages.add(chatMessage(item.getMessageRole(), item.getContent()));
        }

        String reply = aiModelGatewayService.chat(messages);
        if (StringUtils.isBlank(reply)) {
            return null;
        }
        return reply.trim();
    }

    private Map<String, String> chatMessage(String role, String content) {
        Map<String, String> message = new LinkedHashMap<String, String>();
        message.put("role", role);
        message.put("content", content);
        return message;
    }

    private String buildSystemPrompt(String userTable, String role, AiChatSessionEntity session) {
        StringBuilder prompt = new StringBuilder();
        prompt.append("你是线上教育培训办公系统的智能问答助手。");
        prompt.append("你的回答必须聚焦当前系统内的课程学习、课程管理、作业、考试、成绩、学分和页面操作路径。");
        prompt.append("如果用户的问题与系统无关，必须礼貌拒答，并引导对方回到系统相关问题。");
        prompt.append("回答要简洁、准确、可执行，不要编造系统中不存在的入口或数据。");
        if ("jiaoshi".equals(userTable) || "users".equals(userTable)) {
            prompt.append("当前用户更偏教师/后台管理场景，优先给出后台菜单路径和管理建议。");
        } else {
            prompt.append("当前用户是学生，优先解释学习路径、课程内容、作业考试入口和成绩查看方法。");
        }
        if (StringUtils.isNotBlank(session.getBizScene())) {
            prompt.append("当前业务场景为：").append(session.getBizScene()).append("。");
        }
        if (StringUtils.isNotBlank(role)) {
            prompt.append("当前角色标识为：").append(role).append("。");
        }
        return prompt.toString();
    }

    private String buildBusinessContext(Integer userId, String userTable, AiChatSessionEntity session) {
        StringBuilder context = new StringBuilder();
        context.append("以下是当前系统上下文，请仅在此范围内回答：");

        if ("jiaoshi".equals(userTable)) {
            JiaoshiEntity teacher = jiaoshiService.selectById(userId);
            int courseCount = kechengService.selectCount(new EntityWrapper<KechengEntity>().eq("jiaoshi_id", userId));
            int homeworkCount = zuoyeService.selectCount(new EntityWrapper<ZuoyeEntity>().eq("jiaoshi_id", userId).eq("zuoye_delete", 1));
            int examCount = examService.selectCount(new EntityWrapper<ExamEntity>().eq("jiaoshi_id", userId).eq("is_deleted", 1));
            context.append("当前用户是教师。");
            if (teacher != null) {
                context.append("教师姓名：").append(teacher.getJiaoshiName()).append("。");
            }
            context.append("名下课程数：").append(courseCount)
                .append("；作业数：").append(homeworkCount)
                .append("；考试数：").append(examCount).append("。");
        } else if ("yonghu".equals(userTable)) {
            YonghuEntity student = yonghuService.selectById(userId);
            int submitCount = zuoyeSubmitService.selectCount(new EntityWrapper<ZuoyeSubmitEntity>().eq("yonghu_id", userId).eq("submit_delete", 1));
            int examRecordCount = examRecordService.selectCount(new EntityWrapper<ExamRecordEntity>()
                .eq("yonghu_id", userId)
                .notIn("record_status", Arrays.asList("reset", "voided")));
            context.append("当前用户是学生。");
            if (student != null) {
                context.append("学生姓名：").append(student.getYonghuName()).append("。");
            }
            context.append("作业提交记录数：").append(submitCount)
                .append("；考试记录数：").append(examRecordCount).append("。");
        } else {
            context.append("当前用户位于后台管理侧。");
        }

        KechengEntity course = session.getCourseId() == null ? null : kechengService.selectById(session.getCourseId());
        CourseChapterEntity chapter = session.getChapterId() == null ? null : courseChapterService.selectById(session.getChapterId());
        if (course != null) {
            context.append("当前课程：").append(course.getKechengName()).append("。");
            if (StringUtils.isNotBlank(course.getKechengContent())) {
                context.append("课程简介：").append(truncatePlain(course.getKechengContent(), 180)).append("。");
            }
        }
        if (chapter != null) {
            context.append("当前章节：").append(chapter.getChapterName()).append("。");
            if (StringUtils.isNotBlank(chapter.getChapterSummary())) {
                context.append("章节摘要：").append(truncatePlain(chapter.getChapterSummary(), 180)).append("。");
            }
        }
        context.append("如果用户询问操作路径，请优先回答系统中的菜单入口；如果用户询问课程重点，可结合课程简介和章节摘要总结，但不要虚构未提供的知识细节。");
        return context.toString();
    }

    private String buildHomeworkAnswer(Integer userId, String userTable, AiChatSessionEntity session) {
        if ("jiaoshi".equals(userTable) || "users".equals(userTable)) {
            int homeworkCount = zuoyeService.selectCount(new EntityWrapper<ZuoyeEntity>()
                .eq("jiaoshi_id", userId)
                .eq("zuoye_delete", 1));
            return "你当前可在后台左侧“作业管理”中发布和维护作业。系统中你名下共有 " + homeworkCount + " 条作业记录，如需查看提交情况，可进入“提交记录”或“作业管理”中的对应课程进行处理。";
        }
        Wrapper<ZuoyeEntity> wrapper = new EntityWrapper<ZuoyeEntity>()
            .eq("zuoye_delete", 1);
        if (session.getCourseId() != null) {
            wrapper.eq("kecheng_id", session.getCourseId());
        }
        int homeworkCount = zuoyeService.selectCount(wrapper);
        int submitCount = zuoyeSubmitService.selectCount(new EntityWrapper<ZuoyeSubmitEntity>()
            .eq("yonghu_id", userId)
            .eq("submit_delete", 1));
        return "你可以在学生端顶部导航“作业”中查看老师发布的作业。"
            + (session.getCourseId() != null ? "当前课程下已发布作业约 " + homeworkCount + " 条，" : "")
            + "你当前已有 " + submitCount + " 条提交记录。";
    }

    private String buildExamAnswer(Integer userId, String userTable, AiChatSessionEntity session) {
        if ("jiaoshi".equals(userTable) || "users".equals(userTable)) {
            int examCount = examService.selectCount(new EntityWrapper<ExamEntity>()
                .eq("jiaoshi_id", userId)
                .eq("is_deleted", 1));
            return "你可以在后台左侧“考试管理”中发布考试，在“题库管理”中维护题目，在“阅卷管理”中处理学生答卷。当前你名下共有 " + examCount + " 场考试。";
        }
        Wrapper<ExamEntity> examWrapper = new EntityWrapper<ExamEntity>()
            .eq("is_deleted", 1);
        if (session.getCourseId() != null) {
            examWrapper.eq("kecheng_id", session.getCourseId());
        }
        int examCount = examService.selectCount(examWrapper);
        int recordCount = examRecordService.selectCount(new EntityWrapper<ExamRecordEntity>()
            .eq("yonghu_id", userId)
            .notIn("record_status", Arrays.asList("reset", "voided")));
        return "你可以在学生端顶部导航“考试”中进入考试列表和答题页面。"
            + (session.getCourseId() != null ? "当前课程下可见考试约 " + examCount + " 场，" : "")
            + "你当前已有 " + recordCount + " 条考试记录。";
    }

    private String buildScoreAnswer(Integer userId, String userTable) {
        if ("jiaoshi".equals(userTable) || "users".equals(userTable)) {
            Map<String, Object> overview = courseReportService.buildOverview("教师", userId);
            Map<String, Object> summary = safeMap(overview.get("summary"));
            return "你可以在后台仪表盘查看课程进度、作业均分、考试均分、结课人数和学分发放汇总。当前统计课程数为 "
                + safeInt(summary.get("courseCount")) + "，结课人数为 " + safeInt(summary.get("finishedCount")) + "。";
        }
        Map<String, Object> summaryData = courseReportService.buildStudentSummary(userId);
        Map<String, Object> summary = safeMap(summaryData.get("summary"));
        return "你可以在学生端“我的成绩”页面查看课程维度成绩、结课状态和学分结果。当前你已结课 "
            + safeInt(summary.get("finishedCount")) + " 门课程，已发放学分课程 "
            + safeInt(summary.get("grantedCreditCount")) + " 门。";
    }

    private String buildCourseAnswer(Integer userId, String userTable, AiChatSessionEntity session, String content) {
        KechengEntity course = session.getCourseId() == null ? null : kechengService.selectById(session.getCourseId());
        CourseChapterEntity chapter = session.getChapterId() == null ? null : courseChapterService.selectById(session.getChapterId());
        if ("jiaoshi".equals(userTable) || "users".equals(userTable)) {
            int courseCount = kechengService.selectCount(new EntityWrapper<KechengEntity>().eq("jiaoshi_id", userId));
            return "你当前主要可以围绕课程结构、章节安排、作业考试发布流程向我提问。"
                + (course != null ? "当前上下文课程是《" + course.getKechengName() + "》。" : "")
                + "你名下共有 " + courseCount + " 门课程。";
        }
        StringBuilder builder = new StringBuilder("我可以先基于当前系统里的课程与章节信息帮助你梳理学习重点。");
        if (course != null) {
            builder.append("当前课程是《").append(course.getKechengName()).append("》");
            if (StringUtils.isNotBlank(course.getKechengContent())) {
                builder.append("，课程简介为：").append(truncatePlain(course.getKechengContent(), 90));
            }
            builder.append("。");
        }
        if (chapter != null) {
            builder.append("当前章节是“").append(chapter.getChapterName()).append("”");
            if (StringUtils.isNotBlank(chapter.getChapterSummary())) {
                builder.append("，章节摘要为：").append(truncatePlain(chapter.getChapterSummary(), 90));
            }
            builder.append("。");
        }
        if (containsAny(content, "例子", "举例")) {
            builder.append("如果你希望我进一步举例，可以继续告诉我具体概念名或当前章节名。");
        } else if (containsAny(content, "总结", "重点")) {
            builder.append("你也可以继续追问“这一节最容易出错的点是什么”。");
        } else {
            builder.append("你可以继续问我“帮我总结这一节内容”或“这个概念是什么意思”。");
        }
        return builder.toString();
    }

    private String buildNavigationAnswer(String userTable, AiChatSessionEntity session, String content) {
        if ("jiaoshi".equals(userTable) || "users".equals(userTable)) {
            if (containsAny(content, "新增课程", "新建课程", "课程")) {
                return "新增课程请进入后台左侧“课程管理”。创建课程后，再到“章节管理”“资源管理”“作业管理”“考试管理”补齐教学内容。";
            }
            if (containsAny(content, "章节")) {
                return "新增或维护章节请进入后台左侧“章节管理”，先选择课程，再补充章节摘要和排序。";
            }
            if (containsAny(content, "作业")) {
                return "发布作业请进入后台左侧“作业管理”；如果还要查看学生提交情况，再进入“提交记录”。";
            }
            if (containsAny(content, "考试", "题目")) {
                return "考试相关操作分三步：先在“考试管理”创建考试，再到“题库管理”维护题目，最后在“阅卷管理”处理答卷。";
            }
            return "你可以从后台左侧菜单进入课程、章节、资源、作业、考试、题库和阅卷等模块。如果你告诉我具体要做哪一步，我可以直接给出操作路径。";
        }
        if (containsAny(content, "作业")) {
            return "查看作业请进入学生端顶部导航“作业”，点进具体作业后可查看要求并提交文件或文字内容。";
        }
        if (containsAny(content, "考试")) {
            return "考试入口在学生端顶部导航“考试”。进入后可以查看考试列表、开始考试、继续作答或查看历史成绩。";
        }
        if (containsAny(content, "ppt", "资料", "下载")) {
            return "课程资料通常可以在“课程”或“我的课程”进入具体课程详情后查看章节资源；旧资料也可以在顶部导航“备课”里查看。";
        }
        if (containsAny(content, "成绩")) {
            return "成绩查看入口在学生端顶部导航“我的成绩”，这里会按课程展示作业、考试、结课和学分结果。";
        }
        return "你可以从学生端顶部导航进入课程、我的课程、作业、考试、我的成绩、公告、论坛、备课和会议模块。";
    }

    private String buildGenericAnswer(Integer userId, String userTable, AiChatSessionEntity session) {
        if ("jiaoshi".equals(userTable) || "users".equals(userTable)) {
            JiaoshiEntity teacher = jiaoshiService.selectById(userId);
            return "当前你正在使用教师/后台侧问答助手。"
                + (teacher != null ? "姓名为 " + teacher.getJiaoshiName() + "。" : "")
                + "你可以继续问我课程创建、章节维护、作业发布、考试配置或阅卷流程。";
        }
        YonghuEntity student = yonghuService.selectById(userId);
        String name = student == null ? "同学" : student.getYonghuName();
        return name + "，我当前更适合回答课程学习、系统导航、作业、考试和成绩相关问题。"
            + (session.getCourseId() != null ? "你也可以继续围绕当前课程提问。" : "");
    }

    private boolean isRelevantQuestion(String content, AiChatSessionEntity session) {
        if (StringUtils.isBlank(content)) {
            return false;
        }
        if (session.getCourseId() != null || session.getChapterId() != null) {
            if (containsAny(content, "总结", "重点", "概念", "例子", "这一节", "这一章", "学习")) {
                return true;
            }
        }
        return containsAny(content,
            "课程", "章节", "资源", "视频", "ppt", "学习",
            "作业", "考试", "题库", "阅卷", "成绩", "学分", "结课",
            "系统", "入口", "哪里", "查看", "下载", "新增", "发布",
            "老师", "教师", "学生", "课程中心", "我的课程");
    }

    private boolean containsAny(String value, String... words) {
        if (value == null) {
            return false;
        }
        for (String word : words) {
            if (value.contains(word)) {
                return true;
            }
        }
        return false;
    }

    private String buildContextJson(Map<String, Object> params, AiChatSessionEntity session) {
        Map<String, Object> context = new LinkedHashMap<String, Object>();
        context.put("bizScene", stringValue(params.get("bizScene")));
        context.put("pageCode", stringValue(params.get("pageCode")));
        context.put("courseId", session.getCourseId());
        context.put("chapterId", session.getChapterId());
        context.put("resourceId", session.getResourceId());
        context.put("modelEnabled", aiModelGatewayService.isEnabled());
        return JSONObject.toJSONString(context);
    }

    private String defaultSessionTitle(String bizScene) {
        if ("course_learning".equals(bizScene)) {
            return "新会话-课程学习";
        }
        if ("course_manage".equals(bizScene)) {
            return "新会话-课程管理";
        }
        return "新会话-问AI";
    }

    private String buildTitleFromContent(String content) {
        String normalized = StringUtils.defaultString(content).replaceAll("\\s+", " ").trim();
        if (normalized.length() <= 16) {
            return normalized;
        }
        return normalized.substring(0, 16) + "...";
    }

    private String truncatePlain(String value, int maxLength) {
        String normalized = value.replaceAll("<[^>]+>", "").replaceAll("\\s+", " ").trim();
        if (normalized.length() <= maxLength) {
            return normalized;
        }
        return normalized.substring(0, maxLength) + "...";
    }

    private int estimateTokens(String content) {
        if (StringUtils.isBlank(content)) {
            return 0;
        }
        return Math.max(1, content.length() / 2);
    }

    private String stringValue(Object value) {
        return value == null ? null : String.valueOf(value).trim();
    }

    private Integer intValue(Object value) {
        if (value == null || StringUtils.isBlank(String.valueOf(value))) {
            return null;
        }
        return Integer.valueOf(String.valueOf(value));
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> safeMap(Object value) {
        return value instanceof Map ? (Map<String, Object>) value : Collections.<String, Object>emptyMap();
    }

    private int safeInt(Object value) {
        if (value == null) {
            return 0;
        }
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        return Integer.parseInt(String.valueOf(value));
    }
}
