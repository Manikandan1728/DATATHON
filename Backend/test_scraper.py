import sys
sys.path.insert(0, '.')
from scraper import scrape_ebay, scrape_walmart, scrape_all_sites

print("=== Testing eBay ===")
ebay = scrape_ebay('laptop', 4)
print(f"eBay: {len(ebay)} products")
for p in ebay:
    print(f"  [{p['source']}] {p['title'][:55]} | {p['price']}")

print("\n=== Testing Walmart ===")
walmart = scrape_walmart('laptop', 4)
print(f"Walmart: {len(walmart)} products")
for p in walmart:
    print(f"  [{p['source']}] {p['title'][:55]} | {p['price']}")

print(f"\n=== Total: {len(ebay) + len(walmart)} products ===")
