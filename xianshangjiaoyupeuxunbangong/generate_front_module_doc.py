from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parent
TEMPLATE_DOCX = ROOT / "辅助修改论文" / "第三章 需求分析" / "第三章_现有系统分析.docx"
OUTPUT_DOCX = ROOT / "辅助修改论文" / "前台实现模块部分的修改" / "前台模块实现部分.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CONTENT_WIDTH = 9026


def attr(**kwargs: str | int | None) -> str:
    parts: list[str] = []
    for key, value in kwargs.items():
        if value is None:
            continue
        parts.append(f' w:{key}="{value}"')
    return "".join(parts)


def run(
    text: str,
    *,
    font: str = "SimSun",
    size: int = 24,
    bold: bool = False,
    italic: bool = False,
    color: str = "000000",
    preserve: bool = True,
) -> str:
    rpr = (
        f"<w:rPr><w:rFonts w:ascii=\"{font}\" w:hAnsi=\"{font}\" w:eastAsia=\"{font}\" w:cs=\"{font}\"/>"
        f"<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/>"
    )
    if bold:
        rpr += "<w:b/><w:bCs/>"
    if italic:
        rpr += "<w:i/><w:iCs/>"
    rpr += f"<w:color w:val=\"{color}\"/></w:rPr>"
    space = ' xml:space="preserve"' if preserve else ""
    return f"<w:r>{rpr}<w:t{space}>{escape(text)}</w:t></w:r>"


def paragraph(
    text: str = "",
    *,
    style: str | None = None,
    align: str = "both",
    first_line: int = 420,
    before: int = 0,
    after: int = 120,
    line: int = 360,
    font: str = "SimSun",
    size: int = 24,
    bold: bool = False,
    italic: bool = False,
    color: str = "000000",
    keep_next: bool = False,
    center: bool = False,
) -> str:
    ppr = "<w:pPr>"
    if style:
        ppr += f"<w:pStyle w:val=\"{style}\"/>"
    if center:
        ppr += '<w:jc w:val="center"/>'
    else:
        ppr += f'<w:jc w:val="{align}"/>'
    ppr += f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>'
    ppr += f'<w:ind w:firstLine="{first_line}"/>'
    if keep_next:
        ppr += "<w:keepNext/>"
    ppr += "</w:pPr>"
    body = run(
        text,
        font=font,
        size=size,
        bold=bold,
        italic=italic,
        color=color,
    )
    return f"<w:p>{ppr}{body}</w:p>"


def blank_paragraph(after: int = 0) -> str:
    return (
        "<w:p><w:pPr><w:jc w:val=\"both\"/>"
        f"<w:spacing w:before=\"0\" w:after=\"{after}\" w:line=\"240\" w:lineRule=\"auto\"/>"
        "<w:ind w:firstLine=\"0\"/></w:pPr></w:p>"
    )


def table(
    rows: list[list[list[str]]],
    *,
    widths: list[int],
    shading: str | None = None,
    cell_bg: str = "F7F7F7",
    valign: str = "top",
    row_height: int | None = None,
    border: str = "BFBFBF",
    font: str = "SimSun",
    size: int = 22,
) -> str:
    total_width = sum(widths)
    tblpr = [
        "<w:tblPr>",
        f"<w:tblW w:w=\"{total_width}\" w:type=\"dxa\"/>",
        "<w:tblLayout w:type=\"fixed\"/>",
        '<w:tblCellMar>'
        '<w:top w:w="80" w:type="dxa"/>'
        '<w:left w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/>'
        '<w:right w:w="120" w:type="dxa"/>'
        "</w:tblCellMar>",
        "<w:tblBorders>"
        f'<w:top w:val="single" w:sz="8" w:space="0" w:color="{border}"/>'
        f'<w:left w:val="single" w:sz="8" w:space="0" w:color="{border}"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{border}"/>'
        f'<w:right w:val="single" w:sz="8" w:space="0" w:color="{border}"/>'
        f'<w:insideH w:val="single" w:sz="8" w:space="0" w:color="{border}"/>'
        f'<w:insideV w:val="single" w:sz="8" w:space="0" w:color="{border}"/>'
        "</w:tblBorders>",
    ]
    if shading:
        tblpr.append(
            f'<w:shd w:val="clear" w:color="auto" w:fill="{shading}"/>'
        )
    tblpr.append("</w:tblPr>")
    grid = "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in widths) + "</w:tblGrid>"

    rows_xml: list[str] = []
    for row in rows:
        trpr = ""
        if row_height is not None:
            trpr = (
                "<w:trPr>"
                f'<w:trHeight w:val="{row_height}" w:hRule="atLeast"/>'
                "</w:trPr>"
            )
        cells: list[str] = []
        for cell in row:
            cell_xml = "".join(cell)
            cells.append(
                "<w:tc>"
                "<w:tcPr>"
                f'<w:tcW w:w="{widths[len(cells)]}" w:type="dxa"/>'
                f'<w:vAlign w:val="{valign}"/>'
                '<w:tcMar>'
                '<w:top w:w="80" w:type="dxa"/>'
                '<w:left w:w="120" w:type="dxa"/>'
                '<w:bottom w:w="80" w:type="dxa"/>'
                '<w:right w:w="120" w:type="dxa"/>'
                '</w:tcMar>'
                + (
                    f'<w:shd w:val="clear" w:color="auto" w:fill="{cell_bg}"/>'
                    if cell_bg
                    else ""
                )
                + "</w:tcPr>"
                + cell_xml
                + "</w:tc>"
            )
        rows_xml.append("<w:tr>" + trpr + "".join(cells) + "</w:tr>")

    return "<w:tbl>" + "".join(tblpr) + grid + "".join(rows_xml) + "</w:tbl>"


def code_block(lines: list[str]) -> str:
    paras = [
        paragraph(
            line,
            align="left",
            first_line=0,
            before=0,
            after=0,
            line=280,
            font="Courier New",
            size=20,
        )
        for line in lines
    ]
    return table(
        [[paras]],
        widths=[CONTENT_WIDTH],
        shading="F4F4F4",
        cell_bg="F4F4F4",
        valign="top",
        row_height=None,
        border="C8C8C8",
    )


def screenshot_box(caption: str, height: int = 1800) -> str:
    box_text = [
        paragraph(caption, align="center", first_line=0, before=60, after=40, line=300, font="SimHei", size=20, bold=True, center=True),
        paragraph("（此处插入截图）", align="center", first_line=0, before=0, after=0, line=300, font="SimSun", size=22, italic=True, color="666666", center=True),
    ]
    return table(
        [[box_text]],
        widths=[CONTENT_WIDTH],
        shading="FBFBFB",
        cell_bg="FBFBFB",
        valign="center",
        row_height=height,
        border="BFBFBF",
    )


def body_xml() -> str:
    parts: list[str] = []
    parts.append(paragraph("前台模块实现部分", style="Title", align="center", first_line=0, before=240, after=220, line=360, font="SimHei", size=36, bold=True, center=True))
    parts.append(paragraph("基于新前端的用户登录、公共导航、课程学习、作业考试、个人中心与智能问答功能实现说明", align="center", first_line=0, before=0, after=180, line=300, font="SimSun", size=22, color="666666", center=True))
    parts.append(paragraph(
        "前台模块采用 Vue 3、Vite、TypeScript、Pinia 与 Vue Router 构建，以 PublicLayout 作为统一页面容器，通过路由切换完成功能组织。"
        "用户完成登录后，系统按照页面顶部从左到右的顺序依次展示首页、课程、公告、论坛、我的课程、作业、考试、会议、个人中心和智能问答等入口，"
        "并在各业务页面中完成课程浏览、章节学习、进度记录、作业提交、在线考试和成绩查看等操作。",
        first_line=420,
        before=0,
        after=120,
    ))
    parts.append(paragraph(
        "本节结合当前仓库中的前台源码与 docs 目录下的实施说明，对前台模块的主要页面和关键逻辑进行说明。文中的截图位置均已预留，后续可根据实际界面补充对应图片。",
        first_line=420,
        before=0,
        after=180,
    ))

    sections = [
        {
            "title": "4.1 用户登录模块",
            "paras": [
                "系统登录页用于完成身份选择与账号鉴权。页面提供学生、教师和管理员三类身份入口，用户根据自身角色选择对应账号类型后输入账号与密码即可登录。"
                "登录成功后，系统会将 Token、角色、用户编号和表名等信息写入前台会话缓存，并自动跳转到个人中心页面，保证后续业务页面可以直接读取登录态。",
                "登录阶段同时加入了基础校验逻辑，账号或密码为空时立即给出提示，避免无效请求进入后端。前台会话对象还承担了后续路由守卫的判断依据，因此登录模块是整套前台功能的起点。",
            ],
            "figure": "图4-1 登录页面界面",
            "code": [
                "const session = ref<AuthSession | null>(readSession(STORAGE_KEY));",
                "async function login(payload: { tableName: UserTable; username: string; password: string; }) {",
                "  const { data } = await axios.post(`${DEFAULT_BASE_URL}${loginEndpointMap[payload.tableName]}`, null, { params: payload });",
                "  if (data.code !== 0) throw new Error(data.msg || \"登录失败\");",
                "  setSession({ token: data.token, role: data.role, userId: data.userId, tableName: payload.tableName, username: payload.username });",
                "}",
                "",
                "router.beforeEach(async (to) => {",
                "  const session = useSessionStore();",
                "  if (to.meta.requiresAuth && !session.isLoggedIn) {",
                "    return { name: \"login\", query: { redirect: to.fullPath } };",
                "  }",
                "});",
            ],
        },
        {
            "title": "4.2 前台总体布局",
            "paras": [
                "登录成功后，系统统一进入前台主布局页面。该页面以顶部导航作为主入口，左侧集中展示公共服务入口，右侧集中展示我的学习入口和账户操作入口，形成清晰的功能分组。"
                "这种布局方式既保留了公共浏览场景，也保留了登录后的学习场景，用户无需在多个页面之间重复寻找入口即可完成主要操作。",
                "顶部公共服务入口包含首页、课程、公告和论坛，右侧操作区包含问 AI、身份标识和退出登录按钮；我的学习入口包含我的课程、作业、考试、会议和个人中心。"
                "当前路由激活状态会在菜单中实时高亮，便于用户判断当前位置。",
            ],
            "figure": "图4-2 前台主布局界面",
            "code": [
                "const aiLink = computed(() => {",
                "  const query: Record<string, string | number> = {",
                "    bizScene: route.name === \"course-detail\" ? \"course_learning\" : \"system_nav\",",
                "    pageCode: String(route.name ?? \"public\")",
                "  };",
                "  if (route.name === \"course-detail\" && route.params.id) {",
                "    query.courseId = Number(route.params.id);",
                "  }",
                "  return { name: \"ai-chat\", query };",
                "});",
                "",
                "function handleLogout() {",
                "  session.logout();",
                "  router.push({ name: \"login\" });",
                "}",
            ],
        },
        {
            "title": "4.3 首页模块",
            "paras": [
                "首页承担前台内容聚合与快速导览的作用。页面上方展示轮播图和学习引导区，中部通过快捷入口分组展示公共服务和学习入口，下方展示课程推荐和最新公告，形成由概览到详情的浏览路径。"
                "首页不是单纯的静态展示页，而是连接课程、公告、作业、论坛等模块的统一入口，用户可以从首页直接进入后续功能页面。",
                "首页还会同步读取课程、作业、论坛、公告、会议等基础数据，并将当前可浏览课程数量、已发布作业数量和近期讨论数量以卡片形式展示，增强页面的信息密度和可读性。",
            ],
            "figure": "图4-3 首页界面",
        },
        {
            "title": "4.4 课程浏览与课程详情模块",
            "paras": [
                "课程模块由课程列表和课程详情两个层次构成。课程列表支持按课程名称、教师和课程类型进行筛选，便于学生快速定位目标课程；课程详情则展示课程封面、课程简介、学分、授课教师、开始结束时间以及适用班级等信息。"
                "进入课程详情后，页面左侧展示课程总览和全部资源，右侧按章节推进学习。视频资源可以直接进入播放页，附件资源则通过下载方式打开，课程学习链路由此被完整串联起来。",
                "学生在课程详情中点击立即选课后，系统会调用选课接口生成选课记录，同时结合我的课程接口判断是否已经选课。课程详情页还会联动学习进度接口，将已完成和未完成的资源进度回显到页面中。",
            ],
            "figure": "图4-4 课程列表与课程详情界面",
            "code": [
                "async function handleEnroll() {",
                "  if (!session.isLoggedIn) {",
                "    showUiToast(\"请先登录后再选课\", \"error\");",
                "    return;",
                "  }",
                "  const result = await createCourseEnroll({ kechengId: Number(route.params.id) });",
                "  if (result.code !== 0) throw new Error(result.msg || \"选课失败\");",
                "  enrolled.value = true;",
                "}",
                "",
                "function handleResourceAction(resource: CourseResourceItem) {",
                "  if (isVideoResource(resource)) {",
                "    router.push({ name: \"course-video\", params: { courseId: route.params.id, resourceId: resource.id } });",
                "    return;",
                "  }",
                "  window.open(downloadUrl(resource.resourceUrl), \"_blank\");",
                "}",
            ],
        },
        {
            "title": "4.5 视频学习模块",
            "paras": [
                "视频学习页面用于承载课程章节中的视频资源播放。页面采用左右分栏布局，左侧显示视频播放器，右侧显示课程信息、当前进度、章节信息和相关说明，便于学生在观看视频时同步掌握学习状态。"
                "当视频播放到一定时长后，系统会按照时间片自动保存学习进度；当视频播放结束后，系统会将该资源标记为完成状态，并在再次进入时显示学习完成提示。",
                "该页面同时支持视频地址兜底、播放失败切换、离开页面前保存进度和课程资源跳转等处理逻辑，从而保证学习进度记录尽量完整、准确。",
            ],
            "figure": "图4-5 视频学习界面",
            "code": [
                "async function handleTimeUpdate() {",
                "  const currentSeconds = Math.floor(videoRef.value?.currentTime || 0);",
                "  if (currentSeconds - lastSavedSeconds.value < 5) {",
                "    return;",
                "  }",
                "  pendingSeekSeconds.value = currentSeconds;",
                "  await ensureSaved(false);",
                "}",
                "",
                "async function handleEnded() {",
                "  pendingSeekSeconds.value = 0;",
                "  await ensureSaved(true);",
                "  overlayDismissed.value = false;",
                "}",
            ],
        },
        {
            "title": "4.6 公告模块",
            "paras": [
                "公告模块用于展示系统发布的通知信息，页面支持按标题、公告类型和发布时间顺序筛选。列表采用卡片形式呈现，公告封面、标题、摘要和发布时间均在同一视图中直观显示。"
                "用户在首页或公告页中均可快速查看公告内容，从而及时获取课程安排、系统通知和学习提醒等信息。",
                "公告模块保持了较强的可读性，长文本会在前台进行摘要截取，防止列表页因内容过长而破坏整体布局。",
            ],
            "figure": "图4-6 公告列表界面",
        },
        {
            "title": "4.7 论坛模块",
            "paras": [
                "论坛模块用于承载学生和教师之间的交流内容。页面将主题帖和回复帖统一纳入列表展示，并支持按标题、身份和帖子类型进行筛选。"
                "用户可以在列表中直接查看帖子内容摘要，也可以进入帖子详情继续浏览讨论内容，从而形成相对完整的互动链路。",
                "该模块在展示层面区分了主题帖与回复帖，并保留了发布者身份、帖子状态和发布时间等字段，方便用户快速识别帖子上下文。",
            ],
            "figure": "图4-7 论坛列表界面",
        },
        {
            "title": "4.8 我的课程模块",
            "paras": [
                "我的课程模块用于展示当前账号已经选课的课程列表，并将学习进度、课程状态、授课教师和结课时间一并展示出来。"
                "学生可以从该模块直接回到课程详情页面继续学习，也可以查看课程结算后的学分信息，避免在多个页面之间重复跳转。",
                "该页面同时读取课程学分汇总信息，将已发放和待发放的学分结果归纳到课程维度，为后续成绩查看提供统一入口。",
            ],
            "figure": "图4-8 我的课程界面",
        },
        {
            "title": "4.9 作业模块",
            "paras": [
                "作业模块按照课程维度展示待完成作业，用户可以通过标题、课程和作业类型进行检索。作业详情页则进一步展示作业说明、题目数量、总分、起止时间以及附件信息。"
                "学生点击开始作业后，系统会创建作业作答记录，并在详情页中逐题完成填答；提交作业时，系统会保存答题快照和补充说明，便于后续批改和回看。",
                "当作业处于作答中状态时，页面会允许继续编辑答案；当作业超过截止时间后，页面会根据时间判断禁止再次提交，保证作业流程与业务规则一致。",
            ],
            "figure": "图4-9 作业列表与作业详情界面",
        },
        {
            "title": "4.10 考试模块",
            "paras": [
                "考试模块采用“列表 + 详情 + 作答”的三段式结构。考试列表展示课程、教师、总分、及格分和考试状态，学生点击进入考试后，系统再加载题目并进入计时作答状态。"
                "考试页面支持开始考试、继续考试和提交试卷三类操作；考试进行中离开页面时系统会进行提示，避免学生误退出导致试卷状态丢失。",
                "提交试卷后，系统会把答题快照发送到后端进行评分，并在页面中同步显示当前成绩、考试状态和剩余作答次数等信息。",
            ],
            "figure": "图4-10 考试列表与考试详情界面",
            "code": [
                "async function startNewAttempt() {",
                "  const result = await startExam({ examId: Number(route.params.id) });",
                "  if (result.code !== 0) throw new Error(result.msg || \"开始考试失败\");",
                "  applyRecord(result.data, false);",
                "  showQuestions.value = true;",
                "}",
                "",
                "async function submitCurrentExam(byTimeout = false) {",
                "  const result = await submitExam({ id: recordId.value, answerSnapshot: JSON.stringify(answers) });",
                "  if (result.code !== 0) throw new Error(result.msg || \"提交失败\");",
                "  const latest = await loadLatestRecord();",
                "  applyRecord(latest, false);",
                "}",
            ],
        },
        {
            "title": "4.11 会议模块",
            "paras": [
                "会议模块主要用于展示开会通知和相关安排。页面支持按会议标题、会议类型和发布时间顺序浏览，用户可以直接查看会议摘要并进入详情页。"
                "该模块与公告模块保持一致的视觉风格，便于用户快速识别公共通知类信息。",
                "会议详情页进一步展示会议内容、时间安排和补充说明，为课程相关会议的查看和提醒提供统一入口。",
            ],
            "figure": "图4-11 会议列表与会议详情界面",
        },
        {
            "title": "4.12 个人中心模块",
            "paras": [
                "个人中心模块用于展示学生的基础资料和学习概览。页面左侧显示头像、账号、学号和班级信息，右侧提供姓名、手机号、邮箱和头像的编辑入口。"
                "用户在个人中心中完成头像上传后，系统会直接调用文件上传接口，并在保存时将最新资料写回学生档案，从而保证账号资料与实际信息保持一致。",
                "个人中心下方还汇总了待学课程、已学课程、待批作业、通过考试和累计学分等统计信息，帮助用户从整体上掌握学习进度。",
            ],
            "figure": "图4-12 个人中心界面",
        },
        {
            "title": "4.13 智能问答模块",
            "paras": [
                "智能问答模块作为前台的辅助功能，既可以在公共浏览场景下提供系统导航问答，也可以在课程学习场景下提供课程相关问答。"
                "系统会根据当前页面和课程上下文生成推荐问题，并将会话、消息和推荐问题统一保存，保证问答过程可以连续追溯。",
                "该模块与前台主导航共用统一入口，用户点击问 AI 后即可进入独立问答界面，从而围绕课程学习、作业、考试、成绩和系统操作等问题获取辅助信息。",
            ],
            "figure": "图4-13 智能问答界面",
            "code": [
                "const bizScene = computed(() => String(route.query.bizScene ?? \"system_nav\"));",
                "async function ensureSession() {",
                "  if (activeSessionId.value) return activeSessionId.value;",
                "  const result = await createAiSession({ bizScene: bizScene.value, courseId: courseId.value, chapterId: chapterId.value, pageCode: pageCode.value });",
                "  activeSessionId.value = result.session.id;",
                "  recommendQuestions.value = result.recommendQuestions;",
                "  return activeSessionId.value;",
                "}",
                "",
                "async function handleSend(override?: string) {",
                "  const sessionId = await ensureSession();",
                "  const result = await sendAiMessage({ sessionId, content, bizScene: bizScene.value, courseId: courseId.value, chapterId: chapterId.value, pageCode: pageCode.value });",
                "  messages.value = [...messages.value, result.userMessage, result.assistantMessage];",
                "}",
            ],
        },
    ]

    for index, section in enumerate(sections, start=1):
        parts.append(paragraph(section["title"], style="Heading1", align="left", first_line=0, before=220, after=120, line=320, font="SimHei", size=28, bold=True))
        for para in section["paras"]:
            parts.append(paragraph(para, first_line=420, before=0, after=120))
        parts.append(screenshot_box(section["figure"]))
        parts.append(blank_paragraph(after=0))
        if "code" in section:
            parts.append(paragraph("关键代码如下：", first_line=420, before=0, after=60, line=320, font="SimSun", size=22, bold=True))
            parts.append(code_block(section["code"]))
        if index != len(sections):
            parts.append(blank_paragraph(after=0))

    parts.append(paragraph(
        "本节对前台模块的主要页面、核心交互和关键代码进行了说明。前台功能已经按照登录、导航、课程学习、作业考试、个人中心和智能问答的顺序完成组织，"
        "后续只需结合实际运行截图补齐图示即可。",
        first_line=420,
        before=220,
        after=180,
    ))

    return "".join(parts)


def build_document_xml() -> str:
    with ZipFile(TEMPLATE_DOCX, "r") as zf:
        template_xml = zf.read("word/document.xml").decode("utf-8")
    start = template_xml.index("<w:body>") + len("<w:body>")
    end = template_xml.rindex("<w:sectPr>")
    sect = template_xml[end:template_xml.rindex("</w:body>")]
    body = body_xml()
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}">'
        f"<w:body>{body}{sect}</w:body>"
        "</w:document>"
    )


def build_core_xml() -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>前台模块实现部分</dc:title>
  <dc:subject>前台模块实现部分</dc:subject>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>
"""


def main() -> None:
    if not TEMPLATE_DOCX.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_DOCX}")
    OUTPUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    document_xml = build_document_xml()
    core_xml = build_core_xml()

    # Validate the generated document XML before writing the package.
    import xml.etree.ElementTree as ET

    ET.fromstring(document_xml)

    with ZipFile(TEMPLATE_DOCX, "r") as src, ZipFile(OUTPUT_DOCX, "w", ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/document.xml":
                data = document_xml.encode("utf-8")
            elif item.filename == "docProps/core.xml":
                data = core_xml.encode("utf-8")
            dst.writestr(item, data)


if __name__ == "__main__":
    main()
