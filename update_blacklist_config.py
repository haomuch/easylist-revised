import requests

def update_config_file(url, new_rules, output_filename='优化版黑名单.conf'):
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
            # Modify the skip-proxy line
            if line.startswith("skip-proxy ="):
                if "www.baidu.com" not in line:
                    line += ", www.baidu.com"
                updated_lines.append(line)
            # Skip (delete) the specified line
            elif "DOMAIN-SUFFIX,microsoft.com,Proxy" in line:
                print("Found and removed 'DOMAIN-SUFFIX,microsoft.com,Proxy' rule.")
                continue  # This line will not be added to updated_lines
            # Skip (delete) the specified line
            elif "DOMAIN-SUFFIX,live.com,Proxy" in line:
                print("Found and removed 'DOMAIN-SUFFIX,live.com,Proxy' rule.")
                continue  # This line will not be added to updated_lines
            # Skip (delete) the specified line
            elif "DOMAIN-SUFFIX,api.onedrive.com,Proxy" in line:
                print("Found and removed 'DOMAIN-SUFFIX,api.onedrive.com,Proxy' rule.")
                continue  # This line will not be added to updated_lines
            # Skip (delete) the specified line
            elif "DOMAIN-SUFFIX,skyapi.live.net,Proxy" in line:
                print("Found and removed 'DOMAIN-SUFFIX,skyapi.live.net,Proxy' rule.")
                continue  # This line will not be added to updated_lines
            elif "DOMAIN-SUFFIX,odc.officeapps.live.com,Proxy" in line:
                print("Found and removed 'DOMAIN-SUFFIX,odc.officeapps.live.com,Proxy' rule.")
                continue  # This line will not be added to updated_lines
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
    
    # New rules to add
    rules_to_add = """DOMAIN-SUFFIX,akadns.net,DIRECT
DOMAIN-SUFFIX,cdn.apple-mapkit.com,DIRECT
DOMAIN-SUFFIX,apple.com,DIRECT
DOMAIN-SUFFIX,icloud.com,DIRECT
DOMAIN-SUFFIX,amazonaws.com.cn,DIRECT
DOMAIN-SUFFIX,in.appcenter.ms,DIRECT
DOMAIN-SUFFIX,pdst.fm,PROXY
DOMAIN-SUFFIX,feeds.megaphone.fm,PROXY
DOMAIN-SUFFIX,www.omnycontent.com,PROXY
DOMAIN-SUFFIX,dowjones.io,PROXY"""

    # Run the function
    update_config_file(config_url, rules_to_add)