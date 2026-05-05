ALTER TABLE `zuoye`
ADD COLUMN `question_ids` text COMMENT '题目ID集合' AFTER `publish_status`;

ALTER TABLE `zuoye_submit`
ADD COLUMN `answer_snapshot` longtext COMMENT '答案快照' AFTER `submit_status`,
ADD COLUMN `question_snapshot` longtext COMMENT '题目快照' AFTER `answer_snapshot`,
ADD COLUMN `auto_score` decimal(10,2) DEFAULT NULL COMMENT '自动评分' AFTER `question_snapshot`;
