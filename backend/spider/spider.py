import time
import requests
import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from . import login

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

    course_pages = [
        "https://course.pku.edu.cn/webapps/portal/execute/tabs/tabAction?tab_tab_group_id=_1_1",
        "https://course.pku.edu.cn/webapps/blackboard/content/listContent.jsp?course_id=_86236_1&content_id=_1421420_1",
        "https://course.pku.edu.cn/webapps/blackboard/content/listContent.jsp?course_id=_86236_1&content_id=_1421419_1&mode=reset",
    ]

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
            if len(all_file_links) >= 10:  #  限制最多收集10个
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

    print(f"\n🔍 共发现 {len(all_file_links)} 个文件（限制10个）")

    # 下载阶段
    for i, file_url in enumerate(all_file_links, start=1):
        print(f"\n [{i}/{len(all_file_links)}] 正在下载: {file_url}")
        saved_path = download_file(file_url, s)
        if saved_path:
            downloaded_files.append(saved_path)
        time.sleep(1)

    print(f"\ 下载任务完成，共下载 {len(downloaded_files)} 个文件。")
    return downloaded_files


if __name__ == "__main__":
    start_spidering()
