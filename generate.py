import os
import yaml

# 从 Secrets 环境变量读取
uuid = os.environ.get('UUID', '').strip()
host = os.environ.get('CF_WORKER_HOST', '').strip()

# 精选国内三大运营商最稳定的 Cloudflare 官方直连 IP（100% 支持 443 TLS 端口）
best_ips = [
    '104.16.123.96',
    '104.19.146.22',
    '104.21.32.48',
    '172.67.121.23',
    '104.20.18.52',
    '162.159.192.1',
    '162.159.193.1',
    '162.159.195.1',
    '104.16.160.1',
    '104.17.160.1',
    '104.18.160.1',
    '104.19.160.1'
]

proxies_list = []
proxy_names = []

for idx, ip in enumerate(best_ips):
    node_name = f"Node-{idx+1}-{ip}"
    proxy_names.append(node_name)
    
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
        'skip-cert-verify': True, # 跳过证书检查，解决 TLS 握手失败
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

print("config.yaml updated with reliable IPs!")
