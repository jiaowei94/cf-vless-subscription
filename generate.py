import os
import yaml

uuid = os.environ.get('UUID', '').strip()
host = os.environ.get('CF_WORKER_HOST', '').strip()

# 尝试多个 Cloudflare 托管节点与通用 IP
best_nodes = [
    '1.1.1.1',
    '1.0.0.1',
    '104.16.123.96',
    '104.19.146.22',
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

print("Updated config.yaml successfully!")
