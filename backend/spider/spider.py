import time
import requests
import os
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from . import login
from pathlib import Path

CURRENT_SEMESTER_LABEL = os.getenv("CURRENT_SEMESTER_LABEL", "25-26学年第1学期") # 手动指定“本学期”的标记
SEMESTER_PATTERN = re.compile(r"\d{2}-\d{2}学年第[1-2]学期") # 用来从课程名里提取 “25-26学年第1学期” 这一段


DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def get_filename_from_response(response, fallback_url):
    
    """从响应头或URL提取真实文件名"""
    cd = response.headers.get('Content-Disposition', '')
    filename = None

    if 'filename=' in cd:
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


def ensure_unique_filename(filename):
    """若重名则自动加编号"""
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(DOWNLOAD_DIR, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1
    return filename


def download_file(file_url, session):
    """下载单个文件到 downloads 文件夹"""
    try:
        response = session.get(file_url, stream=True)
        response.raise_for_status()

        filename = get_filename_from_response(response, file_url)
        filename = ensure_unique_filename(filename)
        save_path = os.path.join(DOWNLOAD_DIR, filename)

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"文件下载成功: {save_path}")
        return save_path
    except Exception as e:
        print(f"下载文件失败 {file_url}: {e}")
        return None


def get_all_courses(session):
    """
    从课程首页解析当前账号的所有课程入口。

    返回一个列表，每个元素是：
      {
        "name": "课程显示名",
        "course_id": "_83408_1",
        "launcher_url": "https://course.pku.edu.cn/webapps/blackboard/execute/launcher?type=Course&id=PkId{key=_83408_1,...}&url="
      }
    """
    # 尝试两个入口：登录首页和原来的 portal tab 页面
    candidate_urls = [
        login.COURSE_BASE_URL,  # 一般是 https://course.pku.edu.cn/
        "https://course.pku.edu.cn/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1",
    ]

    html = None
    base_url = None

    for url in candidate_urls:
        try:
            resp = session.get(url, allow_redirects=True)
            resp.raise_for_status()
            # 粗略判断一下页面里是不是有 "type=Course" 这样的课程入口
            if "execute/launcher" in resp.text and "type=Course" in resp.text:
                html = resp.text
                base_url = resp.url  # 注意可能重定向
                print(f"在页面 {resp.url} 找到课程列表。")
                break
        except requests.exceptions.RequestException as e:
            print(f"访问 {url} 失败: {e}")
            continue

    if not html:
        print("未在课程首页发现课程列表 HTML。")
        return []

    soup = BeautifulSoup(html, "html.parser")
    courses = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        # 匹配：课程入口链接
        #   /webapps/blackboard/execute/launcher?type=Course&id=PkId{key=_83408_1,...}&url=
        if "execute/launcher" in href and "type=Course" in href and "PkId{key=" in href:
            full_url = urljoin(base_url, href)

            # 补充一段：检查是不是本学期的课程，只选择本学期的；如果想要所有学期的则删掉这段
            sem_match = SEMESTER_PATTERN.search(text)
            semester_label = sem_match.group(0) if sem_match else None
            if semester_label is not None and semester_label != CURRENT_SEMESTER_LABEL: 
                continue # 这是历史学期 → 直接 continue

            # 从 id 参数中提取 course_id: PkId{key=_83408_1, ...}
            m = re.search(r"PkId\{key=([^,}]+)", href)
            course_id = m.group(1) if m else None

            courses.append({
                "name": text,
                "course_id": course_id,
                "launcher_url": full_url,
            })

    print(f"诶！ 解析到 {len(courses)} 门课程。")
    for c in courses:
        print(f"  - {c['course_id']}: {c['name']}")

    return courses


def get_course_content_pages(session, course):
    """
    给定一门课程（包含 launcher_url, course_id），
    访问课程主页，从中解析出若干个内容列表页面 listContent.jsp?course_id=...&content_id=...

    返回 list[str]，每个元素是一个 URL。
    """
    launcher_url = course["launcher_url"]
    course_id = course["course_id"]
    content_pages = set()

    try:
        resp = session.get(launcher_url, allow_redirects=True)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"访问课程主页失败 {launcher_url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    for a in soup.find_all("a", href=True):
        href = a["href"]
        # 典型的：/webapps/blackboard/content/listContent.jsp?course_id=_83408_1&content_id=...
        if "listContent.jsp" in href and "course_id=" in href:
            # 如果需要限制只抓本课程，可以加：
            if course_id is None or f"course_id={course_id}" in href:
                full_url = urljoin(resp.url, href)
                content_pages.add(full_url)

    print(f"  课程 {course_id} - {course['name']} 发现 {len(content_pages)} 个 listContent.jsp 内容页。")
    return list(content_pages)

def get_first_course_name(session):
    """
    调用 get_all_courses(session)，返回第一门课程的名称字符串。
    如果当前账号没有课程，返回空字符串 ""。
    """
    courses = get_all_courses(session)

    # courses 是一个列表，每个元素形如：
    # { "name": "...", "course_id": "...", "launcher_url": "..." }
    first_course = courses[0]
    return first_course.get("name", "")


def start_spidering():
    """主函数：访问页面 → 收集文件链接 → 下载前10个"""
    downloaded_files = []

    s = login.pku_login_and_get_session(login.PKU_USERNAME, login.PKU_PASSWORD, login.COURSE_BASE_URL)

    if s is None:
        print(" 登录失败，爬虫终止")
        return downloaded_files

    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0 Safari/537.36'
    })

    # course_pages = [
    #     "https://course.pku.edu.cn/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1",
    #     "https://course.pku.edu.cn/webapps/blackboard/content/listContent.jsp?course_id=_86236_1&content_id=_1421420_1",
    #     "https://course.pku.edu.cn/webapps/blackboard/content/listContent.jsp?course_id=_86236_1&content_id=_1421419_1&mode=reset",
    # ]

    # 1) 先解析当前账号的所有课程（名字 + course_id + launcher_url）
    courses = get_all_courses(s)
    course_name = courses[0]['name'] if courses else 'N/A'
    print(courses) # 调试使用
    if not courses:
        print("没有解析到任何课程，爬虫终止。")
        return downloaded_files

    # 2) 对每门课程找 listContent.jsp 内容页，汇总成 course_pages
    course_pages = []
    for course in courses:
        pages = get_course_content_pages(s, course)
        course_pages.extend(pages)

    # 去重一下
    course_pages = list(dict.fromkeys(course_pages))
    print(f"总共收集到 {len(course_pages)} 个课程内容页，用于后续文件扫描。")


    all_file_links = []
    allowed_exts = ('.pdf', '.docx', '.pptx')

    # 第一层：访问课程页面，提取“详情页”链接
    for page_url in course_pages:
        print(f"\n 正在访问课程页面: {page_url}")
        try:
            resp = s.get(page_url)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f" 访问失败: {e}")
            continue

        soup = BeautifulSoup(resp.text, 'html.parser')
        mid_links = []

        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'content' in href and 'listContent.jsp' not in href:
                full_url = urljoin(page_url, href)
                mid_links.append(full_url)

        print(f"  发现 {len(mid_links)} 个可能的文件详情页")

        # 第二层：访问详情页，提取真实文件直链
        for mid_url in mid_links:
            if len(all_file_links) >= 3:  #  限制最多收集3个
                break
            try:
                sub_resp = s.get(mid_url, stream=True)
                sub_resp.raise_for_status()
                content_type = sub_resp.headers.get("Content-Type", "").lower()

                # 若直接返回文件，则加入下载队列
                if any(ft in content_type for ft in ["pdf", "officedocument", "ms-powerpoint", "msword"]):
                    if mid_url not in all_file_links:
                        all_file_links.append(mid_url)
                        print(f"  检测到直接文件: {mid_url}")
                    continue

                # 否则继续解析 HTML
                sub_soup = BeautifulSoup(sub_resp.text, 'html.parser')
                for a2 in sub_soup.find_all('a', href=True):
                    href2 = a2['href']
                    if 'bbcswebdav' in href2 and href2.lower().endswith(allowed_exts):
                        full_url = urljoin(mid_url, href2)
                        if full_url not in all_file_links:
                            all_file_links.append(full_url)
                            print(f" 找到文件: {full_url}")
                    if len(all_file_links) >= 10:
                        break
                time.sleep(0.5)

            except Exception as e:
                print(f"  访问 {mid_url} 时出错: {e}")

    print(f"\n🔍 共发现 {len(all_file_links)} 个文件（限制3个）")

    # 下载阶段
    for i, file_url in enumerate(all_file_links, start=1):
        print(f"\n [{i}/{len(all_file_links)}] 正在下载: {file_url}")
        saved_path = download_file(file_url, s)
        if saved_path:
            downloaded_files.append(saved_path)
        time.sleep(1)

    print(f"下载任务完成，共下载 {len(downloaded_files)} 个文件。")
    return downloaded_files


if __name__ == "__main__":
    start_spidering()