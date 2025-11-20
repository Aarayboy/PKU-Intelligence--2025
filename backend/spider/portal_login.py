import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ======================= 基本配置 =======================

# 北大门户首页地址
PKU_PORTAL_BASE_URL = "https://portal.pku.edu.cn/"

# IAAA 统一认证页面上的元素（和你原来的 login.py 相同）
IAAA_USERNAME_ID = "2200011085"      # 用户名输入框 ID
IAAA_PASSWORD_ID = "Lizhangxin38"       # 密码输入框 ID
IAAA_LOGIN_BUTTON_ID = "logon_button"  # 登录按钮 ID

# 登录成功后，通常会跳回 portal.pku.edu.cn 下的某个页面
PORTAL_URL_FEATURE = "portal.pku.edu.cn"

# =======================================================

def pku_portal_login_and_get_session(username: str,
                                     password: str,
                                     base_url: str = PKU_PORTAL_BASE_URL) -> requests.Session | None:
    """
    完整流程：
    1. 访问 https://portal.pku.edu.cn/
    2. 自动 302 跳转到 iaaa.pku.edu.cn 统一认证页面
    3. 在 IAAA 页面输入学号/密码并提交
    4. 等待跳回门户（portal.pku.edu.cn），从 Selenium 中取出 Cookies
    5. 把 Cookies 注入到一个 requests.Session 里，作为返回值

    登录成功：返回带登录 Cookies 的 Session
    登录失败：返回 None
    """

    # ==== Selenium 启动配置 ====
    options = webdriver.ChromeOptions()
    # 如需无头模式可取消下面注释
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("log-level=3")  # 减少控制台输出

    driver = webdriver.Chrome(options=options)
    session = requests.Session()

    try:
        # 1. 访问门户首页（会被重定向到 IAAA）
        print(f"-> 访问北大门户: {base_url}")
        driver.get(base_url)

        # 2. 等待 URL 中出现 iaaa，说明已经跳到了统一认证
        print("-> 等待跳转到 IAAA 统一身份认证页面...")
        WebDriverWait(driver, 15).until(
            EC.url_contains("iaaa.pku.edu.cn")
        )

        # 3. 等待用户名输入框出现，并填入账号密码
        print("-> 输入用户名和密码...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, IAAA_USERNAME_ID))
        )

        user_input = driver.find_element(By.ID, IAAA_USERNAME_ID)
        pwd_input = driver.find_element(By.ID, IAAA_PASSWORD_ID)

        user_input.clear()
        user_input.send_keys(username)
        pwd_input.clear()
        pwd_input.send_keys(password)

        # 4. 点击“登录”按钮
        print("-> 点击登录按钮...")
        driver.find_element(By.ID, IAAA_LOGIN_BUTTON_ID).click()

        # 5. 等待跳转回 portal（登录成功后 URL 中会重新出现 portal.pku.edu.cn）
        print("-> 等待跳回门户页面...")
        WebDriverWait(driver, 30).until(
            EC.url_contains(PORTAL_URL_FEATURE)
        )

        # 再等一小会儿，确保 Cookies 都设置好了
        time.sleep(2)

        # 6. 从 Selenium 中取出 Cookies 注入到 requests.Session
        print("-> 登录成功，提取 Cookies 注入 Session...")
        for cookie in driver.get_cookies():
            # Selenium cookie: {'name': 'xxx', 'value': 'yyy', ...}
            session.cookies.set(cookie["name"], cookie["value"])

        print("-> Session 构造完成，可以用来请求 myCourseTable 等接口。")
        return session

    except Exception as e:
        print(f"[错误] 门户登录过程失败: {e}")
        return None

    finally:
        driver.quit()
