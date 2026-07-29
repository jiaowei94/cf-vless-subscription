import os
import yaml

uuid = os.environ.get('UUID', '').strip()
host = os.environ.get('CF_WORKER_HOST', '').strip() # vless.ai-small.xyz

# 社区优质的 Cloudflare 反代中转 IP/域名列表
reverse_proxy_nodes = [
    {'name': '反代域名-01', 'server': 'cf.090227.xyz'},
    {'name': '反代IP-02', 'server': '104.21.80.1'},
    {'name': '反代IP-03', 'server': '172.67.200.1'},
    {'name': '反代IP-04', 'server': '104.16.123.96'},
    {'name': '直连域名-05', 'server': host}
]

proxies_list = []
proxy_names = []

for idx, item in enumerate(reverse_proxy_nodes):
    node_name = f"Node-{idx+1}-{item['name']}"
    proxy_names.append(node_name)
    
    node_config = {
        'name': node_name,
        'type': 'vless',
        'server': item['server'],        # 连接反代 IP 避开 GFW 阻断
        'port': 443,
        'uuid': uuid,
        'network': 'ws',
        'tls': True,
        'udp': True,
        'servername': host,             # SNI 指向你的自定义域名
        'sni': host,
        'skip-cert-verify': True,
        'client-fingerprint': 'chrome',
        'ws-opts': {
            'path': '/?ed=2048',         # 社区 Padding 抗封锁路径
            'headers': {
                'Host': host            # Host 指向你的自定义域名
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
            'type': 'select',          # 手动选择模式
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

print("Updated config with edgetunnel reverse proxy successfully!")
