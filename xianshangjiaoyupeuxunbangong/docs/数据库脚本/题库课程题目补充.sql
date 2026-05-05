-- 为 4 门课程补充课程相关题库：
-- 高等数学、新概念英语、大学语文、大学历史
-- 每门课程 4 种题型，每种题型 5 道题，共 80 道题

-- 如果旧库里还没有 kecheng_id 字段，先补上这个字段
SET @col_count := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'exam_question'
    AND COLUMN_NAME = 'kecheng_id'
);

SET @sql := IF(
  @col_count = 0,
  'ALTER TABLE `exam_question` ADD COLUMN `kecheng_id` int(11) DEFAULT NULL COMMENT ''课程'' AFTER `id`',
  'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

INSERT INTO exam_question
  (kecheng_id, exam_id, question_type, question_title, option_json, correct_answer, question_score, sort_no, analysis_text, is_deleted, create_time)
SELECT
  k.id,
  0,
  t.question_type,
  CONCAT('[', k.kecheng_name, '] ', t.question_title),
  t.option_json,
  t.correct_answer,
  t.question_score,
  t.sort_no,
  t.analysis_text,
  1,
  NOW()
FROM kecheng k
CROSS JOIN (
  SELECT '选择题' AS question_type, 1 AS sort_no, '在求函数极限时，常用的方法是观察函数在趋近点附近的变化趋势。' AS question_title, JSON_OBJECT('A', '直接取趋近点的值', 'B', '只看函数图像不计算', 'C', '分析趋近过程中的变化', 'D', '忽略定义域') AS option_json, 'C' AS correct_answer, 5 AS question_score, '极限题的核心是研究变量逼近时的变化规律。' AS analysis_text
  UNION ALL SELECT '选择题', 2, '导数的几何意义通常表示什么？', JSON_OBJECT('A', '曲线在某点的切线斜率', 'B', '曲线的面积', 'C', '曲线的长度', 'D', '曲线的最高点'), 'A', 5, '导数在几何上表示切线斜率。'
  UNION ALL SELECT '选择题', 3, '不定积分的主要作用是求原函数。', JSON_OBJECT('A', '正确', 'B', '错误', 'C', '与函数无关', 'D', '只能求数列'), 'A', 5, '不定积分与求原函数密切相关。'
  UNION ALL SELECT '选择题', 4, '定积分在实际中常用于计算什么？', JSON_OBJECT('A', '面积和累积量', 'B', '质数个数', 'C', '字符长度', 'D', '图像颜色'), 'A', 5, '定积分适合处理面积、体积和累积量。'
  UNION ALL SELECT '选择题', 5, '学习高等数学时，最重要的习惯之一是什么？', JSON_OBJECT('A', '只背公式不做题', 'B', '边学边练并及时总结', 'C', '只看答案不思考', 'D', '只看标题'), 'B', 5, '数学学习强调练习和总结。'
  UNION ALL SELECT '判断题', 1, '函数连续不一定说明它在该点可导。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '连续与可导是不同的概念。'
  UNION ALL SELECT '判断题', 2, '导数可以帮助分析函数的单调性。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '导数常用于判断单调区间。'
  UNION ALL SELECT '判断题', 3, '定积分一定等于函数的最大值。', JSON_OBJECT('A', '正确', 'B', '错误'), 'B', 5, '定积分表示累积量，不等于最大值。'
  UNION ALL SELECT '判断题', 4, '高等数学中的公式需要结合例题理解。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '只记公式不练习通常效果不好。'
  UNION ALL SELECT '判断题', 5, '学习高等数学时，做错题整理有助于提升掌握程度。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '错题整理能帮助发现薄弱环节。'
  UNION ALL SELECT '填空题', 1, '函数在某点连续，是研究可导性的____。', NULL, '基础', 5, '连续是讨论可导的前提之一。'
  UNION ALL SELECT '填空题', 2, '导数反映的是函数变化的____。', NULL, '快慢', 5, '导数描述变化率。'
  UNION ALL SELECT '填空题', 3, '定积分常用于计算图形的____。', NULL, '面积', 5, '积分常用于面积计算。'
  UNION ALL SELECT '填空题', 4, '学习高等数学要重视____和总结。', NULL, '练习', 5, '练习是数学学习的重要环节。'
  UNION ALL SELECT '填空题', 5, '高等数学中的核心思想之一是用____描述变化。', NULL, '函数', 5, '函数是数学建模的重要工具。'
  UNION ALL SELECT '简答题', 1, '请简述你如何理解“极限”这个概念。', NULL, '极限描述的是变量在接近某个值时函数的变化趋势，是高等数学的重要基础。', 10, 1, '回答应体现“逼近”和“趋势”。'
  UNION ALL SELECT '简答题', 2, '请简述导数在实际中的一个应用。', NULL, '导数可以用于分析速度变化、成本变化和最优值问题等。', 10, 2, '可结合速度、最值、优化等场景。'
  UNION ALL SELECT '简答题', 3, '请简述你会如何复习高等数学。', NULL, '先整理公式和概念，再结合例题和错题反复练习，最后总结常见题型。', 10, 3, '回答应体现整理、练习和总结。'
  UNION ALL SELECT '简答题', 4, '请简述定积分的学习重点。', NULL, '定积分的重点在于理解累积思想、积分上下限以及与面积的联系。', 10, 4, '回答可围绕累积思想展开。'
  UNION ALL SELECT '简答题', 5, '请简述学习高等数学时为什么要多做题。', NULL, '做题可以帮助理解概念、熟悉题型并发现自己对知识点的薄弱之处。', 10, 5, '强调理解、熟悉和查漏补缺。'
) AS t
WHERE k.kecheng_name = '高等数学';

INSERT INTO exam_question
  (kecheng_id, exam_id, question_type, question_title, option_json, correct_answer, question_score, sort_no, analysis_text, is_deleted, create_time)
SELECT
  k.id,
  0,
  t.question_type,
  CONCAT('[', k.kecheng_name, '] ', t.question_title),
  t.option_json,
  t.correct_answer,
  t.question_score,
  t.sort_no,
  t.analysis_text,
  1,
  NOW()
FROM kecheng k
CROSS JOIN (
  SELECT '选择题' AS question_type, 1 AS sort_no, '学习新概念英语时，首先要关注什么？' AS question_title, JSON_OBJECT('A', '只背单词不读句子', 'B', '词汇、句型和语境结合', 'C', '只看中文翻译', 'D', '忽略发音') AS option_json, 'B' AS correct_answer, 5 AS question_score, '英语学习需要词汇、语法和语境一起掌握。' AS analysis_text
  UNION ALL SELECT '选择题', 2, '遇到不认识的单词时，比较好的做法是结合上下文猜测并查词。', JSON_OBJECT('A', '直接跳过', 'B', '结合上下文并查词', 'C', '只背中文意思', 'D', '不做记录'), 'B', 5, '上下文能帮助理解词义。'
  UNION ALL SELECT '选择题', 3, '英语阅读中，标题通常能帮助我们预测什么？', JSON_OBJECT('A', '文章主题', 'B', '文章页码', 'C', '作者生日', 'D', '字母数量'), 'A', 5, '标题常常概括文章主题。'
  UNION ALL SELECT '选择题', 4, '学习英语语法时，最有效的方式之一是什么？', JSON_OBJECT('A', '只背规则不做练习', 'B', '结合例句理解并练习', 'C', '只看答案', 'D', '只听不说'), 'B', 5, '语法要结合例句和练习。'
  UNION ALL SELECT '选择题', 5, '提高英语听力，比较重要的习惯是？', JSON_OBJECT('A', '只听一次就放弃', 'B', '反复听并总结关键词', 'C', '只看字幕不听音频', 'D', '忽略发音'), 'B', 5, '反复听可以提升辨音和理解。'
  UNION ALL SELECT '判断题', 1, '学习英语时，音标和发音会影响听说能力。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '发音基础会影响听力和口语。'
  UNION ALL SELECT '判断题', 2, '只记单词中文意思就足够掌握新概念英语。', JSON_OBJECT('A', '正确', 'B', '错误'), 'B', 5, '单词需要放在句子和语境中学习。'
  UNION ALL SELECT '判断题', 3, '英语阅读时，边读边标记关键词有助于理解。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '关键词能帮助抓住文章主旨。'
  UNION ALL SELECT '判断题', 4, '语法学习不需要例句，只记规则就可以。', JSON_OBJECT('A', '正确', 'B', '错误'), 'B', 5, '例句有助于理解和应用语法。'
  UNION ALL SELECT '判断题', 5, '复习英语时，整理错词和错句有助于提高水平。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '错词错句整理能提升复习效率。'
  UNION ALL SELECT '填空题', 1, '英语学习中，词汇是理解句子的____。', NULL, '基础', 5, '词汇是语言理解的基础。'
  UNION ALL SELECT '填空题', 2, '阅读英语文章时，可以先看____。', NULL, '标题', 5, '标题有助于快速把握主题。'
  UNION ALL SELECT '填空题', 3, '练习英语听力时，要注意抓住____词。', NULL, '关键词', 5, '关键词能帮助理解重点信息。'
  UNION ALL SELECT '填空题', 4, '学习新概念英语要做到听、说、读、____结合。', NULL, '写', 5, '听说读写要综合训练。'
  UNION ALL SELECT '填空题', 5, '积累英语表达时，要注意搭配和____。', NULL, '语境', 5, '语境决定表达是否自然。'
  UNION ALL SELECT '简答题', 1, '请简述你如何学习新概念英语中的单词。', NULL, '可以结合课文语境记忆单词，同时通过例句和反复复习加强印象。', 10, 1, '回答应体现语境和复习。'
  UNION ALL SELECT '简答题', 2, '请简述英语阅读理解的关键方法。', NULL, '先看标题和首尾段，再抓关键词，最后结合上下文理解全文意思。', 10, 2, '回答应体现阅读步骤。'
  UNION ALL SELECT '简答题', 3, '请简述你会如何提升英语听力。', NULL, '通过反复听、跟读、模仿和整理生词，逐步提高听辨能力。', 10, 3, '回答应体现反复练习。'
  UNION ALL SELECT '简答题', 4, '请简述语法学习为什么要结合例句。', NULL, '例句能帮助理解规则在真实语境中的用法，也能减少死记硬背的困难。', 10, 4, '回答应体现理解和应用。'
  UNION ALL SELECT '简答题', 5, '请简述你认为学好英语最重要的一个习惯。', NULL, '坚持每天接触英语，保持输入和输出，长期积累才能看到效果。', 10, 5, '回答可围绕持续积累。'
) AS t
WHERE k.kecheng_name = '新概念英语';

INSERT INTO exam_question
  (kecheng_id, exam_id, question_type, question_title, option_json, correct_answer, question_score, sort_no, analysis_text, is_deleted, create_time)
SELECT
  k.id,
  0,
  t.question_type,
  CONCAT('[', k.kecheng_name, '] ', t.question_title),
  t.option_json,
  t.correct_answer,
  t.question_score,
  t.sort_no,
  t.analysis_text,
  1,
  NOW()
FROM kecheng k
CROSS JOIN (
  SELECT '选择题' AS question_type, 1 AS sort_no, '阅读古诗文时，首先应关注什么？' AS question_title, JSON_OBJECT('A', '只看字数', 'B', '作者姓名', 'C', '题目和注释', 'D', '纸张颜色') AS option_json, 'C' AS correct_answer, 5 AS question_score, '题目和注释有助于理解文章背景。' AS analysis_text
  UNION ALL SELECT '选择题', 2, '学习大学语文时，理解文章主旨的重要性在于什么？', JSON_OBJECT('A', '知道文章讲了什么', 'B', '只背诵标题', 'C', '忽略段落关系', 'D', '只看字数'), 'A', 5, '主旨是理解文本的核心。'
  UNION ALL SELECT '选择题', 3, '现代文阅读中，概括段意有助于什么？', JSON_OBJECT('A', '理解文章结构', 'B', '增加字数', 'C', '减少阅读', 'D', '替代原文'), 'A', 5, '概括段意能帮助把握层次。'
  UNION ALL SELECT '选择题', 4, '学习大学语文中的修辞手法，最重要的是？', JSON_OBJECT('A', '只背名词', 'B', '理解作用并举例', 'C', '忽略语境', 'D', '只看定义'), 'B', 5, '修辞需要结合文本理解。'
  UNION ALL SELECT '选择题', 5, '古诗词赏析中，常需要联系什么来理解情感？', JSON_OBJECT('A', '时代背景和作者经历', 'B', '纸张大小', 'C', '字母顺序', 'D', '装订方式'), 'A', 5, '背景常与情感表达有关。'
  UNION ALL SELECT '判断题', 1, '大学语文学习中，积累文言词汇有助于理解古文。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '文言词汇是古文理解基础。'
  UNION ALL SELECT '判断题', 2, '只背诵文章标题就能掌握整篇课文。', JSON_OBJECT('A', '正确', 'B', '错误'), 'B', 5, '需要理解内容、结构和情感。'
  UNION ALL SELECT '判断题', 3, '阅读文章时，注意段落之间的逻辑关系很重要。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '段落逻辑关系有助于把握结构。'
  UNION ALL SELECT '判断题', 4, '大学语文的作文训练只需要堆砌华丽词语。', JSON_OBJECT('A', '正确', 'B', '错误'), 'B', 5, '写作更看重立意、结构和表达。'
  UNION ALL SELECT '判断题', 5, '平时多做阅读和写作练习有助于提高语文素养。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '阅读和写作练习能提升综合能力。'
  UNION ALL SELECT '填空题', 1, '大学语文学习的重点之一是理解文章的____。', NULL, '主旨', 5, '主旨决定文章核心意思。'
  UNION ALL SELECT '填空题', 2, '文言文阅读时要注意常见的____字。', NULL, '实词', 5, '实词影响句子含义。'
  UNION ALL SELECT '填空题', 3, '赏析诗歌时要关注诗人的情感和____。', NULL, '意境', 5, '意境是诗歌赏析重点。'
  UNION ALL SELECT '填空题', 4, '写作时，文章结构通常包括开头、____和结尾。', NULL, '中间', 5, '结构完整有助于表达清晰。'
  UNION ALL SELECT '填空题', 5, '阅读理解训练有助于提升学生的____能力。', NULL, '概括', 5, '概括能力是语文核心能力之一。'
  UNION ALL SELECT '简答题', 1, '请简述如何学习大学语文中的古诗文。', NULL, '先读注释和译文，再结合背景理解内容，最后通过背诵和赏析加深印象。', 10, 1, '回答应体现理解、背诵和赏析。'
  UNION ALL SELECT '简答题', 2, '请简述现代文阅读的基本方法。', NULL, '先抓住标题和中心句，再梳理段落关系，最后总结文章主旨和表达方式。', 10, 2, '回答应体现结构分析。'
  UNION ALL SELECT '简答题', 3, '请简述写好大学语文作文需要注意什么。', NULL, '作文要注意立意明确、结构完整、语言通顺，并结合实际材料展开。', 10, 3, '回答应体现立意与结构。'
  UNION ALL SELECT '简答题', 4, '请简述修辞手法学习的作用。', NULL, '学习修辞有助于提升表达能力，理解文章语言特色，也能增强写作效果。', 10, 4, '回答应体现表达和理解。'
  UNION ALL SELECT '简答题', 5, '请简述你认为提高语文素养的有效方式。', NULL, '多读、多写、多思考，长期积累词汇、阅读能力和表达能力。', 10, 5, '回答可围绕积累与训练。'
) AS t
WHERE k.kecheng_name = '大学语文';

INSERT INTO exam_question
  (kecheng_id, exam_id, question_type, question_title, option_json, correct_answer, question_score, sort_no, analysis_text, is_deleted, create_time)
SELECT
  k.id,
  0,
  t.question_type,
  CONCAT('[', k.kecheng_name, '] ', t.question_title),
  t.option_json,
  t.correct_answer,
  t.question_score,
  t.sort_no,
  t.analysis_text,
  1,
  NOW()
FROM kecheng k
CROSS JOIN (
  SELECT '选择题' AS question_type, 1 AS sort_no, '学习中国古代史时，首先应重视什么？' AS question_title, JSON_OBJECT('A', '时间线和朝代顺序', 'B', '只背皇帝名字', 'C', '只看图片', 'D', '忽略年代') AS option_json, 'A' AS correct_answer, 5 AS question_score, '历史学习重在建立时间顺序和整体框架。' AS analysis_text
  UNION ALL SELECT '选择题', 2, '研究历史事件时，应该关注哪些因素？', JSON_OBJECT('A', '背景、过程和影响', 'B', '只看事件标题', 'C', '只记结论', 'D', '只看地图颜色'), 'A', 5, '历史分析需要关注背景、过程和结果。'
  UNION ALL SELECT '选择题', 3, '学习历史人物时，常需要结合什么理解其行为？', JSON_OBJECT('A', '时代背景', 'B', '字数', 'C', '字体', 'D', '纸张厚度'), 'A', 5, '时代背景决定人物行为逻辑。'
  UNION ALL SELECT '选择题', 4, '下列哪项最适合用于梳理历史知识？', JSON_OBJECT('A', '时间轴', 'B', '随机记忆', 'C', '只看标题', 'D', '忽略顺序'), 'A', 5, '时间轴有利于梳理历史脉络。'
  UNION ALL SELECT '选择题', 5, '学习大学历史时，做比较研究的意义在于什么？', JSON_OBJECT('A', '看清不同阶段的变化与联系', 'B', '增加字数', 'C', '减少理解', 'D', '只记人名'), 'A', 5, '比较研究有助于发现历史发展规律。'
  UNION ALL SELECT '判断题', 1, '历史学习中，时间顺序非常重要。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '时间顺序是理解历史脉络的基础。'
  UNION ALL SELECT '判断题', 2, '只背结论就能理解历史事件。', JSON_OBJECT('A', '正确', 'B', '错误'), 'B', 5, '历史学习需要理解背景和过程。'
  UNION ALL SELECT '判断题', 3, '历史人物的行为通常和当时的时代背景有关。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '时代背景会影响人物选择。'
  UNION ALL SELECT '判断题', 4, '历史地图和时间轴可以帮助理解历史发展。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '图表工具有助于知识梳理。'
  UNION ALL SELECT '判断题', 5, '复习历史时，整理事件之间的因果关系有帮助。', JSON_OBJECT('A', '正确', 'B', '错误'), 'A', 5, '因果关系能帮助形成知识网络。'
  UNION ALL SELECT '填空题', 1, '历史学习的关键之一是掌握事件的____。', NULL, '时间顺序', 5, '时间顺序帮助建立历史框架。'
  UNION ALL SELECT '填空题', 2, '分析历史事件时要关注其产生的____。', NULL, '背景', 5, '背景决定事件发生条件。'
  UNION ALL SELECT '填空题', 3, '学习历史人物要结合他们所处的____。', NULL, '时代', 5, '时代背景有助于理解人物。'
  UNION ALL SELECT '填空题', 4, '整理历史知识时常用的方法之一是制作____。', NULL, '时间轴', 5, '时间轴便于梳理顺序。'
  UNION ALL SELECT '填空题', 5, '历史复习时要注意事件之间的____关系。', NULL, '因果', 5, '因果关系帮助理解发展逻辑。'
  UNION ALL SELECT '简答题', 1, '请简述你如何学习大学历史。', NULL, '我会先按时间顺序梳理朝代和事件，再结合背景理解原因和影响，最后通过时间轴和错题复习巩固。', 10, 1, '回答应体现时间线和复习方法。'
  UNION ALL SELECT '简答题', 2, '请简述历史事件分析时应关注的内容。', NULL, '需要关注事件发生的背景、发展过程、关键人物以及最终影响。', 10, 2, '回答应体现分析维度。'
  UNION ALL SELECT '简答题', 3, '请简述学习历史人物时为什么要结合时代背景。', NULL, '因为人物的思想和行为往往受当时政治、经济和社会环境影响，结合背景才能更准确理解。', 10, 3, '回答应体现背景影响。'
  UNION ALL SELECT '简答题', 4, '请简述历史学习中时间轴的作用。', NULL, '时间轴可以帮助我们把零散事件串联起来，形成清晰的历史发展脉络。', 10, 4, '回答应体现梳理脉络。'
  UNION ALL SELECT '简答题', 5, '请简述你认为历史学习中最重要的一个习惯。', NULL, '我认为最重要的是按主题和时间进行整理，及时总结事件之间的联系。', 10, 5, '回答可围绕整理和总结。'
) AS t
WHERE k.kecheng_name = '大学历史';
