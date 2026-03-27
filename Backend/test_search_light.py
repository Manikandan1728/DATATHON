import requests, json

KEY = "f4247235eamsh64865872ff73a85p1c57d0jsn48521b69a546"
HOST = "real-time-product-search.p.rapidapi.com"

r = requests.get(
    f"https://{HOST}/search-light",
    headers={"X-RapidAPI-Key": KEY, "X-RapidAPI-Host": HOST},
    params={"q": "laptop", "country": "us", "language": "en", "limit": "5"},
    timeout=20,
)
print("Status:", r.status_code)
data = r.json()
print("Full response:")
print(json.dumps(data, indent=2)[:2000])
