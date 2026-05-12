from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
CHAPTER_DIR = ROOT / "辅助修改论文" / "第四章 数据库的逻辑设计"
TEMPLATE_DOCX = CHAPTER_DIR / "参考数据库的逻辑设计.docx"
OUTPUT_DOCX = CHAPTER_DIR / "现有系统数据库的逻辑设计.docx"
DIAGRAM_DIR = CHAPTER_DIR / "代码和图"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
CONTENT_WIDTH = 9026

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)
ET.register_namespace("cp", CP_NS)
ET.register_namespace("dc", DC_NS)


@dataclass
class Card:
    key: str
    title: str
    attrs: list[str]
    x: int
    y: int
    w: int = 240


@dataclass
class Edge:
    source: str
    target: str
    label: str


@dataclass
class Diagram:
    number: str
    title: str
    filename: str
    cards: list[Card]
    edges: list[Edge]
    width: int = 1200
    height: int = 780


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
    header_fill: str = "F2F4F7",
    body_fill: str = "FFFFFF",
    border_color: str = "BFC7D1",
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
            trpr = "<w:trPr>" f'<w:trHeight w:val="{row_height}" w:hRule="atLeast"/>' "</w:trPr>"
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
                    "图形文件已同步生成到“代码和图”文件夹，可在 Word 中手动插入 SVG 图。",
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
        border_color="C9CED6",
        row_height=1400,
        align="center",
    ) + caption_xml(f"{fig_no} {fig_title}")


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
            child.text = "第四章数据库逻辑设计"
    ET.ElementTree(root).write(core_path, encoding="utf-8", xml_declaration=True)


def build_paragraphs(diagrams: list[Diagram]) -> list[str]:
    intro = [
        title_xml("数据库的逻辑设计"),
        paragraph_xml(
            "本系统数据库采用关系型数据库模型进行设计，在基础用户管理表之上，进一步围绕课程教学主链路、作业与考试链路、学习进度统计链路以及智能问答扩展链路构建逻辑结构。结合现有系统后端实体类、数据库初始化脚本和 docs 目录中的增量脚本可以看出，数据库已经从传统的课程展示型结构扩展为支持课程审核、章节资源管理、选课学习、作业批改、在线考试、结课学分和 AI 会话管理的复合型数据模型。"
        ),
        paragraph_xml(
            "现有系统的数据库逻辑设计主要包括总体 E-R 图以及若干核心实体或实体组合 E-R 图。总体图用于说明系统核心数据表之间的主从关系和业务流向，单体或组合实体图则重点刻画各表的关键属性和联系字段，为后续数据库表设计、接口设计和业务实现提供依据。"
        ),
    ]

    descriptions = {
        "4.14": "如图4.14所示，系统总体E-R图描述了管理员、教师、学生、课程、章节、资源、选课、学习进度、作业、考试、学分记录以及智能问答等核心实体之间的联系，体现了现有系统围绕“课程学习全流程”组织数据的整体逻辑结构。",
        "4.15": "如图4.15所示，管理员实体主要用于后台登录认证、课程与资源审核以及系统参数维护，包含用户名、密码、角色和创建时间等基本字段，是平台级管理能力的数据基础。",
        "4.16": "如图4.16所示，教师实体保存教师账号、身份信息和联系方式等内容，并通过教师编号与课程、作业、考试等业务表建立关联，是教学内容生产端的核心主体。",
        "4.17": "如图4.17所示，学生实体记录学生账号、班级、联系方式等基础信息，用于支撑选课、学习进度、作业提交、考试作答和 AI 会话等前台业务。",
        "4.18": "如图4.18所示，课程实体是整个教学链路的中心实体，既保存课程名称、类型、开始结束时间、学分和审核状态等核心属性，又通过外键字段与教师、章节、作业、考试和选课记录发生联系。",
        "4.19": "如图4.19所示，课程章节与资源实体反映了课程内容的层级化组织方式。课程章节负责描述教学目录结构，课程资源则负责挂接视频、课件等具体学习材料，两者共同构成课程内容管理的基础。",
        "4.20": "如图4.20所示，选课与学习进度实体用于记录学生与课程之间的学习关系。选课实体描述学生是否选课、当前进度和结课时间，学习进度实体则细化到章节资源粒度，用于跟踪每个学习资源的完成情况。",
        "4.21": "如图4.21所示，作业与作业提交实体用于支撑课程作业发布、提交和批改流程。作业实体负责记录所属课程、章节、时间窗口和总分，作业提交实体则保存学生提交内容、评分、评语和题目快照等信息。",
        "4.22": "如图4.22所示，考试与题库实体反映了现有系统的在线考试逻辑。考试实体描述考试规则与时间范围，题库实体记录题型、答案和分值，考试记录实体保存学生答题快照、自动评分与最终成绩。",
        "4.23": "如图4.23所示，课程结课与学分记录实体用于沉淀结课判定结果。它与课程和选课记录保持关联，通过发放状态、发放时间和规则快照等字段记录学生课程达标后的学分授予结果。",
        "4.24": "如图4.24所示，智能问答模块实体由 AI 会话表和 AI 消息表构成，用于保存用户在不同业务场景下的会话标题、上下文绑定关系、多轮消息内容和工具调用痕迹，是系统 AI 能力落库的核心支撑。",
    }

    result = list(intro)
    for diagram in diagrams:
        result.append(paragraph_xml(descriptions[diagram.number]))
        result.append(figure_box_xml(f"图{diagram.number}", diagram.title, diagram.filename))
    return result


def wrap_document_xml(fragments: Iterable[str], template_bytes: bytes) -> bytes:
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


def card_height(card: Card) -> int:
    return 58 + len(card.attrs) * 28 + 18


def card_center(card: Card) -> tuple[float, float]:
    return (card.x + card.w / 2, card.y + card_height(card) / 2)


def draw_card_svg(card: Card) -> str:
    h = card_height(card)
    header_h = 42
    parts = [
        f'<rect x="{card.x}" y="{card.y}" width="{card.w}" height="{h}" rx="12" ry="12" fill="#ffffff" stroke="#3f5066" stroke-width="2"/>',
        f'<rect x="{card.x}" y="{card.y}" width="{card.w}" height="{header_h}" rx="12" ry="12" fill="#e9eef5" stroke="#3f5066" stroke-width="2"/>',
        f'<line x1="{card.x}" y1="{card.y + header_h}" x2="{card.x + card.w}" y2="{card.y + header_h}" stroke="#3f5066" stroke-width="1.6"/>',
        f'<text x="{card.x + card.w / 2}" y="{card.y + 27}" text-anchor="middle" class="card-title">{escape(card.title)}</text>',
    ]
    for idx, attr in enumerate(card.attrs):
        y = card.y + header_h + 24 + idx * 28
        parts.append(f'<text x="{card.x + 16}" y="{y}" class="card-attr">{escape(attr)}</text>')
    return "\n".join(parts)


def edge_anchor(cards: dict[str, Card], edge: Edge) -> tuple[float, float, float, float]:
    source = cards[edge.source]
    target = cards[edge.target]
    sx, sy = card_center(source)
    tx, ty = card_center(target)
    dx = tx - sx
    dy = ty - sy
    if abs(dx) >= abs(dy):
        x1 = source.x + source.w if dx >= 0 else source.x
        y1 = sy
        x2 = target.x if dx >= 0 else target.x + target.w
        y2 = ty
    else:
        x1 = sx
        y1 = source.y + card_height(source) if dy >= 0 else source.y
        x2 = tx
        y2 = target.y if dy >= 0 else target.y + card_height(target)
    return x1, y1, x2, y2


def draw_edge_svg(cards: dict[str, Card], edge: Edge) -> str:
    x1, y1, x2, y2 = edge_anchor(cards, edge)
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2 - 6
    return "\n".join(
        [
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge"/>',
            f'<text x="{mx}" y="{my}" text-anchor="middle" class="edge-label">{escape(edge.label)}</text>',
        ]
    )


def diagram_svg(diagram: Diagram) -> str:
    cards = {card.key: card for card in diagram.cards}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{diagram.width}" height="{diagram.height}" viewBox="0 0 {diagram.width} {diagram.height}">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>',
        "</marker>",
        '<style><![CDATA['
        '.title { font: 700 28px "Microsoft YaHei", "PingFang SC", sans-serif; fill: #1f2937; }'
        '.card-title { font: 700 18px "Microsoft YaHei", "PingFang SC", sans-serif; fill: #1f2937; }'
        '.card-attr { font: 15px "Microsoft YaHei", "PingFang SC", sans-serif; fill: #334155; }'
        '.edge { stroke: #64748b; stroke-width: 2; fill: none; marker-end: url(#arrow); }'
        '.edge-label { font: 14px "Microsoft YaHei", "PingFang SC", sans-serif; fill: #475569; }'
        ']]></style>',
        "</defs>",
        f'<rect x="1" y="1" width="{diagram.width - 2}" height="{diagram.height - 2}" fill="#fbfcfe" stroke="#d5dce5" stroke-width="1"/>',
        f'<text x="{diagram.width / 2}" y="38" text-anchor="middle" class="title">{escape(diagram.title)}</text>',
    ]
    for edge in diagram.edges:
        parts.append(draw_edge_svg(cards, edge))
    for card in diagram.cards:
        parts.append(draw_card_svg(card))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def card_dot(card: Card) -> str:
    attrs = "".join(f"| {attr}" for attr in card.attrs)
    label = "{" + card.title + attrs + "}"
    pos_y = 1000 - card.y
    return f'"{card.key}" [shape=record, label="{label}", pos="{card.x + card.w / 2},{pos_y}!"];'


def diagram_dot(diagram: Diagram) -> str:
    lines = [
        "digraph G {",
        '  graph [charset="UTF-8", rankdir="LR", splines=polyline, nodesep=0.6, ranksep=0.8, bgcolor="white", labelloc="t", label="%s", fontname="Microsoft YaHei", fontsize=22];'
        % diagram.title,
        '  node [shape=record, fontname="Microsoft YaHei", fontsize=11, color="#3f5066", penwidth=1.4, style="rounded,filled", fillcolor="#ffffff"];',
        '  edge [fontname="Microsoft YaHei", fontsize=10, color="#64748b", penwidth=1.2, arrowsize=0.7];',
        "",
    ]
    for card in diagram.cards:
        lines.append("  " + card_dot(card))
    lines.append("")
    for edge in diagram.edges:
        lines.append(f'  "{edge.source}" -> "{edge.target}" [label="{edge.label}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def diagrams() -> list[Diagram]:
    return [
        Diagram(
            number="4.14",
            title="系统总体E-R图",
            filename="图4.14 系统总体E-R图.svg",
            width=1500,
            height=980,
            cards=[
                Card("users", "管理员", ["id", "username", "password", "role", "addtime"], 70, 120, 220),
                Card("teacher", "教师", ["id", "username", "jiaoshi_name", "phone", "email"], 70, 330, 220),
                Card("student", "学生", ["id", "username", "yonghu_name", "banji_types", "phone"], 70, 570, 220),
                Card("course", "课程", ["id", "kecheng_name", "jiaoshi_id", "course_status", "credit_score"], 430, 110, 250),
                Card("chapter", "课程章节", ["id", "kecheng_id", "chapter_name", "chapter_status"], 820, 90, 250),
                Card("resource", "课程资源", ["id", "chapter_id", "resource_name", "resource_type"], 1150, 90, 260),
                Card("enroll", "选课记录", ["id", "kecheng_id", "yonghu_id", "progress_percent"], 430, 360, 250),
                Card("progress", "学习进度", ["id", "resource_id", "yonghu_id", "is_completed"], 820, 330, 250),
                Card("homework", "作业", ["id", "kecheng_id", "chapter_id", "score_total"], 430, 610, 250),
                Card("submit", "作业提交", ["id", "zuoye_id", "yonghu_id", "submit_score"], 820, 580, 250),
                Card("exam", "考试", ["id", "kecheng_id", "pass_score", "exam_status"], 1150, 330, 260),
                Card("record", "考试记录", ["id", "exam_id", "yonghu_id", "final_score"], 1150, 580, 260),
                Card("credit", "学分记录", ["id", "kecheng_id", "yonghu_id", "grant_status"], 430, 800, 250),
                Card("ai_session", "AI会话", ["id", "user_id", "biz_scene", "session_title"], 820, 800, 250),
                Card("ai_message", "AI消息", ["id", "session_id", "message_role", "content"], 1150, 800, 260),
            ],
            edges=[
                Edge("users", "course", "审核"),
                Edge("teacher", "course", "开设"),
                Edge("student", "enroll", "选课"),
                Edge("course", "chapter", "1:N"),
                Edge("chapter", "resource", "1:N"),
                Edge("course", "enroll", "1:N"),
                Edge("resource", "progress", "1:N"),
                Edge("student", "progress", "学习"),
                Edge("course", "homework", "1:N"),
                Edge("homework", "submit", "1:N"),
                Edge("student", "submit", "提交"),
                Edge("course", "exam", "1:N"),
                Edge("exam", "record", "1:N"),
                Edge("student", "record", "作答"),
                Edge("course", "credit", "结课"),
                Edge("student", "credit", "获得"),
                Edge("student", "ai_session", "发起"),
                Edge("teacher", "ai_session", "发起"),
                Edge("ai_session", "ai_message", "1:N"),
            ],
        ),
        Diagram(
            number="4.15",
            title="管理员实体E-R图",
            filename="图4.15 管理员实体E-R图.svg",
            cards=[Card("users", "管理员（users）", ["id", "username", "password", "role", "addtime"], 420, 180, 360)],
            edges=[],
            width=1200,
            height=520,
        ),
        Diagram(
            number="4.16",
            title="教师实体E-R图",
            filename="图4.16 教师实体E-R图.svg",
            cards=[Card("teacher", "教师（jiaoshi）", ["id", "username", "password", "jiaoshi_name", "sex_types", "jiaoshi_phone", "jiaoshi_email", "create_time"], 380, 140, 420)],
            edges=[],
            width=1200,
            height=560,
        ),
        Diagram(
            number="4.17",
            title="学生实体E-R图",
            filename="图4.17 学生实体E-R图.svg",
            cards=[Card("student", "学生（yonghu）", ["id", "username", "password", "yonghu_name", "sex_types", "banji_types", "yonghu_phone", "yonghu_email", "create_time"], 360, 120, 460)],
            edges=[],
            width=1200,
            height=580,
        ),
        Diagram(
            number="4.18",
            title="课程实体E-R图",
            filename="图4.18 课程实体E-R图.svg",
            cards=[
                Card("teacher", "教师", ["id", "jiaoshi_name"], 90, 220, 220),
                Card("course", "课程（kecheng）", ["id", "kecheng_name", "kecheng_types", "kecheng_time", "kecheng_end_time", "jiaoshi_id", "course_status", "credit_score"], 390, 120, 420),
                Card("admin", "管理员", ["id", "role"], 920, 220, 200),
            ],
            edges=[Edge("teacher", "course", "1:N"), Edge("admin", "course", "审核")],
            width=1200,
            height=560,
        ),
        Diagram(
            number="4.19",
            title="课程章节与资源实体E-R图",
            filename="图4.19 课程章节与资源实体E-R图.svg",
            cards=[
                Card("course", "课程", ["id", "kecheng_name"], 80, 250, 210),
                Card("chapter", "课程章节（course_chapter）", ["id", "kecheng_id", "chapter_name", "chapter_sort", "chapter_status", "review_time"], 390, 120, 340),
                Card("resource", "课程资源（course_resource）", ["id", "chapter_id", "resource_name", "resource_type", "resource_url", "resource_status"], 860, 120, 340),
            ],
            edges=[Edge("course", "chapter", "1:N"), Edge("chapter", "resource", "1:N")],
            width=1300,
            height=520,
        ),
        Diagram(
            number="4.20",
            title="选课与学习进度实体E-R图",
            filename="图4.20 选课与学习进度实体E-R图.svg",
            cards=[
                Card("student", "学生", ["id", "yonghu_name"], 80, 260, 210),
                Card("enroll", "选课记录（course_enroll）", ["id", "kecheng_id", "yonghu_id", "enroll_status", "progress_percent", "finish_time"], 360, 120, 340),
                Card("progress", "学习进度（study_progress）", ["id", "resource_id", "yonghu_id", "study_seconds", "progress_percent", "is_completed"], 820, 120, 340),
                Card("resource", "课程资源", ["id", "resource_name"], 1080, 380, 180),
            ],
            edges=[
                Edge("student", "enroll", "1:N"),
                Edge("student", "progress", "1:N"),
                Edge("enroll", "progress", "汇总"),
                Edge("resource", "progress", "1:N"),
            ],
            width=1360,
            height=620,
        ),
        Diagram(
            number="4.21",
            title="作业与作业提交实体E-R图",
            filename="图4.21 作业与作业提交实体E-R图.svg",
            cards=[
                Card("course", "课程", ["id", "kecheng_name"], 80, 250, 210),
                Card("homework", "作业（zuoye）", ["id", "kecheng_id", "chapter_id", "zuoye_name", "start_time", "end_time", "score_total", "question_ids"], 360, 120, 340),
                Card("submit", "作业提交（zuoye_submit）", ["id", "zuoye_id", "yonghu_id", "submit_status", "submit_score", "auto_score", "check_time"], 860, 120, 340),
                Card("student", "学生", ["id", "yonghu_name"], 1080, 420, 180),
            ],
            edges=[
                Edge("course", "homework", "1:N"),
                Edge("homework", "submit", "1:N"),
                Edge("student", "submit", "1:N"),
            ],
            width=1360,
            height=620,
        ),
        Diagram(
            number="4.22",
            title="考试与题库实体E-R图",
            filename="图4.22 考试与题库实体E-R图.svg",
            cards=[
                Card("course", "课程", ["id", "kecheng_name"], 60, 300, 190),
                Card("exam", "考试（exam）", ["id", "kecheng_id", "chapter_id", "exam_name", "duration_minutes", "pass_score", "allow_retake", "allow_resume"], 300, 120, 330),
                Card("question", "题库（exam_question）", ["id", "exam_id", "kecheng_id", "question_type", "question_title", "correct_answer", "question_score"], 740, 120, 330),
                Card("record", "考试记录（exam_record）", ["id", "exam_id", "yonghu_id", "final_score", "pass_status", "record_status", "attempt_no"], 740, 430, 330),
                Card("student", "学生", ["id", "yonghu_name"], 1140, 470, 180),
            ],
            edges=[
                Edge("course", "exam", "1:N"),
                Edge("exam", "question", "1:N"),
                Edge("exam", "record", "1:N"),
                Edge("student", "record", "1:N"),
            ],
            width=1380,
            height=760,
        ),
        Diagram(
            number="4.23",
            title="课程结课与学分记录实体E-R图",
            filename="图4.23 课程结课与学分记录实体E-R图.svg",
            cards=[
                Card("course", "课程", ["id", "kecheng_name", "credit_score"], 100, 260, 220),
                Card("enroll", "选课记录", ["id", "kecheng_id", "yonghu_id", "enroll_status", "finish_time"], 420, 120, 320),
                Card("credit", "学分记录（course_credit_record）", ["id", "kecheng_id", "yonghu_id", "credit_score", "grant_status", "grant_time", "source_rule_snapshot"], 820, 120, 360),
                Card("student", "学生", ["id", "yonghu_name"], 980, 460, 180),
            ],
            edges=[
                Edge("course", "enroll", "1:N"),
                Edge("course", "credit", "1:N"),
                Edge("student", "credit", "1:N"),
                Edge("enroll", "credit", "结课发放"),
            ],
            width=1320,
            height=680,
        ),
        Diagram(
            number="4.24",
            title="智能问答模块实体E-R图",
            filename="图4.24 智能问答模块实体E-R图.svg",
            cards=[
                Card("session", "AI会话（ai_chat_session）", ["id", "user_id", "user_table", "role_type", "session_title", "biz_scene", "course_id", "last_message_at", "status"], 220, 120, 380),
                Card("message", "AI消息（ai_chat_message）", ["id", "session_id", "message_role", "message_type", "content", "tool_name", "token_estimate", "sort_no", "create_time"], 720, 120, 380),
                Card("user", "用户", ["student / teacher / admin"], 500, 470, 220),
            ],
            edges=[
                Edge("user", "session", "发起"),
                Edge("session", "message", "1:N"),
            ],
            width=1320,
            height=700,
        ),
    ]


def build_docx(diagrams_meta: list[Diagram]) -> None:
    if not TEMPLATE_DOCX.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_DOCX}")

    fragments = build_paragraphs(diagrams_meta)
    with ZipFile(TEMPLATE_DOCX, "r") as zin:
        with ZipFile(OUTPUT_DOCX, "w", compression=ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    data = wrap_document_xml(fragments, data)
                zout.writestr(item, data)

    extract_dir = CHAPTER_DIR / ".tmp_chapter4_logic"
    if extract_dir.exists():
        for p in sorted(extract_dir.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                p.rmdir()
        extract_dir.rmdir()
    extract_dir.mkdir()
    with ZipFile(OUTPUT_DOCX, "r") as zf:
        zf.extractall(extract_dir)
    update_core_props(extract_dir / "docProps" / "core.xml", "数据库的逻辑设计")
    with ZipFile(OUTPUT_DOCX, "w", compression=ZIP_DEFLATED) as zout:
        for file_path in extract_dir.rglob("*"):
            if file_path.is_file():
                zout.write(file_path, file_path.relative_to(extract_dir).as_posix())
    for p in sorted(extract_dir.rglob("*"), reverse=True):
        if p.is_file():
            p.unlink()
        elif p.is_dir():
            p.rmdir()
    extract_dir.rmdir()


def build_diagrams(diagrams_meta: list[Diagram]) -> None:
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    for diagram in diagrams_meta:
        svg_path = DIAGRAM_DIR / diagram.filename
        dot_path = DIAGRAM_DIR / diagram.filename.replace(".svg", ".dot")
        svg_path.write_text(diagram_svg(diagram), encoding="utf-8")
        dot_path.write_text(diagram_dot(diagram), encoding="utf-8")


def main() -> None:
    CHAPTER_DIR.mkdir(parents=True, exist_ok=True)
    diagrams_meta = diagrams()
    build_diagrams(diagrams_meta)
    build_docx(diagrams_meta)
    print(OUTPUT_DOCX)


if __name__ == "__main__":
    main()
