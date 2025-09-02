import requests
import os
from datetime import datetime

# EasyList 原文件 URL
EASYLIST_URL = "https://easylist.to/easylist/easylist.txt"
# 要删除的行
LINE_TO_REMOVE = "||imasdk.googleapis.com^"
# 输出文件名
OUTPUT_FILE = "modified_easylist.txt"

def fetch_easylist():
    """从 easylist.to 下载最新的 EasyList 文件"""
    try:
        response = requests.get(EASYLIST_URL)
        response.raise_for_status()  # 确保请求成功
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching EasyList: {e}")
        return None

def modify_easylist(content):
    """删除指定的行"""
    if content is None:
        return None
    lines = content.splitlines()
    modified_lines = [line for line in lines if line.strip() != LINE_TO_REMOVE]
    return "\n".join(modified_lines)

def save_file(content):
    """将修改后的内容保存到文件"""
    if content is None:
        return
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    # 获取 EasyList 文件
    easylist_content = fetch_easylist()
    if easylist_content:
        # 修改内容
        modified_content = modify_easylist(easylist_content)
        # 保存到文件
        save_file(modified_content)
        print(f"Modified EasyList saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
