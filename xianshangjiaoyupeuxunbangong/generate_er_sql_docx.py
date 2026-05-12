from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
CHAPTER_DIR = ROOT / "辅助修改论文" / "第四章 数据库的逻辑设计"
TEMPLATE_DOCX = CHAPTER_DIR / "参考数据库的逻辑设计.docx"
OUTPUT_DOCX = CHAPTER_DIR / "实体关系图SQL说明.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)
ET.register_namespace("cp", CP_NS)
ET.register_namespace("dc", DC_NS)


@dataclass
class SqlSection:
    title: str
    intro: str
    sql: str


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def run_xml(
    text: str,
    *,
    font: str = "宋体",
    size: int = 24,
    bold: bool = False,
    color: str = "000000",
    preserve: bool = True,
) -> str:
    rpr = (
        "<w:rPr>"
        f"<w:rFonts w:ascii=\"{font}\" w:hAnsi=\"{font}\" w:eastAsia=\"{font}\" w:cs=\"{font}\"/>"
        f"<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/>"
    )
    if bold:
        rpr += "<w:b/><w:bCs/>"
    if color:
        rpr += f"<w:color w:val=\"{color}\"/>"
    rpr += "</w:rPr>"
    space = ' xml:space="preserve"' if preserve else ""
    return f"<w:r>{rpr}<w:t{space}>{escape(text)}</w:t></w:r>"


def paragraph_xml(
    text: str = "",
    *,
    align: str = "both",
    first_line: int = 420,
    left: int = 0,
    before: int = 0,
    after: int = 120,
    line: int = 360,
    font: str = "宋体",
    size: int = 24,
    bold: bool = False,
    color: str = "000000",
) -> str:
    ppr = (
        "<w:pPr>"
        f"<w:jc w:val=\"{align}\"/>"
        f"<w:spacing w:before=\"{before}\" w:after=\"{after}\" w:line=\"{line}\" w:lineRule=\"auto\"/>"
        f"<w:ind w:firstLine=\"{first_line}\" w:left=\"{left}\"/>"
        "</w:pPr>"
    )
    return "<w:p>" + ppr + run_xml(text, font=font, size=size, bold=bold, color=color) + "</w:p>"


def title_xml(text: str) -> str:
    return paragraph_xml(
        text,
        align="center",
        first_line=0,
        before=180,
        after=180,
        line=360,
        font="黑体",
        size=32,
        bold=True,
    )


def heading1_xml(text: str) -> str:
    return paragraph_xml(
        text,
        align="left",
        first_line=0,
        before=180,
        after=120,
        line=320,
        font="黑体",
        size=28,
        bold=True,
    )


def heading2_xml(text: str) -> str:
    return paragraph_xml(
        text,
        align="left",
        first_line=0,
        before=120,
        after=80,
        line=300,
        font="黑体",
        size=24,
        bold=True,
    )


def code_block_xml(text: str) -> str:
    lines = text.strip("\n").splitlines()
    ppr = (
        "<w:pPr>"
        "<w:jc w:val=\"left\"/>"
        "<w:spacing w:before=\"60\" w:after=\"160\" w:line=\"300\" w:lineRule=\"auto\"/>"
        "<w:ind w:firstLine=\"0\" w:left=\"240\" w:right=\"120\"/>"
        "<w:shd w:val=\"clear\" w:color=\"auto\" w:fill=\"F6F8FA\"/>"
        "<w:pBdr>"
        "<w:top w:val=\"single\" w:sz=\"6\" w:space=\"1\" w:color=\"D0D7DE\"/>"
        "<w:left w:val=\"single\" w:sz=\"6\" w:space=\"1\" w:color=\"D0D7DE\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"6\" w:space=\"1\" w:color=\"D0D7DE\"/>"
        "<w:right w:val=\"single\" w:sz=\"6\" w:space=\"1\" w:color=\"D0D7DE\"/>"
        "</w:pBdr>"
        "</w:pPr>"
    )
    parts = [
        "<w:p>",
        ppr,
    ]
    for idx, line in enumerate(lines):
        parts.append(
            run_xml(
                line,
                font="Consolas",
                size=18,
                color="1F2328",
                preserve=True,
            )
        )
        if idx != len(lines) - 1:
            parts.append("<w:r><w:br/></w:r>")
    parts.append("</w:p>")
    return "".join(parts)


def update_core_props(core_path: Path, title_text: str) -> None:
    if not core_path.exists():
        return
    root = ET.parse(core_path).getroot()
    for child in root:
        if child.tag == qn(DC_NS, "title"):
            child.text = title_text
        elif child.tag == qn(DC_NS, "subject"):
            child.text = title_text
        elif child.tag == qn(DC_NS, "description"):
            child.text = "用于 SQL 转 ER 图网站生成数据库实体关系图"
    ET.ElementTree(root).write(core_path, encoding="utf-8", xml_declaration=True)


def sections() -> list[SqlSection]:
    overall_sql = """
CREATE TABLE `users` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `username` VARCHAR(200) NOT NULL,
  `password` VARCHAR(200) NOT NULL,
  `role` VARCHAR(100) NOT NULL,
  `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `jiaoshi` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `username` VARCHAR(200) NOT NULL,
  `password` VARCHAR(200) NOT NULL,
  `jiaoshi_name` VARCHAR(200) NOT NULL,
  `sex_types` INT,
  `jiaoshi_photo` VARCHAR(200),
  `jiaoshi_id_number` VARCHAR(200),
  `jiaoshi_phone` VARCHAR(200),
  `jiaoshi_email` VARCHAR(200),
  `jiaoshi_delete` INT DEFAULT 1,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `yonghu` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `username` VARCHAR(200) NOT NULL,
  `password` VARCHAR(200) NOT NULL,
  `yonghu_name` VARCHAR(200) NOT NULL,
  `sex_types` INT,
  `yonghu_photo` VARCHAR(200),
  `yonghu_id_number` VARCHAR(200),
  `yonghu_phone` VARCHAR(200),
  `yonghu_email` VARCHAR(200),
  `banji_types` INT,
  `yonghu_delete` INT DEFAULT 1,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `kecheng` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `kecheng_name` VARCHAR(200) NOT NULL,
  `kecheng_photo` VARCHAR(200),
  `kecheng_types` INT,
  `kecheng_shichang` INT,
  `kecheng_time` DATETIME,
  `kecheng_end_time` DATETIME,
  `banji_types` INT,
  `jiaoshi_id` INT,
  `course_status` VARCHAR(50) DEFAULT 'pending_review',
  `credit_score` INT DEFAULT 0,
  `review_remark` VARCHAR(255),
  `review_time` DATETIME,
  `review_admin_id` INT,
  `kecheng_delete` INT DEFAULT 1,
  `kecheng_content` TEXT,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_kecheng_jiaoshi` FOREIGN KEY (`jiaoshi_id`) REFERENCES `jiaoshi` (`id`),
  CONSTRAINT `fk_kecheng_admin` FOREIGN KEY (`review_admin_id`) REFERENCES `users` (`id`)
);

CREATE TABLE `course_chapter` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `kecheng_id` INT NOT NULL,
  `chapter_name` VARCHAR(200) NOT NULL,
  `chapter_sort` INT,
  `chapter_summary` TEXT,
  `chapter_status` VARCHAR(50) DEFAULT 'pending_review',
  `review_time` DATETIME,
  CONSTRAINT `fk_course_chapter_kecheng` FOREIGN KEY (`kecheng_id`) REFERENCES `kecheng` (`id`)
);

CREATE TABLE `course_resource` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `kecheng_id` INT NOT NULL,
  `chapter_id` INT NOT NULL,
  `resource_name` VARCHAR(200) NOT NULL,
  `resource_type` VARCHAR(50),
  `resource_url` VARCHAR(255),
  `resource_status` VARCHAR(50) DEFAULT 'pending_review',
  CONSTRAINT `fk_course_resource_kecheng` FOREIGN KEY (`kecheng_id`) REFERENCES `kecheng` (`id`),
  CONSTRAINT `fk_course_resource_chapter` FOREIGN KEY (`chapter_id`) REFERENCES `course_chapter` (`id`)
);

CREATE TABLE `course_enroll` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `kecheng_id` INT NOT NULL,
  `yonghu_id` INT NOT NULL,
  `enroll_status` VARCHAR(50) DEFAULT '已选课',
  `progress_percent` DECIMAL(5,2) DEFAULT 0.00,
  `finish_time` DATETIME,
  CONSTRAINT `fk_course_enroll_kecheng` FOREIGN KEY (`kecheng_id`) REFERENCES `kecheng` (`id`),
  CONSTRAINT `fk_course_enroll_yonghu` FOREIGN KEY (`yonghu_id`) REFERENCES `yonghu` (`id`)
);

CREATE TABLE `study_progress` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `resource_id` INT NOT NULL,
  `yonghu_id` INT NOT NULL,
  `study_seconds` INT DEFAULT 0,
  `progress_percent` DECIMAL(5,2) DEFAULT 0.00,
  `is_completed` INT DEFAULT 0,
  CONSTRAINT `fk_study_progress_resource` FOREIGN KEY (`resource_id`) REFERENCES `course_resource` (`id`),
  CONSTRAINT `fk_study_progress_yonghu` FOREIGN KEY (`yonghu_id`) REFERENCES `yonghu` (`id`)
);

CREATE TABLE `zuoye` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `zuoye_name` VARCHAR(200) NOT NULL,
  `jiaoshi_id` INT,
  `kecheng_id` INT,
  `chapter_id` INT,
  `start_time` DATETIME,
  `end_time` DATETIME,
  `score_total` INT DEFAULT 100,
  `publish_status` VARCHAR(50) DEFAULT 'published',
  `question_ids` TEXT,
  `zuoye_content` TEXT,
  CONSTRAINT `fk_zuoye_jiaoshi` FOREIGN KEY (`jiaoshi_id`) REFERENCES `jiaoshi` (`id`),
  CONSTRAINT `fk_zuoye_kecheng` FOREIGN KEY (`kecheng_id`) REFERENCES `kecheng` (`id`),
  CONSTRAINT `fk_zuoye_chapter` FOREIGN KEY (`chapter_id`) REFERENCES `course_chapter` (`id`)
);

CREATE TABLE `zuoye_submit` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `zuoye_id` INT NOT NULL,
  `yonghu_id` INT NOT NULL,
  `submit_status` VARCHAR(50) DEFAULT '待批改',
  `submit_score` DECIMAL(10,2),
  `check_time` DATETIME,
  CONSTRAINT `fk_zuoye_submit_zuoye` FOREIGN KEY (`zuoye_id`) REFERENCES `zuoye` (`id`),
  CONSTRAINT `fk_zuoye_submit_yonghu` FOREIGN KEY (`yonghu_id`) REFERENCES `yonghu` (`id`)
);

CREATE TABLE `exam` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `kecheng_id` INT NOT NULL,
  `chapter_id` INT,
  `jiaoshi_id` INT,
  `exam_name` VARCHAR(200) NOT NULL,
  `exam_summary` TEXT,
  `duration_minutes` INT DEFAULT 60,
  `total_score` INT DEFAULT 100,
  `pass_score` INT DEFAULT 60,
  `start_time` DATETIME,
  `end_time` DATETIME,
  `exam_status` VARCHAR(50) DEFAULT 'draft',
  CONSTRAINT `fk_exam_kecheng` FOREIGN KEY (`kecheng_id`) REFERENCES `kecheng` (`id`),
  CONSTRAINT `fk_exam_chapter` FOREIGN KEY (`chapter_id`) REFERENCES `course_chapter` (`id`),
  CONSTRAINT `fk_exam_jiaoshi` FOREIGN KEY (`jiaoshi_id`) REFERENCES `jiaoshi` (`id`)
);

CREATE TABLE `exam_question` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `exam_id` INT NOT NULL,
  `kecheng_id` INT,
  `question_type` VARCHAR(50) NOT NULL,
  `question_title` TEXT NOT NULL,
  `option_json` TEXT,
  `correct_answer` VARCHAR(500),
  `question_score` INT DEFAULT 5,
  CONSTRAINT `fk_exam_question_exam` FOREIGN KEY (`exam_id`) REFERENCES `exam` (`id`),
  CONSTRAINT `fk_exam_question_kecheng` FOREIGN KEY (`kecheng_id`) REFERENCES `kecheng` (`id`)
);

CREATE TABLE `exam_record` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `exam_id` INT NOT NULL,
  `kecheng_id` INT NOT NULL,
  `yonghu_id` INT NOT NULL,
  `final_score` DECIMAL(10,2),
  `pass_status` VARCHAR(50) DEFAULT 'pending',
  `record_status` VARCHAR(50) DEFAULT 'started',
  `attempt_no` INT DEFAULT 1,
  CONSTRAINT `fk_exam_record_exam` FOREIGN KEY (`exam_id`) REFERENCES `exam` (`id`),
  CONSTRAINT `fk_exam_record_kecheng` FOREIGN KEY (`kecheng_id`) REFERENCES `kecheng` (`id`),
  CONSTRAINT `fk_exam_record_yonghu` FOREIGN KEY (`yonghu_id`) REFERENCES `yonghu` (`id`)
);

CREATE TABLE `course_credit_record` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `kecheng_id` INT NOT NULL,
  `yonghu_id` INT NOT NULL,
  `credit_score` INT DEFAULT 0,
  `grant_status` VARCHAR(50) DEFAULT '待发放',
  `grant_time` DATETIME,
  CONSTRAINT `fk_course_credit_kecheng` FOREIGN KEY (`kecheng_id`) REFERENCES `kecheng` (`id`),
  CONSTRAINT `fk_course_credit_yonghu` FOREIGN KEY (`yonghu_id`) REFERENCES `yonghu` (`id`)
);

CREATE TABLE `ai_chat_session` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `user_table` VARCHAR(32) NOT NULL,
  `role_type` VARCHAR(32),
  `session_title` VARCHAR(128) NOT NULL,
  `biz_scene` VARCHAR(64),
  `course_id` INT,
  `chapter_id` INT,
  `resource_id` INT,
  `message_count` INT DEFAULT 0,
  `status` VARCHAR(16) DEFAULT 'active',
  CONSTRAINT `fk_ai_chat_session_course` FOREIGN KEY (`course_id`) REFERENCES `kecheng` (`id`),
  CONSTRAINT `fk_ai_chat_session_chapter` FOREIGN KEY (`chapter_id`) REFERENCES `course_chapter` (`id`),
  CONSTRAINT `fk_ai_chat_session_resource` FOREIGN KEY (`resource_id`) REFERENCES `course_resource` (`id`)
);

CREATE TABLE `zuoye_question_link` (
  `zuoye_id` INT NOT NULL,
  `question_id` INT NOT NULL,
  PRIMARY KEY (`zuoye_id`, `question_id`),
  CONSTRAINT `fk_zuoye_question_link_zuoye` FOREIGN KEY (`zuoye_id`) REFERENCES `zuoye` (`id`),
  CONSTRAINT `fk_zuoye_question_link_question` FOREIGN KEY (`question_id`) REFERENCES `exam_question` (`id`)
);
"""

    return [
        SqlSection(
            title="系统总体E-R图 SQL",
            intro="本段 SQL 用于在 SQL 转 ER 图网站中生成系统总体E-R图。考虑到网站通常依赖主键和外键自动识别关系，因此这里除了总体图中的核心实体外，还补入了选课、学习进度、作业提交和作业题目关联等关系表，以便完整还原总体图关系。",
            sql=overall_sql,
        ),
        SqlSection(
            title="管理员实体E-R图 SQL",
            intro="本段 SQL 对应管理员实体E-R图，字段按现有系统 `users` 表与实体图字段整理。",
            sql="""
CREATE TABLE `users` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '编号',
  `username` VARCHAR(200) NOT NULL COMMENT '用户名',
  `password` VARCHAR(200) NOT NULL COMMENT '密码',
  `role` VARCHAR(100) NOT NULL COMMENT '角色',
  `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);
""",
        ),
        SqlSection(
            title="教师实体E-R图 SQL",
            intro="本段 SQL 对应教师实体E-R图，表名使用现有系统中的 `jiaoshi`。",
            sql="""
CREATE TABLE `jiaoshi` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '编号',
  `username` VARCHAR(200) NOT NULL COMMENT '用户名',
  `password` VARCHAR(200) NOT NULL COMMENT '密码',
  `jiaoshi_name` VARCHAR(200) NOT NULL COMMENT '姓名',
  `jiaoshi_photo` VARCHAR(200) COMMENT '头像',
  `jiaoshi_id_number` VARCHAR(200) COMMENT '身份证号',
  `jiaoshi_phone` VARCHAR(200) COMMENT '电话号码',
  `jiaoshi_email` VARCHAR(200) COMMENT '电子邮箱',
  `sex_types` INT COMMENT '性别'
);
""",
        ),
        SqlSection(
            title="学生实体E-R图 SQL",
            intro="本段 SQL 对应学生实体E-R图，表名使用现有系统中的 `yonghu`。",
            sql="""
CREATE TABLE `yonghu` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '编号',
  `username` VARCHAR(200) NOT NULL COMMENT '用户名',
  `password` VARCHAR(200) NOT NULL COMMENT '密码',
  `yonghu_name` VARCHAR(200) NOT NULL COMMENT '姓名',
  `yonghu_photo` VARCHAR(200) COMMENT '头像',
  `yonghu_id_number` VARCHAR(200) COMMENT '身份证号',
  `yonghu_phone` VARCHAR(200) COMMENT '电话号码',
  `yonghu_email` VARCHAR(200) COMMENT '电子邮箱',
  `banji_types` INT COMMENT '班级',
  `sex_types` INT COMMENT '性别'
);
""",
        ),
        SqlSection(
            title="课程实体E-R图 SQL",
            intro="本段 SQL 对应课程实体E-R图，字段按现有 `kecheng` 表与实体图要求整理。",
            sql="""
CREATE TABLE `kecheng` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '编号',
  `kecheng_name` VARCHAR(200) NOT NULL COMMENT '课程名称',
  `kecheng_photo` VARCHAR(200) COMMENT '课程封面',
  `kecheng_types` INT COMMENT '课程类型',
  `kecheng_shichang` INT COMMENT '课程时长',
  `kecheng_time` DATETIME COMMENT '开始时间',
  `kecheng_end_time` DATETIME COMMENT '结束时间',
  `credit_score` INT DEFAULT 0 COMMENT '课程学分',
  `course_status` VARCHAR(50) DEFAULT 'pending_review' COMMENT '审核状态',
  `kecheng_content` TEXT COMMENT '课程详情'
);
""",
        ),
        SqlSection(
            title="作业实体E-R图 SQL",
            intro="本段 SQL 对应作业实体E-R图，表名使用现有系统中的 `zuoye`。",
            sql="""
CREATE TABLE `zuoye` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '编号',
  `zuoye_name` VARCHAR(200) NOT NULL COMMENT '作业名称',
  `kecheng_id` INT COMMENT '课程编号',
  `chapter_id` INT COMMENT '章节编号',
  `start_time` DATETIME COMMENT '开始时间',
  `end_time` DATETIME COMMENT '结束时间',
  `score_total` INT DEFAULT 100 COMMENT '总分',
  `publish_status` VARCHAR(50) DEFAULT 'published' COMMENT '发布状态',
  `question_ids` TEXT COMMENT '题目集合',
  `zuoye_content` TEXT COMMENT '作业详情'
);
""",
        ),
        SqlSection(
            title="题目实体E-R图 SQL",
            intro="本段 SQL 对应题目实体E-R图，表名使用现有系统中的 `exam_question`。实体图中 A/B/C/D 选项拆开表达，但现有库实际使用 `option_json` 保存选项集合。",
            sql="""
CREATE TABLE `exam_question` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '编号',
  `exam_id` INT COMMENT '考试编号',
  `kecheng_id` INT COMMENT '课程编号',
  `question_type` VARCHAR(50) COMMENT '题型',
  `question_title` TEXT COMMENT '题目内容',
  `option_json` TEXT COMMENT '选项A/选项B/选项C/选项D',
  `correct_answer` VARCHAR(500) COMMENT '答案',
  `question_score` INT DEFAULT 5 COMMENT '题目分值'
);
""",
        ),
        SqlSection(
            title="考试实体E-R图 SQL",
            intro="本段 SQL 对应考试实体E-R图，表名使用现有系统中的 `exam`。",
            sql="""
CREATE TABLE `exam` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '编号',
  `kecheng_id` INT COMMENT '课程编号',
  `chapter_id` INT COMMENT '章节编号',
  `exam_name` VARCHAR(200) NOT NULL COMMENT '考试名称',
  `exam_summary` TEXT COMMENT '考试说明',
  `duration_minutes` INT DEFAULT 60 COMMENT '考试时长',
  `total_score` INT DEFAULT 100 COMMENT '总分',
  `pass_score` INT DEFAULT 60 COMMENT '及格分',
  `start_time` DATETIME COMMENT '开始时间',
  `end_time` DATETIME COMMENT '结束时间',
  `exam_status` VARCHAR(50) DEFAULT 'draft' COMMENT '考试状态'
);
""",
        ),
        SqlSection(
            title="AI会话实体E-R图 SQL",
            intro="本段 SQL 对应 AI会话 实体E-R图，表名使用现有系统中的 `ai_chat_session`。",
            sql="""
CREATE TABLE `ai_chat_session` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '编号',
  `user_id` INT NOT NULL COMMENT '用户编号',
  `user_table` VARCHAR(32) NOT NULL COMMENT '用户表',
  `role_type` VARCHAR(32) COMMENT '角色类型',
  `session_title` VARCHAR(128) NOT NULL COMMENT '会话标题',
  `biz_scene` VARCHAR(64) COMMENT '业务场景',
  `course_id` INT COMMENT '课程编号',
  `chapter_id` INT COMMENT '章节编号',
  `resource_id` INT COMMENT '资源编号',
  `message_count` INT DEFAULT 0 COMMENT '消息数',
  `status` VARCHAR(16) DEFAULT 'active' COMMENT '状态'
);
""",
        ),
    ]


def build_paragraphs() -> list[str]:
    fragments = [
        title_xml("实体关系图 SQL 说明"),
        paragraph_xml(
            "本文档用于为 SQL 转 ER 图网站提供可直接导入的 SQL。内容依据“第四章 数据库的逻辑设计”文件夹中现有 E-R 图代码、数据库脚本和后端实体类整理而成，目标是让网站能够自动生成系统总体E-R图以及各单体实体E-R图。"
        ),
        paragraph_xml(
            "说明：系统总体E-R图部分优先保证关系可识别，因此采用“主表 + 关系表 + 外键”写法；各单体实体E-R图部分则采用与单个实体图字段一致的单表 SQL，便于分别生成单体图。"
        ),
        heading1_xml("SQL 内容"),
    ]
    for section in sections():
        fragments.append(heading2_xml(section.title))
        fragments.append(paragraph_xml(section.intro))
        fragments.append(code_block_xml(section.sql))
    return fragments


def wrap_document_xml(fragments: list[str], template_bytes: bytes) -> bytes:
    root = ET.fromstring(template_bytes)
    body = root.find(qn(W_NS, "body"))
    if body is None:
        raise RuntimeError("Template document has no body element")
    sect_pr = body.find(qn(W_NS, "sectPr"))
    if sect_pr is None:
        raise RuntimeError("Template document has no sectPr element")

    new_body = ET.Element(qn(W_NS, "body"))
    wrapper = ET.fromstring(f'<root xmlns:w="{W_NS}" xmlns:r="{R_NS}">' + "".join(fragments) + "</root>")
    for child in wrapper:
        new_body.append(child)
    new_body.append(copy.deepcopy(sect_pr))
    root.remove(body)
    root.append(new_body)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def build_docx() -> Path:
    if not TEMPLATE_DOCX.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_DOCX}")

    fragments = build_paragraphs()
    with ZipFile(TEMPLATE_DOCX, "r") as zin:
        with ZipFile(OUTPUT_DOCX, "w", compression=ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    data = wrap_document_xml(fragments, data)
                zout.writestr(item, data)

    extract_dir = CHAPTER_DIR / ".tmp_er_sql_docx"
    if extract_dir.exists():
        for p in sorted(extract_dir.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            else:
                p.rmdir()
        extract_dir.rmdir()
    extract_dir.mkdir()
    with ZipFile(OUTPUT_DOCX, "r") as zf:
        zf.extractall(extract_dir)
    update_core_props(extract_dir / "docProps" / "core.xml", "实体关系图 SQL 说明")
    with ZipFile(OUTPUT_DOCX, "w", compression=ZIP_DEFLATED) as zout:
        for file_path in extract_dir.rglob("*"):
            if file_path.is_file():
                zout.write(file_path, file_path.relative_to(extract_dir).as_posix())
    for p in sorted(extract_dir.rglob("*"), reverse=True):
        if p.is_file():
            p.unlink()
        else:
            p.rmdir()
    extract_dir.rmdir()
    return OUTPUT_DOCX


def main() -> None:
    CHAPTER_DIR.mkdir(parents=True, exist_ok=True)
    print(build_docx())


if __name__ == "__main__":
    main()
