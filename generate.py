import urllib.request
import os
import yaml

# 从 Secrets 环境变量读取
uuid = os.environ.get('UUID', '').strip()
host = os.environ.get('CF_WORKER_HOST', '').strip()

# 抓取优选 IP 列表
url = 'https://raw.githubusercontent.com/ymyuuu/IPDB/main/bestcf.txt'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    ips = urllib.request.urlopen(req).read().decode('utf-8').splitlines()
except Exception as e:
    print(f"Fetch failed: {e}, using fallback IPs")
    ips = ['104.16.123.96', '104.19.146.22', '104.21.32.48', '172.67.121.23', '104.20.18.52']

valid_ips = [ip.strip() for ip in ips if ip.strip()][:30]

# 构建标准的 Python 数据结构，彻底避免语法与名称拼写不一致
proxies_list = []
proxy_names = []

for idx, ip in enumerate(valid_ips):
    # 统一命名规范
    node_name = f"Node-{idx+1}-{ip}"
    proxy_names.append(node_name)
    
    # 每一个节点的独立字典定义
    node_config = {
        'name': node_name,
        'type': 'vless',
        'server': ip,
        'port': 443,
        'uuid': uuid,
        'network': 'ws',
        'tls': True,
        'udp': True,
        'sni': host,
        'client-fingerprint': 'chrome',
        'ws-opts': {
            'path': '/',
            'headers': {
                'Host': host
            }
        }
    }
    proxies_list.append(node_config)

# 完整 Clash Meta 字典
clash_config = {
    'port': 7890,
    'socks-port': 7891,
    'allow-lan': True,
    'mode': 'rule',
    'log-level': 'info',
    'unified-delay': True,
    'dns': {
        'enable': True,
        'listen': '0.0.0.0:53',
        'default-nameserver': ['223.5.5.5', '114.114.114.114'],
        'nameserver': ['https://dns.alidns.com/dns-query', 'https://doh.pub/dns-query']
    },
    'proxies': proxies_list,
    'proxy-groups': [
        {
            'name': 'Auto-Select', # 使用无特殊字符的统一英文名称
            'type': 'url-test',
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300,
            'tolerance': 50,
            'proxies': proxy_names # 强关联，确保策略组引用的名称与节点完全一致
        }
    ],
    'rules': [
        'GEOIP,LAN,DIRECT',
        'GEOIP,CN,DIRECT',
        'MATCH,Auto-Select'
    ]
}

# 使用官方 PyYAML 进行格式化输出，严格确保缩进合规
with open('config.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)

print("config.yaml generated successfully via PyYAML!")
