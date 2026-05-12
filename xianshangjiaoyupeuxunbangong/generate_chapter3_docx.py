from __future__ import annotations

import copy
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
CHAPTER_DIR = ROOT / "辅助修改论文" / "第三章 需求分析"
TEMPLATE_DOCX = CHAPTER_DIR / "参考论文的第三章.docx"
OUTPUT_DOCX = CHAPTER_DIR / "第三章_现有系统需求分析.docx"

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


def blank_xml(after: int = 0) -> str:
    return (
        "<w:p><w:pPr><w:jc w:val=\"both\"/>"
        f"<w:spacing w:before=\"0\" w:after=\"{after}\" w:line=\"240\" w:lineRule=\"auto\"/>"
        "<w:ind w:firstLine=\"0\"/></w:pPr></w:p>"
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
                    "插图由本次任务同步生成，用户可在 Word 中手动插入 SVG 图。",
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


def spec_table_xml(table_no: str, table_title: str, spec: list[tuple[str, str]]) -> str:
    rows: list[list[list[str]]] = [
        [
            [paragraph_xml("项目", align="center", first_line=0, before=0, after=0, line=300, font="黑体", size=22, bold=True)],
            [paragraph_xml("说明", align="center", first_line=0, before=0, after=0, line=300, font="黑体", size=22, bold=True)],
        ]
    ]
    for key, value in spec:
        rows.append(
            [
                [paragraph_xml(key, align="center", first_line=0, before=0, after=0, line=300, font="宋体", size=21)],
                [paragraph_xml(value, align="left", first_line=0, before=0, after=0, line=300, font="宋体", size=21)],
            ]
        )
    return caption_xml(f"{table_no} {table_title}") + table_xml(rows, [1800, 7226], header_rows=1)


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
            child.text = "第三章 需求分析"
    ET.ElementTree(root).write(core_path, encoding="utf-8", xml_declaration=True)


def body_fragments() -> list[str]:
    fragments: list[str] = []

    fragments.append(title_xml("第三章 需求分析"))
    fragments.append(
        paragraph_xml(
            "需求分析是系统设计与实现之前的重要基础工作。结合当前仓库中的后端代码、新前端工程、数据库脚本以及 docs 目录下的相关说明，可以看出该系统已经形成较为完整的线上教育培训办公业务闭环。本章在参考论文第三章编排方式的基础上，围绕现有系统的用户角色、功能性需求和非功能性需求展开分析，为后续系统设计与实现章节提供依据。",
            after=120,
        )
    )
    fragments.append(
        paragraph_xml(
            "从现有实现来看，系统不仅支持课程、章节、资源、作业、考试和成绩等核心教学功能，还已经扩展出结课判定、学分发放、公告管理、题库 AI 出题和智能问答助手等能力。因此，本章需求分析不再停留在简单教学演示层面，而是围绕一个可持续迭代的综合教学平台来展开。",
            after=160,
        )
    )

    fragments.append(heading1_xml("3.1 系统用户角色分析"))
    fragments.append(
        paragraph_xml(
            "根据现有系统的业务边界和权限结构，可以将系统用户划分为管理员、教师和学生三类角色。三类角色共同围绕课程教学、学习过程管理和平台运营展开协作，分别承担平台维护、教学组织和学习参与等不同职责。现有系统的角色用例图如图3-1所示："
        )
    )
    fragments.append(
        figure_box_xml(
            "图3-1",
            "现有系统角色用例图",
            "fig3-1-system-role-usecase.svg",
        )
    )
    fragments.append(
        paragraph_xml(
            "管理员负责平台级配置与审核管理，主要涵盖用户与教师信息维护、课程审核、字典配置、公告维护以及部分考试和 AI 参数相关配置，是系统中权限范围最大的角色。管理员需要保障整个平台的数据规范性和运行稳定性。"
        )
    )
    fragments.append(
        paragraph_xml(
            "教师负责教学业务的组织与维护，主要包括课程创建、章节维护、资源上传、作业发布与批改、考试与题库管理、成绩统计以及 AI 辅助出题等功能。教师角色直接决定课程内容质量和教学流程的完整性。"
        )
    )
    fragments.append(
        paragraph_xml(
            "学生是教学活动的最终参与者，主要进行选课、视频学习、作业提交、在线考试、成绩查看、结课状态查询以及智能问答等操作。学生侧需求更关注页面易用性、学习过程连续性以及结果反馈的及时性。"
        )
    )

    fragments.append(heading1_xml("3.2 系统功能性需求分析"))
    fragments.append(
        paragraph_xml(
            "结合当前系统实现情况，可以将功能性需求划分为系统登录、课程与资源管理、学习进度与作业管理、考试与题库管理、结课统计与公告管理以及智能问答功能六个方面。各模块既相互独立，又通过课程学习主链路形成完整闭环。"
        )
    )

    fragments.append(heading2_xml("3.2.1 系统登录功能"))
    fragments.append(
        paragraph_xml(
            "系统登录功能用于校验用户身份并建立会话，是所有业务功能的入口。现有系统支持学生、教师和管理员三类身份登录，登录成功后前端会保存 token、角色、用户编号和表名等信息，并在后续请求中带入鉴权标识。登录功能用例图如图3-2所示："
        )
    )
    fragments.append(
        figure_box_xml(
            "图3-2",
            "系统登录功能用例图",
            "fig3-2-login-usecase.svg",
        )
    )
    fragments.append(
        paragraph_xml(
            "登录页面除身份切换外，还承担基础输入校验、错误提示、退出重定向和登录后跳转等职责。由于系统当前采取 token 与 session 结合的鉴权模式，因此登录功能的稳定性直接影响后续课程学习、考试与管理操作。系统登录功能用例规约如表3-1所示："
        )
    )
    fragments.append(
        spec_table_xml(
            "表3-1",
            "系统登录功能用例规约表",
            [
                ("用例名称", "系统登录"),
                ("参与角色", "管理员、教师、学生"),
                ("前置条件", "用户账号已在系统中存在，系统服务和数据库连接正常。"),
                ("基本流程", "用户选择身份并输入账号密码；系统校验非空与身份信息；后端验证账号密码正确性；验证通过后返回 token 与角色信息；前端保存会话并跳转到对应页面。"),
                ("异常流程", "账号或密码为空时提示补全；账号密码错误或角色不匹配时提示登录失败；网络异常时提示稍后重试。"),
                ("后置条件", "系统建立有效登录态，后续页面可按角色权限访问对应业务功能。"),
            ],
        )
    )

    fragments.append(heading2_xml("3.2.2 课程与资源管理"))
    fragments.append(
        paragraph_xml(
            "课程与资源管理是现有系统的基础教学模块，主要围绕课程创建、课程审核、章节维护、资源上传与审核展开。教师负责维护教学内容，管理员负责审核和配置，学生则在前台浏览已审核通过的课程与资源。课程与资源管理用例图如图3-3所示："
        )
    )
    fragments.append(
        figure_box_xml(
            "图3-3",
            "课程与资源管理用例图",
            "fig3-3-course-resource-usecase.svg",
        )
    )
    fragments.append(
        paragraph_xml(
            "在课程管理阶段，教师需录入课程基本信息、课程学分和课程状态等内容，并提交管理员审核。章节管理阶段，教师可维护章节目录和关联资源；资源管理阶段则要求教师补全资源名称、资源类型、所属章节等信息，系统还补充了必填校验，以避免空数据写入。课程与资源管理用例规约如表3-2所示："
        )
    )
    fragments.append(
        spec_table_xml(
            "表3-2",
            "课程与资源管理用例规约表",
            [
                ("用例名称", "课程与资源管理"),
                ("参与角色", "教师、管理员、学生"),
                ("前置条件", "教师和管理员已完成登录；课程相关基础字典存在；数据库中具备课程、章节与资源表结构。"),
                ("基本流程", "教师创建课程并提交审核；管理员审核课程；教师维护章节信息；教师上传并编辑课程资源；管理员审核资源；学生查看已通过审核的课程详情、章节目录和资源内容。"),
                ("异常流程", "课程信息不完整或资源必填项缺失时，系统阻止保存并提示；未审核通过的课程不对学生展示；资源审核失败时不能进入学生端。"),
                ("后置条件", "课程、章节与资源形成完整层级结构，为后续选课、学习进度和作业考试提供基础数据。"),
            ],
        )
    )

    fragments.append(heading2_xml("3.2.3 学习进度与作业管理"))
    fragments.append(
        paragraph_xml(
            "学习进度与作业管理负责支撑学生的日常学习过程。学生在选课后进入“我的课程”，可按章节观看视频和资料，系统实时记录学习进度；教师则通过作业模块布置任务、接收提交并完成批改。学习进度与作业管理用例图如图3-4所示："
        )
    )
    fragments.append(
        figure_box_xml(
            "图3-4",
            "学习进度与作业管理用例图",
            "fig3-4-study-homework-usecase.svg",
        )
    )
    fragments.append(
        paragraph_xml(
            "当前系统已对学习进度记录做了多项体验修复，例如播放完成由 99% 修正为 100%、再次进入页面不再回显 0%，并保证后台与学生端完成态统一。作业模块支持课程关联、截止时间、评分与评语，是结课判定的重要组成部分。学习进度与作业管理用例规约如表3-3所示："
        )
    )
    fragments.append(
        spec_table_xml(
            "表3-3",
            "学习进度与作业管理用例规约表",
            [
                ("用例名称", "学习进度与作业管理"),
                ("参与角色", "学生、教师"),
                ("前置条件", "学生已完成选课；教师已创建对应课程章节与作业；课程资源可正常访问。"),
                ("基本流程", "学生进入课程详情并选择章节学习；系统记录视频学习进度；教师发布作业任务；学生按要求提交作业；教师查看提交记录并进行评分和评语反馈；学生查看作业成绩和进度结果。"),
                ("异常流程", "学生未选课时不能进入学习主链路；作业超过截止时间后不可正常提交；视频或资源异常时系统给出提示。"),
                ("后置条件", "学习进度和作业成绩被持久化，并参与成绩汇总与结课判定。"),
            ],
        )
    )

    fragments.append(heading2_xml("3.2.4 考试与题库管理"))
    fragments.append(
        paragraph_xml(
            "考试与题库管理模块主要面向教师和学生两类角色。教师负责题库维护、按课程筛题、考试发布与阅卷；学生负责在线考试、交卷和成绩查看。当前系统还在题库管理页补充了 AI 出题能力，使该模块具备更强的扩展性。考试与题库管理用例图如图3-5所示："
        )
    )
    fragments.append(
        figure_box_xml(
            "图3-5",
            "考试与题库管理用例图",
            "fig3-5-exam-question-usecase.svg",
        )
    )
    fragments.append(
        paragraph_xml(
            "现有题库已经支持按课程和题型分类筛选，考试可按当前课程从题库选题，并支持客观题自动判分、主观题待阅卷和成绩汇总等流程。对于模型网关已启用的场景，教师还可通过 AI 出题面板生成题目草稿并保存入题库。考试与题库管理用例规约如表3-4所示："
        )
    )
    fragments.append(
        spec_table_xml(
            "表3-4",
            "考试与题库管理用例规约表",
            [
                ("用例名称", "考试与题库管理"),
                ("参与角色", "教师、学生"),
                ("前置条件", "教师已登录并拥有课程；题库、考试和考试记录相关表已初始化；学生已选课。"),
                ("基本流程", "教师维护题库并按课程筛选题目；教师发布考试并设置规则；学生在线参加考试并提交答卷；系统对客观题自动判分；教师完成主观题阅卷；系统汇总成绩并提供查看；教师可按需调用 AI 生成题目草稿。"),
                ("异常流程", "题库未关联课程时不能按当前课程选题；学生超过尝试次数或考试时间结束后不能继续作答；模型未启用时 AI 出题接口返回明确错误。"),
                ("后置条件", "考试成绩、答题记录和题库数据被保存，并为成绩统计与结课判定提供依据。"),
            ],
        )
    )

    fragments.append(heading2_xml("3.2.5 结课统计与公告管理"))
    fragments.append(
        paragraph_xml(
            "结课统计与公告管理模块承担课程结果收束和平台信息发布两类职责。系统会综合学习进度、作业成绩和考试成绩进行结课判定并发放学分，同时在学生端和后台端展示成绩汇总与统计概览；公告模块则负责平台信息通知和公告类型管理。结课统计与公告管理用例图如图3-6所示："
        )
    )
    fragments.append(
        figure_box_xml(
            "图3-6",
            "结课统计与公告管理用例图",
            "fig3-6-settlement-report-notice-usecase.svg",
        )
    )
    fragments.append(
        paragraph_xml(
            "结课统计部分已经实现课程维度统计和学生成绩汇总接口，公告管理部分则补充了公告类型管理和编辑保存修复。两者共同保证平台既能形成可追踪的学习结果，又能及时向用户发布运行信息。结课统计与公告管理用例规约如表3-5所示："
        )
    )
    fragments.append(
        spec_table_xml(
            "表3-5",
            "结课统计与公告管理用例规约表",
            [
                ("用例名称", "结课统计与公告管理"),
                ("参与角色", "管理员、教师、学生"),
                ("前置条件", "课程学习、作业和考试数据已经产生；公告与字典模块可正常访问。"),
                ("基本流程", "系统汇总学习进度、作业成绩和考试成绩；根据结课规则判断是否结课并发放学分；后台生成课程维度统计概览；学生查看个人成绩与学分结果；管理员或教师维护公告内容和公告类型；学生浏览公告信息。"),
                ("异常流程", "结课条件未满足时不发放学分；统计接口异常时后台页面提示加载失败；公告内容保存异常时阻止提交并保留编辑状态。"),
                ("后置条件", "课程结果、学分记录和公告信息被统一管理，支撑平台运营和学习结果展示。"),
            ],
        )
    )

    fragments.append(heading2_xml("3.2.6 智能问答功能"))
    fragments.append(
        paragraph_xml(
            "智能问答功能是现有系统中较新的扩展模块，目标是在平台内部提供统一的“问 AI”入口。学生和管理员可以创建会话、进行多轮提问、查看历史记录并接收推荐问题；教师端则在题库管理页面复用 AI 能力生成试题草稿。智能问答功能用例图如图3-7所示："
        )
    )
    fragments.append(
        figure_box_xml(
            "图3-7",
            "智能问答功能用例图",
            "fig3-7-ai-assistant-usecase.svg",
        )
    )
    fragments.append(
        paragraph_xml(
            "当前 AI 问答能力已与系统业务数据打通，可围绕课程、作业、考试和成绩等上下文进行回答；当模型不可用时，系统还支持规则回退，避免直接失效。智能问答功能用例规约如表3-6所示："
        )
    )
    fragments.append(
        spec_table_xml(
            "表3-6",
            "智能问答功能用例规约表",
            [
                ("用例名称", "智能问答功能"),
                ("参与角色", "学生、教师、管理员"),
                ("前置条件", "用户已登录；AI 会话与消息表已存在；AI 相关接口和配置项已部署。"),
                ("基本流程", "用户进入问 AI 页面并创建会话；系统保存会话信息；用户进行多轮提问；后端结合系统业务上下文调用模型或规则回答；系统保存消息记录并返回前端展示；教师在题库页可调用 AI 生成题目草稿。"),
                ("异常流程", "模型服务不可用时走规则回退或返回明确错误；用户未登录时不能创建会话；输出不可解析时题目草稿不写入题库。"),
                ("后置条件", "AI 会话和消息记录被持久化，问答结果和题目草稿可在业务页面继续复用。"),
            ],
        )
    )

    fragments.append(heading1_xml("3.3 系统非功能性需求分析"))
    fragments.append(
        paragraph_xml(
            "除功能性需求外，现有系统还需要满足性能、安全性、可用性和易维护性等非功能性要求。由于平台已经承载课程学习、作业考试和 AI 问答等多种业务场景，因此这些非功能性需求会直接影响系统的实际可用程度。"
        )
    )

    fragments.append(heading2_xml("3.3.1 性能"))
    fragments.append(
        paragraph_xml(
            "系统需要保证常用页面和接口具有可接受的响应速度。对于课程列表、公告列表、题库分页、考试记录等典型查询操作，应尽量控制在较短时间内完成返回；对于学习进度写入、作业提交和考试交卷等操作，也应保证在并发场景下仍能稳定完成。由于当前系统已经引入分页、课程筛选和统一接口封装，因此后续仍需围绕数据库索引、连接池和前端请求策略继续优化性能。"
        )
    )

    fragments.append(heading2_xml("3.3.2 安全性"))
    fragments.append(
        paragraph_xml(
            "系统中涉及用户账号、教师信息、学生学习记录、作业成绩、考试成绩以及 AI 会话记录等数据，因此必须保证数据访问安全和业务权限安全。现有系统通过 token 与 session 结合的方式完成身份恢复，并以角色菜单和后端接口双重控制权限范围。对于敏感操作，如课程审核、题库维护、成绩查看和 AI 参数配置，应严格限制可访问角色，防止越权访问和数据泄露。"
        )
    )

    fragments.append(heading2_xml("3.3.3 可用性"))
    fragments.append(
        paragraph_xml(
            "系统需要支持学生、教师和管理员在日常教学周期内持续使用，因此可用性要求较高。对于登录、选课、学习、作业提交、考试作答和公告查看等高频操作，应尽量减少因前端状态异常、接口失败或数据回显不一致导致的中断。当前系统已对学习进度回显、资源表单校验和公告编辑保存等问题进行修复，说明可用性优化已经成为现阶段的重要工作内容。"
        )
    )

    fragments.append(heading2_xml("3.3.4 易维护性"))
    fragments.append(
        paragraph_xml(
            "现有系统采用较为清晰的前后端分层和模块拆分方式，具备一定易维护性。后端围绕控制器、服务、实体和数据访问层组织业务代码，前端则通过 front-web、admin-web 和 shared 进行拆分，使不同角色页面和公共逻辑边界较为清楚。与此同时，docs 目录中已经沉淀了系统分析、核心业务进度和 AI 专项说明，这为后续需求追踪、问题定位和功能扩展提供了文档支持。"
        )
    )

    fragments.append(heading1_xml("3.4 本章小结"))
    fragments.append(
        paragraph_xml(
            "本章结合现有系统代码和文档，对线上教育培训办公系统的需求进行了梳理与分析。在角色层面，系统已形成管理员、教师和学生三类清晰分工；在功能层面，系统已覆盖登录、课程资源、学习进度、作业、考试、结课统计、公告和智能问答等核心业务；在非功能层面，也对性能、安全性、可用性和易维护性提出了要求。这些分析结果为后续系统设计、数据库设计和详细实现说明奠定了基础。"
        )
    )

    return fragments


def build_docx() -> None:
    if not TEMPLATE_DOCX.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_DOCX}")

    with ZipFile(TEMPLATE_DOCX, "r") as zin:
        with ZipFile(OUTPUT_DOCX, "w", compression=ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "word/document.xml":
                    root = ET.fromstring(data)
                    body = root.find(qn(W_NS, "body"))
                    if body is None:
                        raise RuntimeError("Template document has no body element")
                    sect_pr = body.find(qn(W_NS, "sectPr"))
                    if sect_pr is None:
                        raise RuntimeError("Template document has no sectPr element")

                    new_body = ET.Element(qn(W_NS, "body"))
                    wrapper = ET.fromstring(
                        f'<root xmlns:w="{W_NS}" xmlns:r="{R_NS}">' + "".join(body_fragments()) + "</root>"
                    )
                    for child in wrapper:
                        new_body.append(child)
                    new_body.append(copy.deepcopy(sect_pr))
                    root.remove(body)
                    root.append(new_body)
                    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                zout.writestr(item, data)

    extract_dir = CHAPTER_DIR / ".tmp_chapter3_docx"
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
    update_core_props(extract_dir / "docProps" / "core.xml", "第三章 需求分析")
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


def dot_text(title: str, actors: list[str], usecases: list[str], edges: list[tuple[str, str]]) -> str:
    lines = [
        "digraph G {",
        '  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="%s", fontname="Microsoft YaHei", fontsize=22, rankdir="LR", splines=line, nodesep=0.35, ranksep=0.70, pad=0.2, margin=0.15];'
        % title,
        '  node [fontname="Microsoft YaHei", fontsize=12, color="#444444", penwidth=1.2];',
        '  edge [fontname="Microsoft YaHei", fontsize=9, color="#666666", penwidth=1.0, arrowsize=0.7];',
        "",
    ]
    for idx, actor in enumerate(actors, start=1):
        lines.append(
            f'  actor{idx} [label="{actor}", shape=box, style="rounded,filled", fillcolor="#FFFFFF"];'
        )
    for idx, usecase in enumerate(usecases, start=1):
        lines.append(
            f'  uc{idx} [label="{usecase}", shape=ellipse, style="filled", fillcolor="#FFFFFF"];'
        )
    lines.append("")
    for source, target in edges:
        lines.append(f"  {source} -> {target};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def svg_text(title: str, actors: list[str], usecases: list[str], edges: list[tuple[str, str]]) -> str:
    actor_w = 96
    actor_h = 34
    usecase_w = 180
    usecase_h = 42
    width = 760
    height = max(260, 80 + max(len(actors), len(usecases)) * 70)

    actor_positions: dict[str, tuple[float, float]] = {}
    usecase_positions: dict[str, tuple[float, float]] = {}

    for idx, actor in enumerate(actors, start=1):
        actor_positions[f"actor{idx}"] = (50, 70 + (idx - 1) * 70)
    for idx, usecase in enumerate(usecases, start=1):
        usecase_positions[f"uc{idx}"] = (340, 60 + (idx - 1) * 70)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<style><![CDATA['
        '.title { font: 700 24px "Microsoft YaHei", "PingFang SC", sans-serif; fill: #222; }'
        '.actor { fill: #fff; stroke: #4b5563; stroke-width: 1.5; }'
        '.usecase { fill: #fff; stroke: #374151; stroke-width: 1.5; }'
        '.label { font: 14px "Microsoft YaHei", "PingFang SC", sans-serif; fill: #222; }'
        '.edge { stroke: #6b7280; stroke-width: 1.2; fill: none; }'
        ']]></style>',
        "</defs>",
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" fill="#ffffff" stroke="#d1d5db" stroke-width="1"/>',
        f'<text x="{width / 2}" y="34" text-anchor="middle" class="title">{escape(title)}</text>',
    ]

    for key, (x, y) in actor_positions.items():
        label = actors[int(key.replace("actor", "")) - 1]
        parts.append(
            f'<rect x="{x}" y="{y}" width="{actor_w}" height="{actor_h}" rx="8" ry="8" class="actor"/>'
        )
        parts.append(
            f'<text x="{x + actor_w / 2}" y="{y + 22}" text-anchor="middle" class="label">{escape(label)}</text>'
        )

    for key, (x, y) in usecase_positions.items():
        label = usecases[int(key.replace("uc", "")) - 1]
        parts.append(
            f'<ellipse cx="{x + usecase_w / 2}" cy="{y + usecase_h / 2}" rx="{usecase_w / 2}" ry="{usecase_h / 2}" class="usecase"/>'
        )
        parts.append(
            f'<text x="{x + usecase_w / 2}" y="{y + 25}" text-anchor="middle" class="label">{escape(label)}</text>'
        )

    for source, target in edges:
        sx, sy = actor_positions.get(source, usecase_positions.get(source))  # type: ignore[arg-type]
        tx, ty = actor_positions.get(target, usecase_positions.get(target))  # type: ignore[arg-type]
        if source.startswith("actor"):
            x1 = sx + actor_w
            y1 = sy + actor_h / 2
        else:
            x1 = sx + usecase_w / 2
            y1 = sy + usecase_h / 2
        if target.startswith("uc"):
            x2 = tx
            y2 = ty + usecase_h / 2
        else:
            x2 = tx
            y2 = ty + actor_h / 2
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge"/>')

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def build_diagrams() -> None:
    diagrams = [
        {
            "base": "fig3-1-system-role-usecase",
            "title": "现有系统角色用例图",
            "actors": ["管理员", "教师", "学生"],
            "usecases": [
                "用户与权限管理",
                "课程与资源维护",
                "选课与课程学习",
                "作业与考试管理",
                "成绩统计与公告发布",
                "AI 问答与题库辅助",
            ],
            "edges": [
                ("actor1", "uc1"),
                ("actor1", "uc5"),
                ("actor1", "uc6"),
                ("actor2", "uc2"),
                ("actor2", "uc4"),
                ("actor2", "uc6"),
                ("actor3", "uc3"),
                ("actor3", "uc4"),
                ("actor3", "uc6"),
            ],
        },
        {
            "base": "fig3-2-login-usecase",
            "title": "系统登录功能用例图",
            "actors": ["用户"],
            "usecases": ["系统登录", "重置密码", "退出系统"],
            "edges": [("actor1", "uc1"), ("actor1", "uc2"), ("actor1", "uc3")],
        },
        {
            "base": "fig3-3-course-resource-usecase",
            "title": "课程与资源管理用例图",
            "actors": ["教师", "管理员", "学生"],
            "usecases": [
                "创建课程",
                "审核课程",
                "维护章节",
                "上传课程资源",
                "审核资源",
                "浏览课程详情",
            ],
            "edges": [
                ("actor1", "uc1"),
                ("actor1", "uc3"),
                ("actor1", "uc4"),
                ("actor2", "uc2"),
                ("actor2", "uc5"),
                ("actor3", "uc6"),
            ],
        },
        {
            "base": "fig3-4-study-homework-usecase",
            "title": "学习进度与作业管理用例图",
            "actors": ["学生", "教师"],
            "usecases": ["选课", "视频学习", "记录学习进度", "提交作业", "批改作业", "查看成绩反馈"],
            "edges": [
                ("actor1", "uc1"),
                ("actor1", "uc2"),
                ("actor1", "uc3"),
                ("actor1", "uc4"),
                ("actor1", "uc6"),
                ("actor2", "uc5"),
            ],
        },
        {
            "base": "fig3-5-exam-question-usecase",
            "title": "考试与题库管理用例图",
            "actors": ["教师", "学生"],
            "usecases": ["题库管理", "AI 生成题目草稿", "发布考试", "在线答题", "自动判分", "阅卷与成绩汇总"],
            "edges": [
                ("actor1", "uc1"),
                ("actor1", "uc2"),
                ("actor1", "uc3"),
                ("actor1", "uc6"),
                ("actor2", "uc4"),
                ("actor2", "uc5"),
            ],
        },
        {
            "base": "fig3-6-settlement-report-notice-usecase",
            "title": "结课统计与公告管理用例图",
            "actors": ["管理员", "教师", "学生"],
            "usecases": ["结课判定", "学分发放", "课程统计概览", "公告发布", "公告浏览", "成绩与学分查看"],
            "edges": [
                ("actor1", "uc1"),
                ("actor1", "uc2"),
                ("actor1", "uc3"),
                ("actor1", "uc4"),
                ("actor2", "uc3"),
                ("actor2", "uc4"),
                ("actor3", "uc5"),
                ("actor3", "uc6"),
            ],
        },
        {
            "base": "fig3-7-ai-assistant-usecase",
            "title": "智能问答功能用例图",
            "actors": ["学生", "教师", "管理员"],
            "usecases": ["创建会话", "多轮提问", "推荐问题", "规则回退回答", "题目草稿生成", "查看历史消息"],
            "edges": [
                ("actor1", "uc1"),
                ("actor1", "uc2"),
                ("actor1", "uc3"),
                ("actor1", "uc4"),
                ("actor1", "uc6"),
                ("actor2", "uc5"),
                ("actor3", "uc1"),
                ("actor3", "uc2"),
                ("actor3", "uc6"),
            ],
        },
    ]

    for diagram in diagrams:
        dot_path = CHAPTER_DIR / f"{diagram['base']}.dot"
        svg_path = CHAPTER_DIR / f"{diagram['base']}.svg"
        dot_path.write_text(
            dot_text(diagram["title"], diagram["actors"], diagram["usecases"], diagram["edges"]),
            encoding="utf-8",
        )
        svg_path.write_text(
            svg_text(diagram["title"], diagram["actors"], diagram["usecases"], diagram["edges"]),
            encoding="utf-8",
        )


def main() -> None:
    CHAPTER_DIR.mkdir(parents=True, exist_ok=True)
    build_docx()
    build_diagrams()
    print(OUTPUT_DOCX)


if __name__ == "__main__":
    main()
