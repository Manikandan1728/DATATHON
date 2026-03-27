"""
Finds which RapidAPI product search APIs your key can access.
Tests a broad list of free product search APIs.
"""
import requests, time

KEY = "b88171c23mshd020129138e4f3ep1d1f24jsn5cf8962026fe"

# Comprehensive list of free product search APIs on RapidAPI
apis = [
    # Real-Time Product Search variants
    ("real-time-product-search.p.rapidapi.com",
     "https://real-time-product-search.p.rapidapi.com/search",
     {"q": "laptop", "country": "us", "language": "en"}),

    # Amazon APIs
    ("amazon-product-data2.p.rapidapi.com",
     "https://amazon-product-data2.p.rapidapi.com/product-search",
     {"query": "laptop", "country": "US"}),

    ("real-time-amazon-data.p.rapidapi.com",
     "https://real-time-amazon-data.p.rapidapi.com/search",
     {"query": "laptop", "country": "US", "category_id": "aps"}),

    ("amazon-products5.p.rapidapi.com",
     "https://amazon-products5.p.rapidapi.com/search",
     {"query": "laptop", "country": "US"}),

    # Google Shopping
    ("google-shopping1.p.rapidapi.com",
     "https://google-shopping1.p.rapidapi.com/search",
     {"q": "laptop"}),

    # General product search
    ("product-search-and-discovery.p.rapidapi.com",
     "https://product-search-and-discovery.p.rapidapi.com/search",
     {"q": "laptop"}),

    ("cheap-products.p.rapidapi.com",
     "https://cheap-products.p.rapidapi.com/products",
     {"q": "laptop"}),

    # eBay
    ("ebay-search-result.p.rapidapi.com",
     "https://ebay-search-result.p.rapidapi.com/search/laptop",
     {}),

    # Walmart
    ("walmart.p.rapidapi.com",
     "https://walmart.p.rapidapi.com/",
     {"query": "laptop"}),
]

print(f"Testing {len(apis)} APIs with your key...\n")
for host, url, params in apis:
    try:
        r = requests.get(
            url,
            headers={"X-RapidAPI-Key": KEY, "X-RapidAPI-Host": host},
            params=params,
            timeout=10,
        )
        if r.status_code == 200:
            print(f"✓ WORKS: {host}")
            try:
                d = r.json()
                print(f"  Keys: {list(d.keys())[:4]}")
            except Exception:
                print(f"  Response: {r.text[:80]}")
        elif r.status_code == 429:
            print(f"✓ SUBSCRIBED (rate limited): {host}")
        elif r.status_code == 403:
            print(f"✗ Not subscribed: {host}")
        else:
            print(f"? {r.status_code}: {host} - {r.text[:60]}")
    except Exception as e:
        print(f"! Error: {host} - {str(e)[:50]}")
    time.sleep(0.5)

print("\nDone. Subscribe to any ✓ WORKS API above on rapidapi.com")
