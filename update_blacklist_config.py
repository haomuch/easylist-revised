import sys
import requests

# 提取需要移除的规则列表，转为集合 (Set) 以提高匹配效率
RULES_TO_REMOVE = {
    "DOMAIN-SUFFIX,microsoft.com,Proxy",
    "DOMAIN-SUFFIX,live.com,Proxy",
    "DOMAIN-SUFFIX,api.onedrive.com,Proxy",
    "DOMAIN-SUFFIX,skyapi.live.net,Proxy",
    "DOMAIN-SUFFIX,odc.officeapps.live.com,Proxy",
    "DOMAIN-SUFFIX,cdn.apple-mapkit.com,Proxy",
    "DOMAIN-SUFFIX,apple.news,Proxy",
    "DOMAIN-SUFFIX,apps.mzstatic.com,Proxy",
    "DOMAIN-SUFFIX,bl.com,Proxy",
    "DOMAIN-KEYWORD,amazon,Proxy",
    "DOMAIN-KEYWORD,aws,Proxy",
    "DOMAIN-SUFFIX,cachefly.net,Proxy",
    "DOMAIN-SUFFIX,globalsign.com,Proxy",
    "DOMAIN-SUFFIX,onedrive.com,Proxy",
    "DOMAIN-SUFFIX,onedrive.live.com,Proxy",
    "DOMAIN-SUFFIX,mobile.pipe.aria.microsoft.com,Proxy",
    "DOMAIN-SUFFIX,vortex.data.microsoft.com,Proxy",
    "DOMAIN-SUFFIX,sidestore.io,Proxy",
    "DOMAIN-SUFFIX,tencent.com,Proxy",
    "DOMAIN-SUFFIX,in.appcenter.ms,Proxy"
}

# 新增规则列表
RULES_TO_ADD = """
DOMAIN-SUFFIX,akadns.net,DIRECT
DOMAIN-SUFFIX,apple.com,DIRECT
DOMAIN-SUFFIX,apple-dns.net,DIRECT
DOMAIN-SUFFIX,icloud.com,DIRECT
DOMAIN-SUFFIX,bing.com,DIRECT
DOMAIN-SUFFIX,amazonaws.com.cn,DIRECT
DOMAIN-SUFFIX,pdst.fm,PROXY
DOMAIN-SUFFIX,megaphone.fm,PROXY
DOMAIN-SUFFIX,omnycontent.com,PROXY
DOMAIN-SUFFIX,mc.tritondigital.com,PROXY
DOMAIN-SUFFIX,tracking.swap.fm,PROXY
DOMAIN-SUFFIX,podtrac.com,PROXY
DOMAIN-SUFFIX,chrt.fm,PROXY
DOMAIN-SUFFIX,files.oaiusercontent.com,PROXY
DOMAIN-SUFFIX,grokipedia.com,PROXY
DOMAIN-SUFFIX,gitflic.ru,PROXY
DOMAIN-SUFFIX,mushroomtrack.com,PROXY
DOMAIN-SUFFIX,dowjones.io,PROXY"""

def update_config_file(url, new_rules, output_filename='optimized_blacklist.conf'):
    """
    Downloads a configuration file, applies modifications, and saves the updated file.
    """
    try:
        # Step 1: 下载文件
        print(f"Downloading file from {url}...")
        # 优化点 1: 增加 timeout 防止网络挂起导致 Actions 任务卡死
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        original_content = response.text
        lines = original_content.splitlines()
        updated_lines = []
        removed_count = 0

        # 将要移除的规则做去空格的归一化处理，提高匹配鲁棒性
        normalized_remove_rules = {r.strip().replace(" ", "").lower() for r in RULES_TO_REMOVE}

        # Step 2: 逐行处理并应用修改
        for line in lines:
            stripped_line = line.strip()
            
            # 跳过空行或纯注释
            if not stripped_line:
                updated_lines.append(line)
                continue
                
            # 优化点 2: 归一化后比对，避免因为大小写或多余空格导致过滤失效
            normalized_line = stripped_line.replace(" ", "").lower()
            if normalized_line in normalized_remove_rules:
                removed_count += 1
                continue

            # 优化点 3: 键值对健壮解析，防止等号两边空格格式变化导致无法匹配
            if '=' in stripped_line:
                key, val = [part.strip() for part in stripped_line.split('=', 1)]
                
                # 修改 skip-proxy 这一行
                if key == "skip-proxy":
                    # 拆分成列表进行精确的 `in` 查重，避免子串误判
                    items = [item.strip() for item in val.split(',')]
                    domains_to_add = [
                        "www.baidu.com",
                        "*.apple.com",
                        "kdns.fr",
                        "foxhulio.site",
                        "eastmoney.com",
                        "*.mzstatic.com"
                    ]
                    for domain in domains_to_add:
                        if domain not in items:
                            items.append(domain)
                    line = f"skip-proxy = {', '.join(items)}"
                    updated_lines.append(line)
                    
                # 修改 hostname 这一行
                elif key == "hostname":
                    # 拆分成列表过滤，完美解决首位、末位逗号替换问题
                    items = [item.strip() for item in val.split(',')]
                    original_len = len(items)
                    items = [item for item in items if item != "*.googlevideo.com"]
                    if len(items) != original_len:
                        print("Modified hostname line to remove *.googlevideo.com.")
                    line = f"hostname = {', '.join(items)}"
                    updated_lines.append(line)
                    
                # 修改 dns-server 这一行
                elif key == "dns-server":
                    if "dns.alidns.com" in val and "doh.pub" in val:
                        line = "dns-server = system"
                        print("Modified dns-server line to remove DNS servers.")
                    updated_lines.append(line)
                    
                # 修改 ipv6 这一行
                elif key == "ipv6":
                    if val.lower() == "false":
                        line = "ipv6 = true"
                        print("Modified ipv6 line from false to true.")
                    updated_lines.append(line)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # 重新组合修改后的行
        processed_content = "\n".join(updated_lines)

        if removed_count > 0:
            print(f"Successfully removed {removed_count} RULES_TO_REMOVE entries.")

        # Step 3: 查找插入点并添加新规则
        insertion_point = "[Rule]"
        
        # 忽略大小写查找段落
        idx = processed_content.lower().find(insertion_point.lower())
        if idx != -1:
            # 获取原文本中实际的大小写形式（保持兼容性）
            actual_insertion = processed_content[idx:idx+len(insertion_point)]
            parts = processed_content.split(actual_insertion, 1)
            final_content = parts[0] + actual_insertion + "\n" + new_rules.strip() + "\n" + parts[1]
            print("Successfully inserted new rules into the '[Rule]' section.")
        else:
            print("Warning: '[Rule]' section not found. Appending rules to the end.")
            final_content = processed_content + "\n" + new_rules.strip()
            
        # Step 4: 保存更新后的文件
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"Successfully created and saved the updated file to {output_filename}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during download: {e}", file=sys.stderr)
        # 优化点 4: 异常时非零退出，确保 GitHub Action 能检测到工作流失败并报警
        sys.exit(1)
    except IOError as e:
        print(f"An error occurred while writing the file: {e}", file=sys.stderr)
        sys.exit(1)

# --- Example Usage ---
if __name__ == "__main__":
    config_url = "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_banlist.conf"
    update_config_file(config_url, RULES_TO_ADD)
