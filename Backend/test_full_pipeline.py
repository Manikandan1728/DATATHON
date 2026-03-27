import sys, os
sys.path.insert(0, 'Backend')

# Use environment variables instead of hardcoded keys
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from pipeline import run_pipeline

print("Running full pipeline for 'laptop'...")
result = run_pipeline("laptop", max_per_site=4)

if "error" in result:
    print("ERROR:", result["error"])
else:
    print(f"\nQuery: {result['query']}")
    print(f"Category: {result['category']}")
    print(f"Total products: {result['total_products']}")
    print(f"Sources: {result['sources']}")
    print(f"Top brand: {result['top_brand']}")
    print(f"Brands: {list(result['brands'].keys())}")
    print(f"Component winners: {list(result['component_winners'].keys())[:5]}")
    print(f"Customer issues: {len(result['customer_issues'])}")
    print(f"Execution time: {result['execution_time']}")
    print("\nInsights:")
    for k, v in result['insights'].items():
        print(f"  {k}: {v[:100]}")
    print("\nProducts:")
    for p in result['products'][:5]:
        print(f"  [{p['brand']}] {p['name'][:50]} | ${p['price']} | {p['rating']}★")
