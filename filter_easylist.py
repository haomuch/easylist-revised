import requests

# 下载源 EasyList
url = "https://easylist.to/easylist/easylist.txt"
r = requests.get(url)
r.raise_for_status()
lines = r.text.splitlines()

# 设置要删除的关键字
keyword = "||imasdk.googleapis.com^"  # 把这里改成你想删除的那一行的内容或关键字

# 过滤掉包含关键字的行
filtered = [line for line in lines if keyword not in line]

# 写入新文件
with open("easylist.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(filtered))
