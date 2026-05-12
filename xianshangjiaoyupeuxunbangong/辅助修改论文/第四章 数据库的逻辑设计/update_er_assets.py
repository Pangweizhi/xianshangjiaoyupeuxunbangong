from __future__ import annotations

import copy
import os
import subprocess
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace("w", W_NS)


BASE_DIR = Path(__file__).resolve().parent
DOCX_PATH = BASE_DIR / "实体关系图SQL说明_工作副本.docx"
DOT_DIR = BASE_DIR / "代码和图"


PARAGRAPH_REPLACEMENTS = {
    2: "本文档用于为 SQL 转 E-R 图网站提供可直接导入的 SQL。现按“总体图突出 1-n 关系、单体图统一中文实体与中文属性”的要求，对系统总体E-R图及各单体实体E-R图的生成 SQL 进行统一整理。",
    3: "说明：系统总体E-R图部分仅保留实体核心属性，并通过外键重点表达实体之间的 1-n 关系；各单体实体E-R图部分统一采用中文表名与中文字段名，便于直接生成中文版 E-R 图。",
    6: "本段 SQL 用于在 SQL 转 E-R 图网站中生成系统总体E-R图。为避免总体图因表过多而杂乱，这里只保留核心实体与核心属性，并通过主键、外键突出管理员、教师、学生、课程、章节、资源、作业、考试、题目、考试记录、学分记录、AI会话之间的 1-n 关系。",
    7: """CREATE TABLE `管理员` (
  `管理员编号` INT PRIMARY KEY AUTO_INCREMENT,
  `用户名` VARCHAR(100) NOT NULL,
  `角色` VARCHAR(50) NOT NULL
);

CREATE TABLE `教师` (
  `教师编号` INT PRIMARY KEY AUTO_INCREMENT,
  `用户名` VARCHAR(100) NOT NULL,
  `姓名` VARCHAR(100) NOT NULL
);

CREATE TABLE `学生` (
  `学生编号` INT PRIMARY KEY AUTO_INCREMENT,
  `用户名` VARCHAR(100) NOT NULL,
  `姓名` VARCHAR(100) NOT NULL,
  `班级` VARCHAR(100)
);

CREATE TABLE `课程` (
  `课程编号` INT PRIMARY KEY AUTO_INCREMENT,
  `课程名称` VARCHAR(200) NOT NULL,
  `课程类型` VARCHAR(100),
  `教师编号` INT NOT NULL,
  `审核管理员编号` INT,
  CONSTRAINT `fk_课程_教师` FOREIGN KEY (`教师编号`) REFERENCES `教师` (`教师编号`),
  CONSTRAINT `fk_课程_管理员` FOREIGN KEY (`审核管理员编号`) REFERENCES `管理员` (`管理员编号`)
);

CREATE TABLE `章节` (
  `章节编号` INT PRIMARY KEY AUTO_INCREMENT,
  `课程编号` INT NOT NULL,
  `章节名称` VARCHAR(200) NOT NULL,
  CONSTRAINT `fk_章节_课程` FOREIGN KEY (`课程编号`) REFERENCES `课程` (`课程编号`)
);

CREATE TABLE `资源` (
  `资源编号` INT PRIMARY KEY AUTO_INCREMENT,
  `章节编号` INT NOT NULL,
  `资源名称` VARCHAR(200) NOT NULL,
  `资源类型` VARCHAR(50),
  CONSTRAINT `fk_资源_章节` FOREIGN KEY (`章节编号`) REFERENCES `章节` (`章节编号`)
);

CREATE TABLE `作业` (
  `作业编号` INT PRIMARY KEY AUTO_INCREMENT,
  `课程编号` INT NOT NULL,
  `章节编号` INT,
  `教师编号` INT NOT NULL,
  `作业名称` VARCHAR(200) NOT NULL,
  CONSTRAINT `fk_作业_课程` FOREIGN KEY (`课程编号`) REFERENCES `课程` (`课程编号`),
  CONSTRAINT `fk_作业_章节` FOREIGN KEY (`章节编号`) REFERENCES `章节` (`章节编号`),
  CONSTRAINT `fk_作业_教师` FOREIGN KEY (`教师编号`) REFERENCES `教师` (`教师编号`)
);

CREATE TABLE `考试` (
  `考试编号` INT PRIMARY KEY AUTO_INCREMENT,
  `课程编号` INT NOT NULL,
  `章节编号` INT,
  `考试名称` VARCHAR(200) NOT NULL,
  CONSTRAINT `fk_考试_课程` FOREIGN KEY (`课程编号`) REFERENCES `课程` (`课程编号`),
  CONSTRAINT `fk_考试_章节` FOREIGN KEY (`章节编号`) REFERENCES `章节` (`章节编号`)
);

CREATE TABLE `题目` (
  `题目编号` INT PRIMARY KEY AUTO_INCREMENT,
  `考试编号` INT NOT NULL,
  `题型` VARCHAR(50) NOT NULL,
  `题目内容` TEXT NOT NULL,
  CONSTRAINT `fk_题目_考试` FOREIGN KEY (`考试编号`) REFERENCES `考试` (`考试编号`)
);

CREATE TABLE `考试记录` (
  `记录编号` INT PRIMARY KEY AUTO_INCREMENT,
  `考试编号` INT NOT NULL,
  `学生编号` INT NOT NULL,
  `成绩` DECIMAL(10,2),
  CONSTRAINT `fk_考试记录_考试` FOREIGN KEY (`考试编号`) REFERENCES `考试` (`考试编号`),
  CONSTRAINT `fk_考试记录_学生` FOREIGN KEY (`学生编号`) REFERENCES `学生` (`学生编号`)
);

CREATE TABLE `学分记录` (
  `记录编号` INT PRIMARY KEY AUTO_INCREMENT,
  `课程编号` INT NOT NULL,
  `学生编号` INT NOT NULL,
  `学分` INT DEFAULT 0,
  CONSTRAINT `fk_学分记录_课程` FOREIGN KEY (`课程编号`) REFERENCES `课程` (`课程编号`),
  CONSTRAINT `fk_学分记录_学生` FOREIGN KEY (`学生编号`) REFERENCES `学生` (`学生编号`)
);

CREATE TABLE `AI会话` (
  `会话编号` INT PRIMARY KEY AUTO_INCREMENT,
  `学生编号` INT NOT NULL,
  `课程编号` INT,
  `章节编号` INT,
  `会话标题` VARCHAR(200) NOT NULL,
  CONSTRAINT `fk_AI会话_学生` FOREIGN KEY (`学生编号`) REFERENCES `学生` (`学生编号`),
  CONSTRAINT `fk_AI会话_课程` FOREIGN KEY (`课程编号`) REFERENCES `课程` (`课程编号`),
  CONSTRAINT `fk_AI会话_章节` FOREIGN KEY (`章节编号`) REFERENCES `章节` (`章节编号`)
);""",
    9: "本段 SQL 对应管理员实体E-R图，统一采用中文实体名与中文属性名。",
    10: """CREATE TABLE `管理员` (
  `编号` INT PRIMARY KEY AUTO_INCREMENT,
  `用户名` VARCHAR(200) NOT NULL,
  `密码` VARCHAR(200) NOT NULL,
  `角色` VARCHAR(100) NOT NULL,
  `创建时间` DATETIME DEFAULT CURRENT_TIMESTAMP
);""",
    12: "本段 SQL 对应教师实体E-R图，统一采用中文实体名与中文属性名。",
    13: """CREATE TABLE `教师` (
  `编号` INT PRIMARY KEY AUTO_INCREMENT,
  `用户名` VARCHAR(200) NOT NULL,
  `密码` VARCHAR(200) NOT NULL,
  `姓名` VARCHAR(200) NOT NULL,
  `头像` VARCHAR(200),
  `身份证号` VARCHAR(200),
  `电话号码` VARCHAR(200),
  `电子邮箱` VARCHAR(200),
  `性别` INT
);""",
    15: "本段 SQL 对应学生实体E-R图，统一采用中文实体名与中文属性名。",
    16: """CREATE TABLE `学生` (
  `编号` INT PRIMARY KEY AUTO_INCREMENT,
  `用户名` VARCHAR(200) NOT NULL,
  `密码` VARCHAR(200) NOT NULL,
  `姓名` VARCHAR(200) NOT NULL,
  `头像` VARCHAR(200),
  `身份证号` VARCHAR(200),
  `电话号码` VARCHAR(200),
  `电子邮箱` VARCHAR(200),
  `班级` INT,
  `性别` INT
);""",
    18: "本段 SQL 对应课程实体E-R图，统一采用中文实体名与中文属性名。",
    19: """CREATE TABLE `课程` (
  `编号` INT PRIMARY KEY AUTO_INCREMENT,
  `课程名称` VARCHAR(200) NOT NULL,
  `课程封面` VARCHAR(200),
  `课程类型` INT,
  `课程时长` INT,
  `开始时间` DATETIME,
  `结束时间` DATETIME,
  `课程学分` INT DEFAULT 0,
  `审核状态` VARCHAR(50) DEFAULT 'pending_review',
  `课程详情` TEXT
);""",
    21: "本段 SQL 对应作业实体E-R图，统一采用中文实体名与中文属性名。",
    22: """CREATE TABLE `作业` (
  `编号` INT PRIMARY KEY AUTO_INCREMENT,
  `作业名称` VARCHAR(200) NOT NULL,
  `课程编号` INT,
  `章节编号` INT,
  `开始时间` DATETIME,
  `结束时间` DATETIME,
  `总分` INT DEFAULT 100,
  `发布状态` VARCHAR(50) DEFAULT 'published',
  `题目集合` TEXT,
  `作业详情` TEXT
);""",
    24: "本段 SQL 对应题目实体E-R图，统一采用中文实体名与中文属性名。为便于单体图展示，选项 A/B/C/D 继续拆分为独立属性。",
    25: """CREATE TABLE `题目` (
  `编号` INT PRIMARY KEY AUTO_INCREMENT,
  `考试编号` INT,
  `课程编号` INT,
  `题型` VARCHAR(50),
  `题目内容` TEXT,
  `选项A` TEXT,
  `选项B` TEXT,
  `选项C` TEXT,
  `选项D` TEXT,
  `答案` VARCHAR(500),
  `题目分值` INT DEFAULT 5
);""",
    27: "本段 SQL 对应考试实体E-R图，统一采用中文实体名与中文属性名。",
    28: """CREATE TABLE `考试` (
  `编号` INT PRIMARY KEY AUTO_INCREMENT,
  `课程编号` INT,
  `章节编号` INT,
  `考试名称` VARCHAR(200) NOT NULL,
  `考试说明` TEXT,
  `考试时长` INT DEFAULT 60,
  `总分` INT DEFAULT 100,
  `及格分` INT DEFAULT 60,
  `开始时间` DATETIME,
  `结束时间` DATETIME,
  `考试状态` VARCHAR(50) DEFAULT 'draft'
);""",
    30: "本段 SQL 对应 AI会话 实体E-R图，统一采用中文实体名与中文属性名。",
    31: """CREATE TABLE `AI会话` (
  `编号` INT PRIMARY KEY AUTO_INCREMENT,
  `用户编号` INT NOT NULL,
  `用户表` VARCHAR(32) NOT NULL,
  `角色类型` VARCHAR(32),
  `会话标题` VARCHAR(128) NOT NULL,
  `业务场景` VARCHAR(64),
  `课程编号` INT,
  `章节编号` INT,
  `资源编号` INT,
  `消息数` INT DEFAULT 0,
  `状态` VARCHAR(16) DEFAULT 'active'
);""",
}


ENTITY_DOTS = {
    "管理员实体E-R图.dot": ("管理员", ["编号", "用户名", "密码", "角色", "创建时间"]),
    "教师实体E-R图.dot": ("教师", ["编号", "用户名", "密码", "姓名", "头像", "身份证号", "电话号码", "电子邮箱", "性别"]),
    "学生实体E-R图.dot": ("学生", ["编号", "用户名", "密码", "姓名", "头像", "身份证号", "电话号码", "电子邮箱", "班级", "性别"]),
    "课程实体E-R图.dot": ("课程", ["编号", "课程名称", "课程封面", "课程类型", "课程时长", "开始时间", "结束时间", "课程学分", "审核状态", "课程详情"]),
    "作业实体E-R图.dot": ("作业", ["编号", "作业名称", "课程编号", "章节编号", "开始时间", "结束时间", "总分", "发布状态", "题目集合", "作业详情"]),
    "题目实体E-R图.dot": ("题目", ["编号", "考试编号", "课程编号", "题型", "题目内容", "选项A", "选项B", "选项C", "选项D", "答案", "题目分值"]),
    "考试实体E-R图.dot": ("考试", ["编号", "课程编号", "章节编号", "考试名称", "考试说明", "考试时长", "总分", "及格分", "开始时间", "结束时间", "考试状态"]),
    "AI会话实体E-R图.dot": ("AI会话", ["编号", "用户编号", "用户表", "角色类型", "会话标题", "业务场景", "课程编号", "章节编号", "资源编号", "消息数", "状态"]),
}


OVERALL_DOT = """digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="系统总体E-R图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=polyline, nodesep=0.55, ranksep=0.85, pad=0.2, margin=0.15];
  node [shape=box, fontname="Microsoft YaHei", fontsize=10, color="#333333", penwidth=1.2, style="rounded,filled", fillcolor="#ffffff", margin="0.12,0.08"];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#555555", penwidth=1.0, arrowsize=0.8];

  管理员 [label="管理员\\n管理员编号\\n用户名\\n角色"];
  教师 [label="教师\\n教师编号\\n用户名\\n姓名"];
  学生 [label="学生\\n学生编号\\n用户名\\n姓名\\n班级"];
  课程 [label="课程\\n课程编号\\n课程名称\\n课程类型\\n教师编号\\n审核管理员编号"];
  章节 [label="章节\\n章节编号\\n课程编号\\n章节名称"];
  资源 [label="资源\\n资源编号\\n章节编号\\n资源名称\\n资源类型"];
  作业 [label="作业\\n作业编号\\n课程编号\\n章节编号\\n教师编号\\n作业名称"];
  考试 [label="考试\\n考试编号\\n课程编号\\n章节编号\\n考试名称"];
  题目 [label="题目\\n题目编号\\n考试编号\\n题型\\n题目内容"];
  考试记录 [label="考试记录\\n记录编号\\n考试编号\\n学生编号\\n成绩"];
  学分记录 [label="学分记录\\n记录编号\\n课程编号\\n学生编号\\n学分"];
  AI会话 [label="AI会话\\n会话编号\\n学生编号\\n课程编号\\n章节编号\\n会话标题"];

  管理员 -> 课程 [label="1:n 审核"];
  教师 -> 课程 [label="1:n 创建"];
  课程 -> 章节 [label="1:n 包含"];
  章节 -> 资源 [label="1:n 包含"];
  教师 -> 作业 [label="1:n 发布"];
  课程 -> 作业 [label="1:n 布置"];
  章节 -> 作业 [label="1:n 对应"];
  课程 -> 考试 [label="1:n 包含"];
  章节 -> 考试 [label="1:n 对应"];
  考试 -> 题目 [label="1:n 生成"];
  考试 -> 考试记录 [label="1:n 产生"];
  学生 -> 考试记录 [label="1:n 参加"];
  课程 -> 学分记录 [label="1:n 发放"];
  学生 -> 学分记录 [label="1:n 获得"];
  学生 -> AI会话 [label="1:n 发起"];
  课程 -> AI会话 [label="1:n 关联"];
  章节 -> AI会话 [label="1:n 关联"];

  { rank=same; 管理员; 教师; 学生; }
  { rank=same; 课程; 学分记录; AI会话; }
  { rank=same; 章节; 作业; 考试; }
  { rank=same; 资源; 题目; 考试记录; }
}"""


def qn(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def replace_paragraph_text(paragraph: ET.Element, new_text: str) -> None:
    template_run = paragraph.find(qn("r"))
    template_rpr = None
    if template_run is not None:
        template_rpr = template_run.find(qn("rPr"))
    ppr = paragraph.find(qn("pPr"))
    for child in list(paragraph):
        if child is not ppr:
            paragraph.remove(child)
    lines = new_text.splitlines()
    if not lines:
        lines = [""]
    for idx, line in enumerate(lines):
        run = ET.SubElement(paragraph, qn("r"))
        if template_rpr is not None:
            run.append(copy.deepcopy(template_rpr))
        text_el = ET.SubElement(run, qn("t"))
        text_el.set(f"{{{XML_NS}}}space", "preserve")
        text_el.text = line
        if idx != len(lines) - 1:
            br_run = ET.SubElement(paragraph, qn("r"))
            ET.SubElement(br_run, qn("br"))


def update_docx() -> None:
    extract_dir = BASE_DIR / "_docx_work"
    if extract_dir.exists():
        for path in sorted(extract_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            else:
                path.rmdir()
        extract_dir.rmdir()
    extract_dir.mkdir()
    with zipfile.ZipFile(DOCX_PATH, "r") as zf:
        zf.extractall(extract_dir)

    document_xml = extract_dir / "word" / "document.xml"
    tree = ET.parse(document_xml)
    root = tree.getroot()
    body = root.find(qn("body"))
    if body is None:
        raise RuntimeError("document.xml missing body")
    paragraphs = [child for child in list(body) if child.tag == qn("p")]
    for index, replacement in PARAGRAPH_REPLACEMENTS.items():
        replace_paragraph_text(paragraphs[index - 1], replacement)
    tree.write(document_xml, encoding="UTF-8", xml_declaration=True)

    out_docx = BASE_DIR / "实体关系图SQL说明.docx"
    if out_docx.exists():
        out_docx.unlink()
    with zipfile.ZipFile(out_docx, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(extract_dir.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(extract_dir))


def entity_dot_content(title: str, attributes: list[str]) -> str:
    lines = [
        "digraph G {",
        f'  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="{title}实体E-R图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=false, nodesep=0.45, ranksep=0.6, pad=0.18, margin=0.12, size="8,5!"];',
        '  node [fontname="Microsoft YaHei", fontsize=10, color="#333333", penwidth=1.35];',
        '  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7, dir=none];',
        "",
        f'  entity [label="{title}", shape=box, style="rounded,filled", fillcolor="#ffffff"];',
    ]
    for idx, attr in enumerate(attributes, start=1):
        lines.append(f'  a{idx} [label="{attr}", shape=ellipse, style="filled", fillcolor="#ffffff"];')
        lines.append(f"  entity -> a{idx};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def update_dot_and_svg() -> None:
    for filename, (title, attributes) in ENTITY_DOTS.items():
        dot_path = DOT_DIR / filename
        dot_path.write_text(entity_dot_content(title, attributes), encoding="utf-8")
        svg_path = dot_path.with_suffix(".svg")
        subprocess.run(["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)], check=True)

    overall_path = DOT_DIR / "系统总体E-R图.dot"
    overall_path.write_text(OVERALL_DOT + "\n", encoding="utf-8")
    subprocess.run(["dot", "-Tsvg", str(overall_path), "-o", str(overall_path.with_suffix(".svg"))], check=True)


def main() -> None:
    update_docx()
    update_dot_and_svg()


if __name__ == "__main__":
    main()
