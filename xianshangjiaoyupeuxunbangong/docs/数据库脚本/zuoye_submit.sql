CREATE TABLE IF NOT EXISTS `zuoye_submit` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `zuoye_id` int(11) NOT NULL COMMENT '作业',
  `yonghu_id` int(11) NOT NULL COMMENT '学生',
  `submit_file` varchar(255) DEFAULT NULL COMMENT '提交附件',
  `submit_content` text COMMENT '提交说明',
  `submit_status` varchar(50) DEFAULT '待批改' COMMENT '提交状态',
  `submit_score` decimal(10,2) DEFAULT NULL COMMENT '评分',
  `submit_remark` text COMMENT '评语',
  `submit_delete` int(11) DEFAULT '1' COMMENT '逻辑删除',
  `check_time` timestamp NULL DEFAULT NULL COMMENT '批改时间',
  `insert_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='作业提交';

SET @db_name = DATABASE();

SET @sql = (
    SELECT IF(
        EXISTS (
            SELECT 1
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = @db_name
              AND TABLE_NAME = 'zuoye_submit'
              AND COLUMN_NAME = 'submit_status'
        ),
        'SELECT 1',
        "ALTER TABLE `zuoye_submit` ADD COLUMN `submit_status` varchar(50) DEFAULT '待批改' COMMENT '提交状态' AFTER `submit_content`"
    )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
    SELECT IF(
        EXISTS (
            SELECT 1
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = @db_name
              AND TABLE_NAME = 'zuoye_submit'
              AND COLUMN_NAME = 'submit_score'
        ),
        'SELECT 1',
        "ALTER TABLE `zuoye_submit` ADD COLUMN `submit_score` decimal(10,2) DEFAULT NULL COMMENT '评分' AFTER `submit_status`"
    )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
    SELECT IF(
        EXISTS (
            SELECT 1
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = @db_name
              AND TABLE_NAME = 'zuoye_submit'
              AND COLUMN_NAME = 'submit_remark'
        ),
        'SELECT 1',
        "ALTER TABLE `zuoye_submit` ADD COLUMN `submit_remark` text COMMENT '评语' AFTER `submit_score`"
    )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql = (
    SELECT IF(
        EXISTS (
            SELECT 1
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = @db_name
              AND TABLE_NAME = 'zuoye_submit'
              AND COLUMN_NAME = 'check_time'
        ),
        'SELECT 1',
        "ALTER TABLE `zuoye_submit` ADD COLUMN `check_time` timestamp NULL DEFAULT NULL COMMENT '批改时间' AFTER `submit_delete`"
    )
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
