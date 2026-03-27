"""Test RapidAPI connection with the provided key."""
import sys
sys.path.insert(0, '.')

import os
os.environ["RAPIDAPI_KEY"] = "b88171c23mshd020129138e4f3ep1d1f24jsn5cf8962026fe"

from scraper import search_products, scrape_all_sites

print("=== Testing RapidAPI Product Search ===")
products = search_products("laptop", max_products=5)
print(f"Found: {len(products)} products\n")
for p in products:
    print(f"  [{p['source']}] {p['title'][:60]}")
    print(f"    Price: {p['price']} | Rating: {p['rating']} | Reviews: {len(p['reviews'])}")

if not products:
    print("No products returned - check API key or quota")
else:
    print("\n=== Full scrape_all_sites test ===")
    all_p = scrape_all_sites("wireless headphones", max_per_site=3)
    print(f"Total products: {len(all_p)}")
    brands = set()
    for p in all_p:
        first_word = p['title'].split()[0]
        brands.add(first_word)
    print(f"Brands found: {list(brands)[:8]}")
