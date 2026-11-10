import re
import urllib.request

# 待合并的规则源列表
RULE_URLS = [
    "https://filters.adtidy.org/extension/chromium/filters/2.txt",       # AdGuard Base
    "https://filters.adtidy.org/extension/chromium/filters/224.txt",     # AdGuard Chinese
    "https://filters.adtidy.org/extension/chromium/filters/11.txt",      # AdGuard Mobile Ads
    "https://filters.adtidy.org/extension/chromium/filters/15.txt",      # AdGuard DNS
    "https://raw.githubusercontent.com/cats-team/AdRules/main/dns.txt",    # AdRules DNS List
    "https://raw.githubusercontent.com/cjx896208/cjxlist/master/cjx-annoyance.txt", # CJX's Annoyance List
    "https://easylist.to/easylist/easylist.txt",                          # EasyList
    "https://easylist-downloads.adblockplus.org/easylistchina.txt",       # EasyList China
    "https://easylist.to/easylist/easyprivacy.txt",                       # EasyPrivacy
    "https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/mv.txt", # xinggsf mv
    "https://raw.githubusercontent.com/jiekouAD/ad/main/v.txt",           # jiekouAD
    "https://raw.githubusercontent.com/AWAvenue/AWAvenue-Adblock-Rule/main/AWAvenue-Adblock-Rule.txt", # AWAvenue
    "https://big.oisd.nl/basic",                                           # OISD Basic
    "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",    # StevenBlack hosts
    "https://raw.githubusercontent.com/jdlingyu/ad-wars/master/hosts",    # Pollock hosts
]

def fetch_and_extract_domains():
    domains = set()

    # 匹配规则正则：
    # 1. ABP/AdGuard 语法: ||example.com^
    # 2. Hosts 语法: 0.0.0.0 example.com 或 127.0.0.1 example.com
    # 3. 纯域名或 Surge DOMAIN/DOMAIN-SUFFIX 语法
    abp_pattern = re.compile(r"^\|\|([a-zA-Z0-9\.\-\_]+)\^")
    hosts_pattern = re.compile(r"^(?:0\.0\.0\.0|127\.0\.0\.1)\s+([a-zA-Z0-9\.\-\_]+)")
    domain_pattern = re.compile(r"^(?:DOMAIN-SUFFIX,|DOMAIN,)?([a-zA-Z0-9\.\-\_]+\.[a-zA-Z]{2,})$")

    for url in RULE_URLS:
        print(f"Fetching: {url}")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                lines = response.read().decode('utf-8', errors='ignore').splitlines()
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('!') or line.startswith('#') or line.startswith('['):
                        continue
                    
                    # 匹配 ||example.com^
                    m_abp = abp_pattern.match(line)
                    if m_abp:
                        domain = m_abp.group(1).lower()
                        if '.' in domain and not domain.startswith('.'):
                            domains.add(domain)
                        continue

                    # 匹配 Hosts
                    m_hosts = hosts_pattern.match(line)
                    if m_hosts:
                        domain = m_hosts.group(1).lower()
                        if domain != "localhost" and '.' in domain:
                            domains.add(domain)
                        continue

                    # 匹配直接域名或已知前缀
                    m_domain = domain_pattern.match(line)
                    if m_domain:
                        domain = m_domain.group(1).lower()
                        domains.add(domain)

        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

    return sorted(list(domains))

def save_surge_files(domains):
    # 1. 生成标准的 Surge RULE-SET (.list) 格式
    with open("surge_adblock_ruleset.list", "w", encoding="utf-8") as f:
        f.write("# Surge AdBlock Rule-Set (Merged & Deduplicated)\n")
        f.write(f"# Total Domains: {len(domains)}\n\n")
        for d in domains:
            f.write(f"DOMAIN-SUFFIX,{d}\n")

    # 2. 生成高性能的 Surge DOMAIN-SET (.list) 格式 (推荐)
    with open("surge_adblock_domainset.list", "w", encoding="utf-8") as f:
        f.write("# Surge DOMAIN-SET AdBlock Rules\n")
        f.write(f"# Total Domains: {len(domains)}\n\n")
        for d in domains:
            f.write(f".{d}\n")

if __name__ == "__main__":
    extracted_domains = fetch_and_extract_domains()
    print(f"Total Unique Domains Extracted: {len(extracted_domains)}")
    save_surge_files(extracted_domains)
