from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "辅助修改论文" / "第四章 数据库的逻辑设计" / "代码和图"
DOT_EXE = Path(r"D:\develop_software\Graphviz\bin\dot.exe")


def graph_header(title: str, *, rankdir: str = "TB", size: str = "8,8!") -> str:
    return (
        "digraph G {\n"
        f'  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="{title}", '
        f'fontname="Microsoft YaHei", fontsize=22, rankdir="{rankdir}", splines=false, '
        f'nodesep=0.45, ranksep=0.6, pad=0.18, margin=0.12, size="{size}"];\n'
        '  node [fontname="Microsoft YaHei", fontsize=10, color="#333333", penwidth=1.35];\n'
        '  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7, dir=none];\n\n'
    )


def entity(name: str, label: str) -> str:
    return f'  {name} [label="{label}", shape=box, style="rounded,filled", fillcolor="#ffffff"];\n'


def relation(name: str, label: str) -> str:
    return f'  {name} [label="{label}", shape=diamond, style="filled", fillcolor="#ffffff"];\n'


def attr(name: str, label: str) -> str:
    return f'  {name} [label="{label}", shape=ellipse, style="filled", fillcolor="#ffffff"];\n'


def connect(center: str, *others: str) -> str:
    return "".join(f"  {center} -> {node};\n" for node in others)


def single_entity_diagram(title: str, entity_name: str, entity_label: str, attrs: list[str]) -> str:
    lines = [graph_header(title, size="8,5!")]
    lines.append(entity(entity_name, entity_label))
    for idx, text in enumerate(attrs, start=1):
        aname = f"a{idx}"
        lines.append(attr(aname, text))
        lines.append(f"  {entity_name} -> {aname};\n")
    lines.append("}\n")
    return "".join(lines)


def overall_diagram() -> str:
    lines = [graph_header("系统总体E-R图", size="10,8!")]
    lines.extend(
        [
            entity("admin", "管理员"),
            entity("teacher", "教师"),
            entity("student", "学生"),
            entity("course", "课程"),
            entity("chapter", "章节"),
            entity("resource", "资源"),
            entity("homework", "作业"),
            entity("question", "题目"),
            entity("exam", "考试"),
            entity("record", "考试记录"),
            entity("credit", "学分记录"),
            entity("ai", "AI会话"),
            relation("r1", "审核"),
            relation("r2", "创建"),
            relation("r3", "包含"),
            relation("r4", "选课"),
            relation("r5", "学习"),
            relation("r6", "发布"),
            relation("r7", "提交"),
            relation("r8", "生成"),
            relation("r9", "参加"),
            relation("r10", "发放"),
            relation("r11", "发起"),
            relation("r12", "关联"),
            '  admin -> r1; r1 -> course;\n',
            '  teacher -> r2; r2 -> course;\n',
            '  course -> r3; r3 -> chapter;\n',
            '  chapter -> r3; r3 -> resource;\n',
            '  student -> r4; r4 -> course;\n',
            '  student -> r5; r5 -> resource;\n',
            '  teacher -> r6; r6 -> homework;\n',
            '  student -> r7; r7 -> homework;\n',
            '  exam -> r8; r8 -> question;\n',
            '  student -> r9; r9 -> exam;\n',
            '  exam -> r9; r9 -> record;\n',
            '  course -> r10; r10 -> credit;\n',
            '  student -> r10; r10 -> credit;\n',
            '  student -> r11; r11 -> ai;\n',
            '  teacher -> r11; r11 -> ai;\n',
            '  ai -> r12; r12 -> course;\n',
            '  ai -> r12; r12 -> chapter;\n',
            '  homework -> r12; r12 -> question;\n',
            "  { rank=same; admin; teacher; student; }\n",
            "  { rank=same; course; ai; }\n",
            "  { rank=same; chapter; resource; homework; exam; credit; }\n",
            "  { rank=same; question; record; }\n",
        ]
    )
    lines.append("}\n")
    return "".join(lines)


def make_diagrams() -> dict[str, str]:
    return {
        "系统总体E-R图.dot": overall_diagram(),
        "管理员实体E-R图.dot": single_entity_diagram(
            "管理员实体E-R图",
            "admin",
            "管理员",
            ["编号", "用户名", "密码", "角色", "创建时间"],
        ),
        "教师实体E-R图.dot": single_entity_diagram(
            "教师实体E-R图",
            "teacher",
            "教师",
            ["编号", "用户名", "密码", "姓名", "头像", "身份证号", "电话号码", "电子邮箱", "性别"],
        ),
        "学生实体E-R图.dot": single_entity_diagram(
            "学生实体E-R图",
            "student",
            "学生",
            ["编号", "用户名", "密码", "姓名", "头像", "身份证号", "电话号码", "电子邮箱", "班级", "性别"],
        ),
        "课程实体E-R图.dot": single_entity_diagram(
            "课程实体E-R图",
            "course",
            "课程",
            ["编号", "课程名称", "课程封面", "课程类型", "课程时长", "开始时间", "结束时间", "课程学分", "审核状态", "课程详情"],
        ),
        "作业实体E-R图.dot": single_entity_diagram(
            "作业实体E-R图",
            "homework",
            "作业",
            ["编号", "作业名称", "课程编号", "章节编号", "开始时间", "结束时间", "总分", "发布状态", "题目集合", "作业详情"],
        ),
        "题目实体E-R图.dot": single_entity_diagram(
            "题目实体E-R图",
            "question",
            "题目",
            ["编号", "考试编号", "课程编号", "题型", "题目内容", "选项A", "选项B", "选项C", "选项D", "答案", "题目分值"],
        ),
        "考试实体E-R图.dot": single_entity_diagram(
            "考试实体E-R图",
            "exam",
            "考试",
            ["编号", "课程编号", "章节编号", "考试名称", "考试说明", "考试时长", "总分", "及格分", "开始时间", "结束时间", "考试状态"],
        ),
        "AI会话实体E-R图.dot": single_entity_diagram(
            "AI会话实体E-R图",
            "ai",
            "AI会话",
            ["编号", "用户编号", "用户表", "角色类型", "会话标题", "业务场景", "课程编号", "章节编号", "资源编号", "消息数", "状态"],
        ),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    diagrams = make_diagrams()
    for name, content in diagrams.items():
        dot_path = OUT_DIR / name
        svg_path = OUT_DIR / name.replace(".dot", ".svg")
        dot_path.write_text(content, encoding="utf-8")
        subprocess.run([str(DOT_EXE), "-Tsvg", str(dot_path), "-o", str(svg_path)], check=True)
    print(OUT_DIR)


if __name__ == "__main__":
    main()
