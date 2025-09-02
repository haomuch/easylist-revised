import requests
import sys
import os

# 源 EasyList 链接
URL = "https://easylist.to/easylist/easylist.txt"

# 要删除的内容/关键字，可以改成你需要的内容
REMOVE_KEYWORD = "||imasdk.googleapis.com^"

# 输出文件名
OUTPUT_FILE = "easylist.txt"

try:
    # 下载源 EasyList
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
except Exception as e:
    print(f"[ERROR] 下载 EasyList 失败: {e}")
    sys.exit(1)

# 按行拆分
lines = response.text.splitlines()

# 删除包含 REMOVE_KEYWORD 的行
filtered_lines = [line for line in lines if REMOVE_KEYWORD not in line]

# 检查输出文件是否已存在，以及内容是否有变化
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        existing = f.read().splitlines()
    if existing == filtered_lines:
        print("[INFO] 文件内容未变化，无需更新。")
        sys.exit(0)

# 写入新文件
try:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))
    print(f"[INFO] 文件 {OUTPUT_FILE} 已更新，删除了包含 '{REMOVE_KEYWORD}' 的行。")
except Exception as e:
    print(f"[ERROR] 写入文件失败: {e}")
    sys.exit(1)
