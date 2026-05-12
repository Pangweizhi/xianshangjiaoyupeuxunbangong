from pathlib import Path
import subprocess
import textwrap


ROOT = Path(__file__).resolve().parent


def write_diagram(folder_name: str, base_name: str, dot_text: str) -> None:
    folder = ROOT / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    dot_path = folder / f"{base_name}.dot"
    png_path = folder / f"{base_name}.png"
    dot_path.write_text(textwrap.dedent(dot_text).strip() + "\n", encoding="utf-8")
    subprocess.run(
        ["dot", "-Tpng", str(dot_path), "-o", str(png_path)],
        check=True,
    )


architecture_dot = r'''
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
'''


function_dot = r'''
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
'''


student_flow_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="学生核心学习流程图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.28, ranksep=0.40, pad=0.16, margin=0.10, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=11, shape=box, style="rounded,filled", fillcolor="white", color="#444444", penwidth=1.25, margin="0.10,0.08"];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  start [label="开始", shape=ellipse, fillcolor="#f7f7f7"];
  login [label="用户登录"];
  check [label="是否存在", shape=diamond, style="filled", fillcolor="white"];
  home [label="学生系统"];
  select [label="选课 / 进入我的课程"];
  study [label="查看章节\n学习视频与资源"];
  progress [label="记录学习进度"];
  homework [label="查看并提交作业"];
  exam [label="参加考试"];
  result [label="查看成绩与学分"];
  exit [label="退出系统"];
  no [label="不存在", shape=plaintext];
  yes [label="存在", shape=plaintext];

  start -> login -> check;
  check -> home [xlabel="存在"];
  check -> login [xlabel="不存在", constraint=false];
  home -> select -> study -> progress;
  study -> homework;
  progress -> exam;
  homework -> result;
  exam -> result;
  result -> exit;
}
'''


teacher_flow_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="教师核心教学流程图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.28, ranksep=0.40, pad=0.16, margin=0.10, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=11, shape=box, style="rounded,filled", fillcolor="white", color="#444444", penwidth=1.25, margin="0.10,0.08"];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  start [label="开始", shape=ellipse, fillcolor="#f7f7f7"];
  login [label="教师登录"];
  check [label="是否存在", shape=diamond, style="filled", fillcolor="white"];
  home [label="后台教学系统"];
  course [label="创建 / 维护课程"];
  chapter [label="维护章节目录"];
  resource [label="维护课程资源"];
  homework [label="发布作业"];
  exam [label="配置考试与题库"];
  review [label="审核与发布"];
  stat [label="查看学生进度\n成绩与学分统计"];
  exit [label="退出系统"];

  start -> login -> check;
  check -> home [xlabel="存在"];
  check -> login [xlabel="不存在", constraint=false];
  home -> course -> chapter -> resource;
  resource -> homework;
  homework -> exam;
  exam -> review -> stat -> exit;
}
'''


admin_flow_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="管理员审核与维护流程图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.28, ranksep=0.40, pad=0.16, margin=0.10, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=11, shape=box, style="rounded,filled", fillcolor="white", color="#444444", penwidth=1.25, margin="0.10,0.08"];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  start [label="开始", shape=ellipse, fillcolor="#f7f7f7"];
  login [label="管理员登录"];
  check [label="是否存在", shape=diamond, style="filled", fillcolor="white"];
  home [label="后台管理系统"];
  auditCourse [label="审核课程"];
  auditChapter [label="审核章节"];
  auditResource [label="审核资源"];
  user [label="用户 / 教师管理"];
  dict [label="字典 / 配置维护"];
  notice [label="公告与新闻维护"];
  exam [label="考试 / 题库维护"];
  ai [label="AI 问题配置"];
  exit [label="退出系统"];

  start -> login -> check;
  check -> home [xlabel="存在"];
  check -> login [xlabel="不存在", constraint=false];
  home -> auditCourse -> auditChapter -> auditResource;
  auditResource -> user -> dict -> notice -> exam -> ai -> exit;
}
'''


ai_flow_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="AI题库生成流程图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.28, ranksep=0.40, pad=0.16, margin=0.10, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=11, shape=box, style="rounded,filled", fillcolor="white", color="#444444", penwidth=1.25, margin="0.10,0.08"];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  start [label="开始", shape=ellipse, fillcolor="#f7f7f7"];
  select [label="选择课程 / 章节 / 题型"];
  prompt [label="组装题目生成参数"];
  check [label="AI 配置是否启用", shape=diamond, style="filled", fillcolor="white"];
  call [label="调用 AI 服务"];
  draft [label="生成题目草稿"];
  review [label="教师确认 / 编辑"];
  save [label="保存到题库"];
  fallback [label="降级为规则草稿"];
  end [label="结束", shape=ellipse, fillcolor="#f7f7f7"];

  start -> select -> prompt -> check;
  check -> call [xlabel="启用"];
  check -> fallback [xlabel="未启用"];
  call -> draft -> review -> save -> end;
  fallback -> review;
}
'''


student_usecase_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="学生用例图", fontname="Microsoft YaHei", fontsize=22, rankdir="LR", splines=ortho, nodesep=0.25, ranksep=0.55, pad=0.15, margin=0.10, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=11, color="#444444", penwidth=1.25];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  actor [label="学生", shape=box, style="rounded,filled", fillcolor="white"];
  c1 [label="个人中心", shape=ellipse, style="filled", fillcolor="white"];
  c2 [label="选课与我的课程", shape=ellipse, style="filled", fillcolor="white"];
  c3 [label="章节学习 / 视频播放", shape=ellipse, style="filled", fillcolor="white"];
  c4 [label="学习进度查看", shape=ellipse, style="filled", fillcolor="white"];
  c5 [label="作业提交", shape=ellipse, style="filled", fillcolor="white"];
  c6 [label="参加考试", shape=ellipse, style="filled", fillcolor="white"];
  c7 [label="查看成绩与学分", shape=ellipse, style="filled", fillcolor="white"];
  c8 [label="AI 智能问答", shape=ellipse, style="filled", fillcolor="white"];

  actor -> c1;
  actor -> c2;
  actor -> c3;
  actor -> c4;
  actor -> c5;
  actor -> c6;
  actor -> c7;
  actor -> c8;
}
'''


teacher_usecase_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="教师用例图", fontname="Microsoft YaHei", fontsize=22, rankdir="LR", splines=ortho, nodesep=0.25, ranksep=0.55, pad=0.15, margin=0.10, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=11, color="#444444", penwidth=1.25];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  actor [label="教师", shape=box, style="rounded,filled", fillcolor="white"];
  c1 [label="个人中心", shape=ellipse, style="filled", fillcolor="white"];
  c2 [label="课程管理", shape=ellipse, style="filled", fillcolor="white"];
  c3 [label="章节管理", shape=ellipse, style="filled", fillcolor="white"];
  c4 [label="资源管理", shape=ellipse, style="filled", fillcolor="white"];
  c5 [label="作业管理", shape=ellipse, style="filled", fillcolor="white"];
  c6 [label="考试与题库管理", shape=ellipse, style="filled", fillcolor="white"];
  c7 [label="成绩统计", shape=ellipse, style="filled", fillcolor="white"];
  c8 [label="AI 题目生成", shape=ellipse, style="filled", fillcolor="white"];

  actor -> c1;
  actor -> c2;
  actor -> c3;
  actor -> c4;
  actor -> c5;
  actor -> c6;
  actor -> c7;
  actor -> c8;
}
'''


admin_usecase_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="管理员用例图", fontname="Microsoft YaHei", fontsize=22, rankdir="LR", splines=ortho, nodesep=0.25, ranksep=0.55, pad=0.15, margin=0.10, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=11, color="#444444", penwidth=1.25];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  actor [label="管理员", shape=box, style="rounded,filled", fillcolor="white"];
  c1 [label="个人中心", shape=ellipse, style="filled", fillcolor="white"];
  c2 [label="用户管理", shape=ellipse, style="filled", fillcolor="white"];
  c3 [label="教师管理", shape=ellipse, style="filled", fillcolor="white"];
  c4 [label="课程审核", shape=ellipse, style="filled", fillcolor="white"];
  c5 [label="字典与配置", shape=ellipse, style="filled", fillcolor="white"];
  c6 [label="公告管理", shape=ellipse, style="filled", fillcolor="white"];
  c7 [label="考试 / 题库审核", shape=ellipse, style="filled", fillcolor="white"];
  c8 [label="AI 参数配置", shape=ellipse, style="filled", fillcolor="white"];

  actor -> c1;
  actor -> c2;
  actor -> c3;
  actor -> c4;
  actor -> c5;
  actor -> c6;
  actor -> c7;
  actor -> c8;
}
'''


total_er_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="总数据库E-R图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.35, ranksep=0.50, pad=0.18, margin=0.12, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=10, color="#444444", penwidth=1.25];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  admin [label="管理员\nusers", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  teacher [label="教师\njiaoshi", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  student [label="学生\nyonghu", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  course [label="课程\nkecheng", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  chapter [label="章节\ncourse_chapter", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  resource [label="资源\ncourse_resource", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  enroll [label="选课\ncourse_enroll", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  progress [label="进度\nstudy_progress", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  credit [label="学分记录\ncourse_credit_record", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  homework [label="作业\nzuoye", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  submit [label="作业提交\nzuoye_submit", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  exam [label="考试\nexam", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  question [label="题目\nexam_question", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  record [label="考试记录\nexam_record", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  ai_session [label="AI 会话\nai_chat_session", shape=box, style="rounded,filled", fillcolor="#fff5e8"];
  ai_msg [label="AI 消息\nai_chat_message", shape=box, style="rounded,filled", fillcolor="#fff5e8"];

  d1 [label="审核", shape=diamond, style="filled", fillcolor="white"];
  d2 [label="创建", shape=diamond, style="filled", fillcolor="white"];
  d3 [label="包含", shape=diamond, style="filled", fillcolor="white"];
  d4 [label="选课", shape=diamond, style="filled", fillcolor="white"];
  d5 [label="学习", shape=diamond, style="filled", fillcolor="white"];
  d6 [label="发放", shape=diamond, style="filled", fillcolor="white"];
  d7 [label="发布", shape=diamond, style="filled", fillcolor="white"];
  d8 [label="提交", shape=diamond, style="filled", fillcolor="white"];
  d9 [label="参加", shape=diamond, style="filled", fillcolor="white"];
  d10 [label="生成", shape=diamond, style="filled", fillcolor="white"];
  d11 [label="会话", shape=diamond, style="filled", fillcolor="white"];

  admin -> d1 -> course;
  teacher -> d2 -> course;
  course -> d3 -> chapter;
  chapter -> d3 -> resource;
  student -> d4 -> enroll;
  enroll -> d5 -> progress;
  course -> d4 -> enroll;
  course -> d5 -> progress;
  course -> d6 -> credit;
  course -> d7 -> homework;
  homework -> d8 -> submit;
  course -> d9 -> exam;
  exam -> d10 -> question;
  exam -> d9 -> record;
  student -> d11 -> ai_session;
  ai_session -> d3 -> ai_msg;

  { rank=same; admin; teacher; student; }
  { rank=same; course; }
  { rank=same; chapter; resource; homework; exam; ai_session; }
  { rank=same; enroll; progress; credit; submit; question; record; ai_msg; }
}
'''


student_er_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="学生实体E-R图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.35, ranksep=0.48, pad=0.18, margin=0.12, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=10, color="#444444", penwidth=1.25];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  student [label="学生\nyonghu\nid, username, yonghu_name", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  enroll [label="选课\ncourse_enroll", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  progress [label="学习进度\nstudy_progress", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  submit [label="作业提交\nzuoye_submit", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  record [label="考试记录\nexam_record", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  credit [label="学分记录\ncourse_credit_record", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  ai [label="AI 会话\nai_chat_session", shape=box, style="rounded,filled", fillcolor="#fff5e8"];

  e1 [label="选课", shape=diamond, style="filled", fillcolor="white"];
  e2 [label="学习", shape=diamond, style="filled", fillcolor="white"];
  e3 [label="提交", shape=diamond, style="filled", fillcolor="white"];
  e4 [label="参加", shape=diamond, style="filled", fillcolor="white"];
  e5 [label="获得", shape=diamond, style="filled", fillcolor="white"];
  e6 [label="会话", shape=diamond, style="filled", fillcolor="white"];

  student -> e1 -> enroll;
  student -> e2 -> progress;
  student -> e3 -> submit;
  student -> e4 -> record;
  student -> e5 -> credit;
  student -> e6 -> ai;
}
'''


teacher_er_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="教师实体E-R图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.35, ranksep=0.48, pad=0.18, margin=0.12, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=10, color="#444444", penwidth=1.25];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  teacher [label="教师\njiaoshi\nid, username, jiaoshi_name", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  course [label="课程\nkecheng", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  chapter [label="章节\ncourse_chapter", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  resource [label="资源\ncourse_resource", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  homework [label="作业\nzuoye", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  exam [label="考试\nexam", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  notice [label="公告\nnews", shape=box, style="rounded,filled", fillcolor="#ffffff"];

  e1 [label="创建", shape=diamond, style="filled", fillcolor="white"];
  e2 [label="维护", shape=diamond, style="filled", fillcolor="white"];
  e3 [label="发布", shape=diamond, style="filled", fillcolor="white"];
  e4 [label="管理", shape=diamond, style="filled", fillcolor="white"];
  e5 [label="出题", shape=diamond, style="filled", fillcolor="white"];
  e6 [label="公告", shape=diamond, style="filled", fillcolor="white"];

  teacher -> e1 -> course;
  teacher -> e2 -> chapter;
  teacher -> e2 -> resource;
  teacher -> e3 -> homework;
  teacher -> e4 -> exam;
  teacher -> e6 -> notice;
}
'''


course_er_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="课程实体E-R图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.35, ranksep=0.48, pad=0.18, margin=0.12, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=10, color="#444444", penwidth=1.25];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  course [label="课程\nkecheng\nid, kecheng_name, course_status", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  teacher [label="教师\njiaoshi", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  chapter [label="章节\ncourse_chapter", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  resource [label="资源\ncourse_resource", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  enroll [label="选课\ncourse_enroll", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  progress [label="学习进度\nstudy_progress", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  credit [label="学分记录\ncourse_credit_record", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  homework [label="作业\nzuoye", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  exam [label="考试\nexam", shape=box, style="rounded,filled", fillcolor="#ffffff"];

  e1 [label="归属", shape=diamond, style="filled", fillcolor="white"];
  e2 [label="包含", shape=diamond, style="filled", fillcolor="white"];
  e3 [label="选课", shape=diamond, style="filled", fillcolor="white"];
  e4 [label="学习", shape=diamond, style="filled", fillcolor="white"];
  e5 [label="发放", shape=diamond, style="filled", fillcolor="white"];
  e6 [label="发布", shape=diamond, style="filled", fillcolor="white"];
  e7 [label="组织", shape=diamond, style="filled", fillcolor="white"];

  course -> e1 -> teacher;
  course -> e2 -> chapter;
  course -> e2 -> resource;
  course -> e3 -> enroll;
  course -> e4 -> progress;
  course -> e5 -> credit;
  course -> e6 -> homework;
  course -> e7 -> exam;
}
'''


homework_er_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="作业实体E-R图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.35, ranksep=0.48, pad=0.18, margin=0.12, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=10, color="#444444", penwidth=1.25];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  homework [label="作业\nzuoye\nid, zuoye_name, publish_status", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  teacher [label="教师\njiaoshi", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  course [label="课程\nkecheng", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  chapter [label="章节\ncourse_chapter", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  submit [label="作业提交\nzuoye_submit", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  student [label="学生\nyonghu", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  question [label="题目\nexam_question", shape=box, style="rounded,filled", fillcolor="#ffffff"];

  e1 [label="发布", shape=diamond, style="filled", fillcolor="white"];
  e2 [label="归属", shape=diamond, style="filled", fillcolor="white"];
  e3 [label="关联", shape=diamond, style="filled", fillcolor="white"];
  e4 [label="提交", shape=diamond, style="filled", fillcolor="white"];
  e5 [label="包含", shape=diamond, style="filled", fillcolor="white"];

  homework -> e1 -> teacher;
  homework -> e2 -> course;
  homework -> e3 -> chapter;
  homework -> e4 -> submit;
  submit -> e5 -> student;
  homework -> e5 -> question;
}
'''


exam_er_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="考试实体E-R图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.35, ranksep=0.48, pad=0.18, margin=0.12, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=10, color="#444444", penwidth=1.25];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  exam [label="考试\nexam\nid, exam_name, exam_status", shape=box, style="rounded,filled", fillcolor="#f8fbff"];
  course [label="课程\nkecheng", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  chapter [label="章节\ncourse_chapter", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  question [label="题目\nexam_question", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  record [label="考试记录\nexam_record", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  student [label="学生\nyonghu", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  teacher [label="教师\njiaoshi", shape=box, style="rounded,filled", fillcolor="#ffffff"];

  e1 [label="归属", shape=diamond, style="filled", fillcolor="white"];
  e2 [label="生成", shape=diamond, style="filled", fillcolor="white"];
  e3 [label="参加", shape=diamond, style="filled", fillcolor="white"];
  e4 [label="记录", shape=diamond, style="filled", fillcolor="white"];
  e5 [label="命题", shape=diamond, style="filled", fillcolor="white"];

  exam -> e1 -> course;
  exam -> e1 -> chapter;
  exam -> e2 -> question;
  exam -> e3 -> student;
  exam -> e4 -> record;
  exam -> e5 -> teacher;
}
'''


ai_er_dot = r'''
digraph G {
  graph [charset="UTF-8", bgcolor="white", labelloc="t", label="AI 会话实体E-R图", fontname="Microsoft YaHei", fontsize=22, rankdir="TB", splines=ortho, nodesep=0.35, ranksep=0.48, pad=0.18, margin=0.12, size="8,8!"];
  node [fontname="Microsoft YaHei", fontsize=10, color="#444444", penwidth=1.25];
  edge [fontname="Microsoft YaHei", fontsize=9, color="#333333", penwidth=1.0, arrowsize=0.7];

  session [label="AI 会话\nai_chat_session\nid, session_title, biz_scene", shape=box, style="rounded,filled", fillcolor="#fff5e8"];
  message [label="AI 消息\nai_chat_message", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  student [label="学生\nyonghu", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  teacher [label="教师\njiaoshi", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  course [label="课程\nkecheng", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  chapter [label="章节\ncourse_chapter", shape=box, style="rounded,filled", fillcolor="#ffffff"];
  resource [label="资源\ncourse_resource", shape=box, style="rounded,filled", fillcolor="#ffffff"];

  e1 [label="包含", shape=diamond, style="filled", fillcolor="white"];
  e2 [label="发起", shape=diamond, style="filled", fillcolor="white"];
  e3 [label="关联", shape=diamond, style="filled", fillcolor="white"];

  session -> e1 -> message;
  session -> e2 -> student;
  session -> e2 -> teacher;
  session -> e3 -> course;
  session -> e3 -> chapter;
  session -> e3 -> resource;
}
'''


def main() -> None:
    diagrams = [
        ("系统总体架构设计图", "系统总体架构设计图", architecture_dot),
        ("系统功能结构设计图", "系统功能结构设计图", function_dot),
        ("流程图", "学生核心学习流程图", student_flow_dot),
        ("流程图", "教师核心教学流程图", teacher_flow_dot),
        ("流程图", "管理员审核与维护流程图", admin_flow_dot),
        ("流程图", "AI题库生成流程图", ai_flow_dot),
        ("用例图", "学生用例图", student_usecase_dot),
        ("用例图", "教师用例图", teacher_usecase_dot),
        ("用例图", "管理员用例图", admin_usecase_dot),
        ("E-R图", "总数据库E-R图", total_er_dot),
        ("E-R图", "学生实体E-R图", student_er_dot),
        ("E-R图", "教师实体E-R图", teacher_er_dot),
        ("E-R图", "课程实体E-R图", course_er_dot),
        ("E-R图", "作业实体E-R图", homework_er_dot),
        ("E-R图", "考试实体E-R图", exam_er_dot),
        ("E-R图", "AI会话实体E-R图", ai_er_dot),
    ]

    for folder_name, base_name, dot_text in diagrams:
        write_diagram(folder_name, base_name, dot_text)


if __name__ == "__main__":
    main()
