import requests, time

KEY = "f4247235eamsh64865872ff73a85p1c57d0jsn48521b69a546"
HOST = "real-time-product-search.p.rapidapi.com"
BASE = f"https://{HOST}"

# Try all known endpoint paths for this API
endpoints = [
    ("/search", {"q": "laptop", "country": "us", "language": "en"}),
    ("/product-search", {"q": "laptop", "country": "us", "language": "en"}),
    ("/products/search", {"q": "laptop", "country": "us"}),
    ("/search-v2", {"q": "laptop", "country": "us", "language": "en"}),
    ("/product/search", {"q": "laptop"}),
    ("/v2/search", {"q": "laptop", "country": "us"}),
    ("/search-light", {"q": "laptop", "country": "us", "language": "en"}),
]

print(f"Testing endpoints on {HOST}...\n")
for path, params in endpoints:
    try:
        r = requests.get(
            BASE + path,
            headers={"X-RapidAPI-Key": KEY, "X-RapidAPI-Host": HOST},
            params=params,
            timeout=10,
        )
        if r.status_code == 200:
            print(f"SUCCESS {path} -> {list(r.json().keys())[:4]}")
        elif r.status_code == 404:
            print(f"404 (not found): {path}")
        elif r.status_code == 403:
            print(f"403 (not subscribed): {path}")
        elif r.status_code == 422:
            print(f"422 (wrong params): {path} - {r.text[:80]}")
        else:
            print(f"{r.status_code}: {path} - {r.text[:80]}")
    except Exception as e:
        print(f"Error {path}: {e}")
    time.sleep(0.3)
