##Cache.py
cache = {}

def get_cached_response(url):
    if url in cache:
        print(f"Cache HIT for {url}")
        return cache[url]
    print(f"Cache MISS for {url}")
    return None

def cache_response(url, response):
    cache[url] = response
    print(f"Cached response for {url}")
