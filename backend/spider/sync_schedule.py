import requests
from bs4 import BeautifulSoup
from portal_login import pku_portal_login_and_get_session
from typing import List
MY_COURSE_TABLE_URL = "https://portal.pku.edu.cn/publicQuery/#/myCourseTable"
# 登录并获取课程表的函数

def fetch_course_table_html(username: str, password: str) -> str | None:
    """
    登陆门户后，访问“我的课表”页面，返回 HTML 文本。
    """
    session = pku_portal_login_and_get_session(username, password)
    if session is None:
        print("登录失败，无法获取课表。")
        return None

    # 注意：# 后面的 fragment 前端用来路由，HTTP 请求时不会带这一段，
    # 但直接写完整 URL 也没关系，requests 会自动去掉。
    resp = session.get(MY_COURSE_TABLE_URL)
    if resp.status_code != 200:
        print(f"获取课表页面失败，状态码: {resp.status_code}")
        return None

    return resp.text

def parse_course_table(html: str) -> List[List[str]]:
    """
    解析“我的课表”页面 HTML，返回一个二维数组 grid[row][col]，
    row 表示第几节课（从 0 开始），col 表示星期（0=周一, 1=周二,...）

    若某格无课则为空字符串 ""。
    """
    soup = BeautifulSoup(html, "html.parser")

    target_table = None

    # 1. 找到真正放课表的 table：
    #    策略：寻找包含“上课信息”字样的 table
    for table in soup.find_all("table"):
        if "上课信息" in table.get_text():
            target_table = table
            break

    if target_table is None:
        raise ValueError("未找到包含课表的 <table>，请检查页面结构或调整解析逻辑。")

    # 2. 行：每个 <tr> 一行，通常第一行是表头（周一~周日），先判断
    rows = target_table.find_all("tr")
    if not rows:
        return []

    # 可能第一行是表头：含有 <th> 或“周一/周二”等字样，就跳过
    header_like = False
    head_text = rows[0].get_text()
    if "周一" in head_text or rows[0].find("th") is not None:
        header_like = True

    body_rows = rows[1:] if header_like else rows

    grid: List[List[str]] = []

    for r_idx, tr in enumerate(body_rows):
        cols = tr.find_all("td")
        row_data: List[str] = []

        for c_idx, td in enumerate(cols):
            # 一个单元格内可能多个课程，用 span 块分开，全部抓出
            spans = td.find_all("span")
            cell_blocks: List[str] = []

            if spans:
                for sp in spans:
                    # 把 <br> 用换行拼起来
                    text = sp.get_text(separator="\n", strip=True)
                    if text:
                        cell_blocks.append(text)
            else:
                # 退而求其次，直接取 td 文本
                text = td.get_text(separator="\n", strip=True)
                if text:
                    cell_blocks.append(text)

            # 最终单元格文本：同一格多个课程，用空行分隔
            cell_text = "\n\n".join(cell_blocks)
            row_data.append(cell_text)

        grid.append(row_data)

    return grid

def grid_to_course_list(grid: List[List[str]]):
    """
    将二维网格转为 [{row, col, text}, ...]，
    只保留非空的课程格子，方便前端使用。
    row/col 均从 1 开始计数。
    """
    result = []
    for r_idx, row in enumerate(grid, start=1):
        for c_idx, cell_text in enumerate(row, start=1):
            if cell_text.strip():
                result.append({
                    "row": r_idx,
                    "col": c_idx,
                    "text": cell_text
                })
    return result

def sync_schedule(username: str, password: str):
    """
    总入口函数：
    1. 登录门户
    2. 抓取“我的课表”页面 HTML
    3. 解析为 grid 和带坐标的列表

    返回：
        success: bool
        data:    dict | str  (成功时是课程数据，失败时是错误信息)
    """
    html = fetch_course_table_html(username, password)
    if html is None:
        return False, "登录或获取课表页面失败"

    try:
        grid = parse_course_table(html)
        course_list = grid_to_course_list(grid)
        data = {
            "grid": grid,             # grid[row][col] 形式
            "course_list": course_list  # [{row, col, text}, ...]
        }
        return True, data
    except Exception as e:
        return False, f"解析课表失败: {e}"
