-- 作业时间窗口补丁
-- 目标：
-- 1. 为 zuoye 表补充 start_time / end_time
-- 2. 尽量沿用现有 deadline_time 作为结束时间
-- 3. 保留 deadline_time 以兼容旧数据，前后端改为展示开始/结束时间

SET @start_col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'zuoye'
    AND COLUMN_NAME = 'start_time'
);

SET @end_col_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'zuoye'
    AND COLUMN_NAME = 'end_time'
);

SET @sql := IF(
  @start_col_exists = 0,
  'ALTER TABLE `zuoye` ADD COLUMN `start_time` timestamp NULL DEFAULT NULL COMMENT ''开始时间'' AFTER `chapter_id`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @sql := IF(
  @end_col_exists = 0,
  'ALTER TABLE `zuoye` ADD COLUMN `end_time` timestamp NULL DEFAULT NULL COMMENT ''结束时间'' AFTER `start_time`',
  'SELECT 1'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

UPDATE `zuoye`
SET
  `start_time` = IF(`start_time` IS NULL, COALESCE(`insert_time`, `create_time`, NOW()), `start_time`),
  `end_time` = IF(
    `end_time` IS NULL,
    COALESCE(`deadline_time`, DATE_ADD(COALESCE(`insert_time`, `create_time`, NOW()), INTERVAL 7 DAY)),
    `end_time`
  )
WHERE 1 = 1;
