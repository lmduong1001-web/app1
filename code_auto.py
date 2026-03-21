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


# ================== SETUP DRIVER ==================
def setup_driver(i):
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
        version_main=145,      # 👈 ÉP CHROMEDRIVER 144
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



# ================== AUTO CLICK ==================
def Auto():
    time.sleep(5)
    for _ in range(4):
        for y in [920, 945, 970, 995, 1020]:
            pyautogui.moveTo(1560, y)
            time.sleep(1)
            pyautogui.click()
            time.sleep(1)
        time.sleep(3)

def Auto1():
    time.sleep(5)
    for _ in range(4):
        pyautogui.moveTo(1303, 1018)
        time.sleep(1)
        pyautogui.click()
        time.sleep(3)

def Auto_tin():
    time.sleep(5)
    for _ in range(4):
        for y in [770, 820, 870, 920, 970]:
            pyautogui.moveTo(1560, y)
            time.sleep(1)
            pyautogui.click()
            time.sleep(1)
        time.sleep(3)



# ================== UPLOAD IMAGE ==================
def upload_image(driver, tieude, asset_id, image, retry=3):

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
                return upload_image(driver, tieude, asset_id, image, retry-1)
            return False

        ActionChains(driver).move_to_element(input_area).click().send_keys(tieude).perform()
        time.sleep(2)

        driver.find_element(By.XPATH, "//*[text()='Thêm ảnh/video' or text()='Thêm ảnh']").click()
        time.sleep(2)

        pyautogui.write(image)
        pyautogui.press("enter")

        time.sleep(20)
        driver.find_element(By.XPATH, "//*[text()='Đăng']").click()
        time.sleep(10)
        return True

    except Exception:
        return False

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
                return upload_image(driver, tieude, asset_id, video, retry-1)
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

# ================== UPLOAD VIDEO ==================
def upload_video(driver, tieude, asset_id, video, retry=3):

    url = f"https://business.facebook.com/latest/reels_composer/?ref=biz_web_home_create_reel&asset_id={asset_id}&context_ref=HOME"

    try:
        driver.get(url)
        driver.implicitly_wait(20)
        time.sleep(5)
        try:
            input_area = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@aria-label='Mô tả thước phim của bạn để mọi người biết nội dung thước phim' or @aria-label='Hãy viết vào ô hộp thoại để thêm văn bản vào bài viết.']")
                )
            )
        except Exception:
            print("❌ Không tìm thấy ô nhập mô tả → chạy lại toàn hàm")
            if retry > 0:
                time.sleep(3)
                return upload_video(driver, tieude, asset_id, video, retry-1)
            return False

        # =============== NHẬP MÔ TẢ ===============
        driver.execute_script("arguments[0].click();", input_area)
        ActionChains(driver).move_to_element(input_area).click().send_keys(tieude).perform()

        # =============== UPLOAD VIDEO ===============
        driver.find_element(By.XPATH, "//*[text()='Thêm video']").click()
        time.sleep(4)

        pyautogui.write(video)
        pyautogui.press("enter")

        time.sleep(60)
        Auto()
        time.sleep(10)
        return True

    except Exception as e:
        print("❌ Lỗi không xác định:", e)
        if retry > 0:
            return upload_video(driver, tieude, asset_id, video, retry-1)
        return False

def upload_dai(driver, tieude, asset_id, video, retry=3):

    url = f"https://business.facebook.com/latest/story_composer/?page_id={asset_id}"

    try:
        driver.get(url)
        driver.implicitly_wait(20)
        time.sleep(5)

        driver.find_element(By.XPATH, "//*[text()='Thêm ảnh/video']").click()
        try:
            input_area = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[text()='Kéo và thả ảnh hoặc video vào đây.']")
                )
            )
        except Exception:
            print("❌ Không tìm thấy ô nhập mô tả → chạy lại toàn hàm")
            if retry > 0:
                time.sleep(3)
                return upload_video(driver, tieude, asset_id, video, retry-1)
            return False

        driver.find_element(By.XPATH, "//*[text()='Thêm ảnh/video']").click()
        time.sleep(4)

        pyautogui.write(video)
        pyautogui.press("enter")

        time.sleep(60)
        Auto_tin()
        time.sleep(10)
        return True

    except Exception as e:
        print("❌ Lỗi không xác định:", e)
        if retry > 0:
            return upload_video(driver, tieude, asset_id, video, retry-1)
        return False

def comment_video(driver, tieude, asset_id, video, retry=3):

    url = f"https://business.facebook.com/latest/posts/published_posts/?asset_id={asset_id}"
    try:
        driver.get(url)
        driver.implicitly_wait(20)
        time.sleep(5)
        pyautogui.moveTo(500, 300, duration=0.2)
        pyautogui.click()
        driver.implicitly_wait(20)
        time.sleep(5)
        try:
            input_area = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@aria-label, 'Bình luận dưới tên')]")
                )
            )
        except Exception:
            print("❌ Không tìm thấy ô nhập mô tả → chạy lại toàn hàm")
            if retry > 0:
                time.sleep(3)
                return comment_video(driver, tieude, asset_id, video, retry-1)
            return False

        # =============== NHẬP MÔ TẢ ===============
        driver.execute_script("arguments[0].click();", input_area)
        ActionChains(driver).move_to_element(input_area).click().send_keys(tieude).perform()
        time.sleep(2)
        location = input_area.location
        size = input_area.size

        # Tính tọa độ giữa của ô comment
        x = location['x'] + size['width'] // 2
        y = location['y'] + size['height'] // 2

        # Di chuột bằng pyautogui tới đúng element rồi click
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()
        time.sleep(2)
        pyautogui.press("enter")

        time.sleep(60)
        return True

    except Exception as e:
        print("❌ Lỗi không xác định:", e)
        if retry > 0:
            return comment_video(driver, tieude, asset_id, None, retry-1)
        return False
