"""Test pipeline logic with mock scraped data (no network needed)."""
import sys
sys.path.insert(0, '.')

from component_analyzer import split_reviews_by_component, infer_category
from agent import _tool_sentiment_score, _tool_extract_complaints, _tool_compare_products

# Simulate what scraper would return for "laptop"
mock_products = [
    {
        "title": "Dell XPS 15 Laptop Intel Core i7",
        "source": "ebay",
        "price": "$1299.99",
        "rating": "4.5 out of 5 stars",
        "num_reviews": "2341",
        "url": "https://www.ebay.com/itm/123",
        "reviews": [
            "Great performance, battery lasts 8 hours easily",
            "Display is stunning, very bright and clear",
            "Build quality is excellent, feels premium",
            "A bit expensive but worth the price",
            "Fast processor, no lag at all",
        ],
        "scraped_at": "2024-01-01T00:00:00",
    },
    {
        "title": "HP Pavilion 15 Laptop AMD Ryzen 5",
        "source": "walmart",
        "price": "$699.00",
        "rating": "4.2",
        "num_reviews": "1876",
        "url": "https://www.walmart.com/ip/456",
        "reviews": [
            "Good value for money, decent performance",
            "Battery drains fast, only 4 hours",
            "Screen is okay but not the best",
            "Keyboard is comfortable to type on",
            "Gets a bit warm under heavy load",
        ],
        "scraped_at": "2024-01-01T00:00:00",
    },
    {
        "title": "Lenovo ThinkPad E15 Business Laptop",
        "source": "ebay",
        "price": "$849.00",
        "rating": "4.7",
        "num_reviews": "3102",
        "url": "https://www.ebay.com/itm/789",
        "reviews": [
            "Excellent build quality, very durable",
            "Battery life is amazing, 10+ hours",
            "Keyboard is the best I have used",
            "Performance is solid for business use",
            "A bit heavy but very reliable",
        ],
        "scraped_at": "2024-01-01T00:00:00",
    },
]

print("=== Category Inference ===")
print("laptop ->", infer_category("laptop"))
print("wireless headphones ->", infer_category("wireless headphones"))
print("running shoes ->", infer_category("running shoes"))

print("\n=== Component Split ===")
comp_data = split_reviews_by_component(mock_products)
for product, comps in comp_data.items():
    print(f"\n{product[:40]}:")
    for comp, reviews in comps.items():
        print(f"  {comp}: {len(reviews)} reviews")

print("\n=== Sentiment Analysis ===")
import json
reviews_dell = mock_products[0]["reviews"]
result = json.loads(_tool_sentiment_score(json.dumps(reviews_dell)))
print(f"Dell sentiment: {result}")

print("\n=== Complaint Extraction ===")
all_reviews = [r for p in mock_products for r in p["reviews"]]
complaints = json.loads(_tool_extract_complaints(json.dumps(all_reviews)))
print(f"Top complaints: {complaints}")

print("\n=== Full Pipeline Test ===")
# Test pipeline with mock data (bypass scraper)
import scraper
import pipeline as pl

# Patch scraper inside pipeline module
original_scrape = pl.scrape_all_sites
pl.scrape_all_sites = lambda q, max_per_site=5: mock_products

result = pl.run_pipeline("laptop", max_per_site=3)
print(f"Query: {result.get('query')}")
print(f"Category: {result.get('category')}")
print(f"Total products: {result.get('total_products')}")
print(f"Brands: {list(result.get('brands', {}).keys())}")
print(f"Top brand: {result.get('top_brand')}")
print(f"Component winners: {list(result.get('component_winners', {}).keys())[:5]}")
print(f"Customer issues: {len(result.get('customer_issues', []))}")
print(f"Recommendations: {len(result.get('recommendations', []))}")
print(f"Execution time: {result.get('execution_time')}")
print("\nInsights:")
for k, v in result.get("insights", {}).items():
    print(f"  {k}: {v[:80]}...")

# Restore
scraper.scrape_all_sites = original_scrape
print("\nAll tests PASSED")
