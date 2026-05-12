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
OUTPUT_DOCX = CHAPTER_DIR / "实体关系图需求说明.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)
ET.register_namespace("cp", CP_NS)
ET.register_namespace("dc", DC_NS)


@dataclass
class Section:
    title: str
    lines: list[str]


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
        f"<w:ind w:firstLine=\"{first_line}\"/>"
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
            child.text = "用于 ProcessOn AI 生成实体关系图的需求说明"
    ET.ElementTree(root).write(core_path, encoding="utf-8", xml_declaration=True)


def sections() -> list[Section]:
    return [
        Section(
            "文档目的与统一要求",
            [
                "本需求文档用于指导 ProcessOn 网站中的 AI 自动生成实体关系图。生成对象包括系统总体E-R图，以及管理员、教师、学生、课程、作业、题目、考试、AI会话等单体实体E-R图。",
                "所有图均采用中文标注，白底黑线风格，实体使用矩形，属性使用椭圆，关系使用菱形。若 ProcessOn 支持，可将“编号”字段标记为主键；若不支持，可仅保留为普通属性，不额外增加复杂标识。",
                "单体实体E-R图以“一个中心实体 + 多个属性节点”的放射式结构为主，整体布局要求疏朗、对称、易读，不要使用过多弯折连线。系统总体E-R图则需要体现核心实体、关键业务关系和主链路方向，避免把所有实体堆叠在同一层。",
            ],
        ),
        Section(
            "系统总体E-R图需求",
            [
                "图名称：系统总体E-R图。",
                "绘制目标：展示线上教育培训管理系统中核心实体之间的整体关系，反映课程教学、学习进度、作业考试、学分发放和AI问答等主要数据链路。",
                "需要包含的实体：管理员、教师、学生、课程、章节、资源、作业、题目、考试、考试记录、学分记录、AI会话。",
                "需要包含的关系：管理员审核课程，教师创建课程，课程包含章节，章节包含资源，学生选课，学生学习资源，教师发布作业，学生提交作业，考试生成题目，学生参加考试并形成考试记录，课程向学生发放学分记录，学生发起AI会话，教师发起AI会话，AI会话关联课程与章节，作业关联题目。",
                "建议布局：第一层放管理员、教师、学生三类角色；第二层放课程和AI会话；第三层放章节、资源、作业、考试、学分记录；第四层放题目和考试记录。关系名称放在菱形节点中间，尽量保持同类关系横向对齐。",
                "绘图说明：本图强调“角色 -> 课程/学习对象 -> 业务结果”的主链路，不需要展开每个实体的全部字段，只需要突出实体名称与关系名称。",
            ],
        ),
        Section(
            "管理员实体E-R图需求",
            [
                "图名称：管理员实体E-R图。",
                "中心实体名称：管理员。",
                "需要绘制的属性：编号、用户名、密码、角色、创建时间。",
                "图形结构：管理员实体放在中间，五个属性节点围绕四周均匀分布，均通过无向直线连接到管理员实体。",
                "业务补充说明：在系统总体E-R图中，管理员与课程之间存在“审核”关系，因此该实体在风格上应体现平台管理主体特征。",
            ],
        ),
        Section(
            "教师实体E-R图需求",
            [
                "图名称：教师实体E-R图。",
                "中心实体名称：教师。",
                "需要绘制的属性：编号、用户名、密码、姓名、头像、身份证号、电话号码、电子邮箱、性别。",
                "图形结构：教师实体居中，属性按左右对称方式排布，优先保证姓名、用户名、电话号码等常用信息易于识别。",
                "业务补充说明：在系统总体E-R图中，教师与课程之间存在“创建”关系，与作业之间存在“发布”关系，与AI会话之间存在“发起”关系，因此教师是教学内容生产端和AI使用端的重要角色。",
            ],
        ),
        Section(
            "学生实体E-R图需求",
            [
                "图名称：学生实体E-R图。",
                "中心实体名称：学生。",
                "需要绘制的属性：编号、用户名、密码、姓名、头像、身份证号、电话号码、电子邮箱、班级、性别。",
                "图形结构：学生实体居中，十个属性分散在四周，排布时保证整体平衡，不要让同一侧过于拥挤。",
                "业务补充说明：在系统总体E-R图中，学生与课程存在“选课”关系，与资源存在“学习”关系，与作业存在“提交”关系，与考试存在“参加”关系，与学分记录存在“发放/获得”关系，与AI会话存在“发起”关系。",
            ],
        ),
        Section(
            "课程实体E-R图需求",
            [
                "图名称：课程实体E-R图。",
                "中心实体名称：课程。",
                "需要绘制的属性：编号、课程名称、课程封面、课程类型、课程时长、开始时间、结束时间、课程学分、审核状态、课程详情。",
                "图形结构：课程实体放在中间，十个属性节点环绕课程实体，属性文字尽量完整显示，不要缩写成英文。",
                "业务补充说明：在系统总体E-R图中，课程是核心枢纽实体，与教师存在“创建”关系，与管理员存在“审核”关系，与章节存在“包含”关系，与学生存在“选课”关系，与学分记录存在“发放”关系，同时也是作业、考试、AI会话等业务对象的上游实体。",
            ],
        ),
        Section(
            "作业实体E-R图需求",
            [
                "图名称：作业实体E-R图。",
                "中心实体名称：作业。",
                "需要绘制的属性：编号、作业名称、课程编号、章节编号、开始时间、结束时间、总分、发布状态、题目集合、作业详情。",
                "图形结构：作业实体居中，属性节点均匀环绕。课程编号、章节编号、题目集合等字段可以靠近同一侧排布，体现其业务关联性。",
                "业务补充说明：在系统总体E-R图中，教师发布作业，学生提交作业，作业与题目之间还存在关联关系，因此该实体应体现其位于课程考核链路中的中间位置。",
            ],
        ),
        Section(
            "题目实体E-R图需求",
            [
                "图名称：题目实体E-R图。",
                "中心实体名称：题目。",
                "需要绘制的属性：编号、考试编号、课程编号、题型、题目内容、选项A、选项B、选项C、选项D、答案、题目分值。",
                "图形结构：题目实体放在中心，内容较长的属性如“题目内容”可放在较宽的一侧，四个选项属性建议连续排布，便于阅读。",
                "业务补充说明：在系统总体E-R图中，题目由考试生成，同时作业也与题目存在关联，因此该实体兼具考试题库和作业题目承载作用。",
            ],
        ),
        Section(
            "考试实体E-R图需求",
            [
                "图名称：考试实体E-R图。",
                "中心实体名称：考试。",
                "需要绘制的属性：编号、课程编号、章节编号、考试名称、考试说明、考试时长、总分、及格分、开始时间、结束时间、考试状态。",
                "图形结构：考试实体居中，属性围绕排布。考试名称、考试说明、考试时长、总分、及格分等核心考核字段要优先清晰展示。",
                "业务补充说明：在系统总体E-R图中，考试生成题目，学生参加考试并形成考试记录，因此考试是连接课程、题库和成绩记录的关键实体。",
            ],
        ),
        Section(
            "AI会话实体E-R图需求",
            [
                "图名称：AI会话实体E-R图。",
                "中心实体名称：AI会话。",
                "需要绘制的属性：编号、用户编号、用户表、角色类型、会话标题、业务场景、课程编号、章节编号、资源编号、消息数、状态。",
                "图形结构：AI会话实体放在中间，属性节点左右分散排布，其中“业务场景、课程编号、章节编号、资源编号”建议放在相邻区域，以体现上下文绑定关系。",
                "业务补充说明：在系统总体E-R图中，学生和教师都可以发起AI会话，AI会话同时关联课程和章节，因此该实体既是用户交互数据，也是业务上下文数据的承载实体。",
            ],
        ),
        Section(
            "生成提示建议",
            [
                "若在 ProcessOn AI 中使用本说明文档生成图形，建议在提示词中补充以下约束：使用标准E-R图风格、中文标签、关系名称清晰、节点不要重叠、线条尽量笔直、整体留白均匀。",
                "若 ProcessOn AI 生成的总体图过于拥挤，优先保留实体名称和关系名称，不强行在总体图中展示单个实体的全部属性；属性应主要放在单体实体E-R图中展开。",
                "最终输出应分别生成系统总体E-R图，以及管理员、教师、学生、课程、作业、题目、考试、AI会话八张单体实体E-R图。如 AI 支持继续扩展，也可额外补绘章节、资源、考试记录、学分记录等辅助实体图。 ",
            ],
        ),
    ]


def build_paragraphs() -> list[str]:
    fragments = [
        title_xml("实体关系图需求说明"),
        paragraph_xml(
            "本文档用于为 ProcessOn 网站中的 AI 提供明确的绘图需求，指导其生成“第四章 数据库的逻辑设计”中所需的系统总体E-R图和各核心实体E-R图。文档内容依据当前“代码和图”文件夹中的各实体E-R图代码和系统总体E-R图代码整理而成，重点转述实体名称、属性要求、关系要求和布局要求。"
        ),
        heading1_xml("一、总体要求"),
    ]
    all_sections = sections()
    for idx, section in enumerate(all_sections):
        if idx > 0:
            fragments.append(heading2_xml(section.title))
        for line in section.lines:
            fragments.append(paragraph_xml(line))
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

    extract_dir = CHAPTER_DIR / ".tmp_er_requirement"
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
    update_core_props(extract_dir / "docProps" / "core.xml", "实体关系图需求说明")
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
