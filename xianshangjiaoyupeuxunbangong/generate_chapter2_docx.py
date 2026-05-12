import argparse
import copy
import os
import shutil
import tempfile
import zipfile
import xml.etree.ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
DCTERMS_NS = "http://purl.org/dc/terms/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)
ET.register_namespace("cp", CP_NS)
ET.register_namespace("dc", DC_NS)
ET.register_namespace("dcterms", DCTERMS_NS)
ET.register_namespace("xsi", XSI_NS)


def qn(ns, tag):
    return f"{{{ns}}}{tag}"


def text_el(text):
    el = ET.Element(qn(W_NS, "t"))
    el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    el.text = text
    return el


def run_el(text, bold=False):
    r = ET.Element(qn(W_NS, "r"))
    if bold:
        rPr = ET.SubElement(r, qn(W_NS, "rPr"))
        ET.SubElement(rPr, qn(W_NS, "b"))
    r.append(text_el(text))
    return r


def make_paragraph(text, style, align="both", before=0, after=120, line=360, first_line=420, bold=False):
    p = ET.Element(qn(W_NS, "p"))
    pPr = ET.SubElement(p, qn(W_NS, "pPr"))
    ET.SubElement(pPr, qn(W_NS, "pStyle"), {qn(W_NS, "val"): style})
    ET.SubElement(pPr, qn(W_NS, "jc"), {qn(W_NS, "val"): align})
    ET.SubElement(
        pPr,
        qn(W_NS, "spacing"),
        {
            qn(W_NS, "before"): str(before),
            qn(W_NS, "after"): str(after),
            qn(W_NS, "line"): str(line),
            qn(W_NS, "lineRule"): "auto",
        },
    )
    ET.SubElement(pPr, qn(W_NS, "ind"), {qn(W_NS, "firstLine"): str(first_line)})
    p.append(run_el(text, bold=bold))
    return p


def make_page_number_footer():
    root = ET.Element(
        qn(W_NS, "ftr"),
        {
            "xmlns:w": W_NS,
            "xmlns:r": R_NS,
        },
    )
    p = ET.SubElement(root, qn(W_NS, "p"))
    pPr = ET.SubElement(p, qn(W_NS, "pPr"))
    ET.SubElement(pPr, qn(W_NS, "jc"), {qn(W_NS, "val"): "center"})
    ET.SubElement(pPr, qn(W_NS, "spacing"), {qn(W_NS, "before"): "0", qn(W_NS, "after"): "0", qn(W_NS, "line"): "240", qn(W_NS, "lineRule"): "auto"})

    def make_field_run(attrs=None, text=None):
        r = ET.Element(qn(W_NS, "r"))
        if attrs:
            fld = ET.SubElement(r, qn(W_NS, "fldChar"), attrs)
        if text is not None:
            ET.SubElement(r, qn(W_NS, "instrText"), {"{http://www.w3.org/XML/1998/namespace}space": "preserve"}).text = text
        return r

    p.append(make_field_run({qn(W_NS, "fldCharType"): "begin"}))
    p.append(make_field_run(text=" PAGE "))
    p.append(make_field_run({qn(W_NS, "fldCharType"): "separate"}))
    r = ET.SubElement(p, qn(W_NS, "r"))
    rPr = ET.SubElement(r, qn(W_NS, "rPr"))
    ET.SubElement(rPr, qn(W_NS, "sz"), {qn(W_NS, "val"): "24"})
    ET.SubElement(rPr, qn(W_NS, "szCs"), {qn(W_NS, "val"): "24"})
    ET.SubElement(rPr, qn(W_NS, "rFonts"), {qn(W_NS, "ascii"): "SimSun", qn(W_NS, "hAnsi"): "SimSun", qn(W_NS, "eastAsia"): "SimSun", qn(W_NS, "cs"): "SimSun"})
    ET.SubElement(r, qn(W_NS, "t")).text = "1"
    p.append(make_field_run({qn(W_NS, "fldCharType"): "end"}))
    return root


def set_core_text(root, tag_local, value):
    for child in root:
        if child.tag == qn(DC_NS, tag_local) or child.tag == qn(CP_NS, tag_local):
            child.text = value
            return True
    return False


def update_core_props(xml_bytes, title_text):
    root = ET.fromstring(xml_bytes)
    set_core_text(root, "title", title_text)
    set_core_text(root, "subject", title_text)
    set_core_text(root, "description", title_text)
    set_core_text(root, "keywords", "相关理论,技术介绍,Spring Boot,Vue,MySQL")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def update_content_types(xml_bytes):
    root = ET.fromstring(xml_bytes)
    footer_part = "/word/footer1.xml"
    footer_ct = "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"
    found = False
    for child in root.findall(qn(CT_NS, "Override")):
        if child.attrib.get("PartName") == footer_part:
            found = True
            break
    if not found:
        ET.SubElement(root, qn(CT_NS, "Override"), {"PartName": footer_part, "ContentType": footer_ct})
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def update_rels(xml_bytes):
    root = ET.fromstring(xml_bytes)
    rels = root.findall(qn(REL_NS, "Relationship"))
    max_id = 0
    for rel in rels:
        rid = rel.attrib.get("Id", "")
        if rid.startswith("rId"):
            try:
                max_id = max(max_id, int(rid[3:]))
            except ValueError:
                pass
    new_id = f"rId{max_id + 1}"
    footer_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
    ET.SubElement(
        root,
        qn(REL_NS, "Relationship"),
        {"Id": new_id, "Type": footer_type, "Target": "footer1.xml"},
    )
    return ET.tostring(root, encoding="utf-8", xml_declaration=True), new_id


def build_body(section_props):
    body = ET.Element(qn(W_NS, "body"))

    paragraphs = [
        ("Title", "2 相关理论和技术介绍", "center", 260, 220, 360, 0, False),
        ("Normal", "本章结合当前系统的后端源码、前端重写工程以及 docs 目录下的专项说明，对现有系统所采用的关键理论和技术进行说明。相关内容并不追求理论上的全面展开，而是围绕本系统实际使用到的架构模式、后端框架、前端框架、数据库和支撑工具进行归纳，为后续功能设计和实现分析提供基础。", "both", 0, 120, 360, 420, False),
        ("Normal", "从当前仓库的实现方式看，系统已经形成了较完整的教学业务闭环，课程、章节、资源、学习进度、作业、考试、公告以及智能问答都已经落到具体的控制器、实体类和数据库表中。因此，本章的技术介绍既要说明这些技术的理论背景，也要说明它们如何服务于当前系统的开发与运行。", "both", 0, 120, 360, 420, False),
        ("Heading1", "2.1 系统开发架构", "left", 220, 120, 320, 0, False),
        ("Normal", "当前系统采用典型的 B/S 架构，并在此基础上引入前后端分离思想。浏览器作为统一入口，负责页面展示和交互逻辑；服务器端负责业务处理、权限控制、数据持久化和文件管理。这样的组织方式适合在线教育培训平台这类多角色、多终端访问的系统，也便于后续在不改变核心业务的前提下持续扩展功能。", "both", 0, 120, 360, 420, False),
        ("Normal", "与传统桌面系统相比，B/S 架构减少了客户端部署成本，用户只要通过浏览器即可访问系统。对于本系统而言，学生端、教师端和管理员端虽然面向不同角色，但都可以通过统一的 Web 入口进入，后台也可以围绕相同的业务模型进行扩展和维护，这种方式在教学类平台中具有较高的通用性。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.1.1 B/S 架构", "left", 160, 100, 300, 0, False),
        ("Normal", "B/S 架构是当前 Web 应用最常见的部署模式之一，其核心特征是将主要业务逻辑放置在服务器端，客户端只承担界面渲染和交互请求的职责。这样做的好处在于系统维护更加集中，数据统一管理，版本升级也更加方便。对于教学培训系统这种需要经常调整课程、题库和公告内容的应用场景，B/S 架构能够明显降低维护复杂度。", "both", 0, 120, 360, 420, False),
        ("Normal", "本系统中，课程浏览、章节学习、视频播放、作业提交、考试答题和 AI 问答等操作，都可以通过浏览器向服务器发起请求，再由后端完成权限判断和数据处理后返回结果。用户不需要安装额外客户端，教学活动也不受单一终端限制，因此系统更容易在实际教学环境中推广使用。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.1.2 前后端分离", "left", 160, 100, 300, 0, False),
        ("Normal", "前后端分离强调界面层与业务层的独立开发和独立部署。前端只负责页面、路由、状态和交互，后端只负责接口、权限、数据库和业务规则，两者通过 HTTP 接口进行数据交换。这样一来，前端可以更专注于用户体验，后端可以更专注于业务稳定性，二者的修改边界也更加清晰。", "both", 0, 120, 360, 420, False),
        ("Normal", "当前系统在实现上已经体现出明显的分离特征：前端工程位于 new-frontend 目录下，学生端和管理端分别对应独立项目；后端则继续沿用 Spring Boot 单体服务，统一提供 JSON 接口。前端使用 Axios 发起请求，后端通过拦截器和鉴权组件完成身份识别，这种模式既保留了原系统的业务积累，也方便后续逐步迭代页面和交互体验。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.1.3 RESTful API", "left", 160, 100, 300, 0, False),
        ("Normal", "RESTful API 是一种围绕资源设计接口的风格，通常利用 GET、POST、PUT、DELETE 等 HTTP 方法来表达不同的数据操作。与早期以动作命名的接口相比，RESTful 风格更强调语义统一和资源清晰，接口的可读性和可维护性都更强。对于课程、章节、资源、考试和公告等业务对象，采用这一风格能够让前端调用和接口管理都更直观。", "both", 0, 120, 360, 420, False),
        ("Normal", "本系统的大量页面都需要对列表、详情、保存、删除和审核等动作进行交互，RESTful API 正好可以把这些操作映射到统一的接口规范中。接口通常返回 JSON 数据，前端组件再根据返回结果完成页面刷新、表单提示和状态切换。这样的设计既能降低前后端沟通成本，也有利于后续对接口进行统一封装和权限控制。", "both", 0, 120, 360, 420, False),
        ("Heading1", "2.2 后端核心技术", "left", 220, 120, 320, 0, False),
        ("Normal", "当前系统的后端以 Spring Boot 为基础，结合 MyBatis-Plus、Shiro、MySQL 以及若干通用工具包完成业务实现。后端既承担课程、作业、考试、成绩、公告和字典等核心业务，也承担文件上传、导出、AI 会话记录保存等支撑性工作，因此其技术选型需要兼顾开发效率、扩展性和稳定性。", "both", 0, 120, 360, 420, False),
        ("Normal", "从工程结构来看，系统的控制器、服务层、数据访问层和实体层划分较为清晰，后端代码围绕统一的业务对象展开。这样的分层方式让接口职责更加明确，也让新增功能能够沿着“控制器 - 服务 - 数据层”的路径逐步落地，减少了功能堆叠带来的维护压力。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.2.1 Spring Boot", "left", 160, 100, 300, 0, False),
        ("Normal", "Spring Boot 是当前系统后端的基础框架，它通过自动配置、约定优于配置和独立运行的应用入口，大幅降低了传统 Spring 项目的配置复杂度。项目只需引入相应的 starter 依赖，即可快速完成 Web、JDBC、测试等基础能力的装配，从而把更多精力放在业务实现上。", "both", 0, 120, 360, 420, False),
        ("Normal", "在本系统中，Spring Boot 负责承载控制器、过滤器、拦截器、服务实现类和配置类等核心组件。课程管理、章节管理、考试管理、作业管理以及 AI 会话模块等功能，最终都通过统一的 Spring Boot 容器进行组织和调度。这样的结构便于后续引入新的业务模块，也方便在本地开发环境和部署环境之间保持一致。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.2.2 MyBatis-Plus", "left", 160, 100, 300, 0, False),
        ("Normal", "MyBatis-Plus 是基于 MyBatis 的增强工具，强调在保持 SQL 可控性的同时提升单表 CRUD 和分页查询的开发效率。它通过实体映射、条件构造器、服务基类和分页插件等能力，让开发者能够在较少样板代码的情况下完成常见持久化操作，这一点对于业务表较多的教学平台尤为重要。", "both", 0, 120, 360, 420, False),
        ("Normal", "当前系统中，课程、章节、课程资源、作业提交、考试记录、学习进度、字典项和 AI 会话消息等数据都可以通过 MyBatis-Plus 进行映射和处理。对于列表查询、条件筛选和批量操作，MyBatis-Plus 能够显著减少重复性代码；对于复杂查询，系统仍然可以保留手写 SQL 的灵活性，从而兼顾开发效率与表达能力。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.2.3 Shiro 与鉴权机制", "left", 160, 100, 300, 0, False),
        ("Normal", "Shiro 是本系统用于身份认证和权限控制的核心组件之一。它能够把登录、角色、权限和会话管理集中到统一的安全框架中处理，开发者只需围绕业务接口配置相应的认证和授权规则即可。相比把权限判断散落在各处代码中的做法，Shiro 更利于系统形成稳定、可复用的安全策略。", "both", 0, 120, 360, 420, False),
        ("Normal", "在当前实现中，用户登录后会拿到 token，后端则通过拦截器和权限注解完成身份校验，并根据管理员、教师和学生等不同角色过滤接口访问范围。这样的设计使前端菜单和后端接口能够形成双层控制，既避免了越权访问，也让不同角色的页面入口和业务边界保持清晰。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.2.4 MySQL 数据库", "left", 160, 100, 300, 0, False),
        ("Normal", "MySQL 是当前系统的主要数据存储方案，用于保存课程、章节、资源、考试、作业、公告、字典、用户以及 AI 对话记录等业务数据。作为关系型数据库，MySQL 在事务一致性、查询性能和数据完整性方面具有较强优势，适合教育管理类系统中结构化数据较多、关联关系较明显的场景。", "both", 0, 120, 360, 420, False),
        ("Normal", "当前系统的数据表设计遵循“以业务实体为中心”的原则，核心表之间的关联关系比较清晰。例如课程与章节、课程与资源、考试与题目、作业与提交记录、会话与消息之间都存在直接或间接关联，这样的结构有利于支撑后续统计、追踪和审核等功能。数据库层的稳定性直接决定了整个平台的数据可靠性，因此 MySQL 依然是系统最重要的基础组件之一。", "both", 0, 120, 360, 420, False),
        ("Heading1", "2.3 前端核心技术", "left", 220, 120, 320, 0, False),
        ("Normal", "前端部分采用 Vue 3 生态完成重写，并根据学生端和管理端的不同使用场景分别组织项目结构。前端不仅负责界面展示，还承担路由导航、状态管理、请求调度、表单交互和局部缓存等职责，因此其技术栈需要兼顾响应式开发效率和较好的工程化能力。", "both", 0, 120, 360, 420, False),
        ("Normal", "当前系统的前端已经不再是简单的静态页面集合，而是围绕课程学习、课程管理、考试作答和 AI 问答等多条业务链路建立起来的组件化应用。学生端更注重交互流畅度和移动端适配，管理端更注重表格、表单和批量操作效率，这也决定了前端技术选型必须足够灵活。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.3.1 Vue 3", "left", 160, 100, 300, 0, False),
        ("Normal", "Vue 3 是当前系统前端页面构建的主要框架，它以组件化和响应式数据绑定为核心，能够把复杂页面拆分为多个可复用模块。相比早期的手工 DOM 操作方式，Vue 3 让页面状态变化可以更自然地映射到视图更新，从而提升了开发效率和代码可维护性。", "both", 0, 120, 360, 420, False),
        ("Normal", "在本系统中，Vue 3 主要用于学生端和管理端页面组织、路由切换、组件复用和局部状态更新。课程列表、详情页、学习进度、作业提交、考试界面和公告列表等页面，都可以通过组件化方式复用公共布局与交互逻辑。这样的实现方式既降低了重复开发成本，也让界面迭代更容易控制影响范围。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.3.2 Vite、TypeScript、Pinia 与 Vue Router", "left", 160, 100, 300, 0, False),
        ("Normal", "Vite 为前端提供了更轻量的开发服务器和更快的构建体验，适合当前这种需要频繁调整页面、接口和样式的项目。TypeScript 则在语法层面为组件、接口和业务对象增加类型约束，能够提前发现参数结构不一致等问题。Pinia 负责前端状态管理，Vue Router 负责页面路由组织，二者共同构成了前端工程化开发的基本骨架。", "both", 0, 120, 360, 420, False),
        ("Normal", "对于当前系统而言，路由层可以将首页、课程页、学习页、管理页和 AI 问答页清晰地划分开来，状态层则负责保存登录信息、用户信息、选课状态和局部页面缓存。Axios 通过统一封装后与后端接口交互，使 token 传递、错误处理和结果解析更加集中。这样一来，前端既保留了页面开发的灵活性，也维持了较好的代码组织能力。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.3.3 Element Plus", "left", 160, 100, 300, 0, False),
        ("Normal", "Element Plus 是管理端中使用较多的组件库，它提供了表格、表单、弹窗、分页、菜单和消息提示等常用组件，能够显著提升后台页面的开发效率。对于课程管理、字典管理、公告管理、题库管理和考试管理这类典型后台页面来说，Element Plus 提供的组件足以覆盖大部分常见交互场景。", "both", 0, 120, 360, 420, False),
        ("Normal", "在本系统中，管理端页面大量依赖表格查询、条件筛选和表单编辑，因此组件库的稳定性与可用性很重要。Element Plus 不仅能够帮助开发者快速拼装页面，还能保持较为统一的视觉风格和交互反馈。结合 Vue 3 的响应式机制后，后台页面可以较快完成列表管理、审核确认和信息维护等操作。", "both", 0, 120, 360, 420, False),
        ("Heading1", "2.4 辅助支撑技术", "left", 220, 120, 320, 0, False),
        ("Normal", "除主干框架外，当前系统还使用了 JSON 处理、文件工具、办公文档处理和 AI 接口 SDK 等辅助技术。这些技术虽然不直接决定系统主业务流程，但在接口交换、附件上传、数据导出和智能问答等场景中起到了重要支撑作用。", "both", 0, 120, 360, 420, False),
        ("Normal", "从实际开发角度看，教学平台中的很多功能都具有明显的“业务主线 + 辅助能力”特征。主线负责完成学习和管理流程，辅助能力则保证数据格式统一、文件操作稳定和扩展接口可用，因此它们在系统整体架构中同样不可忽视。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.4.1 JSON 与 Fastjson", "left", 160, 100, 300, 0, False),
        ("Normal", "JSON 是前后端数据交换最常见的表达格式之一，结构清晰、可读性强、跨语言兼容性好，因此特别适合 Web 系统接口调用。当前系统中的列表查询、表单提交和权限信息返回，基本都以 JSON 作为传输格式。Fastjson 则承担了对象与 JSON 之间的序列化和反序列化工作，便于后端快速构建统一响应。", "both", 0, 120, 360, 420, False),
        ("Normal", "当接口返回的数据结构较复杂时，JSON 格式仍然便于前端组件直接解析和渲染。与 XML 等格式相比，JSON 在前端生态中拥有更自然的使用方式，因此本系统在接口层保持统一的 JSON 风格，能够减少前后端之间的数据转换负担。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.4.2 Hutool、POI 与文件处理", "left", 160, 100, 300, 0, False),
        ("Normal", "Hutool 是常用的 Java 工具库，能够在日期处理、字符串处理、集合操作和常用转换等方面提供简洁接口。对于业务开发来说，这类工具可以减少重复性代码，并提高代码的可读性。当前系统在一些通用功能中引入了 Hutool，以便更方便地完成常见的数据加工和格式化任务。", "both", 0, 120, 360, 420, False),
        ("Normal", "POI 主要用于处理办公文档和表格数据，适合在课程资料导出、成绩汇总、考试记录整理等场景中使用。教育培训平台经常会遇到数据导出和文档生成需求，因此引入 POI 可以让系统在保持在线业务能力的同时，继续支持传统办公文档的交互方式，这也是教学管理系统常见的扩展能力之一。", "both", 0, 120, 360, 420, False),
        ("Heading2", "2.4.3 智能问答接口支持", "left", 160, 100, 300, 0, False),
        ("Normal", "当前系统已经包含 AI 问答相关模块，因此还引入了与智能服务交互相关的支持组件。相关能力主要体现在会话记录保存、消息转发、模型调用和结果回写等环节。这样做的好处是，智能问答不再只是一次性的页面展示，而是可以作为持续对话功能融入课程学习和平台运营流程中。", "both", 0, 120, 360, 420, False),
        ("Normal", "从系统演进角度看，智能问答模块与课程、公告、题库等业务数据共享同一套账号体系和数据库基础，后续如果需要调整模型来源或扩展知识范围，只需要在服务层和配置层做局部调整即可。这样的设计体现出当前系统较强的可扩展性，也为后续进一步完善智能教学能力留下了空间。", "both", 0, 120, 360, 420, False),
        ("Heading1", "2.5 本章小结", "left", 220, 120, 320, 0, False),
        ("Normal", "本章围绕当前系统实际采用的主要技术进行了说明，包括 B/S 架构、前后端分离、RESTful API、Spring Boot、MyBatis-Plus、Shiro、MySQL、Vue 3、Vite、Pinia、Vue Router、Element Plus 以及若干辅助工具。通过对这些技术的梳理，可以看出当前系统已经形成了较完整的 Web 应用技术基础。", "both", 0, 120, 360, 420, False),
        ("Normal", "这些技术并不是孤立存在的，而是分别承担架构承载、业务实现、权限控制、数据持久化、界面组织和辅助扩展等不同职责。正是由于各层技术能够相互配合，系统才能在保持原有业务基础的同时继续演进。下一章将结合具体需求，对系统的功能设计和实现逻辑进行进一步分析。", "both", 0, 120, 360, 420, False),
    ]

    for style, text, align, before, after, line, first_line, bold in paragraphs:
        body.append(
            make_paragraph(
                text,
                style,
                align=align,
                before=before,
                after=after,
                line=line,
                first_line=first_line,
                bold=bold,
            )
        )

    body.append(copy.deepcopy(section_props))
    return body


def replace_document(template_path, output_path, title_text):
    with tempfile.TemporaryDirectory() as tmpdir:
        extract_dir = os.path.join(tmpdir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(template_path, "r") as zin:
            zin.extractall(extract_dir)

        document_path = os.path.join(extract_dir, "word", "document.xml")
        rels_path = os.path.join(extract_dir, "word", "_rels", "document.xml.rels")
        content_types_path = os.path.join(extract_dir, "[Content_Types].xml")
        core_path = os.path.join(extract_dir, "docProps", "core.xml")
        footer_path = os.path.join(extract_dir, "word", "footer1.xml")

        root = ET.parse(document_path).getroot()
        body = root.find(qn(W_NS, "body"))
        if body is None:
            raise RuntimeError("word/document.xml is missing body element")
        sect_pr = body.find(qn(W_NS, "sectPr"))
        if sect_pr is None:
            raise RuntimeError("template document does not contain sectPr")

        new_body = build_body(sect_pr)
        root.remove(body)
        root.append(new_body)
        ET.ElementTree(root).write(document_path, encoding="utf-8", xml_declaration=True)

        with open(rels_path, "rb") as f:
            rels_xml = f.read()
        rels_updated, footer_rid = update_rels(rels_xml)
        with open(rels_path, "wb") as f:
            f.write(rels_updated)

        footer_root = make_page_number_footer()
        ET.ElementTree(footer_root).write(footer_path, encoding="utf-8", xml_declaration=True)

        new_document = ET.parse(document_path).getroot()
        new_sect_pr = new_document.find(".//" + qn(W_NS, "sectPr"))
        if new_sect_pr is not None:
            footer_ref = ET.Element(qn(W_NS, "footerReference"), {qn(W_NS, "type"): "default", qn(R_NS, "id"): footer_rid})
            new_sect_pr.insert(0, footer_ref)
            ET.ElementTree(new_document).write(document_path, encoding="utf-8", xml_declaration=True)

        with open(content_types_path, "rb") as f:
            content_types_xml = f.read()
        with open(content_types_path, "wb") as f:
            f.write(update_content_types(content_types_xml))

        if os.path.exists(core_path):
            with open(core_path, "rb") as f:
                core_xml = f.read()
            with open(core_path, "wb") as f:
                f.write(update_core_props(core_xml, title_text))

        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for folder, _, files in os.walk(extract_dir):
                for name in files:
                    full = os.path.join(folder, name)
                    rel = os.path.relpath(full, extract_dir).replace(os.sep, "/")
                    zout.write(full, rel)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", default=os.environ.get("TEMPLATE_DOCX"), help="Path to the template docx")
    parser.add_argument("--output", default=os.environ.get("OUTPUT_DOCX"), help="Path to the output docx")
    parser.add_argument("--title", default="2 相关理论和技术介绍", help="Document title")
    args = parser.parse_args()

    if not args.template:
        raise SystemExit("Missing --template or TEMPLATE_DOCX")
    if not args.output:
        raise SystemExit("Missing --output or OUTPUT_DOCX")

    replace_document(args.template, args.output, args.title)


if __name__ == "__main__":
    main()
