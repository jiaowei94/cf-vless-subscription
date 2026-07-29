import os
import yaml

uuid = os.environ.get('UUID', '').strip()
host = os.environ.get('CF_WORKER_HOST', '').strip() # vless.ai-small.xyz

# 使用 Cloudflare 原生支持的 2053 备用端口，避开 443 端口拦截
port = 2053

# 精选优质 Anycast IP 与备用节点
nodes_list = [
    {'name': '备用端口-直连域名', 'server': cf.090227.xyz},
    {'name': '备用端口-IP-1', 'server': '104.21.80.1'},
    {'name': '备用端口-IP-2', 'server': '172.67.200.1'},
    {'name': '备用端口-IP-3', 'server': '162.159.192.1'},
    {'name': '备用端口-域名-Visa', 'server': 'visa.cn'}
]

proxies_list = []
proxy_names = []

for idx, item in enumerate(nodes_list):
    node_name = f"Node-{idx+1}-{item['name']}"
    proxy_names.append(node_name)
    
    node_config = {
        'name': node_name,
        'type': 'vless',
        'server': item['server'],
        'port': port,                  # 改用 2053 端口
        'uuid': uuid,
        'network': 'ws',
        'tls': True,
        'udp': True,
        'servername': host,
        'sni': host,
        'skip-cert-verify': True,
        'client-fingerprint': 'chrome',
        'ws-opts': {
            'path': '/',
            'headers': {
                'Host': host
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
            'type': 'select',
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

print("Updated config.yaml with port 2053 successfully!")
