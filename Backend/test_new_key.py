import requests, time

KEY = "f4247235eamsh64865872ff73a85p1c57d0jsn48521b69a546"

apis = [
    ("real-time-product-search.p.rapidapi.com",
     "https://real-time-product-search.p.rapidapi.com/search",
     {"q": "laptop", "country": "us", "language": "en"}),

    ("real-time-amazon-data.p.rapidapi.com",
     "https://real-time-amazon-data.p.rapidapi.com/search",
     {"query": "laptop", "country": "US", "category_id": "aps"}),

    ("amazon23.p.rapidapi.com",
     "https://amazon23.p.rapidapi.com/product-search",
     {"q": "laptop", "country": "US"}),

    ("facebook-scraper3.p.rapidapi.com",
     "https://facebook-scraper3.p.rapidapi.com/search/pages",
     {"query": "laptop"}),
]

print("Testing new key...\n")
for host, url, params in apis:
    try:
        r = requests.get(
            url,
            headers={"X-RapidAPI-Key": KEY, "X-RapidAPI-Host": host},
            params=params,
            timeout=10,
        )
        if r.status_code == 200:
            print(f"WORKS: {host}")
        elif r.status_code == 429:
            print(f"SUBSCRIBED (rate limited): {host}")
        elif r.status_code == 403:
            print(f"Not subscribed: {host}")
        else:
            print(f"{r.status_code}: {host}")
    except Exception as e:
        print(f"Error: {host} - {e}")
    time.sleep(0.5)
