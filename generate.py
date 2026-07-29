import os
import yaml

uuid = os.environ.get('UUID', '').strip()
host = os.environ.get('CF_WORKER_HOST', '').strip() # vless.ai-small.xyz

node_config = {
    'name': '直连节点-自定义域名',
    'type': 'vless',
    'server': host,               # 直接连接 vless.ai-small.xyz
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
    'proxies': [node_config],
    'proxy-groups': [
        {
            'name': 'Auto-Select',
            'type': 'select',
            'proxies': ['直连节点-自定义域名']
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
