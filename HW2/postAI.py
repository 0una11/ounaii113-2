from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
from dotenv import load_dotenv, find_dotenv

# 強制重新載入 .env
os.environ.pop("USERNAME", None)
os.environ.pop("PASSWORD", None)

dotenv_path = find_dotenv()
print(f"🔍 使用的 .env 檔案：{dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
print(f"📦 使用帳號：{USERNAME}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 顯示瀏覽器
    page = browser.new_page()

    print("啟動瀏覽器，開始登入 NTNU校務行政入口...")

    # 進入 校務行政入口 登入頁面
    page.goto("https://iportal.ntnu.edu.tw/ntnu/")
    page.wait_for_selector("#muid")  # 確保頁面載入完畢再操作

    # 使用 .env 讀取帳號密碼
    page.fill("#muid", USERNAME)
    page.fill("#mpassword", PASSWORD)

    # 改成直接呼叫登入的 JavaScript 函數
    page.evaluate("login1()")

    # 等待登入完成
    page.wait_for_timeout(5000)
    print("登入成功！")
    page.screenshot(path="debug_1_after_login.png")

    # 點擊展開「學務相關系統」資料夾
    page.click('#apImg-affair')
    page.wait_for_selector('a:has-text("學生請假系統")')  # 等待連結出現

    # 點擊「學生請假系統」並等待新分頁彈出
    with page.expect_popup() as popup_info:
        page.click('a:has-text("學生請假系統")')
    leave_page = popup_info.value
    leave_page.wait_for_load_state()
    print("✅ 成功進入請假系統")
    leave_page.screenshot(path="debug_2_after_profile.png")

    # 保持瀏覽器開啟，方便 Debug
    input("瀏覽器保持開啟，按 Enter 關閉...")

    # 關閉瀏覽器
    browser.close()
    print("瀏覽器已關閉")