import requests

# 提取需要移除的规则列表，方便后续维护和阅读
RULES_TO_REMOVE = [
    "DOMAIN-SUFFIX,microsoft.com,Proxy",
    "DOMAIN-SUFFIX,live.com,Proxy",
    "DOMAIN-SUFFIX,api.onedrive.com,Proxy",
    "DOMAIN-SUFFIX,skyapi.live.net,Proxy",
    "DOMAIN-SUFFIX,odc.officeapps.live.com,Proxy",
    "DOMAIN-SUFFIX,cdn.apple-mapkit.com,Proxy",
    "DOMAIN-SUFFIX,apple.news,Proxy",
    "DOMAIN-SUFFIX,bl.com,Proxy",
    "DOMAIN-SUFFIX,globalsign.com,Proxy",
    "DOMAIN-SUFFIX,onedrive.com,Proxy",
    "DOMAIN-SUFFIX,onedrive.live.com,Proxy",
    "DOMAIN-SUFFIX,mobile.pipe.aria.microsoft.com,Proxy",
    "DOMAIN-SUFFIX,vortex.data.microsoft.com,Proxy",
    "DOMAIN-SUFFIX,in.appcenter.ms,Proxy",
    "DOMAIN-SUFFIX,spotify.com,Proxy"
]

# 新增规则列表，方便统一管理
RULES_TO_ADD = """DOMAIN-SUFFIX,spotify.com,DIRECT
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
DOMAIN-SUFFIX,dowjones.io,PROXY"""

def update_config_file(url, new_rules, output_filename='optimized_blacklist.conf'):
    """
    Downloads a configuration file, applies modifications, and saves the updated file.

    Args:
        url (str): The URL of the configuration file to download.
        new_rules (str): A string containing the new rules to add.
        output_filename (str): The name of the file to save the updated content.
    """
    try:
        # Step 1: Download the content from the URL
        print(f"Downloading file from {url}...")
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        original_content = response.text
        lines = original_content.splitlines()
        updated_lines = []

        # Step 2: Process each line to apply modifications
        for line in lines:
            # 优先检查是否需要移除该行，简化后续逻辑
            if any(rule in line for rule in RULES_TO_REMOVE):
                continue

            # Modify the skip-proxy line
            elif line.startswith("skip-proxy ="):
                if "www.baidu.com" not in line:
                    line += ", www.baidu.com"
                updated_lines.append(line)
            # Modify the MITM line
            elif line.startswith("hostname ="):
                original_line = line
                # 移除 *.googlevideo.com
                if ",*.googlevideo.com" in line:
                    line = line.replace(",*.googlevideo.com", "")
    
                print("Modified hostname line to change MITM rules.")
                updated_lines.append(line)
            # Modify dns-server line
            elif line.startswith("dns-server ="):
                if "https://dns.alidns.com/dns-query, https://doh.pub/dns-query" in line:
                    line = "dns-server ="
                    print("Modified dns-server line to remove DNS servers.")
                updated_lines.append(line)
            # Modify ipv6 line
            elif line.startswith("ipv6 ="):
                if "false" in line:
                    line = "ipv6 = true"
                    print("Modified ipv6 line from false to true.")
                updated_lines.append(line)
            # Add other lines as they are
            else:
                updated_lines.append(line)

        # Re-join the lines to get the updated content
        processed_content = "\n".join(updated_lines)

        # Step 3: Find the insertion point and add the new rules
        insertion_point = "[Rule]"
        
        if insertion_point in processed_content:
            parts = processed_content.split(insertion_point, 1)
            final_content = parts[0] + insertion_point + "\n" + new_rules + "\n" + parts[1]
        else:
            print("Warning: '[Rule]' section not found. Appending rules to the end.")
            final_content = processed_content + "\n" + new_rules
            
        # Step 4: Save the updated content to a new file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"Successfully created and saved the updated file to {output_filename}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during download: {e}")
    except IOError as e:
        print(f"An error occurred while writing the file: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    # URL of the configuration file you want to download
    config_url = "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_banlist.conf"

    # Run the function
    update_config_file(config_url, RULES_TO_ADD)
