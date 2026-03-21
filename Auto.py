import os
import json
import time
from datetime import datetime

from code_auto import (
    upload_tin,
    setup_driver
)


# ================= MÁY HIỆN TẠI =================
CURRENT_MAY = "1"

# ================= SHEET =================
sheet_name = "lich"
RUN_MINUTE = 0

# ================= CONFIG =================
BASE_DIR = r"\\vmware-host\Shared Folders\Auto"

JSON_DIR = os.path.join(BASE_DIR, "json")
VIDEO_BASE = os.path.join(BASE_DIR, "Videos")

LICH_JSON = os.path.join(JSON_DIR, f"{sheet_name}.json")
USED_JSON = os.path.join(JSON_DIR, f"used_files_may_{CURRENT_MAY}.json")


# ================= LOAD USED FILES =================
if os.path.exists(USED_JSON):
    with open(USED_JSON, "r", encoding="utf-8") as f:
        used_files = set(json.load(f))
else:
    used_files = set()


# ================= LOAD SCHEDULE =================
def load_schedule():
    if not os.path.exists(LICH_JSON):
        return {}
    with open(LICH_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


schedule = load_schedule()


# ================= PICK FILE =================
def get_first_unused_file(base_dir, folder, exts):

    if not folder:
        return None

    path = os.path.join(base_dir, folder)

    if not os.path.exists(path):
        return None

    for f in os.listdir(path):

        full = os.path.join(path, f)

        if f.lower().endswith(exts) and full not in used_files:
            return full

    return None


# ================= DRIVER =================
DRIVER = None

executed_hours = set()
last_refresh_hour = None

print(f"🚀 KHỞI ĐỘNG MÁY {CURRENT_MAY}")


# ================= MAIN LOOP =================
while True:

    now = datetime.now()
    hour_key = str(now.hour)

    if hour_key in schedule and hour_key not in executed_hours and now.minute == RUN_MINUTE:

        print(f"\n🚀 [MÁY {CURRENT_MAY}] ĐANG CHẠY GIỜ {hour_key}")

        posts = schedule[hour_key]

        # ===== MỞ DRIVER KHI CẦN =====
        if DRIVER is None:
            print("🌐 MỞ DRIVER")
            DRIVER = setup_driver(int(CURRENT_MAY))


        # ===== TIN =====
        for t in posts.get("tin", []):

            if t.get("may") != CURRENT_MAY:
                continue

            while True:

                file = get_first_unused_file(
                    VIDEO_BASE,
                    t["folder"],
                    (".mp4", ".mov", ".jpg", ".png")
                )

                if not file:
                    print("❌ Hết file để đăng TIN")
                    break

                success = upload_tin(
                    DRIVER,
                    t["title"],
                    t["page_id"],
                    file
                )

                if success:

                    used_files.add(file)

                    print("📢 TIN OK:", file)

                    os.remove(file)

                    break

                else:
                    print("⚠️ Upload lỗi -> thử file khác:", file)
                    os.remove(file)
                    used_files.add(file)


        # ===== SAVE USED FILES =====
        with open(USED_JSON, "w", encoding="utf-8") as f:
            json.dump(list(used_files), f, ensure_ascii=False, indent=2)


        executed_hours.add(hour_key)

        print(f"✅ [MÁY {CURRENT_MAY}] XONG GIỜ {hour_key}")


        # ===== TẮT DRIVER SAU KHI CHẠY =====
        if DRIVER:
            print("🔻 ĐÓNG DRIVER")
            DRIVER.quit()
            DRIVER = None


    time.sleep(30)