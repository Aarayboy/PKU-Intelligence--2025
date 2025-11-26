import os
import re
<<<<<<< HEAD
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from spider import login
=======
import time
>>>>>>> 2ae7a216e2d50b653a54d5d99148d85f564484c9
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from spider import login


def get_filename_from_response(response, fallback_url):
    """从响应头或URL提取真实文件名"""
    cd = response.headers.get("Content-Disposition", "")
    filename = None

    if "filename=" in cd:
        import re

        match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', cd)
        if match:
            filename = match.group(1)
            filename = requests.utils.unquote(filename)  # 解码中文名

    if not filename:
        filename = os.path.basename(urlparse(fallback_url).path)

    # 如果没有扩展名，尝试根据 Content-Type 推断
    if not os.path.splitext(filename)[1]:
        content_type = response.headers.get("Content-Type", "").lower()
        if "pdf" in content_type:
            filename += ".pdf"
        elif "word" in content_type:
            filename += ".docx"
        elif "powerpoint" in content_type:
            filename += ".pptx"
        else:
            filename += ".bin"

    return filename


def ensure_unique_filename(filename: str, directory: Path) -> str:
    """
    若重名则自动加编号
    directory: 要检查重名的目标目录（Path 对象）。
    """
    base, ext = os.path.splitext(filename)
    counter = 1
    candidate = filename
    while (directory / candidate).exists():
        candidate = f"{base}_{counter}{ext}"
        counter += 1
    return candidate


def download_file(file_url, session, save_dir: str | Path | None = None):
    """
    下载单个文件到指定目录（默认 DOWNLOAD_DIR）。

    参数:
        file_url:  文件的完整 URL
        session:   已登录的 requests.Session
        save_dir:  目标保存目录，可以是 str 或 Path，不传则用全局 DOWNLOAD_DIR。

    返回:
        本地保存路径（str），失败则返回 None
    """
    try:
        resp = session.get(file_url, stream=True, timeout=60)
        resp.raise_for_status()
    except Exception as e:
        print(f"下载文件失败 {file_url}: {e}")
        return None

    # 处理保存目录
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    # 获取文件名并确保不重名
    filename = get_filename_from_response(resp, file_url)
    filename = ensure_unique_filename(filename, save_dir)
    save_path = save_dir / filename

    try:
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        print(f"写文件失败 {save_path}: {e}")
        return None

    print(f"文件下载成功: {save_path}")
    return str(save_path)


def _extract_pure_course_name(full_text: str) -> str:
    """
    从完整课程标题中提取“纯净课程名”。

    例如：
        "25261-00011-...: 人类的性、生育与健康(25-26学年第1学期)"
    ->  "人类的性、生育与健康"
    """
    # 1) 去掉前面的课号部分（以第一个冒号 : 为界）
    parts = full_text.split(":", 1)
    after_code = parts[1].strip() if len(parts) == 2 else full_text.strip()

    # 2) 去掉末尾的学期描述括号 "(25-26学年第1学期)" / "(25-26学年第1学期本研合上)" 等
    paren_idx = after_code.rfind("(")
    if paren_idx != -1:
        pure_name = after_code[:paren_idx].strip()
    else:
        pure_name = after_code.strip()

    return pure_name


def get_current_semester_course_list(session):
    """
    使用传入的已登录 Session，从首页“当前学期课程”区块抓取课程列表。
    参数：
        session: 已登录的 requests.Session，对应 pku_login_and_get_session 返回值
    返回：
        一个 Python 列表（可直接用于 jsonify）：
        [
            {"id": 1, "name": "人类的性、生育与健康"},
            {"id": 2, "name": "太极拳"},
            ...
        ]
    """
    if session is None:
        print("传入的 Session 为 None，无法获取课程列表")
        return []

    # 1. 访问可能包含“当前学期课程框”的页面
    candidate_urls = [
        login.COURSE_BASE_URL,
        "https://course.pku.edu.cn/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1",
    ]

    found_ul = None

    for url in candidate_urls:
        try:
            resp = session.get(url, allow_redirects=True, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # 精准找 <ul class="portletList-img courseListing coursefakeclass ">
            # 注意 class 有多个，所以用 lambda 判断包含 'coursefakeclass'
            ul = soup.find(
                "ul", attrs={"class": lambda v: v and "coursefakeclass" in v}
            )
            if ul:
                found_ul = ul
                print(f"在页面 {resp.url} 找到当前学期课程列表区块。")
                break
        except requests.exceptions.RequestException as e:
            print(f"访问 {url} 失败: {e}")
            continue

    if not found_ul:
        print("没有找到当前学期课程列表的 <ul class='... coursefakeclass ...'> 区块。")
        return []

    # 2. 解析该 <ul> 中所有 <a>，并把课程名清洗成“纯净名称”
    result = []

    for idx, a in enumerate(found_ul.find_all("a", href=True), start=1):
        full_text = a.get_text(strip=True)
        pure_name = _extract_pure_course_name(full_text)

        result.append(
            {
                "id": idx,
                "name": pure_name,
            }
        )

    print(f"当前学期课程列表共 {len(result)} 门：")
    for c in result:
        print(f"  - {c['id']}: {c['name']}")

    return result


def download_handouts_for_course(
    session,
    course_id,
    section_names=None,
    max_files=3,
    download_root: str | Path | None = None,
):
    """
    根据前端选中的课程 id（1 开始，对应“当前学期课程”列表里的第几个 <li>），
    进入该课程后，寻找左侧边栏中名称为 “课程讲义” / “课程文件” 等栏目的页面，
    下载其中所有 /bbcswebdav/... 形式的文件到 downloads 文件夹。

    参数:
        session: 已登录的 requests.Session（外部负责登录好并传进来）
        course_id: 1 开始的整数或字符串（"1"、"2"...）
        section_names: 要遍历的栏目名列表，默认 ["课程讲义"]
        max_files: 最多下载多少个文件
        download_root: 下载根目录

    返回:
        downloaded_files: List[dict]，每个元素形如：
            {
                "path": "本地保存路径",
                "name": "可见文件名（例如 2025秋季软件工程课程介绍20250909）"
            }
    """
    if session is None:
        print("传入的 Session 为 None，爬虫终止")
        return []

    # 0. course_id 可能是字符串，先转成 int
    try:
        idx = int(course_id)
    except (TypeError, ValueError):
        print(f"无效的课程 id: {course_id}")
        return []

    if section_names is None:
        section_names = ["课程讲义"]

    downloaded_files: list[dict[str, str]] = []

    # 1. 先找到“当前学期课程” <ul class="... coursefakeclass ...">
    candidate_urls = [
        login.COURSE_BASE_URL,
        "https://course.pku.edu.cn/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1",
    ]

    found_ul = None
    base_url = None

    for url in candidate_urls:
        try:
            resp = session.get(url, allow_redirects=True, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            ul = soup.find(
                "ul", attrs={"class": lambda v: v and "coursefakeclass" in v}
            )
            if ul:
                found_ul = ul
                base_url = resp.url
                print(f"在页面 {resp.url} 找到当前学期课程列表区块。")
                break
        except requests.exceptions.RequestException as e:
            print(f"访问 {url} 失败: {e}")
            continue

    if not found_ul:
        print("没有找到当前学期课程列表的 <ul class='... coursefakeclass ...'> 区块。")
        return downloaded_files

    # 2. 取这个 <ul> 里所有课程 <a>，按顺序编号，从 1 开始
    course_links = [a for a in found_ul.find_all("a", href=True)]
    if not course_links:
        print("当前学期课程列表中没有任何链接。")
        return downloaded_files

    if idx < 1 or idx > len(course_links):
        print(f"课程 id 越界: {idx}, 当前学期共有 {len(course_links)} 门课")
        return downloaded_files

    target_a = course_links[idx - 1]
    full_text = target_a.get_text(strip=True)
    pure_name = _extract_pure_course_name(full_text)
    launcher_url = urljoin(base_url, target_a["href"]) if base_url else target_a["href"]

    print(f"选择第 {idx} 门课程：{pure_name}")
    print(f"课程入口链接：{launcher_url}")

    # 3. 打开这门课的主页
    try:
        course_resp = session.get(launcher_url, allow_redirects=True)
        course_resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"访问课程主页失败 {launcher_url}: {e}")
        return downloaded_files

    course_soup = BeautifulSoup(course_resp.text, "html.parser")

    # 4. 在左侧边栏寻找名称为 section_names 中任意一个的栏目链接
    section_urls = []
    target_set = set(section_names)

    for a in course_soup.find_all("a", href=True):
        span = a.find("span")
        title = span.get("title") if span else None
        text = span.get_text(strip=True) if span else a.get_text(strip=True)

        if title in target_set or text in target_set:
            sec_url = urljoin(course_resp.url, a["href"])
            if sec_url not in section_urls:
                section_urls.append(sec_url)

    if not section_urls:
        print(f"没有在课程主页左侧栏找到指定栏目：{section_names}")
        return downloaded_files

    print(f"找到 {len(section_urls)} 个栏目链接：")
    for u in section_urls:
        print("  -", u)

    # 5. 依次进入每个栏目页面，查找 /bbcswebdav/... 文件链接 + 可见文件名
    all_file_links: list[dict[str, str]] = []

    for sec_url in section_urls:
        print(f"\n进入栏目页面: {sec_url}")
        try:
            sec_resp = session.get(sec_url)
            sec_resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"访问栏目页面失败 {sec_url}: {e}")
            continue

        sec_soup = BeautifulSoup(sec_resp.text, "html.parser")

        for a in sec_soup.find_all("a", href=True):
            href = a["href"]
            if "bbcswebdav" in href:
                full_url = urljoin(sec_resp.url, href)

                # 提取可见文件名，例如 "文件2025秋季软件工程课程介绍20250909"
                raw_text = a.get_text(strip=True)
                display_name = raw_text

                # 常见情况：前面有一个 "文件"（来自 <img alt="文件">）
                if display_name.startswith("文件"):
                    display_name = display_name[len("文件") :].strip()

                # 去重：按 URL 去重
                if not any(item["url"] == full_url for item in all_file_links):
                    all_file_links.append(
                        {
                            "url": full_url,
                            "name": display_name,
                        }
                    )
                    print(f"  找到文件链接: {full_url}  名称: {display_name}")

    print(f"\n🔍 在栏目 {section_names} 中共发现 {len(all_file_links)} 个文件链接。")

    # 6. 逐个下载这些文件，并控制数量
    for i, file_info in enumerate(all_file_links, start=1):
        if max_files is not None and i > max_files:
            print(f"\n⚠️ 已达到 max_files={max_files}，停止继续下载。")
            break

        file_url = file_info["url"]
        display_name = file_info["name"]

        print(f"\n [{i}/{len(all_file_links)}] 正在下载: {file_url} ({display_name})")
        saved_path = download_file(file_url, session, save_dir=download_root)
        if saved_path is not None:
            downloaded_files.append(
                {
                    "path": saved_path,
                    "name": display_name,
                }
            )
        time.sleep(1)

    print(f"\n✅ 栏目文件下载完成，共下载 {len(downloaded_files)} 个文件。")
    return downloaded_files
