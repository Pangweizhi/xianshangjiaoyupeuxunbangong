-- 补录大学语文 / 大学历史课程
-- 用途：
-- 1. 恢复同名课程的软删除状态
-- 2. 若数据库中不存在这两门课程，则安全插入
-- 3. 便于后续执行“题库课程题目补充.sql”
--
-- 说明：
-- - 该脚本尽量保持幂等，重复执行不会重复插入同名课程
-- - kecheng_types / banji_types 在不同库里可能有不同字典值，这里暂时使用 1
-- - 如果你希望更贴近原始字典，可以在插入后按后台页面再手工调整

START TRANSACTION;

-- 1) 恢复已存在的同名课程，避免旧数据处于软删除状态导致看不到
UPDATE kecheng
SET kecheng_delete = 1,
    course_status = 'approved',
    review_remark = '手工补录',
    review_time = NOW()
WHERE kecheng_name IN ('大学语文', '大学历史');

-- 2) 补录大学语文
INSERT INTO kecheng (
    kecheng_name,
    kecheng_photo,
    kecheng_types,
    kecheng_shichang,
    kecheng_time,
    kecheng_end_time,
    banji_types,
    jiaoshi_id,
    course_status,
    credit_score,
    review_remark,
    review_time,
    review_admin_id,
    kecheng_delete,
    kecheng_content,
    create_time
)
SELECT
    '大学语文',
    NULL,
    1,
    60,
    NOW(),
    DATE_ADD(NOW(), INTERVAL 60 MINUTE),
    1,
    NULL,
    'approved',
    0,
    '手工补录',
    NOW(),
    NULL,
    1,
    '大学语文基础课程，用于题库分类展示与补题。',
    NOW()
WHERE NOT EXISTS (
    SELECT 1
    FROM kecheng
    WHERE kecheng_name = '大学语文'
);

-- 3) 补录大学历史
INSERT INTO kecheng (
    kecheng_name,
    kecheng_photo,
    kecheng_types,
    kecheng_shichang,
    kecheng_time,
    kecheng_end_time,
    banji_types,
    jiaoshi_id,
    course_status,
    credit_score,
    review_remark,
    review_time,
    review_admin_id,
    kecheng_delete,
    kecheng_content,
    create_time
)
SELECT
    '大学历史',
    NULL,
    1,
    60,
    NOW(),
    DATE_ADD(NOW(), INTERVAL 60 MINUTE),
    1,
    NULL,
    'approved',
    0,
    '手工补录',
    NOW(),
    NULL,
    1,
    '大学历史基础课程，用于题库分类展示与补题。',
    NOW()
WHERE NOT EXISTS (
    SELECT 1
    FROM kecheng
    WHERE kecheng_name = '大学历史'
);

COMMIT;

-- 4) 执行后验证
SELECT id, kecheng_name, kecheng_types, banji_types, course_status, kecheng_delete
FROM kecheng
WHERE kecheng_name IN ('高等数学', '新概念英语', '大学语文', '大学历史')
ORDER BY id;
