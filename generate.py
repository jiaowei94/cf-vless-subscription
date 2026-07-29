import urllib.request
import os

uuid = os.environ.get('UUID', '').strip()
host = os.environ.get('CF_WORKER_HOST', '').strip()

url = 'https://raw.githubusercontent.com/ymyuuu/IPDB/main/bestcf.txt'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    ips = urllib.request.urlopen(req).read().decode('utf-8').splitlines()
except Exception as e:
    print(f"Fetch failed: {e}, using fallback IPs")
    ips = ['104.16.123.96', '104.19.146.22', '104.21.32.48', '172.67.121.23', '104.20.18.52']

valid_ips = [ip.strip() for ip in ips if ip.strip()][:30]

lines = [
    "port: 7890",
    "socks-port: 7891",
    "allow-lan: true",
    "mode: rule",
    "log-level: info",
    "unified-delay: true",
    "dns:",
    "  enable: true",
    "  listen: 0.0.0.0:53",
    "  default-nameserver: [223.5.5.5, 114.114.114.114]",
    "  nameserver: [https://dns.alidns.com/dns-query, https://doh.pub/dns-query]",
    "proxies:"
]

proxy_names = []
for idx, ip in enumerate(valid_ips):
    name = f"优选IP-{idx+1}-{ip}"
    proxy_names.append(name)
    lines.append(f"  - name: '{name}'")
    lines.append("    type: vless")
    lines.append(f"    server: {ip}")
    lines.append("    port: 443")
    lines.append(f"    uuid: {uuid}")
    lines.append("    network: ws")
    lines.append("    tls: true")
    lines.append("    udp: true")
    lines.append(f"    sni: {host}")
    lines.append("    client-fingerprint: chrome")
    lines.append("    ws-opts:")
    lines.append("      path: '/'")
    lines.append("      headers:")
    lines.append(f"        Host: {host}")

lines.append("proxy-groups:")
lines.append("  - name: 🚀 自动选路")
lines.append("    type: url-test")
lines.append("    url: http://www.gstatic.com/generate_204")
lines.append("    interval: 300")
lines.append("    tolerance: 50")
lines.append("    proxies:")

for name in proxy_names:
    lines.append(f"      - '{name}'")

lines.append("rules:")
lines.append("  - GEOIP,LAN,DIRECT")
lines.append("  - GEOIP,CN,DIRECT")
lines.append("  - MATCH,🚀 自动选路")

with open('config.yaml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("config.yaml generated successfully!")
