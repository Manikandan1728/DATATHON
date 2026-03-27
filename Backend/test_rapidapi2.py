import time, requests, json, os, sys
sys.path.insert(0, '.')

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv('Backend/.env')
except Exception:
    pass

KEY = os.getenv("RAPIDAPI_KEY", "f4247235eamsh64865872ff73a85p1c57d0jsn48521b69a546")
print(f"Using key: {KEY[:20]}...")
print("Testing Real-Time Product Search API...")

r = requests.get(
    "https://real-time-product-search.p.rapidapi.com/search",
    headers={
        "X-RapidAPI-Key": KEY,
        "X-RapidAPI-Host": "real-time-product-search.p.rapidapi.com",
    },
    params={"q": "laptop", "country": "us", "language": "en", "limit": "5"},
    timeout=25,
)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    items = data.get("data", [])
    print(f"Products found: {len(items)}")
    for item in items[:5]:
        title = item.get("product_title", "?")
        price = "N/A"
        if item.get("typical_price_range"):
            price = item["typical_price_range"][0]
        rating = item.get("product_rating", "N/A")
        print(f"  - {title[:60]} | {price} | {rating}")
elif r.status_code == 403:
    print("Not subscribed - go to pricing tab and click Subscribe on Basic plan")
elif r.status_code == 429:
    print("Rate limited - quota hit, wait a minute")
else:
    print(f"Error: {r.text[:300]}")
