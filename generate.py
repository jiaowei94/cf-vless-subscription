import os
import yaml

# 从环境变量获取，确保去除空格
uuid = os.environ.get('UUID', '').strip()
host = os.environ.get('CF_WORKER_HOST', '').strip()

# 整理精选的 Cloudflare 国内优质节点/域名
best_nodes = [
    '104.16.123.96',
    '104.19.146.22',
    '104.16.160.1',
    '172.67.180.1',
    '162.159.192.1',
    'visa.cn'
]

proxies_list = []
proxy_names = []

for idx, node in enumerate(best_nodes):
    node_name = f"Node-{idx+1}-{node}"
    proxy_names.append(node_name)
    
    node_config = {
        'name': node_name,
        'type': 'vless',
        'server': node,
        'port': 443,
        'uuid': uuid,
        'network': 'ws',
        'tls': True,
        'udp': True,
        'sni': host,                   # 必须为 vless.ai-small.xyz
        'skip-cert-verify': False,      # 既然用了正常域名，可以设为 False
        'client-fingerprint': 'chrome',
        'ws-opts': {
            'path': '/',
            'headers': {
                'Host': host            # 必须为 vless.ai-small.xyz
            }
        }
    }
    proxies_list.append(node_config)

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
            'name': 'Auto-Select',
            'type': 'url-test',
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300,
            'tolerance': 50,
            'proxies': proxy_names
        }
    ],
    'rules': [
        'GEOIP,LAN,DIRECT',
        'GEOIP,CN,DIRECT',
        'MATCH,Auto-Select'
    ]
}

with open('config.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)

print("Updated config.yaml with custom domain successfully!")
