import requests
import os
import traceback

URL = "https://easylist.to/easylist/easylist.txt"
REMOVE_KEYWORD = "||imasdk.googleapis.com^"  # 改成你需要删除的内容
OUTPUT_FILE = "easylist.txt"

try:
    # 下载 EasyList
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    lines = response.text.splitlines()
    filtered_lines = [line for line in lines if REMOVE_KEYWORD not in line]

    # 写入文件前判断文件是否存在和是否有变化
    write_file = True
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing_lines = f.read().splitlines()
        if existing_lines == filtered_lines:
            print("[INFO] 文件内容未变化，无需更新。")
            write_file = False

    if write_file:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(filtered_lines))
        print(f"[INFO] 文件 {OUTPUT_FILE} 已生成/更新，删除了包含 '{REMOVE_KEYWORD}' 的行。")
    else:
        print(f"[INFO] 文件 {OUTPUT_FILE} 已存在且内容未变化。")

except Exception:
    print("[ERROR] 脚本执行出错：")
    traceback.print_exc()
    # 出错也不让 workflow 失败
    exit(0)
