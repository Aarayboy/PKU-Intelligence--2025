import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ======================= 【TODO: 你的凭证和平台URL】 =======================
# 请替换为你的真实信息
PKU_USERNAME = "your stu_id" 
PKU_PASSWORD = "your password"
# 课程平台首页，从这里开始点击登录
COURSE_BASE_URL = "https://course.pku.edu.cn/" 
# 登录成功后跳转的页面URL特征，用于等待
COURSE_PORTAL_URL_FEATURE = "webapps/portal" 

# ======================= 【元素定位器配置】 =======================

# 1. 课程平台页面 (course.pku.edu.cn) 上触发 IAAA 跳转的按钮
COURSE_AUTH_BUTTON_TYPE = By.CLASS_NAME      # "校园卡用户" 按钮没有 ID，使用 Class Name
COURSE_AUTH_BUTTON_VALUE = "login_stu_a"     

# 2. IAAA 统一认证页面 (iaaa.pku.edu.cn) 上的元素
IAAA_USERNAME_ID = "user_name"               # 用户名输入框的 ID
IAAA_PASSWORD_ID = "password"                # 密码输入框的 ID
IAAA_LOGIN_BUTTON_ID = "logon_button"        # 登录提交按钮的 ID

# =====================================================================


def pku_login_and_get_session(username, password, base_url):
    """
    模拟：课程平台 -> 点击按钮 -> IAAA 认证 -> 返回课程平台的完整登录过程。
    返回一个带有登录状态 Cookies 的 requests.Session 对象。
    """
    
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')s
    options.add_argument('log-level=3') # 减少控制台输出

    driver = webdriver.Chrome(options=options)
    session = requests.Session()
    
    try:
        # 1. 访问课程平台首页
        print(f"-> 访问课程平台首页: {base_url}")
        driver.get(base_url)

        # 2. 等待并点击“校园卡用户”按钮，触发跳转到 IAAA
        print("-> 等待并点击登录按钮，触发跳转...")
        auth_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((COURSE_AUTH_BUTTON_TYPE, COURSE_AUTH_BUTTON_VALUE)) 
        )
        auth_button.click()

        # 3. 等待跳转到 IAAA 登录页面
        print("-> 等待跳转到统一身份认证页面 (iaaa.pku.edu.cn)...")
        WebDriverWait(driver, 10).until(
            EC.url_contains("iaaa.pku.edu.cn")
        )
        
        # 4. 输入 IAAA 页面的用户名和密码
        print("-> 正在输入 IAAA 认证页面的用户名和密码...")
        # 等待用户名输入框出现
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, IAAA_USERNAME_ID))
        )
        driver.find_element(By.ID, IAAA_USERNAME_ID).send_keys(username)
        driver.find_element(By.ID, IAAA_PASSWORD_ID).send_keys(password)

        # 5. 点击 IAAA 登录按钮
        print("-> 正在点击 IAAA 登录...")
        driver.find_element(By.ID, IAAA_LOGIN_BUTTON_ID).click()
        
        # 6. 等待登录成功并跳转回课程平台
        print(f"-> 等待跳转回课程平台 ({COURSE_PORTAL_URL_FEATURE})...")
        WebDriverWait(driver, 20).until(
            EC.url_contains(COURSE_PORTAL_URL_FEATURE)
        )
        
        # 额外的等待时间，确保 Cookies 被设置
        time.sleep(2) 

        # 7. 登录成功，获取 Cookies
        print("-> 登录成功，正在提取 Cookies...")
        for cookie in driver.get_cookies():
            # 将 Selenium 的 Cookie 格式转换成 requests.Session 可用的格式
            session.cookies.set(cookie['name'], cookie['value'])
            
        driver.quit()
        print("-> Cookies 注入 requests Session 成功。")
        return session

    except Exception as e:
        print(f"登录过程中发生错误: {e}")
        driver.quit()
        return None