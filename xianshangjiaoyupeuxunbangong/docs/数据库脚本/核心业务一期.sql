ALTER TABLE `kecheng`
    ADD COLUMN `course_status` varchar(50) DEFAULT 'pending_review' COMMENT '课程审核状态' AFTER `jiaoshi_id`,
    ADD COLUMN `credit_score` int(11) DEFAULT 0 COMMENT '课程学分' AFTER `course_status`,
    ADD COLUMN `review_remark` varchar(255) DEFAULT NULL COMMENT '审核备注' AFTER `credit_score`,
    ADD COLUMN `review_time` timestamp NULL DEFAULT NULL COMMENT '审核时间' AFTER `review_remark`,
    ADD COLUMN `review_admin_id` bigint(20) DEFAULT NULL COMMENT '审核管理员' AFTER `review_time`;

ALTER TABLE `zuoye`
    ADD COLUMN `kecheng_id` int(11) DEFAULT NULL COMMENT '课程' AFTER `jiaoshi_id`,
    ADD COLUMN `chapter_id` int(11) DEFAULT NULL COMMENT '章节' AFTER `kecheng_id`,
    ADD COLUMN `deadline_time` timestamp NULL DEFAULT NULL COMMENT '截止时间' AFTER `chapter_id`,
    ADD COLUMN `score_total` int(11) DEFAULT 100 COMMENT '总分' AFTER `deadline_time`,
    ADD COLUMN `publish_status` varchar(50) DEFAULT 'published' COMMENT '发布状态' AFTER `score_total`;

CREATE TABLE IF NOT EXISTS `course_chapter` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `kecheng_id` int(11) DEFAULT NULL COMMENT '课程',
    `chapter_name` varchar(200) DEFAULT NULL COMMENT '章节名称',
    `chapter_sort` int(11) DEFAULT NULL COMMENT '章节排序',
    `chapter_summary` text COMMENT '章节简介',
    `chapter_status` varchar(50) DEFAULT 'pending_review' COMMENT '章节状态',
    `review_remark` varchar(255) DEFAULT NULL COMMENT '审核备注',
    `review_time` timestamp NULL DEFAULT NULL COMMENT '审核时间',
    `review_admin_id` bigint(20) DEFAULT NULL COMMENT '审核管理员',
    `is_deleted` int(11) DEFAULT 1 COMMENT '逻辑删除',
    `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='课程章节';

CREATE TABLE IF NOT EXISTS `course_resource` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `kecheng_id` int(11) DEFAULT NULL COMMENT '课程',
    `chapter_id` int(11) DEFAULT NULL COMMENT '章节',
    `resource_name` varchar(200) DEFAULT NULL COMMENT '资源名称',
    `resource_type` varchar(50) DEFAULT NULL COMMENT '资源类型',
    `resource_url` varchar(255) DEFAULT NULL COMMENT '资源地址',
    `cover_url` varchar(255) DEFAULT NULL COMMENT '封面地址',
    `duration_seconds` int(11) DEFAULT 0 COMMENT '时长秒数',
    `resource_status` varchar(50) DEFAULT 'pending_review' COMMENT '资源状态',
    `review_remark` varchar(255) DEFAULT NULL COMMENT '审核备注',
    `review_time` timestamp NULL DEFAULT NULL COMMENT '审核时间',
    `review_admin_id` bigint(20) DEFAULT NULL COMMENT '审核管理员',
    `is_deleted` int(11) DEFAULT 1 COMMENT '逻辑删除',
    `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='课程资源';

CREATE TABLE IF NOT EXISTS `course_enroll` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `kecheng_id` int(11) DEFAULT NULL COMMENT '课程',
    `yonghu_id` int(11) DEFAULT NULL COMMENT '学生',
    `enroll_status` varchar(50) DEFAULT '已选课' COMMENT '选课状态',
    `progress_percent` decimal(5,2) DEFAULT 0.00 COMMENT '进度百分比',
    `enroll_time` timestamp NULL DEFAULT NULL COMMENT '选课时间',
    `finish_time` timestamp NULL DEFAULT NULL COMMENT '结课时间',
    `is_deleted` int(11) DEFAULT 1 COMMENT '逻辑删除',
    `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_course_enroll` (`kecheng_id`,`yonghu_id`,`is_deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='课程选课';

CREATE TABLE IF NOT EXISTS `study_progress` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `kecheng_id` int(11) DEFAULT NULL COMMENT '课程',
    `chapter_id` int(11) DEFAULT NULL COMMENT '章节',
    `resource_id` int(11) DEFAULT NULL COMMENT '资源',
    `yonghu_id` int(11) DEFAULT NULL COMMENT '学生',
    `study_seconds` int(11) DEFAULT 0 COMMENT '学习秒数',
    `progress_percent` decimal(5,2) DEFAULT 0.00 COMMENT '进度百分比',
    `is_completed` int(11) DEFAULT 0 COMMENT '是否完成',
    `last_study_time` timestamp NULL DEFAULT NULL COMMENT '最后学习时间',
    `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_study_progress` (`resource_id`,`yonghu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='学习进度';

CREATE TABLE IF NOT EXISTS `course_credit_record` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `kecheng_id` int(11) DEFAULT NULL COMMENT '课程',
    `yonghu_id` int(11) DEFAULT NULL COMMENT '学生',
    `credit_score` int(11) DEFAULT 0 COMMENT '学分',
    `grant_status` varchar(50) DEFAULT '待发放' COMMENT '发放状态',
    `grant_time` timestamp NULL DEFAULT NULL COMMENT '发放时间',
    `grant_remark` varchar(255) DEFAULT NULL COMMENT '发放备注',
    `source_rule_snapshot` varchar(255) DEFAULT NULL COMMENT '规则快照',
    `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_credit_record` (`kecheng_id`,`yonghu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='课程学分记录';
