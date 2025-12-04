# ddl_spider.py
import asyncio
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

import spider.spider as spider  # 这里假设你在后端是 import spider 的结构，里面有 login 和 get_current_semester_course_list


# ================= 异步内部工具函数 =================

async def _find_current_semester_ul(session):
    """
    仿照你原文件的逻辑：
    在 COURSE_BASE_URL / portal 页里找到
       <ul class="... coursefakeclass ...">
    返回 (ul, base_url)
    """
    candidate_urls = [
        spider.login.COURSE_BASE_URL,
        "https://course.pku.edu.cn/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1",
    ]

    found_ul = None
    base_url = None

    for url in candidate_urls:
        try:
            # 把阻塞的 session.get 丢到线程池里执行，避免阻塞事件循环
            resp = await asyncio.to_thread(
                session.get,
                url,
                allow_redirects=True,
                timeout=15,
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            ul = soup.find(
                "ul",
                attrs={"class": lambda v: v and "coursefakeclass" in v}
            )
            if ul:
                found_ul = ul
                base_url = resp.url
                print(f"在页面 {resp.url} 找到当前学期课程列表区块。")
                break
        except requests.exceptions.RequestException as e:
            print(f"访问 {url} 失败: {e}")
            continue

    return found_ul, base_url


async def _get_course_launcher_urls(session):
    """
    只负责从当前学期 <ul> 里拿到每一门课的入口链接（launcher_url），顺序和
    spider.get_current_semester_course_list(session) 一致（第 1 门、第 2 门…）
    """
    found_ul, base_url = await _find_current_semester_ul(session)
    if not found_ul:
        print("没有找到当前学期课程列表区块，无法构造课程入口链接。")
        return []

    course_links = []
    for a in found_ul.find_all("a", href=True):
        launcher_url = urljoin(base_url, a["href"]) if base_url else a["href"]
        course_links.append(launcher_url)

    return course_links


async def _collect_assignment_texts_for_one_course(session, launcher_url, course_name: str):
    """
    给定一门课程的入口链接 launcher_url 和课程名称 course_name：

    1. 打开课程主页
    2. 在左侧边栏找到：<span title="课程作业">课程作业</span> 对应的 <a>
    3. 进入课程作业页面
    4. 在页面里：
       - 找到 <span style="color:#000000;">软件工程第一次作业</span> 这种作业名
       - 从它附近的 <div> 里拿到类似 “第一次作业截止时间为2025年10月30日晚11:59分.” 的整段文本

    返回:
        list[dict]
    """
    items = []

    # 1. 打开课程主页（丢到线程池）
    try:
        course_resp = await asyncio.to_thread(
            session.get,
            launcher_url,
            allow_redirects=True,
            timeout=15,
        )
        course_resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"访问课程主页失败 {launcher_url}: {e}")
        return items

    course_soup = BeautifulSoup(course_resp.text, "html.parser")

    # 2. 在左侧边栏寻找 title="课程作业" 的栏目链接
    assignment_page_url = None
    for a in course_soup.find_all("a", href=True):
        span = a.find("span")
        if span and span.get("title") == "课程作业":
            assignment_page_url = urljoin(course_resp.url, a["href"])
            break

    if not assignment_page_url:
        print(f"  课程《{course_name}》没找到『课程作业』栏目，跳过本课程。")
        return items

    print(f"  课程《{course_name}》的『课程作业』页面：{assignment_page_url}")

    # 3. 打开课程作业页面（丢到线程池）
    try:
        assign_resp = await asyncio.to_thread(
            session.get,
            assignment_page_url,
            timeout=15,
        )
        assign_resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  打开课程作业页面失败 {assignment_page_url}: {e}")
        return items

    assign_soup = BeautifulSoup(assign_resp.text, "html.parser")

    # 4. 在作业页面里找：
    #    <span style="color:#000000;">软件工程第一次作业</span>
    #    再找附近的 <div>...截止时间...</div>
    spans = assign_soup.find_all("span", style=True)
    print(f"  课程《{course_name}》作业页中总共找到 {len(spans)} 个带 style 的 span。")

    for span in spans:
        style = (span.get("style") or "").replace(" ", "")
        # 只考虑你例子中的这种：style="color:#000000;"
        if "color:#000000" not in style:
            continue

        # 4.1 作业标题文本 → 名称
        title_text = span.get_text(strip=True)
        if not title_text:
            continue

        # 排除栏目标题本身
        if title_text in ["课程作业", "全部课程作业", "作业列表"]:
            continue

        # 4.2 在附近寻找一个 <div> 的整段文本（例如截止时间那行）→ 细则
        detail_text = None

        parent = span.parent
        if parent:
            # 优先从父节点下面找 div
            div = parent.find("div")
            if div:
                detail_text = div.get_text(" ", strip=True)

        # 如果父节点里找不到，再找紧接着的下一个 div
        if not detail_text:
            next_div = span.find_next("div")
            if next_div:
                detail_text = next_div.get_text(" ", strip=True)

        if not detail_text:
            detail_text = "无"

        items.append({
            "课程名称": course_name,
            "名称": title_text,
            "细则": detail_text,
        })

    return items


# ================= 核心：异步版本的总入口 =================

async def collect_all_assignment_texts_async(session):
    """
    异步版本：
      - 使用 asyncio 并发爬取每一门课程的作业信息
      - 仍然复用原有的 spider.get_current_semester_course_list(session)
        和 requests.Session，只是通过 asyncio.to_thread 丢进线程池
    """
    if session is None:
        print("传入的 Session 为 None，爬虫终止")
        return []

    # 1) 调用你现有的课程列表函数（丢到线程池执行）
    courses = await asyncio.to_thread(
        spider.get_current_semester_course_list,
        session
    )
    if not courses:
        print("当前学期课程列表为空。")
        return []

    # 2) 拿到每门课对应的入口 URL（顺序与 courses 对齐）
    launcher_urls = await _get_course_launcher_urls(session)
    if not launcher_urls:
        print("无法获取课程入口链接列表。")
        return []

    # 3) 为每门课创建一个爬取任务，并发执行
    tasks = []
    for course in courses:
        # 你现有的 get_current_semester_course_list 返回形如 {"id": 1, "name": "..."}
        idx = int(course["id"]) - 1
        if idx < 0 or idx >= len(launcher_urls):
            continue

        launcher_url = launcher_urls[idx]
        course_name = course.get("name", "")
        print(f"\n===== 课程 {course['id']}: {course_name} =====")

        task = _collect_assignment_texts_for_one_course(
            session,
            launcher_url,
            course_name=course_name,
        )
        tasks.append(task)

        # 文明一点，控制一下任务创建节奏
        await asyncio.sleep(0.05)

    # 4) 并发等待所有课程任务完成
    all_items = []
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for res in results:
        if isinstance(res, Exception):
            print("某门课程爬取任务出错：", res)
            continue
        all_items.extend(res)

    print(f"\n✅ 全部课程扫描完成，共收集到 {len(all_items)} 条作业条目。")
    print(all_items)
    return all_items


# ================= 对外暴露的同步封装 =================

def collect_all_assignment_texts(session):
    """
    保持原来的同步接口不变，内部使用 asyncio 跑异步版。
    这样你原来在别处写的：
        raw_items = collect_all_assignment_texts(session)
    不需要改动。
    """
    return asyncio.run(collect_all_assignment_texts_async(session))