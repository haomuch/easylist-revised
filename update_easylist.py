import sys
import requests

# EasyList 原文件 URL
EASYLIST_URL = "https://easylist.to/easylist/easylist.txt"
# 要删除的规则列表（采用 Set 结构以提高检索效率，并方便后续扩充）
RULES_TO_REMOVE = {
    "||imasdk.googleapis.com^"
}
# 输出文件名
OUTPUT_FILE = "modified_easylist.txt"
# 常见的浏览器 User-Agent，防止请求被 CDN 或源站拦截
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_easylist():
    """从 easylist.to 下载最新的 EasyList 文件"""
    try:
        print(f"Downloading EasyList from {EASYLIST_URL}...")
        # 增加 timeout (15秒) 防止网络无响应导致 GitHub Actions 工作流死锁挂起
        # 增加 headers 模拟浏览器请求，提升下载成功率
        response = requests.get(EASYLIST_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()  # 确保请求成功 (2xx 状态码)
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching EasyList: {e}", file=sys.stderr)
        # 发生网络/HTTP异常时，以非零状态码退出，确保 GitHub Actions 能捕获失败并报警
        sys.exit(1)

def modify_easylist(content):
    """删除指定的行"""
    if not content:
        return None
    
    # 内容安全校验。若下载内容太小或不包含 EasyList 特征头，拒绝写入以防覆盖导致规则丢失
    if "[Adblock Plus]" not in content and "! Homepage:" not in content:
        print("Error: The downloaded content does not seem to be a valid EasyList file.", file=sys.stderr)
        sys.exit(1)
        
    lines = content.splitlines()
    
    # 对过滤规则进行首尾空格的归一化处理
    normalized_remove_rules = {rule.strip() for rule in RULES_TO_REMOVE}
    
    modified_lines = []
    removed_count = 0
    for line in lines:
        # 精确首尾去空匹配，提高过滤鲁棒性
        if line.strip() in normalized_remove_rules:
            removed_count += 1
            continue
        modified_lines.append(line)
        
    print(f"Removed {removed_count} matched rules.")
    return "\n".join(modified_lines)

def save_file(content):
    """将修改后的内容保存到文件"""
    if not content:
        return
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Modified EasyList saved to {OUTPUT_FILE}")
    except IOError as e:
        print(f"Error saving file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    # 获取 EasyList 文件
    easylist_content = fetch_easylist()
    # 修改内容
    modified_content = modify_easylist(easylist_content)
    # 保存到文件
    save_file(modified_content)

if __name__ == "__main__":
    main()
