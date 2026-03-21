import undetected_chromedriver as uc
import os
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def open_profile(i, website_url):
    json_file = f"./facebook/profile_{i}.json"
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            config = json.load(file)

        user_agent = config["user_agent"]
        vendor = config["vendor"]
        renderer = config["renderer"]

        profile_path = os.path.abspath(f"./facebook_data/profile_{i}")

        options = uc.ChromeOptions()
        #options.add_argument("--start-fullscreen")
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-position=0,0")

        driver = uc.Chrome(
            options=options,
            version_main=145,      # 👈 ÉP CHROMEDRIVER 144
            use_subprocess=True
        )
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})

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
        }})();
        """
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_script})

        driver.get(website_url)
        driver.implicitly_wait(10)
        time.sleep(100000)
        driver.quit()
    except Exception as e:
        print(f"Đã xảy ra lỗi với profile_{i}: {e}")


open_profile(1, f"https://www.facebook.com/")