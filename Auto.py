import os
import json
import time
from datetime import datetime

from code_auto import (
    upload_tin,
    setup_driver
)

# ================= CONFIG =================
CURRENT_MAY = "1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_BASE = os.path.join(BASE_DIR, "Videos")

USED_JSON = os.path.join(BASE_DIR, "json", f"used_files_may_{CURRENT_MAY}.json")
COUNTER_JSON = os.path.join(BASE_DIR, "json", "counter.json")
ID_FILE = os.path.join(BASE_DIR, "ids.txt")

RUN_HOURS = [6, 9, 13, 15, 18, 21]
RUN_MINUTE = 25


# ================= LOAD IDS =================
def load_ids():
    if not os.path.exists(ID_FILE):
        return []
    with open(ID_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# ================= LOAD COUNTER =================
if os.path.exists(COUNTER_JSON):
    with open(COUNTER_JSON, "r", encoding="utf-8") as f:
        counters = json.load(f)
else:
    counters = {}


# ================= LOAD USED FILES =================
if os.path.exists(USED_JSON):
    with open(USED_JSON, "r", encoding="utf-8") as f:
        used_files = set(json.load(f))
else:
    used_files = set()


# ================= PICK FILE =================
def get_first_unused_file(folder):

    if not os.path.exists(folder):
        return None

    for f in os.listdir(folder):
        full = os.path.join(folder, f)

        if f.lower().endswith((".mp4", ".mov", ".jpg", ".png")) and full not in used_files:
            return full

    return None


# ================= MAIN =================
DRIVER = None
executed_hours = set()

print("🚀 START TOOL")

while True:

    now = datetime.now()

    if now.hour in RUN_HOURS and now.hour not in executed_hours and now.minute == RUN_MINUTE:

        print(f"\n🚀 CHẠY GIỜ {now.hour}")

        ids = load_ids()

        if DRIVER is None:
            DRIVER = setup_driver(int(CURRENT_MAY))

        for page_id in ids:

            # ===== lấy số hiện tại =====
            current_num = counters.get(page_id, 1)

            # ===== title =====
            title = f"Phim Số {current_num}! Tập 1"

            # ===== lấy video =====
            file = get_first_unused_file(VIDEO_BASE)

            if not file:
                print("❌ Hết video")
                break

            print(f"📤 Đăng ID {page_id} | {title}")

            success = upload_tin(
                DRIVER,
                title,
                page_id,
                file
            )

            if success:
                used_files.add(file)
                os.remove(file)

                # tăng số
                counters[page_id] = current_num + 1

                print("✅ OK:", title)

            else:
                print("❌ Lỗi:", file)
                used_files.add(file)
                os.remove(file)

        # ===== SAVE =====
        with open(USED_JSON, "w", encoding="utf-8") as f:
            json.dump(list(used_files), f, ensure_ascii=False, indent=2)

        with open(COUNTER_JSON, "w", encoding="utf-8") as f:
            json.dump(counters, f, ensure_ascii=False, indent=2)

        executed_hours.add(now.hour)

        if DRIVER:
            DRIVER.quit()
            DRIVER = None

        print(f"✅ XONG GIỜ {now.hour}")

    time.sleep(30)