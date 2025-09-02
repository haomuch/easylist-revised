import requests
import os

# 定义要删除的行内容（假设你想删除包含特定字符串的行）
REMOVE_PATTERN = "||imasdk.googleapis.com^"  # 替换为你想删除的行内容或模式

# 下载 EasyList 文件
def download_easylist(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        raise Exception("无法下载 EasyList 文件")

# 保存新文件
def save_file(lines, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def main():
    url = "https://easylist.to/easylist/easylist.txt"
    output_path = "easylist.txt"
    
    # 下载文件
    lines = download_easylist(url)
    
    # 过滤特定行
    filtered_lines = filter_lines(lines, REMOVE_PATTERN)
    
    # 保存修改后的文件
    save_file(filtered_lines, output_path)
    print(f"已生成过滤后的文件：{output_path}")

if __name__ == "__main__":
    main()
