CREATE TABLE IF NOT EXISTS `ai_chat_session` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` int(11) NOT NULL COMMENT '用户id',
  `user_table` varchar(32) NOT NULL COMMENT '用户表',
  `role_type` varchar(32) DEFAULT NULL COMMENT '角色',
  `session_title` varchar(128) NOT NULL COMMENT '会话标题',
  `biz_scene` varchar(64) DEFAULT NULL COMMENT '业务场景',
  `course_id` int(11) DEFAULT NULL COMMENT '课程id',
  `chapter_id` int(11) DEFAULT NULL COMMENT '章节id',
  `resource_id` int(11) DEFAULT NULL COMMENT '资源id',
  `message_count` int(11) DEFAULT '0' COMMENT '消息数',
  `last_message_at` datetime DEFAULT NULL COMMENT '最后消息时间',
  `status` varchar(16) DEFAULT 'active' COMMENT '状态',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_ai_chat_session_user` (`user_id`,`user_table`),
  KEY `idx_ai_chat_session_last_message` (`last_message_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI会话表';

CREATE TABLE IF NOT EXISTS `ai_chat_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `session_id` int(11) NOT NULL COMMENT '会话id',
  `user_id` int(11) NOT NULL COMMENT '用户id',
  `role_type` varchar(32) DEFAULT NULL COMMENT '角色',
  `message_role` varchar(16) NOT NULL COMMENT '消息角色',
  `message_type` varchar(32) DEFAULT 'text' COMMENT '消息类型',
  `content` text COMMENT '消息内容',
  `tool_name` varchar(64) DEFAULT NULL COMMENT '工具名',
  `tool_request_json` text COMMENT '工具请求',
  `tool_response_json` text COMMENT '工具响应',
  `context_json` text COMMENT '上下文快照',
  `token_estimate` int(11) DEFAULT '0' COMMENT '估算token',
  `sort_no` int(11) DEFAULT '0' COMMENT '排序号',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_ai_chat_message_session` (`session_id`,`sort_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI消息表';
