CREATE TABLE IF NOT EXISTS `exam` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `kecheng_id` int(11) NOT NULL COMMENT '课程',
  `chapter_id` int(11) DEFAULT NULL COMMENT '章节',
  `jiaoshi_id` int(11) DEFAULT NULL COMMENT '教师',
  `exam_name` varchar(200) NOT NULL COMMENT '考试名称',
  `exam_summary` text COMMENT '考试说明',
  `duration_minutes` int(11) DEFAULT 60 COMMENT '时长分钟',
  `total_score` int(11) DEFAULT 100 COMMENT '总分',
  `pass_score` int(11) DEFAULT 60 COMMENT '及格线',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `exam_status` varchar(50) DEFAULT 'draft' COMMENT '状态',
  `allow_retake` int(11) DEFAULT 0 COMMENT '是否允许重复考试',
  `max_attempt_count` int(11) DEFAULT 1 COMMENT '最大作答次数',
  `allow_resume` int(11) DEFAULT 1 COMMENT '是否允许退出后恢复',
  `publish_time` datetime DEFAULT NULL COMMENT '发布时间',
  `is_deleted` int(11) DEFAULT 1 COMMENT '逻辑删除',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考试';

CREATE TABLE IF NOT EXISTS `exam_question` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `exam_id` int(11) NOT NULL COMMENT '考试',
  `question_type` varchar(50) NOT NULL COMMENT '题型',
  `question_title` text NOT NULL COMMENT '题目',
  `option_json` text COMMENT '选项JSON',
  `correct_answer` varchar(500) DEFAULT NULL COMMENT '正确答案',
  `question_score` int(11) DEFAULT 5 COMMENT '题目分值',
  `sort_no` int(11) DEFAULT 1 COMMENT '排序',
  `analysis_text` text COMMENT '解析',
  `is_deleted` int(11) DEFAULT 1 COMMENT '逻辑删除',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考试题目';

CREATE TABLE IF NOT EXISTS `exam_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `exam_id` int(11) NOT NULL COMMENT '考试',
  `kecheng_id` int(11) NOT NULL COMMENT '课程',
  `yonghu_id` int(11) NOT NULL COMMENT '学生',
  `answer_snapshot` longtext COMMENT '答题快照',
  `question_snapshot` longtext COMMENT '题目快照',
  `auto_score` decimal(10,2) DEFAULT NULL COMMENT '自动评分',
  `manual_score` decimal(10,2) DEFAULT NULL COMMENT '人工评分',
  `final_score` decimal(10,2) DEFAULT NULL COMMENT '最终成绩',
  `pass_status` varchar(50) DEFAULT 'pending' COMMENT '是否通过',
  `record_status` varchar(50) DEFAULT 'started' COMMENT '记录状态',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `submit_time` datetime DEFAULT NULL COMMENT '提交时间',
  `check_time` datetime DEFAULT NULL COMMENT '阅卷时间',
  `check_remark` text COMMENT '阅卷评语',
  `attempt_no` int(11) DEFAULT 1 COMMENT '第几次作答',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考试记录';

-- 如果你的 `exam` 表是在旧版本三期脚本执行前就已经创建好的，
-- 再按需手动执行下面 3 条 ALTER。
-- 如果这些字段已经存在，就不要重复执行。

-- ALTER TABLE `exam` ADD COLUMN `allow_retake` int(11) DEFAULT 0 COMMENT '是否允许重复考试' AFTER `exam_status`;
-- ALTER TABLE `exam` ADD COLUMN `max_attempt_count` int(11) DEFAULT 1 COMMENT '最大作答次数' AFTER `allow_retake`;
-- ALTER TABLE `exam` ADD COLUMN `allow_resume` int(11) DEFAULT 1 COMMENT '是否允许退出后恢复' AFTER `max_attempt_count`;
