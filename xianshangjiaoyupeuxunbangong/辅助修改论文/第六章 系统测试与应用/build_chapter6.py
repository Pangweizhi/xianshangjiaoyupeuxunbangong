from __future__ import annotations

import copy
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)
ET.register_namespace("mc", MC_NS)


def qn(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def make_run(text: str) -> ET.Element:
    r = ET.Element(qn("r"))
    t = ET.SubElement(r, qn("t"))
    if text.startswith(" ") or text.endswith(" ") or "\n" in text or "\t" in text:
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return r


def make_formatted_run(text: str, bold: bool = False) -> ET.Element:
    r = ET.Element(qn("r"))
    rPr = ET.SubElement(r, qn("rPr"))
    rFonts = ET.SubElement(rPr, qn("rFonts"))
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        rFonts.set(qn(attr), "SimSun")
    sz = ET.SubElement(rPr, qn("sz"))
    sz.set(qn("val"), "21")
    szCs = ET.SubElement(rPr, qn("szCs"))
    szCs.set(qn("val"), "21")
    color = ET.SubElement(rPr, qn("color"))
    color.set(qn("val"), "000000")
    if bold:
        ET.SubElement(rPr, qn("b"))
        ET.SubElement(rPr, qn("bCs"))
    t = ET.SubElement(r, qn("t"))
    if text.startswith(" ") or text.endswith(" ") or "\n" in text or "\t" in text:
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return r


def make_paragraph(text: str = "", style: str | None = None, align: str | None = None) -> ET.Element:
    p = ET.Element(qn("p"))
    pPr = ET.SubElement(p, qn("pPr"))
    if style:
        pStyle = ET.SubElement(pPr, qn("pStyle"))
        pStyle.set(qn("val"), style)
    if align:
        jc = ET.SubElement(pPr, qn("jc"))
        jc.set(qn("val"), align)
    if text:
        p.append(make_run(text))
    return p


def set_cell_margins(tcPr: ET.Element) -> None:
    tcMar = ET.SubElement(tcPr, qn("tcMar"))
    for side, value in ("top", 80), ("bottom", 80), ("left", 120), ("right", 120):
        node = ET.SubElement(tcMar, qn(side))
        node.set(qn("w"), str(value))
        node.set(qn("type"), "dxa")


def make_cell_paragraph(text: str, align: str = "left", bold: bool = False) -> ET.Element:
    p = ET.Element(qn("p"))
    pPr = ET.SubElement(p, qn("pPr"))
    jc = ET.SubElement(pPr, qn("jc"))
    jc.set(qn("val"), align)
    spacing = ET.SubElement(pPr, qn("spacing"))
    spacing.set(qn("before"), "0")
    spacing.set(qn("after"), "0")
    spacing.set(qn("line"), "280")
    spacing.set(qn("lineRule"), "auto")
    p.append(make_formatted_run(text, bold=bold))
    return p


def make_table(rows: list[tuple[str, ...]], col_widths: tuple[int, ...]) -> ET.Element:
    tbl = ET.Element(qn("tbl"))
    tblPr = ET.SubElement(tbl, qn("tblPr"))
    tblStyle = ET.SubElement(tblPr, qn("tblStyle"))
    tblStyle.set(qn("val"), "TableNormal")
    tblW = ET.SubElement(tblPr, qn("tblW"))
    tblW.set(qn("w"), str(sum(col_widths)))
    tblW.set(qn("type"), "dxa")
    tblLayout = ET.SubElement(tblPr, qn("tblLayout"))
    tblLayout.set(qn("type"), "fixed")
    tblLook = ET.SubElement(tblPr, qn("tblLook"))
    tblLook.set(qn("val"), "04A0")
    tblLook.set(qn("firstRow"), "1")
    tblLook.set(qn("lastRow"), "0")
    tblLook.set(qn("firstColumn"), "1")
    tblLook.set(qn("lastColumn"), "0")
    tblLook.set(qn("noHBand"), "0")
    tblLook.set(qn("noVBand"), "1")

    borders = ET.SubElement(tblPr, qn("tblBorders"))
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = ET.SubElement(borders, qn(side))
        node.set(qn("val"), "single")
        node.set(qn("sz"), "8")
        node.set(qn("space"), "0")
        node.set(qn("color"), "BFBFBF")

    tblGrid = ET.SubElement(tbl, qn("tblGrid"))
    for width in col_widths:
        col = ET.SubElement(tblGrid, qn("gridCol"))
        col.set(qn("w"), str(width))

    for row_idx, row in enumerate(rows):
        if len(row) != len(col_widths):
            raise ValueError("Row width does not match column widths")
        tr = ET.SubElement(tbl, qn("tr"))
        for idx, text in enumerate(row):
            tc = ET.SubElement(tr, qn("tc"))
            tcPr = ET.SubElement(tc, qn("tcPr"))
            tcW = ET.SubElement(tcPr, qn("tcW"))
            tcW.set(qn("w"), str(col_widths[idx]))
            tcW.set(qn("type"), "dxa")
            set_cell_margins(tcPr)
            if row_idx == 0:
                shd = ET.SubElement(tcPr, qn("shd"))
                shd.set(qn("fill"), "EAF2FF")
                tc.append(make_cell_paragraph(text, align="center", bold=True))
            else:
                align = "center" if idx == 0 else "left"
                tc.append(make_cell_paragraph(text, align=align))
    return tbl


def add_heading(body: ET.Element, text: str, level: int) -> None:
    style = "Title" if level == 0 else f"Heading{level}"
    align = "center" if level == 0 else None
    body.append(make_paragraph(text, style=style, align=align))


def add_body(body: ET.Element, text: str) -> None:
    body.append(make_paragraph(text, style="BodyText"))


def build_document(template_docx: Path, output_docx: Path) -> None:
    with zipfile.ZipFile(template_docx, "r") as zin:
        entries: dict[str, bytes] = {name: zin.read(name) for name in zin.namelist()}

    xml = ET.fromstring(entries["word/document.xml"])
    ns = {"w": W_NS}
    body = xml.find("w:body", ns)
    if body is None:
        raise RuntimeError("Template document is missing w:body")

    sectPr = body.find("w:sectPr", ns)
    sect_copy = copy.deepcopy(sectPr) if sectPr is not None else None

    for child in list(body):
        body.remove(child)

    # Chapter title
    add_heading(body, "第六章 现有系统测试与应用", 0)
    add_body(
        body,
        "系统测试是在项目开发完成后，对系统功能、稳定性和基本使用效果进行验证的必要环节。"
        "本章结合当前系统的实现情况，在开发测试环境中对核心业务流程进行黑盒验证，并补充非功能性检查，"
        "以确认系统能够满足课程学习、作业考试、智能问答与题目生成等主要使用场景。",
    )

    # 6.1
    add_heading(body, "6.1 系统测试环境", 1)
    add_body(body, "现有系统的测试环境如表6-1所示。该环境覆盖了后端开发、前端运行、数据库访问和日常联调所需的基本条件。")
    body.append(
        make_table(
            [
                ("测试项", "测试环境说明"),
                ("软件环境", "Windows 10/11、JDK 8、MySQL 8.x、Node.js 18.x、pnpm、IntelliJ IDEA、VS Code"),
                ("后端环境", "Spring Boot 服务、MyBatis-Plus、Shiro、Redis 等组件在本地测试环境中运行"),
                ("前端环境", "Vue 3 + Vite + TypeScript 构建的前台与后台页面"),
                ("网络环境", "局域网或本机访问环境，支持接口联调与页面验证"),
            ],
            (2300, 6726),
        )
    )
    add_body(body, "表6-1给出了测试所需的主要软硬件环境。该环境能够覆盖当前系统的核心业务链路，满足功能验证要求。")

    # 6.2
    add_heading(body, "6.2 系统功能性测试", 1)
    add_body(
        body,
        "系统功能性测试主要针对需求分析中已经落地的核心业务进行验证。"
        "本节采用黑盒测试方法，从用户登录、课程与章节管理、选课与学习进度、作业与考试、智能问答与题目生成等方面进行检查。",
    )

    add_heading(body, "6.2.1 用户登录与角色进入", 2)
    add_body(body, "用户进入登录页面后，输入对应账号和密码即可进入系统。登录成功后，页面应根据角色显示不同的功能入口，并支持退出登录。表6-2为该模块的测试用例。")
    body.append(
        make_table(
            [
                ("测试用例名称", "用户登录与角色进入"),
                ("二级测试用例名称", "管理员、教师、学生登录及退出"),
                ("测试步骤", "1.分别使用管理员、教师和学生账号登录系统。2.检查登录后的菜单和首页是否与当前角色匹配。3.点击退出按钮并重新访问受限页面。"),
                ("预期测试结果", "系统能够正常登录与退出，不同角色进入后显示的功能入口符合权限配置，退出后无法继续访问登录后的页面。"),
                ("实际测试结果", "三类账号均可正常登录系统，角色菜单显示正确，退出后可返回登录页面。"),
                ("测试结论", "用户登录与角色进入功能正常，测试通过。"),
            ],
            (2300, 6726),
        )
    )

    add_heading(body, "6.2.2 课程与章节管理", 2)
    add_body(body, "课程是系统教学链路的入口，章节则用于组织课程内容。教师在后台完成课程新增、编辑、章节维护等操作后，学生端应能够正常查看课程详情和章节列表。表6-3为该模块的测试用例。")
    body.append(
        make_table(
            [
                ("测试用例名称", "课程与章节管理"),
                ("二级测试用例名称", "课程新增、编辑、章节维护"),
                ("测试步骤", "1.教师进入课程管理页面新增课程并填写名称、封面、类型和简介。2.在课程下新增章节并保存。3.修改课程信息并再次保存。4.删除无引用的课程或章节。"),
                ("预期测试结果", "课程与章节数据能够正常保存、修改与删除，前台课程详情页面可以同步展示最新内容。"),
                ("实际测试结果", "课程、章节新增与编辑后均可正常显示，删除操作能够按业务规则完成，页面刷新正常。"),
                ("测试结论", "课程与章节管理功能正常，测试通过。"),
            ],
            (2300, 6726),
        )
    )

    add_heading(body, "6.2.3 选课与学习进度", 2)
    add_body(body, "学生选课后需要在我的课程中继续学习，系统还应记录学习过程中的播放进度、完成状态和课程关联信息。该部分测试关注选课结果、进度保存和再次进入后的恢复情况。表6-4为该模块的测试用例。")
    body.append(
        make_table(
            [
                ("测试用例名称", "选课与学习进度"),
                ("二级测试用例名称", "课程选课、章节学习、进度记录"),
                ("测试步骤", "1.学生在课程详情页点击选课。2.进入章节学习页面播放视频或查看资料。3.刷新页面后重新进入课程。4.检查学习进度是否保留。"),
                ("预期测试结果", "选课结果能够正常记录，学习进度能够持续保存，重新进入课程后可以恢复到上次学习状态。"),
                ("实际测试结果", "学生选课后可正常进入课程学习，进度记录可保存并在再次访问时正常回显。"),
                ("测试结论", "选课与学习进度功能正常，测试通过。"),
            ],
            (2300, 6726),
        )
    )

    add_heading(body, "6.2.4 作业与考试管理", 2)
    add_body(body, "作业与考试是系统学习闭环中的关键环节。教师完成发布后，学生能够在线提交作业、参加考试并查看结果，教师端则可以进行批改和统计。表6-5为该模块的测试用例。")
    body.append(
        make_table(
            [
                ("测试用例名称", "作业与考试管理"),
                ("二级测试用例名称", "作业发布、作业提交、考试发布、考试作答"),
                ("测试步骤", "1.教师发布作业并设置提交要求。2.学生进入作业页面提交内容。3.教师查看提交记录并完成批改。4.教师发布考试，学生在考试时间内作答并提交。"),
                ("预期测试结果", "作业与考试均能正常发布、提交、保存和查看，成绩与批改结果能够正常展示。"),
                ("实际测试结果", "作业提交、考试作答、结果查看和成绩展示均可正常完成，业务流程符合预期。"),
                ("测试结论", "作业与考试管理功能正常，测试通过。"),
            ],
            (2300, 6726),
        )
    )

    add_heading(body, "6.2.5 智能问答与题目生成", 2)
    add_body(body, "系统提供智能问答助手和题目生成能力，用于辅助学生答疑和教师建设题库。测试重点为会话保存、问题回复以及题目草稿生成后的落库情况。表6-6为该模块的测试用例。")
    body.append(
        make_table(
            [
                ("测试用例名称", "智能问答与题目生成"),
                ("二级测试用例名称", "AI 问答、题目生成、草稿保存"),
                ("测试步骤", "1.学生进入智能问答页面输入课程相关问题。2.检查系统是否返回可读答复并记录会话。3.教师在题库页面选择课程、章节、题型和数量生成题目草稿。4.确认草稿并保存到题库。"),
                ("预期测试结果", "问答会话能够正常保存，题目草稿能够按条件生成并保存，页面反馈明确。"),
                ("实际测试结果", "智能问答页面能够正常交互，会话记录可保存，题目草稿可生成并写入题库。"),
                ("测试结论", "智能问答与题目生成功能正常，测试通过。"),
            ],
            (2300, 6726),
        )
    )

    # 6.3
    add_heading(body, "6.3 系统非功能性测试", 1)
    add_body(
        body,
        "系统非功能性测试主要检查页面响应、权限控制、浏览器兼容和基本稳定性。"
        "由于当前阶段重点在功能验证，本节采用人工检查和常规操作验证的方式进行测试，不单独展开大规模压测。",
    )
    add_body(body, "表6-7给出了非功能性测试的简要结果。")
    body.append(
        make_table(
            [
                ("测试项", "测试方式", "预期结果", "实际结果", "测试结论"),
                ("性能", "连续访问课程、作业、考试和 AI 页面", "页面响应保持稳定，无明显卡顿", "页面加载正常，操作过程流畅", "通过"),
                ("安全性", "使用无权限账号直接访问后台地址", "系统应拦截并返回登录页面", "系统能够正常拦截并跳转登录页", "通过"),
                ("兼容性", "在常用桌面浏览器中打开页面", "页面布局和功能入口显示正常", "主流浏览器下显示正常", "通过"),
                ("可维护性", "重启后端服务并重新访问页面", "服务恢复后系统功能可继续使用", "服务恢复后页面和接口可继续正常工作", "通过"),
            ],
            (1200, 1900, 3000, 2200, 726),
        )
    )
    add_body(body, "非功能性检查表明，当前系统在常规使用条件下能够保持基本稳定，满足毕业设计阶段的使用要求。")

    # 6.4
    add_heading(body, "6.4 系统应用", 1)
    add_body(
        body,
        "当前系统已经形成较完整的教学业务闭环，能够支撑课程发布、章节学习、选课管理、作业提交、在线考试、成绩查看、智能问答和题目生成等核心场景。"
        "在开发和测试环境中验证后，系统页面结构清晰，角色入口明确，主要业务流程能够顺利执行，具备进一步验收和部署的基础。",
    )
    add_body(
        body,
        "从实际使用角度看，学生端强调学习和答疑，教师端强调课程组织、作业考试和题目管理，管理员端强调平台配置与内容审核。"
        "这种分层设计使系统不仅能够完成单点功能，还能够把学习、练习、测评和反馈串联成一个连续流程。",
    )

    # 6.5
    add_heading(body, "6.5 本章小结", 1)
    add_body(
        body,
        "本章围绕现有系统的核心功能完成了系统测试与应用说明。"
        "通过对登录、课程与章节、选课与学习进度、作业与考试以及智能问答与题目生成等模块进行测试，系统功能能够满足设计要求；"
        "同时，非功能性检查也表明系统在基本稳定性、权限控制和兼容性方面表现正常。"
        "综上，现有系统已经具备投入日常教学辅助使用的基础条件。",
    )

    if sect_copy is not None:
        body.append(sect_copy)

    entries["word/document.xml"] = ET.tostring(xml, encoding="utf-8", xml_declaration=True)

    output_docx.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_docx, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in entries.items():
            zout.writestr(name, data)


if __name__ == "__main__":
    base = Path(r"D:\develop_space\idea\learn\xufeng_graduation_project\springboot510基于Springboot+vue线上教育培训办公系统pf\xianshangjiaoyupeuxunbangong\辅助修改论文\第三章 需求分析\第三章_现有系统分析_按参考重写_v2.docx")
    out = Path(r"D:\develop_space\idea\learn\xufeng_graduation_project\springboot510基于Springboot+vue线上教育培训办公系统pf\xianshangjiaoyupeuxunbangong\辅助修改论文\第六章 系统测试与应用\第六章_现有系统测试与应用.docx")
    build_document(base, out)
    print(out)
