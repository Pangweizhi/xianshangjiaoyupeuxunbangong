package com.entity;

import com.baomidou.mybatisplus.annotations.TableField;
import com.baomidou.mybatisplus.annotations.TableId;
import com.baomidou.mybatisplus.annotations.TableName;
import com.baomidou.mybatisplus.enums.IdType;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.springframework.format.annotation.DateTimeFormat;

import java.io.Serializable;
import java.util.Date;

@TableName("ai_chat_message")
public class AiChatMessageEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    @TableField(value = "id")
    private Integer id;
    @TableField(value = "session_id")
    private Integer sessionId;
    @TableField(value = "user_id")
    private Integer userId;
    @TableField(value = "role_type")
    private String roleType;
    @TableField(value = "message_role")
    private String messageRole;
    @TableField(value = "message_type")
    private String messageType;
    @TableField(value = "content")
    private String content;
    @TableField(value = "tool_name")
    private String toolName;
    @TableField(value = "tool_request_json")
    private String toolRequestJson;
    @TableField(value = "tool_response_json")
    private String toolResponseJson;
    @TableField(value = "context_json")
    private String contextJson;
    @TableField(value = "token_estimate")
    private Integer tokenEstimate;
    @TableField(value = "sort_no")
    private Integer sortNo;
    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd HH:mm:ss")
    @DateTimeFormat
    @TableField(value = "create_time")
    private Date createTime;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public Integer getSessionId() { return sessionId; }
    public void setSessionId(Integer sessionId) { this.sessionId = sessionId; }
    public Integer getUserId() { return userId; }
    public void setUserId(Integer userId) { this.userId = userId; }
    public String getRoleType() { return roleType; }
    public void setRoleType(String roleType) { this.roleType = roleType; }
    public String getMessageRole() { return messageRole; }
    public void setMessageRole(String messageRole) { this.messageRole = messageRole; }
    public String getMessageType() { return messageType; }
    public void setMessageType(String messageType) { this.messageType = messageType; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getToolName() { return toolName; }
    public void setToolName(String toolName) { this.toolName = toolName; }
    public String getToolRequestJson() { return toolRequestJson; }
    public void setToolRequestJson(String toolRequestJson) { this.toolRequestJson = toolRequestJson; }
    public String getToolResponseJson() { return toolResponseJson; }
    public void setToolResponseJson(String toolResponseJson) { this.toolResponseJson = toolResponseJson; }
    public String getContextJson() { return contextJson; }
    public void setContextJson(String contextJson) { this.contextJson = contextJson; }
    public Integer getTokenEstimate() { return tokenEstimate; }
    public void setTokenEstimate(Integer tokenEstimate) { this.tokenEstimate = tokenEstimate; }
    public Integer getSortNo() { return sortNo; }
    public void setSortNo(Integer sortNo) { this.sortNo = sortNo; }
    public Date getCreateTime() { return createTime; }
    public void setCreateTime(Date createTime) { this.createTime = createTime; }
}
