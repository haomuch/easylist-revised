import requests
import sys
import os
import traceback

URL = "https://easylist.to/easylist/easylist.txt"
REMOVE_KEYWORD = "||imasdk.googleapis.com^"  # 改成你要删除的内容
OUTPUT_FILE = "easylist.txt"

try:
    # 下载 EasyList
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    lines = response.text.splitlines()
    filtered_lines = [line for line in lines if REMOVE_KEYWORD not in line]

    # 如果文件存在且内容未变化，直接退出
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing_lines = f.read().splitlines()
        if existing_lines == filtered_lines:
            print("[INFO] 文件内容未变化，无需更新。")
            sys.exit(0)

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))
    print(f"[INFO] 文件 {OUTPUT_FILE} 已更新，删除了包含 '{REMOVE_KEYWORD}' 的行。")

except Exception:
    print("[ERROR] 脚本执行出错：")
    traceback.print_exc()
    # 返回非零会导致 Actions 失败，如果你希望失败可以保持 1，否则改为 0
    sys.exit(1)
