from __future__ import annotations

import copy
import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
CHAPTER_DIR = ROOT / "辅助修改论文" / "第四章 系统总体功能结构设计、系统功能设计"
FIG_DIR = CHAPTER_DIR / "代码和图"
TMP_DIR = ROOT / ".tmp"
TMP_TEMPLATE = TMP_DIR / "chapter4_ref_copy.docx"
REFERENCE_DOCX = CHAPTER_DIR / "参考文档.docx"
OUTPUT_DOCX = CHAPTER_DIR / "系统总体功能结构设计和系统功能设计.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
CONTENT_WIDTH = 9026

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)
ET.register_namespace("cp", CP_NS)
ET.register_namespace("dc", DC_NS)


def qn(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def run_xml(
    text: str,
    *,
    font: str = "宋体",
    size: int = 24,
    bold: bool = False,
    italic: bool = False,
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
    if italic:
        rpr += "<w:i/><w:iCs/>"
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
    before: int = 0,
    after: int = 120,
    line: int = 360,
    font: str = "宋体",
    size: int = 24,
    bold: bool = False,
    italic: bool = False,
    color: str = "000000",
    style: str | None = None,
) -> str:
    ppr = ["<w:pPr>"]
    if style:
        ppr.append(f"<w:pStyle w:val=\"{style}\"/>")
    ppr.append(f"<w:jc w:val=\"{align}\"/>")
    ppr.append(
        f"<w:spacing w:before=\"{before}\" w:after=\"{after}\" w:line=\"{line}\" w:lineRule=\"auto\"/>"
    )
    ppr.append(f"<w:ind w:firstLine=\"{first_line}\"/>")
    ppr.append("</w:pPr>")
    return (
        "<w:p>"
        + "".join(ppr)
        + run_xml(text, font=font, size=size, bold=bold, italic=italic, color=color)
        + "</w:p>"
    )


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


def caption_xml(text: str) -> str:
    return paragraph_xml(
        text,
        align="center",
        first_line=0,
        before=50,
        after=80,
        line=280,
        font="宋体",
        size=21,
    )


def table_xml(
    rows: list[list[list[str]]],
    widths: list[int],
    *,
    header_rows: int = 0,
    header_fill: str = "EDEDED",
    body_fill: str = "FFFFFF",
    border_color: str = "BFBFBF",
    row_height: int | None = None,
    align: str = "center",
) -> str:
    total_width = sum(widths)
    tblpr = [
        "<w:tblPr>",
        f"<w:tblW w:w=\"{total_width}\" w:type=\"dxa\"/>",
        "<w:tblLayout w:type=\"fixed\"/>",
        '<w:jc w:val="center"/>',
        "<w:tblBorders>",
        f'<w:top w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>',
        f'<w:left w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>',
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>',
        f'<w:right w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>',
        f'<w:insideH w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>',
        f'<w:insideV w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>',
        "</w:tblBorders>",
        '<w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar>',
        "</w:tblPr>",
    ]
    grid = "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"

    tr_xml: list[str] = []
    for row_index, row in enumerate(rows):
        trpr = ""
        if row_height is not None:
            trpr = (
                "<w:trPr>"
                f'<w:trHeight w:val="{row_height}" w:hRule="atLeast"/>'
                "</w:trPr>"
            )
        cells: list[str] = []
        for col_index, cell in enumerate(row):
            fill = header_fill if row_index < header_rows else body_fill
            tcpr = (
                "<w:tcPr>"
                f'<w:tcW w:w="{widths[col_index]}" w:type="dxa"/>'
                f'<w:vAlign w:val="{align}"/>'
                '<w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
                '<w:bottom w:w="80" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tcMar>'
                f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
                "</w:tcPr>"
            )
            cells.append("<w:tc>" + tcpr + "".join(cell) + "</w:tc>")
        tr_xml.append("<w:tr>" + trpr + "".join(cells) + "</w:tr>")
    return "<w:tbl>" + "".join(tblpr) + grid + "".join(tr_xml) + "</w:tbl>"


def figure_box_xml(fig_no: str, fig_title: str, filename: str) -> str:
    box_rows = [
        [
            [
                paragraph_xml(
                    f"此处插入 {fig_no}，对应文件：{filename}",
                    align="center",
                    first_line=0,
                    before=80,
                    after=40,
                    line=300,
                    font="黑体",
                    size=22,
                    bold=True,
                    color="444444",
                ),
                paragraph_xml(
                    "插图与对应 dot 代码已同步生成在“代码和图”文件夹中，可在 Word 中手动插入 SVG 图。",
                    align="center",
                    first_line=0,
                    before=0,
                    after=80,
                    line=300,
                    font="宋体",
                    size=21,
                    italic=True,
                    color="666666",
                ),
            ]
        ]
    ]
    return table_xml(
        box_rows,
        [CONTENT_WIDTH],
        header_rows=0,
        header_fill="FFFFFF",
        body_fill="FAFAFA",
        border_color="BFBFBF",
        row_height=1400,
        align="center",
    ) + caption_xml(f"{fig_no} {fig_title}")


def blank_xml(after: int = 0) -> str:
    return (
        "<w:p><w:pPr><w:jc w:val=\"both\"/>"
        f"<w:spacing w:before=\"0\" w:after=\"{after}\" w:line=\"240\" w:lineRule=\"auto\"/>"
        "<w:ind w:firstLine=\"0\"/></w:pPr></w:p>"
    )


DIAGRAMS: list[dict[str, str]] = [
    {
        "filename": "图4-1_系统总体架构设计图",
        "caption": "系统总体架构设计图",
        "dot": r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="系统总体架构设计图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.35, ranksep=0.48, pad=0.18, margin=0.12, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=11, shape=box, style="rounded,filled", fillcolor="white", color="#4e79a7", penwidth=1.4, margin="0.11,0.08"];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#3f3f3f", penwidth=1.05, arrowsize=0.7];

  users [label="用户与访问层\n学生 / 教师 / 管理员", fillcolor="#f8fbff"];
  ui_student [label="学生端 Web", fillcolor="#f8fbff"];
  ui_teacher [label="教师端 Web", fillcolor="#f8fbff"];
  ui_admin [label="管理端 Web", fillcolor="#f8fbff"];
  auth [label="登录认证", fillcolor="#eef5ff"];
  course_api [label="课程接口", fillcolor="#eef5ff"];
  learn_api [label="学习接口", fillcolor="#eef5ff"];
  exam_api [label="考试接口", fillcolor="#eef5ff"];
  ai_api [label="AI 接口", fillcolor="#eef5ff"];
  teach_service [label="教学服务", fillcolor="#effaf2", color="#4f9964"];
  learn_service [label="学习服务", fillcolor="#effaf2", color="#4f9964"];
  exam_service [label="考试服务", fillcolor="#effaf2", color="#4f9964"];
  ai_service [label="AI 服务", fillcolor="#effaf2", color="#4f9964"];
  dao [label="数据访问层\nMapper / DAO", fillcolor="#f8fbff"];
  mysql [label="MySQL 数据库", fillcolor="#fff5e8", color="#d78b29"];
  files [label="文件 / 图片存储", fillcolor="#fff5e8", color="#d78b29"];
  external [label="第三方 AI 接口", fillcolor="#fff5e8", color="#d78b29"];

  users -> ui_student;
  users -> ui_teacher;
  users -> ui_admin;

  ui_student -> auth;
  ui_student -> course_api;
  ui_student -> learn_api;
  ui_student -> exam_api;
  ui_student -> ai_api;

  ui_teacher -> course_api;
  ui_teacher -> learn_api;
  ui_teacher -> exam_api;
  ui_teacher -> ai_api;

  ui_admin -> auth;
  ui_admin -> course_api;
  ui_admin -> exam_api;
  ui_admin -> ai_api;

  auth -> dao;
  course_api -> teach_service;
  learn_api -> learn_service;
  exam_api -> exam_service;
  ai_api -> ai_service;

  teach_service -> dao;
  learn_service -> dao;
  exam_service -> dao;
  ai_service -> dao;

  dao -> mysql;
  dao -> files;
  dao -> external;

  { rank = same; users; }
  { rank = same; ui_student; ui_teacher; ui_admin; }
  { rank = same; auth; course_api; learn_api; exam_api; ai_api; }
  { rank = same; teach_service; learn_service; exam_service; ai_service; }
  { rank = same; dao; }
  { rank = same; mysql; files; external; }
}
''',
    },
    {
        "filename": "图4-2_系统功能结构设计图",
        "caption": "系统功能结构设计图",
        "dot": r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="系统功能结构设计图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.35, ranksep=0.42, pad=0.18, margin=0.12, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=11, shape=box, style="rounded,filled", fillcolor="white", color="#4d4d4d", penwidth=1.35, margin="0.10,0.08"];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#3f3f3f", penwidth=1.05, arrowsize=0.7];

  root [label="线上教育培训办公系统", fillcolor="#f6f9ff", fontsize=12];

  base [label="基础支撑模块", fillcolor="#eef5ff", color="#5d7db3"];
  core [label="核心教学模块", fillcolor="#eef9f1", color="#5b9b6d"];
  ai [label="智能AI模块", fillcolor="#fff5e8", color="#d78b29"];

  login [label="账号登录"];
  center [label="个人中心"];
  dict [label="字典管理"];
  config [label="系统配置"];
  notice [label="公告管理"];
  forum [label="论坛交流"];

  course [label="课程管理"];
  chapter [label="章节管理"];
  resource [label="资源管理"];
  enroll [label="选课管理"];
  progress [label="学习进度"];
  homework [label="作业管理"];
  submit [label="作业提交"];
  exam [label="考试管理"];
  question [label="题库管理"];
  record [label="考试记录"];
  score [label="成绩统计"];
  settlement [label="结课与学分"];

  chat [label="AI会话"];
  message [label="AI消息记录"];
  generate [label="AI题目生成"];
  assistant [label="问答助手"];

  root -> base;
  root -> core;
  root -> ai;

  base -> login;
  base -> center;
  base -> dict;
  base -> config;
  base -> notice;
  base -> forum;

  core -> course;
  course -> chapter;
  chapter -> resource;
  resource -> enroll;
  enroll -> progress;
  progress -> homework;
  homework -> submit;
  submit -> exam;
  exam -> question;
  question -> record;
  record -> score;
  score -> settlement;

  ai -> chat;
  chat -> message;
  message -> generate;
  generate -> assistant;

  { rank = same; base; core; ai; }
  { rank = same; login; course; chat; }
  { rank = same; center; chapter; message; }
  { rank = same; dict; resource; generate; }
  { rank = same; config; enroll; assistant; }
  { rank = same; notice; progress; }
  { rank = same; forum; homework; }
  { rank = same; submit; }
  { rank = same; exam; }
  { rank = same; question; }
  { rank = same; record; }
  { rank = same; score; }
  { rank = same; settlement; }
}
''',
    },
    {
        "filename": "图4-3_教师课程建设与发布流程图",
        "caption": "教师课程建设与发布流程图",
        "dot": r'''
digraph G {
  graph [rankdir=TB, splines=ortho, nodesep=0.35, ranksep=0.65];
  node [shape=box, style="rounded,filled", fontname="Microsoft YaHei", fontsize=12, color="#5D8CC0", fillcolor="#EEF5FF"];
  edge [color="#6C7F93", arrowsize=0.75];

  start [shape=ellipse, label="开始", fillcolor="#DCEBFA"];
  login [label="教师登录系统"];
  course [label="创建或编辑课程"];
  submit [label="提交课程审核"];
  review [shape=diamond, label="审核通过？", fillcolor="#FFF5E8", color="#D08A3C"];
  revise [label="根据驳回意见修改课程"];
  chapter [label="维护课程章节"];
  resource [label="上传资源并提交资源审核"];
  publish [label="发布作业、题库与考试"];
  tracking [label="查看选课、进度、作业和考试结果"];
  end [shape=ellipse, label="结束", fillcolor="#DCEBFA"];

  start -> login -> course -> submit -> review;
  review -> revise [label="否"];
  revise -> course;
  review -> chapter [label="是"];
  chapter -> resource -> publish -> tracking -> end;
}
''',
    },
    {
        "filename": "图4-4_学生学习作业与考试流程图",
        "caption": "学生学习、作业与考试流程图",
        "dot": r'''
digraph G {
  graph [rankdir=TB, splines=ortho, nodesep=0.35, ranksep=0.65];
  node [shape=box, style="rounded,filled", fontname="Microsoft YaHei", fontsize=12, color="#D08A3C", fillcolor="#FFF6EA"];
  edge [color="#8B7E6A", arrowsize=0.75];

  start [shape=ellipse, label="开始", fillcolor="#FBE7CF"];
  login [label="学生登录系统"];
  browse [label="浏览课程并查看详情"];
  enroll [label="选择已审核通过课程"];
  study [label="按章节学习视频与资源"];
  progress [label="系统保存学习进度"];
  homework [label="进入作业并提交答案"];
  examCheck [shape=diamond, label="学习进度达到 100%？", fillcolor="#FFF1DF", color="#D08A3C"];
  exam [label="参加考试并提交试卷"];
  settle [label="系统汇总进度、作业、考试结果"];
  credit [shape=diamond, label="满足结课条件？", fillcolor="#FFF1DF", color="#D08A3C"];
  finish [label="结课并发放学分"];
  continueStudy [label="继续学习或补交作业"];
  end [shape=ellipse, label="结束", fillcolor="#FBE7CF"];

  start -> login -> browse -> enroll -> study -> progress -> homework -> examCheck;
  examCheck -> continueStudy [label="否"];
  continueStudy -> study;
  examCheck -> exam [label="是"];
  exam -> settle -> credit;
  credit -> finish [label="是"];
  credit -> continueStudy [label="否"];
  finish -> end;
}
''',
    },
    {
        "filename": "图4-5_管理员审核与运行维护流程图",
        "caption": "管理员审核与运行维护流程图",
        "dot": r'''
digraph G {
  graph [rankdir=TB, splines=ortho, nodesep=0.35, ranksep=0.65];
  node [shape=box, style="rounded,filled", fontname="Microsoft YaHei", fontsize=12, color="#6B9B6B", fillcolor="#EEF7F0"];
  edge [color="#6F8B72", arrowsize=0.75];

  start [shape=ellipse, label="开始", fillcolor="#DDEEDC"];
  login [label="管理员登录系统"];
  courseReview [label="审核教师提交的课程"];
  resourceReview [label="审核章节资源与发布内容"];
  userManage [label="维护教师、学生与基础数据"];
  noticeManage [label="维护公告、会议和论坛内容"];
  dashboard [label="查看统计概览与运行情况"];
  optimize [shape=diamond, label="发现异常或配置需求？", fillcolor="#EAF5EA"];
  adjust [label="调整字典、类型或管理策略"];
  end [shape=ellipse, label="结束", fillcolor="#DDEEDC"];

  start -> login -> courseReview -> resourceReview -> userManage -> noticeManage -> dashboard -> optimize;
  optimize -> adjust [label="是"];
  adjust -> dashboard;
  optimize -> end [label="否"];
}
''',
    },
    {
        "filename": "图4-6_学生角色用例图",
        "caption": "学生角色用例图",
        "dot": r'''
digraph G {
  graph [rankdir=LR, splines=true, nodesep=0.5, ranksep=1.0];
  node [fontname="Microsoft YaHei", fontsize=12];
  edge [color="#7A8A99"];

  actor [shape=plaintext, label="学生"];
  subgraph cluster_sys {
    label="线上教育培训办公系统";
    color="#D8D8D8";
    style="rounded";
    uc1 [shape=ellipse, label="登录"];
    uc2 [shape=ellipse, label="浏览课程"];
    uc3 [shape=ellipse, label="选课"];
    uc4 [shape=ellipse, label="学习章节资源"];
    uc5 [shape=ellipse, label="提交作业"];
    uc6 [shape=ellipse, label="参加考试"];
    uc7 [shape=ellipse, label="查看成绩、结课与学分"];
    uc8 [shape=ellipse, label="论坛交流与查看会议"];
    uc9 [shape=ellipse, label="智能问答"];
  }
  actor -> {uc1 uc2 uc3 uc4 uc5 uc6 uc7 uc8 uc9};
}
''',
    },
    {
        "filename": "图4-7_教师角色用例图",
        "caption": "教师角色用例图",
        "dot": r'''
digraph G {
  graph [rankdir=LR, splines=true, nodesep=0.5, ranksep=1.0];
  node [fontname="Microsoft YaHei", fontsize=12];
  edge [color="#7A8A99"];

  actor [shape=plaintext, label="教师"];
  subgraph cluster_sys {
    label="线上教育培训办公系统";
    color="#D8D8D8";
    style="rounded";
    uc1 [shape=ellipse, label="登录"];
    uc2 [shape=ellipse, label="维护课程"];
    uc3 [shape=ellipse, label="维护章节与资源"];
    uc4 [shape=ellipse, label="发布作业"];
    uc5 [shape=ellipse, label="维护题库"];
    uc6 [shape=ellipse, label="发布考试"];
    uc7 [shape=ellipse, label="批改作业与阅卷"];
    uc8 [shape=ellipse, label="查看选课与学习进度"];
    uc9 [shape=ellipse, label="AI 辅助出题"];
  }
  actor -> {uc1 uc2 uc3 uc4 uc5 uc6 uc7 uc8 uc9};
}
''',
    },
    {
        "filename": "图4-8_管理员角色用例图",
        "caption": "管理员角色用例图",
        "dot": r'''
digraph G {
  graph [rankdir=LR, splines=true, nodesep=0.5, ranksep=1.0];
  node [fontname="Microsoft YaHei", fontsize=12];
  edge [color="#7A8A99"];

  actor [shape=plaintext, label="管理员"];
  subgraph cluster_sys {
    label="线上教育培训办公系统";
    color="#D8D8D8";
    style="rounded";
    uc1 [shape=ellipse, label="登录"];
    uc2 [shape=ellipse, label="审核课程"];
    uc3 [shape=ellipse, label="审核资源"];
    uc4 [shape=ellipse, label="用户管理"];
    uc5 [shape=ellipse, label="字典与类型管理"];
    uc6 [shape=ellipse, label="公告、会议与论坛管理"];
    uc7 [shape=ellipse, label="统计概览"];
    uc8 [shape=ellipse, label="系统运行维护"];
    uc9 [shape=ellipse, label="后台智能问答"];
  }
  actor -> {uc1 uc2 uc3 uc4 uc5 uc6 uc7 uc8 uc9};
}
''',
    },
]


def build_body_xml() -> str:
    parts: list[str] = []
    parts.append(title_xml("系统设计"))

    parts.append(heading1_xml("系统总体架构设计"))
    parts.append(
        paragraph_xml(
            "本系统以线上教育培训业务为中心，在保留原有基础管理能力的同时，围绕课程建设、章节学习、作业考试、成绩汇总、结课学分和智能问答等主链路进行扩展。"
            "系统在整体上形成了学生学习端、教师与管理员管理端、业务服务层、数据层以及 AI 能力协同配合的分层架构，以保证教学业务闭环能够稳定运行。"
        )
    )
    parts.append(
        paragraph_xml(
            "系统总体架构设计图如下，见图4.1。图中从表示层、业务服务层、数据层和智能能力接口四个方面展示了现有系统的主要组成关系，能够反映当前仓库中前后端、数据库和智能服务的实际协作方式。"
        )
    )
    parts.append(figure_box_xml("图4.1", "系统总体架构设计图", "图4-1_系统总体架构设计图.svg"))

    parts.append(heading1_xml("系统功能设计"))
    parts.append(
        paragraph_xml(
            "本系统围绕“课程建设与审核、学生选课学习、作业考试评价、结课学分发放、公告与运营支撑、智能问答与 AI 出题”展开功能设计。"
            "通过系统功能结构划分、核心业务流程建模以及角色用例分析，可以对现有系统的功能边界和职责分工进行系统化描述，为后续实现章节和测试章节提供设计依据。"
        )
    )

    parts.append(heading2_xml("系统功能结构设计"))
    parts.append(
        paragraph_xml(
            "系统功能结构设计从整体角度对系统进行模块划分，将现有系统划分为学生学习端、教师教学端、管理运营端以及系统支撑与智能服务四大部分。"
            "各功能域之间通过课程、作业、考试、成绩和 AI 服务等核心对象发生关联，共同支撑线上教育培训办公系统的稳定运行。"
        )
    )
    parts.append(figure_box_xml("图4.2", "系统功能结构设计图", "图4-2_系统功能结构设计图.svg"))
    parts.append(paragraph_xml("如图4.2所示，系统功能主要包括："))
    parts.append(
        paragraph_xml(
            "（1）学生学习端：面向学生角色，提供课程浏览、选课、章节学习、学习进度记录、作业提交、在线考试、成绩查询、结课状态查看、论坛交流和智能问答等功能。"
        )
    )
    parts.append(
        paragraph_xml(
            "（2）教师教学端：面向教师角色，提供课程维护、章节管理、资源维护、作业发布、题库维护、考试发布、作业批改、阅卷以及学习进度查看等教学管理功能。"
        )
    )
    parts.append(
        paragraph_xml(
            "（3）管理运营端：面向管理员角色，提供课程审核、资源审核、用户管理、公告管理、会议管理、基础字典管理和统计概览等运行维护能力。"
        )
    )
    parts.append(
        paragraph_xml(
            "（4）系统支撑与智能服务：为整套业务提供登录认证、角色过滤、文件上传下载、结课判定、学分发放、智能问答、推荐问题以及 AI 题目草稿生成等通用能力。"
        )
    )

    parts.append(heading2_xml("核心业务流程设计"))
    parts.append(
        paragraph_xml(
            "为了更清晰地展示现有系统在关键场景下的处理逻辑，本文选择教师课程建设、学生学习与考试、管理员审核与运维三类典型业务过程进行流程建模。"
            "这些流程均能够在当前仓库的控制器、服务层和新前端页面中找到对应实现。"
        )
    )
    parts.append(
        paragraph_xml(
            "如图4.3所示，该流程图描述教师从登录系统、创建课程、提交审核、维护章节与资源，到发布作业和考试、跟踪学生学习结果的全过程，反映了教师端的课程建设主链路。"
        )
    )
    parts.append(figure_box_xml("图4.3", "教师课程建设与发布流程图", "图4-3_教师课程建设与发布流程图.svg"))
    parts.append(
        paragraph_xml(
            "如图4.4所示，该流程图描述学生在系统中的主要学习路径，包括浏览课程、选课、章节学习、进度记录、作业提交、考试作答以及结课学分判定等关键环节，体现了课程学习闭环。"
        )
    )
    parts.append(figure_box_xml("图4.4", "学生学习、作业与考试流程图", "图4-4_学生学习作业与考试流程图.svg"))
    parts.append(
        paragraph_xml(
            "如图4.5所示，该流程图展示管理员在系统运行中的主要职责，包括课程与资源审核、用户和字典维护、公告会议管理以及统计概览查看等内容，反映了平台治理与运营支撑流程。"
        )
    )
    parts.append(figure_box_xml("图4.5", "管理员审核与运行维护流程图", "图4-5_管理员审核与运行维护流程图.svg"))

    parts.append(heading2_xml("角色用例设计"))
    parts.append(
        paragraph_xml(
            "根据现有系统的权限划分，系统主要包含学生、教师和管理员三类角色。不同角色围绕同一套教学与运营数据开展协同工作，因此需要通过用例图展示角色与功能之间的对应关系。"
        )
    )
    parts.append(
        paragraph_xml(
            "如图4.6所示，学生角色的主要用例集中在学习侧，包括课程浏览、选课、学习资源访问、作业考试参与、成绩学分查询以及智能问答等。"
        )
    )
    parts.append(figure_box_xml("图4.6", "学生角色用例图", "图4-6_学生角色用例图.svg"))
    parts.append(
        paragraph_xml(
            "如图4.7所示，教师角色的主要用例集中在教学建设侧，包括课程维护、章节资源维护、作业和考试发布、题库维护、批改阅卷以及 AI 辅助出题等。"
        )
    )
    parts.append(figure_box_xml("图4.7", "教师角色用例图", "图4-7_教师角色用例图.svg"))
    parts.append(
        paragraph_xml(
            "如图4.8所示，管理员角色的主要用例集中在审核与运维侧，包括课程审核、资源审核、用户管理、字典配置、公告管理、统计概览和后台智能问答等。"
        )
    )
    parts.append(figure_box_xml("图4.8", "管理员角色用例图", "图4-8_管理员角色用例图.svg"))
    parts.append(
        paragraph_xml(
            "通过上述总体架构设计、功能结构设计、流程设计和角色用例设计，可以看出当前系统已经形成较为完整的课程学习与教学管理闭环。"
            "其设计重点不再局限于基础信息管理，而是扩展到了进度跟踪、作业考试、结课学分以及 AI 辅助能力，为后续系统实现和测试分析提供了明确的功能基础。"
        )
    )

    return "".join(parts)


def ensure_template_copy() -> Path:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    if not TMP_TEMPLATE.exists():
        shutil.copy2(REFERENCE_DOCX, TMP_TEMPLATE)
    return TMP_TEMPLATE


def replace_document_body(template_docx: Path, output_docx: Path, body_xml: str) -> None:
    with ZipFile(template_docx, "r") as zin:
        xml_bytes = zin.read("word/document.xml")
        root = ET.fromstring(xml_bytes)
        body = root.find(qn(W_NS, "body"))
        if body is None:
            raise RuntimeError("Template document.xml missing body node")
        sect_pr = body.find(qn(W_NS, "sectPr"))
        sect_copy = copy.deepcopy(sect_pr) if sect_pr is not None else None
        body.clear()
        fragment_root = ET.fromstring(f"<root xmlns:w=\"{W_NS}\">{body_xml}</root>")
        for child in list(fragment_root):
            body.append(copy.deepcopy(child))
        if sect_copy is not None:
            body.append(sect_copy)
        updated_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

        core_bytes = None
        try:
            core_root = ET.fromstring(zin.read("docProps/core.xml"))
            title_node = core_root.find(qn(DC_NS, "title"))
            if title_node is None:
                title_node = ET.SubElement(core_root, qn(DC_NS, "title"))
            title_node.text = "系统总体功能结构设计和系统功能设计"
            core_bytes = ET.tostring(core_root, encoding="utf-8", xml_declaration=True)
        except KeyError:
            core_bytes = None

        output_docx.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(output_docx, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    data = updated_xml
                elif item.filename == "docProps/core.xml" and core_bytes is not None:
                    data = core_bytes
                zout.writestr(item, data)


def write_diagrams() -> list[Path]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    for item in DIAGRAMS:
        dot_path = FIG_DIR / f"{item['filename']}.dot"
        svg_path = FIG_DIR / f"{item['filename']}.svg"
        dot_path.write_text(item["dot"].strip() + "\n", encoding="utf-8")
        subprocess.run(
            ["dot", "-Tsvg", str(dot_path), "-o", str(svg_path)],
            check=True,
            cwd=ROOT,
        )
        generated.extend([dot_path, svg_path])
    return generated


def main() -> None:
    template = ensure_template_copy()
    generated = write_diagrams()
    replace_document_body(template, OUTPUT_DOCX, build_body_xml())
    print(f"Generated DOCX: {OUTPUT_DOCX}")
    for path in generated:
        print(f"Generated: {path}")


if __name__ == "__main__":
    main()
