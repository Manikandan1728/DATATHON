"""
Test multiple free RapidAPI product search APIs to find which works with your key.
Run this after subscribing to any of these on rapidapi.com
"""
import requests, json, time

KEY = "b88171c23mshd020129138e4f3ep1d1f24jsn5cf8962026fe"

tests = [
    {
        "name": "Real-Time Product Search",
        "url": "https://real-time-product-search.p.rapidapi.com/search",
        "host": "real-time-product-search.p.rapidapi.com",
        "params": {"q": "laptop", "country": "us", "language": "en", "limit": "3"},
    },
    {
        "name": "Amazon Product Search (axesso)",
        "url": "https://axesso-amazon-data-service.p.rapidapi.com/amz/amazon-search-by-keyword-asin",
        "host": "axesso-amazon-data-service.p.rapidapi.com",
        "params": {"keyword": "laptop", "page": "1", "domainCode": "com", "sortBy": "relevanceblender", "numberOfProducts": "3"},
    },
    {
        "name": "Amazon Data (cheap2)",
        "url": "https://amazon-product-data6.p.rapidapi.com/product-by-text",
        "host": "amazon-product-data6.p.rapidapi.com",
        "params": {"query": "laptop", "page": "1", "country": "US"},
    },
    {
        "name": "Walmart Product Data",
        "url": "https://walmart-product-data.p.rapidapi.com/search",
        "host": "walmart-product-data.p.rapidapi.com",
        "params": {"query": "laptop"},
    },
]

for t in tests:
    try:
        r = requests.get(
            t["url"],
            headers={"X-RapidAPI-Key": KEY, "X-RapidAPI-Host": t["host"]},
            params=t["params"],
            timeout=12,
        )
        status = r.status_code
        if status == 200:
            print(f"SUCCESS: {t['name']} - {status}")
            data = r.json()
            print(f"  Response keys: {list(data.keys())[:5]}")
        elif status == 403:
            print(f"NOT SUBSCRIBED: {t['name']}")
        elif status == 429:
            print(f"RATE LIMITED (subscribed but quota hit): {t['name']}")
        else:
            print(f"ERROR {status}: {t['name']} - {r.text[:80]}")
    except Exception as e:
        print(f"EXCEPTION: {t['name']} - {e}")
    time.sleep(1)
