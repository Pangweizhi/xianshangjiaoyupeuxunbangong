from __future__ import annotations

import copy
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace("w", W_NS)

BASE_DIR = Path(__file__).resolve().parent
DOCX_PATH = BASE_DIR / "现有系统数据库的逻辑设计.docx"
WORK_DIR = BASE_DIR / "_logic_doc_work"


REPLACEMENTS = {
    "本系统的数据库逻辑设计主要包括总体 E-R 图以及若干核心实体或实体组合 E-R 图。总体图用于说明系统核心数据表之间的主从关系和业务流向，单体或组合实体图则重点刻画各表的关键属性和联系字段，为后续数据库表设计、接口设计和业务实现提供依据。":
    "本系统的数据库逻辑设计主要包括系统总体 E-R 图以及若干核心实体 E-R 图。总体图用于说明课程学习、作业、考试、学分与 AI 会话等核心数据对象之间的关联关系，各实体图则进一步展示单个数据表的关键属性，为后续数据库表设计和业务实现提供依据。",

    "如图4.14所示，系统总体E-R图描述了管理员、教师、学生、课程、章节、资源、选课、学习进度、作业、考试、学分记录以及智能问答等核心实体之间的联系，体现了现有系统围绕“课程学习全流程”组织数据的整体逻辑结构。":
    "如图4.14所示，系统总体E-R图描述了管理员、教师、学生、课程、章节、资源、作业、考试、题目、考试记录、学分记录和 AI 会话等核心实体之间的联系，重点体现了课程教学、学习考核和智能辅学三类业务在数据库层面的整体逻辑结构。",

    "如图4.15所示，管理员实体主要用于后台登录认证、课程与资源审核以及系统参数维护，包含用户名、密码、角色和创建时间等基本字段，是平台级管理能力的数据基础。":
    "如图4.15所示，管理员实体主要用于后台登录认证和平台管理，图中给出了编号、用户名、密码、角色、创建时间等核心属性，是系统执行审核与运维管理的数据基础。",

    "如图4.16所示，教师实体保存教师账号、身份信息和联系方式等内容，并通过教师编号与课程、作业、考试等业务表建立关联，是教学内容生产端的核心主体。":
    "如图4.16所示，教师实体保存教师账号、姓名、头像、身份证号、电话号码、电子邮箱和性别等基础信息，并以编号作为课程、作业和考试等教学业务数据的关联依据，是教学内容发布端的核心实体。",

    "如图4.17所示，学生实体记录学生账号、班级、联系方式等基础信息，用于支撑选课、学习进度、作业提交、考试作答和 AI 会话等前台业务。":
    "如图4.17所示，学生实体记录学生用户名、密码、姓名、头像、身份证号、电话号码、电子邮箱、班级和性别等基础信息，用于支撑课程学习、考试作答和 AI 会话等前台业务。",

    "如图4.18所示，课程实体是整个教学链路的中心实体，既保存课程名称、类型、开始结束时间、学分和审核状态等核心属性，又通过外键字段与教师、章节、作业、考试和选课记录发生联系。":
    "如图4.18所示，课程实体是教学业务的中心实体，图中包含课程名称、课程封面、课程类型、课程时长、开始时间、结束时间、课程学分、审核状态和课程详情等核心属性，用于支撑课程展示、审核和后续教学活动展开。",

    "如图4.21所示，作业与作业提交实体用于支撑课程作业发布、提交和批改流程。作业实体负责记录所属课程、章节、时间窗口和总分，作业提交实体则负责保存学生提交内容、评分、评语和题目快照等信息。":
    "如图4.21所示，作业实体用于支撑课程作业发布环节，图中主要包含作业名称、课程编号、章节编号、开始时间、结束时间、总分、发布状态、题目集合和作业详情等属性，用于描述一次作业任务的基本信息与发布时间要求。",

    "如图4.22所示，考试与题库实体反映了现有系统的在线考试逻辑。考试实体描述考试规则与时间范围，题库实体记录题型、答案和分值，考试记录实体保存学生答题快照、自动评分与最终成绩。":
    "如图4.22所示，考试实体反映了现有系统的在线考试配置逻辑，图中给出了课程编号、章节编号、考试名称、考试说明、考试时长、总分、及格分、开始时间、结束时间和考试状态等属性，用于描述一次考试活动的规则与时间范围。",

    "如图4.23所示，课程结课与学分记录实体用于沉淀结课判定结果。它与课程和选课记录保持关联，通过发放状态、发放时间和规则快照等字段记录学生课程达标后的学分授予结果。":
    "如图4.23所示，题目实体用于描述考试中的具体试题信息，图中包含考试编号、课程编号、题型、题目内容、选项 A/B/C/D、答案和题目分值等属性，用于支撑试卷组装、答题判分和题目管理等业务处理。",

    "如图4.24所示，智能问答模块实体由 AI 会话表和 AI 消息表构成，用于保存用户在不同业务场景下的会话标题、上下文绑定关系、多轮消息内容和工具调用痕迹，是系统 AI 能力落库的核心支撑。":
    "如图4.24所示，AI 会话实体用于保存用户在智能辅学场景中的会话信息，图中包含用户编号、用户表、角色类型、会话标题、业务场景、课程编号、章节编号、资源编号、消息数和状态等属性，用于描述会话归属关系及其上下文绑定信息。",
}


def qn(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def paragraph_text(paragraph: ET.Element) -> str:
    texts = []
    for node in paragraph.iter(qn("t")):
        texts.append(node.text or "")
    return "".join(texts)


def replace_paragraph_text(paragraph: ET.Element, new_text: str) -> None:
    template_run = paragraph.find(qn("r"))
    template_rpr = template_run.find(qn("rPr")) if template_run is not None else None
    ppr = paragraph.find(qn("pPr"))
    for child in list(paragraph):
        if child is not ppr:
            paragraph.remove(child)
    lines = new_text.splitlines() or [""]
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


def clean_work_dir() -> None:
    if not WORK_DIR.exists():
        return
    for path in sorted(WORK_DIR.rglob("*"), reverse=True):
        if path.is_file():
            path.unlink()
        else:
            path.rmdir()
    WORK_DIR.rmdir()


def main() -> None:
    clean_work_dir()
    WORK_DIR.mkdir()
    with zipfile.ZipFile(DOCX_PATH, "r") as zf:
        zf.extractall(WORK_DIR)

    document_xml = WORK_DIR / "word" / "document.xml"
    tree = ET.parse(document_xml)
    root = tree.getroot()
    changed = 0
    for paragraph in root.iter(qn("p")):
        text = paragraph_text(paragraph)
        if text in REPLACEMENTS:
            replace_paragraph_text(paragraph, REPLACEMENTS[text])
            changed += 1
    if changed != len(REPLACEMENTS):
        missing = len(REPLACEMENTS) - changed
        raise RuntimeError(f"Only replaced {changed} paragraphs, missing {missing}")
    tree.write(document_xml, encoding="UTF-8", xml_declaration=True)

    temp_docx = BASE_DIR / "现有系统数据库的逻辑设计_修改后.docx"
    if temp_docx.exists():
        temp_docx.unlink()
    with zipfile.ZipFile(temp_docx, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(WORK_DIR.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(WORK_DIR))

    DOCX_PATH.unlink()
    temp_docx.replace(DOCX_PATH)


if __name__ == "__main__":
    main()
