import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ======================= 基本配置 =======================


# ======================= 【TODO: 你的凭证和平台URL】 =======================
# 请替换为你的真实信息
PKU_USERNAME = "username"
PKU_PASSWORD = "password"
# 北大门户首页，从这里开始点击登录
PKU_PORTAL_BASE_URL = "https://portal.pku.edu.cn/"
COURSE_PORTAL_URL = "https://portal.pku.edu.cn/publicQuery/#/myCourseTable"  # 课表页面 URL
PORTAL_MAIN_URL = "https://portal.pku.edu.cn/portal2017/#/bizCenter"  # 主界面 URL
# 登录成功后跳转的页面URL特征，用于等待
COURSE_PORTAL_URL_FEATURE = "portal2017/#/bizCenter"
COURSE_TABLE_URL_FEATURE = "publicQuery/#/myCourseTable"



# IAAA 统一认证页面上的元素（和你原来的 login.py 相同）
IAAA_USERNAME_ID = "user_name"      # 用户名输入框 ID
IAAA_PASSWORD_ID = "password"       # 密码输入框 ID
IAAA_LOGIN_BUTTON_ID = "logon_button"  # 登录按钮 ID

# 登录成功后，通常会跳回 portal.pku.edu.cn 下的某个页面
PORTAL_URL_FEATURE = "portal.pku.edu.cn"

# =======================================================

def pku_portal_login_and_get_session(username: str, password: str, base_url: str = "https://iaaa.pku.edu.cn/iaaa/oauth.jsp?appID=portal2017&appName=%E5%8C%97%E4%BA%AC%E5%A4%A7%E5%AD%A6%E6%A0%A1%E5%86%85%E4%BF%A1%E6%81%AF%E9%97%A8%E6%88%B7%E6%96%B0%E7%89%88&redirectUrl=https%3A%2F%2Fportal.pku.edu.cn%2Fportal2017%2FssoLogin.do") -> webdriver.Chrome:
    """
    使用 Selenium 模拟浏览器登录北大门户，并返回浏览器 driver 对象。
    """
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("log-level=3")  # 减少控制台输出
    # 不启用无头模式，这样浏览器会显示出来
    # options.add_argument('--headless')  # 注释掉这一行，显示浏览器界面

    driver = webdriver.Chrome(options=options)
    session = requests.Session()

    try:
        # 1. 访问北大门户首页
        print(f"-> 访问北大门户首页: {base_url}")
        driver.get(base_url)

        # 2. 自动跳转到 IAAA 登录页面
        print("-> 等待跳转到统一身份认证页面 (iaaa.pku.edu.cn)...")
        WebDriverWait(driver, 10).until(EC.url_contains("iaaa.pku.edu.cn"))

        # 3. 输入 IAAA 页面的用户名和密码
        print("-> 正在输入 IAAA 认证页面的用户名和密码...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, IAAA_USERNAME_ID))
        )
        driver.find_element(By.ID, IAAA_USERNAME_ID).send_keys(username)
        driver.find_element(By.ID, IAAA_PASSWORD_ID).send_keys(password)

        # 4. 点击 IAAA 登录按钮
        print("-> 正在点击 IAAA 登录...")
        driver.find_element(By.ID, IAAA_LOGIN_BUTTON_ID).click()

        # 5. 等待登录成功并跳转回课程平台
        print("-> 等待跳转回课程平台 ...")
        WebDriverWait(driver, 20).until(EC.url_contains("portal.pku.edu.cn"))

        # 6. 登录成功后，访问主界面页面（bizCenter）
        print(f"-> 访问主界面页面: {PORTAL_MAIN_URL}")
        driver.get(PORTAL_MAIN_URL)


        # 等待页面加载完成
        time.sleep(5)

        # 7. 登录成功，获取 Cookies
        print("-> 登录成功，正在提取 Cookies...")
        for cookie in driver.get_cookies():
            # 将 Selenium 的 Cookie 格式转换成 requests.Session 可用的格式
            session.cookies.set(cookie["name"], cookie["value"])

        driver.quit()
        print("-> Cookies 注入 requests Session 成功。")
        return session

    except Exception as e:
        print(f"登录过程中发生错误: {e}")
        driver.quit()  # 确保在发生错误时关闭浏览器
        return None