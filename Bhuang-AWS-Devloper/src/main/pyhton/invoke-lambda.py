import requests
from requests.auth import HTTPBasicAuth

# 设置Splunk API的URL、用户名和密码
splunk_url = "<SPLUNK_URL>/services/search/jobs"
username = "<USERNAME>"
password = "<PASSWORD>"

# 设置查询字符串
query_string = "<QUERY_STRING>"

# 创建payload，指定要执行的搜索查询
payload = {
    'search': f'search {query_string}',
    'output_mode': 'json',
    'exec_mode': 'oneshot'  # 只执行一次
}

# 发送POST请求到Splunk API
response = requests.post(splunk_url, auth=HTTPBasicAuth(username, password), data=payload)

# 检查响应状态
if response.status_code == 200:
    # 打印返回的JSON数据
    print(response.json())
else:
    print(f"Error: {response.status_code} - {response.text}")
