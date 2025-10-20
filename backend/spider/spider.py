import requests
import os
from urllib.parse import urljoin, urlparse
import login

DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR): # 确保 downloads 文件夹存在
    os.makedirs(DOWNLOAD_DIR)

def get_filename_from_url(url):
    """从URL中提取文件名"""
    path = urlparse(url).path
    return os.path.basename(path) # 取路径最后一段作为文件名

def download_file(file_url, session):
    """下载单个文件到 downloads 文件夹"""
    try:
        # 使用会话(session)发起请求，这在后续处理登录时很有用
        response = session.get(file_url, stream=True) # 发起 HTTP 请求，流式下载
        response.raise_for_status() # 如果请求失败 (相应状态不是200), 则抛出异常

        # 从URL中获取文件名
        filename = get_filename_from_url(file_url)
        if not filename:
            filename = 'downloaded_file.unknown' # 未知文件名

        save_path = os.path.join(DOWNLOAD_DIR, filename) # 构建保存路径

        # 以二进制写模式打开文件，分块写入
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"文件下载成功: {save_path}")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"下载文件失败 {file_url}: {e}")
        return None

# def start_spidering():
#     """
#     爬虫主函数
#     演示函数。没有爬取北大网站，而是下载一个公开的示例PPT。真正的北大教学网爬取需要复杂的登录认证
#     """
    
#     # --- 演示代码开始 ---
#     # 使用一个普通的 session，并假装我们已经“登录”
#     s = requests.Session()
#     s.headers.update({
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     })

#     # 这是一个公开的示例PPTX文件URL，用于测试下载功能
#     # (来源: https://www.slidescarnival.com/ )
#     PPT_EXAMPLE_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

#     print(f"开始模拟下载: {PPT_EXAMPLE_URL}")
    
#     # 模拟“解析”到了这个URL，然后下载它
#     downloaded_files = []
    
#     # 在真实的爬虫中，你会在这里使用 BeautifulSoup 解析 HTML
#     # soup = BeautifulSoup(page_html, 'html.parser')
#     # ppt_links = soup.find_all('a', href=lambda href: href and (href.endswith('.ppt') or href.endswith('.pptx')))
#     # for link in ppt_links:
#     #     file_url = urljoin(COURSE_PAGE_URL, link['href'])
#     #     saved_path = download_file(file_url, s)
#     #     if saved_path:
#     #         downloaded_files.append(saved_path)

#     # 仅用于演示
#     saved_path = download_file(PPT_EXAMPLE_URL, s)
#     if saved_path:
#         downloaded_files.append(saved_path)
#     # --- 演示代码结束 ---

#     return downloaded_files


def start_spidering():
    downloaded_files = []

    # 1. 调用新的登录函数获取 Session
    s = login.pku_login_and_get_session(login.PKU_USERNAME, login.PKU_PASSWORD, login.COURSE_BASE_URL)

    if s is None:
        print("!!! 登录失败，爬虫终止 !!!")
        return downloaded_files

    # 2. 设置 User-Agent (使用登录后的 Session)
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    # 3. **下一步：访问课程页面，开始解析**
    print(f"-> 访问课程主页: {login.COURSE_BASE_URL}")
    
    try:
        pass
        
    except requests.exceptions.RequestException as e:
        print(f"访问课程主页时发生错误: {e}")
        
    return downloaded_files