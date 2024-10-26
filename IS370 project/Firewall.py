blocked_domains = ["blockedwebsite.com"]

def is_blocked(url):
    return any(domain in url for domain in blocked_domains)
