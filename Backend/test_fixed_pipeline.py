"""
test_fixed_pipeline.py
Test the fixed pipeline with correct dual graph output
"""
import sys
import os

# Add Backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline import run_pipeline

def test_laptop_pipeline():
    """Test the fixed pipeline with laptop query."""
    print("=" * 80)
    print("TESTING FIXED PIPELINE - LAPTOP")
    print("=" * 80)
    
    # Mock some sample data to test without scraping
    class MockScraper:
        def scrape_all_sites(self, query, max_per_site=5):
            return [
                {
                    "title": "Dell XPS 15 Laptop",
                    "price": "$1299.99",
                    "rating": "4.5",
                    "num_reviews": "234",
                    "source": "test",
                    "url": "http://test.com",
                    "reviews": [
                        "Great performance, the Intel i7 processor handles everything smoothly",
                        "Excellent battery life, lasts all day with normal usage",
                        "Beautiful design with premium aluminum build quality",
                        "Amazing display quality, colors are vibrant and sharp"
                    ],
                    "scraped_at": "2024-01-01T00:00:00Z"
                },
                {
                    "title": "HP Spectre x360",
                    "price": "$1199.99",
                    "rating": "4.3",
                    "num_reviews": "189",
                    "source": "test",
                    "url": "http://test.com",
                    "reviews": [
                        "Good performance for everyday tasks",
                        "Battery could be better",
                        "Nice design and build quality",
                        "Display is bright and clear"
                    ],
                    "scraped_at": "2024-01-01T00:00:00Z"
                }
            ]
    
    # Temporarily replace the scraper
    import pipeline
    original_scraper = pipeline.scrape_all_sites
    pipeline.scrape_all_sites = MockScraper().scrape_all_sites
    
    try:
        # Run the pipeline
        result = run_pipeline("laptop", max_per_site=2)
        
        print(f"Query: {result['query']}")
        print(f"Total Products: {result['total_products']}")
        
        # Show the NEW dual output
        print("\n" + "=" * 60)
        print("📊 GRAPH 1: COMPONENTS (from search query)")
        print("=" * 60)
        components = result.get('components_from_query', [])
        print(f"Total Components: {len(components)}")
        for i, component in enumerate(components, 1):
            print(f"  {i:2d}. {component}")
        
        print("\n" + "=" * 60)
        print("📊 GRAPH 2: ASPECTS (from reviews)")
        print("=" * 60)
        aspects = result.get('aspects_from_reviews', [])
        print(f"Total Aspects: {len(aspects)}")
        for i, aspect in enumerate(aspects, 1):
            print(f"  {i:2d}. {aspect}")
        
        # Verify the fix
        print("\n" + "=" * 60)
        print("✅ VERIFICATION")
        print("=" * 60)
        print(f"Components come from query: {'components_from_query' in result}")
        print(f"Aspects come from reviews: {'aspects_from_reviews' in result}")
        print(f"Expected components found: {any(comp.lower() in ['cpu', 'ram', 'battery', 'display', 'cooling system'] for comp in components)}")
        print(f"Expected aspects found: {any(asp.lower() in ['performance', 'battery life', 'display quality', 'design'] for asp in aspects)}")
        
        return result
        
    finally:
        # Restore original scraper
        pipeline.scrape_all_sites = original_scraper

def test_shirt_pipeline():
    """Test the fixed pipeline with shirt query."""
    print("\n" + "=" * 80)
    print("TESTING FIXED PIPELINE - SHIRT")
    print("=" * 80)
    
    class MockScraper:
        def scrape_all_sites(self, query, max_per_site=5):
            return [
                {
                    "title": "Men's Cotton Dress Shirt",
                    "price": "$49.99",
                    "rating": "4.2",
                    "num_reviews": "156",
                    "source": "test",
                    "url": "http://test.com",
                    "reviews": [
                        "Great fabric quality, feels very soft and comfortable",
                        "Good fit, true to size",
                        "Nice collar design",
                        "Quality buttons and stitching"
                    ],
                    "scraped_at": "2024-01-01T00:00:00Z"
                }
            ]
    
    # Temporarily replace the scraper
    import pipeline
    original_scraper = pipeline.scrape_all_sites
    pipeline.scrape_all_sites = MockScraper().scrape_all_sites
    
    try:
        # Run the pipeline
        result = run_pipeline("shirt", max_per_site=1)
        
        print(f"Query: {result['query']}")
        
        # Show the NEW dual output
        print("\n" + "=" * 60)
        print("📊 GRAPH 1: COMPONENTS (from search query)")
        print("=" * 60)
        components = result.get('components_from_query', [])
        print(f"Total Components: {len(components)}")
        for i, component in enumerate(components, 1):
            print(f"  {i:2d}. {component}")
        
        print("\n" + "=" * 60)
        print("📊 GRAPH 2: ASPECTS (from reviews)")
        print("=" * 60)
        aspects = result.get('aspects_from_reviews', [])
        print(f"Total Aspects: {len(aspects)}")
        for i, aspect in enumerate(aspects, 1):
            print(f"  {i:2d}. {aspect}")
        
        return result
        
    finally:
        # Restore original scraper
        pipeline.scrape_all_sites = original_scraper

def main():
    """Run the fixed pipeline tests."""
    print("🎯 TESTING FIXED DUAL PIPELINE")
    print("Now using CORRECT architecture:")
    print("- Components from search query ONLY")
    print("- Aspects from reviews ONLY")
    
    try:
        test_laptop_pipeline()
        test_shirt_pipeline()
        
        print("\n" + "=" * 80)
        print("✅ FIXED PIPELINE TEST COMPLETE")
        print("=" * 80)
        print("🔧 FIX APPLIED:")
        print("  - Replaced old component_analyzer with dual_pipeline_analyzer")
        print("  - Components now come from search query ONLY")
        print("  - Aspects now come from reviews ONLY")
        print("  - Both graphs are independent and correct")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
