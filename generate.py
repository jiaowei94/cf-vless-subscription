import os
import yaml

uuid = os.environ.get('UUID', '').strip()
host = os.environ.get('CF_WORKER_HOST', '').strip() # vless.ai-small.xyz

# 优选国内访问最顺畅的 Cloudflare 节点 IP
cf_ips = [
    '104.16.123.96',
    '104.19.146.22',
    '104.20.18.52',
    '172.67.121.23',
    '162.159.192.1'
]

proxies_list = []
proxy_names = []

# 1. 添加一个直连域名节点
proxies_list.append({
    'name': 'Node-0-vless.ai-small.xyz',
    'type': 'vless',
    'server': host,
    'port': 443,
    'uuid': uuid,
    'network': 'ws',
    'tls': True,
    'udp': True,
    'sni': host,
    'skip-cert-verify': True, # 强制跳过证书校验，解决 TLS 握手阻断
    'client-fingerprint': 'chrome',
    'ws-opts': {
        'path': '/',
        'headers': {
            'Host': host
        }
    }
})
proxy_names.append('Node-0-vless.ai-small.xyz')

# 2. 添加优选 IP 节点（固定 SNI 为你的自定义域名）
for idx, ip in enumerate(cf_ips):
    node_name = f"Node-{idx+1}-{ip}"
    proxy_names.append(node_name)
    proxies_list.append({
        'name': node_name,
        'type': 'vless',
        'server': ip,
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
    })

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
