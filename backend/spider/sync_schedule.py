import csv
import requests
from bs4 import BeautifulSoup
from typing import List
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests import Session

# “我的课表”页面 URL（目前主要作为参考，不强依赖 URL 变化）
MY_COURSE_TABLE_URL = "https://portal.pku.edu.cn/publicQuery/#/myCourseTable"

# 统一身份认证 OAuth URL（一定要和 portal_login 里的一致）
PKU_OAUTH_URL = (
    "https://iaaa.pku.edu.cn/iaaa/oauth.jsp"
    "?appID=portal2017"
    "&appName=%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E6%A0%A1%E5%86%85%E4%BF%A1%E6%81%AF%E9%97%A8%E6%88%B7%E6%96%B0%E7%89%88"
    "&redirectUrl=https%3A%2F%2Fportal.pku.edu.cn%2Fportal2017%2FssoLogin.do"
)

# 初始化全局 driver（你之前就是这么做的）
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("log-level=3")
driver = webdriver.Chrome(options=options)


def debug_current_page(driver: webdriver.Chrome):
    url = driver.current_url
    title = driver.title
    html = driver.page_source

    print(f"当前 URL： {url}")
    print(f"页面 Title： {title}")
    print("页面 HTML 预览（前 500 字符）：")
    print(html[:500])

    has_all = "全部" in html
    print(("\n✅" if has_all else "\n❌"),
          f"页面 HTML 中【{'包含' if has_all else '不包含'}】“全部”二字")
    print("页面中 iframe 数量：", len(driver.find_elements(By.TAG_NAME, "iframe")))
    print("========== 页面状态诊断结束 ==========\n")


def fetch_course_table_html(username: str, password: str) -> str | None:
    """
    使用 Selenium 完整模拟：
    IAAA 登录 → portal2017 → 全部 → 我的课表 → 抓取课表 HTML
    """

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("log-level=3")
    # ⚠️ 不要 headless
    # options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    try:
        # ========== 1. 打开 IAAA OAuth ==========
        print("-> 打开 IAAA OAuth 页面 ...")
        oauth_url = (
            "https://iaaa.pku.edu.cn/iaaa/oauth.jsp"
            "?appID=portal2017"
            "&appName=%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E6%A0%A1%E5%86%85%E4%BF%A1%E6%81%AF%E9%97%A8%E6%88%B7%E6%96%B0%E7%89%88"
            "&redirectUrl=https%3A%2F%2Fportal.pku.edu.cn%2Fportal2017%2FssoLogin.do"
        )
        driver.get(oauth_url)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "user_name"))
        )

        # ========== 2. 输入账号密码 ==========
        print("-> 输入账号密码 ...")
        driver.find_element(By.ID, "user_name").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "logon_button").click()

        # ========== 3. 等待跳转 portal ==========
        print("-> 等待跳转到 portal2017 ...")
        WebDriverWait(driver, 30).until(
            EC.url_contains("portal.pku.edu.cn/portal2017")
        )

        # 确保在 bizCenter
        driver.get("https://portal.pku.edu.cn/portal2017/#/bizCenter")
        WebDriverWait(driver, 30).until(
            EC.url_contains("#/bizCenter")
        )
        print("-> 已进入 bizCenter")

        time.sleep(3)

        # ========== 4. 点击“全部” ==========
        print("-> 点击 '全部' 图标 ...")
        all_icon = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "all"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", all_icon)
        time.sleep(1)
        all_icon.click()

        time.sleep(3)

        # ========== 5. 点击“我的课表” ==========
        print("-> 点击 '我的课表' 图标 ...")
        old_windows = driver.window_handles

        course_icon = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "tag_s_coursetable"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", course_icon)
        time.sleep(1)
        course_icon.click()

        # ========== 6. 切换到新窗口 ==========
        WebDriverWait(driver, 30).until(
            lambda d: len(d.window_handles) > len(old_windows)
        )
        new_window = [w for w in driver.window_handles if w not in old_windows][0]
        driver.switch_to.window(new_window)

        print("-> 已切换到课表窗口")
        time.sleep(5)  # ⚠️ 给 Angular 足够时间渲染

        # ========== 7. 获取 HTML ==========
        html = driver.page_source
        print("-> 成功获取课表页面 HTML")

        return html

    except Exception as e:
        print("❌ 课表抓取失败：", e)
        return None

    finally:
        # 用完再关，方便你调试时观察页面
        # driver.quit()
        pass

def parse_course_table(html: str) -> List[List[str]]:
    soup = BeautifulSoup(html, "html.parser")

    # 12节 × 7天
    grid = [["" for _ in range(7)] for _ in range(12)]

    day_map = {
        "mon": 0,
        "tue": 1,
        "wed": 2,
        "thu": 3,
        "fri": 4,
        "sat": 5,
        "sun": 6,
    }

    # ✅ 直接找所有课表格子
    for td in soup.find_all("td", class_="td-compact"):
        td_id = td.get("id")
        if not td_id:
            continue

        # 例如：tue3 / mon10
        for day in day_map:
            if td_id.startswith(day):
                try:
                    row = int(td_id[len(day):]) - 1
                    col = day_map[day]
                except ValueError:
                    continue

                text = td.get_text("\n", strip=True)
                if text:
                    grid[row][col] = text

    return grid

def save_course_grid_to_csv(grid: List[List[str]],
                            filename: str = "course_table.csv") -> None:
    """
    把课表 grid 写入 CSV 文件。
    grid: 12×7 的课表数据
    filename: 输出文件名
    """
    # 表头：节次 + 周一~周日
    header = ["节次", "周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for i, row in enumerate(grid, start=1):
            # 每一行前面加上节次编号（1~12）
            writer.writerow([i] + row)

def sync_schedule(username: str, password: str):


    html = fetch_course_table_html(username, password)
    if html is None:
        return False, "登录或获取课表页面失败"

    try:
        grid = parse_course_table(html)
        save_course_grid_to_csv(grid)  # 保存课表到 CSV 文件
        data = {"grid": grid}
        return True, data
    except Exception as e:
        return False, f"解析课表失败: {e}"


if __name__ == "__main__":
    # 测试用例
    test_username = "username"
    test_password = "password"
    success, data = sync_schedule(test_username, test_password)

    if success:
        print("课表同步成功！")
        print(data)
    else:
        print("课表同步失败：", data)



