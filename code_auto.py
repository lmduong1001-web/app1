import os
import time
import json
import pyautogui
import pyperclip
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import winreg

def get_chrome_version():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Google\Chrome\BLBeacon"
        )
        version, _ = winreg.QueryValueEx(key, "version")
        return int(version.split(".")[0])
    except:
        return None

# ================== SETUP DRIVER ==================
def setup_driver(i):
    chrome_version = get_chrome_version()
    if chrome_version is None:
        raise Exception("Không tìm thấy Chrome")
    json_file = f"facebook/profile_{i}.json"
    with open(json_file, "r", encoding="utf-8") as file:
        config = json.load(file)

    user_agent = config["user_agent"]
    vendor = config["vendor"]
    renderer = config["renderer"]

    profile_path = os.path.abspath(f"./facebook_data/profile_{i}")
    options = uc.ChromeOptions()
    options.add_argument("--start-fullscreen")
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(
        options=options,
        version_main=chrome_version - 1,      # 👈 ÉP CHROMEDRIVER 144
        use_subprocess=True
    )
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})

    # Fake WebGL
    js_script = f"""
    (() => {{
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) return "{vendor}";
            if (parameter === 37446) return "{renderer}";
            return getParameter.call(this, parameter);
        }};
        const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) return "{vendor}";
            if (parameter === 37446) return "{renderer}";
            return getParameter2.call(this, parameter);
        }};
    }})()
    """
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_script})
    return driver

def Auto1():
    time.sleep(5)
    for _ in range(4):
        pyautogui.moveTo(1303, 1018)
        time.sleep(1)
        pyautogui.click()
        time.sleep(3)


def upload_tin(driver, tieude, asset_id, video, retry=3):

    url = f"https://business.facebook.com/latest/composer/?asset_id={asset_id}&nav_ref=internal_nav&ref=biz_web_home_create_post&context_ref=HOME"
    try:
        driver.get(url)
        time.sleep(5)

        try:
            input_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@aria-label='Hãy viết vào ô hộp thoại để thêm văn bản vào bài viết.']")
                )
            )
            driver.execute_script("arguments[0].click();", input_area)
        except Exception:
            print("❌ Không tìm thấy ô nhập văn bản")
            if retry > 0:
                print("🔄 Thử lại upload ảnh...")
                time.sleep(3)
                return upload_tin(driver, tieude, asset_id, video, retry-1)
            return False

        ActionChains(driver).move_to_element(input_area).click().send_keys(tieude).perform()
        time.sleep(2)

        driver.find_element(By.XPATH, "//*[text()='Thêm ảnh/video' or text()='Thêm video']").click()
        time.sleep(1)
        try:
            driver.find_element(By.XPATH, "//*[text()='Tải lên từ máy tính']").click()
        except:
            print("Khong Co")
        time.sleep(2)
        pyautogui.write(video)
        pyautogui.press("enter")
        while True:
            try:
                driver.find_element(By.XPATH, "//*[contains(text(),'Đang kiểm tra nội dung có bản quyền')]")
                print("Phát hiện: đang kiểm tra bản quyền")
                break
            except:
                time.sleep(1)

        # bắt đầu đếm 5 phút
        time.sleep(600)
        start_time = time.time()

        while True:
            try:
                driver.find_element(By.XPATH, "//*[contains(text(),'Không phát hiện vấn đề nào về bản quyền')]")
                print("Không phát hiện vấn đề bản quyền -> cho qua")
                break
            except:
                pass

            if time.time() - start_time > 300:
                raise Exception("Lỗi: quá 5 phút chưa có kết quả bản quyền")

            time.sleep(2)

        time.sleep(3)
        Auto1()
        time.sleep(3)
        return True

    except Exception:
        return False
