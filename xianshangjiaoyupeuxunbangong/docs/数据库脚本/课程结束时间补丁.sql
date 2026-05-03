ALTER TABLE `kecheng`
ADD COLUMN `kecheng_end_time` timestamp NULL DEFAULT NULL COMMENT '课程结束时间' AFTER `kecheng_time`;

UPDATE `kecheng`
SET `kecheng_end_time` = DATE_ADD(`kecheng_time`, INTERVAL IFNULL(`kecheng_shichang`, 0) MINUTE)
WHERE `kecheng_end_time` IS NULL AND `kecheng_time` IS NOT NULL;
