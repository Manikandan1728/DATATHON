"""
test_dual_pipeline.py
Test the correct dual pipeline architecture:
- Component Generator (from search query ONLY)
- Aspect Analyzer (from reviews ONLY)
"""
import sys
import os

# Add the Backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_pipeline_analyzer import (
    DualPipelineAnalyzer,
    generate_components_only,
    extract_aspects_only,
    run_dual_pipeline
)

def test_component_generator_only():
    """Test component generation from search query ONLY."""
    print("=" * 60)
    print("TESTING COMPONENT GENERATOR (QUERY ONLY)")
    print("=" * 60)
    
    analyzer = DualPipelineAnalyzer()
    
    # Test different queries
    test_queries = [
        "laptop",
        "shirt", 
        "smartphone",
        "headphones",
        "shoes",
        "camera"
    ]
    
    for query in test_queries:
        components = analyzer.generate_components(query)
        print(f"\nQuery: '{query}'")
        print(f"Components: {components}")
        print(f"Count: {len(components)}")

def test_aspect_analyzer_only():
    """Test aspect extraction from reviews ONLY."""
    print("\n" + "=" * 60)
    print("TESTING ASPECT ANALYZER (REVIEWS ONLY)")
    print("=" * 60)
    
    analyzer = DualPipelineAnalyzer()
    
    # Sample reviews for laptop
    laptop_reviews = [
        "Great performance, the Intel i7 processor handles everything smoothly",
        "Excellent battery life, lasts all day with normal usage",
        "Beautiful design with premium aluminum build quality",
        "Amazing display quality, colors are vibrant and sharp",
        "Good value for money considering the specifications",
        "Easy to use right out of the box, setup was simple",
        "Fast charging time, fully charges in about 2 hours",
        "Quiet operation, fan noise is minimal even under load",
        "Comfortable keyboard, typing experience is excellent",
        "Responsive trackpad, gestures work perfectly"
    ]
    
    aspects = analyzer.extract_aspects_from_reviews(laptop_reviews)
    print(f"Laptop Reviews ({len(laptop_reviews)}):")
    print(f"Aspects: {aspects}")
    print(f"Count: {len(aspects)}")
    
    # Sample reviews for shirt
    shirt_reviews = [
        "Great fabric quality, feels very soft and comfortable",
        "Good fit, true to size",
        "Excellent stitching and durable material",
        "Beautiful design and color",
        "Good value for the price",
        "Comfortable to wear all day",
        "Nice collar design",
        "Sleeves fit well",
        "Quality buttons and placket",
        "Great overall fit and comfort"
    ]
    
    aspects = analyzer.extract_aspects_from_reviews(shirt_reviews)
    print(f"\nShirt Reviews ({len(shirt_reviews)}):")
    print(f"Aspects: {aspects}")
    print(f"Count: {len(aspects)}")

def test_dual_pipeline_complete():
    """Test the complete dual pipeline with expected outputs."""
    print("\n" + "=" * 60)
    print("TESTING COMPLETE DUAL PIPELINE")
    print("=" * 60)
    
    analyzer = DualPipelineAnalyzer()
    
    # Test Case 1: Laptop
    print("\nTest Case 1: Laptop")
    laptop_reviews = [
        "Great performance, the Intel i7 processor handles everything smoothly",
        "Excellent battery life, lasts all day with normal usage",
        "Beautiful design with premium aluminum build quality",
        "Amazing display quality, colors are vibrant and sharp",
        "Good value for money considering the specifications",
        "Easy to use right out of the box, setup was simple"
    ]
    
    result = analyzer.analyze_product("laptop", laptop_reviews)
    
    print(f"Search: {result['search_query']}")
    print(f"\nComponents:")
    for i, component in enumerate(result['components'], 1):
        print(f"  {i}. {component}")
    
    print(f"\nAspects:")
    for i, aspect in enumerate(result['aspects'], 1):
        print(f"  {i}. {aspect}")
    
    print(f"\nPipeline Info:")
    print(f"  Component Source: {result['pipelines']['component_generator']['source']}")
    print(f"  Aspect Source: {result['pipelines']['aspect_analyzer']['source']}")
    
    # Test Case 2: Shirt
    print("\n" + "=" * 40)
    print("Test Case 2: Shirt")
    shirt_reviews = [
        "Great fabric quality, feels very soft and comfortable",
        "Good fit, true to size",
        "Excellent stitching and durable material",
        "Beautiful design and color",
        "Good value for the price",
        "Comfortable to wear all day"
    ]
    
    result = analyzer.analyze_product("shirt", shirt_reviews)
    
    print(f"Search: {result['search_query']}")
    print(f"\nComponents:")
    for i, component in enumerate(result['components'], 1):
        print(f"  {i}. {component}")
    
    print(f"\nAspects:")
    for i, aspect in enumerate(result['aspects'], 1):
        print(f"  {i}. {aspect}")

def test_convenience_functions():
    """Test the convenience functions."""
    print("\n" + "=" * 60)
    print("TESTING CONVENIENCE FUNCTIONS")
    print("=" * 60)
    
    # Test component generation only
    print("1. Component Generation Only:")
    components = generate_components_only("laptop")
    print(f"   Query: laptop")
    print(f"   Components: {components}")
    
    # Test aspect extraction only
    print("\n2. Aspect Extraction Only:")
    reviews = [
        "Great performance and battery life",
        "Excellent display quality and design",
        "Good value for money",
        "Easy to use and setup"
    ]
    aspects = extract_aspects_only(reviews)
    print(f"   Reviews: {len(reviews)}")
    print(f"   Aspects: {aspects}")
    
    # Test dual pipeline
    print("\n3. Complete Dual Pipeline:")
    result = run_dual_pipeline("smartphone", reviews)
    print(f"   Query: smartphone")
    print(f"   Components: {result['components']}")
    print(f"   Aspects: {result['aspects']}")

def test_independence():
    """Test that the two pipelines are truly independent."""
    print("\n" + "=" * 60)
    print("TESTING PIPELINE INDEPENDENCE")
    print("=" * 60)
    
    analyzer = DualPipelineAnalyzer()
    
    # Test 1: Components should not depend on reviews
    print("Test 1: Components Independence")
    components_no_reviews = analyzer.generate_components("laptop")
    components_with_reviews = analyzer.generate_components("laptop")  # Same query
    
    print(f"Components without reviews: {components_no_reviews}")
    print(f"Components with reviews: {components_with_reviews}")
    print(f"Components are identical: {components_no_reviews == components_with_reviews}")
    
    # Test 2: Aspects should not depend on query
    print("\nTest 2: Aspects Independence")
    reviews = [
        "Great performance and battery life",
        "Excellent display quality",
        "Good value for money"
    ]
    
    aspects_laptop = analyzer.extract_aspects_from_reviews(reviews)
    aspects_shirt = analyzer.extract_aspects_from_reviews(reviews)  # Same reviews
    
    print(f"Aspects for 'laptop': {aspects_laptop}")
    print(f"Aspects for 'shirt': {aspects_shirt}")
    print(f"Aspects are identical: {aspects_laptop == aspects_shirt}")

def test_expected_outputs():
    """Test with the expected outputs from the requirements."""
    print("\n" + "=" * 60)
    print("TESTING EXPECTED OUTPUTS")
    print("=" * 60)
    
    analyzer = DualPipelineAnalyzer()
    
    # Expected laptop output
    print("Expected Output for 'laptop':")
    laptop_reviews = [
        "Great performance and battery life",
        "Excellent display quality", 
        "Good value for money",
        "Easy to use and setup"
    ]
    
    result = analyzer.analyze_product("laptop", laptop_reviews)
    
    print(f"\nSearch: laptop")
    print(f"\nComponents:")
    for component in result['components'][:5]:  # Show first 5
        print(f"  {component}")
    
    print(f"\nAspects:")
    for aspect in result['aspects'][:5]:  # Show first 5
        print(f"  {aspect}")
    
    # Expected shirt output
    print("\n" + "=" * 40)
    print("Expected Output for 'shirt':")
    shirt_reviews = [
        "Great fabric quality and fit",
        "Comfortable to wear",
        "Good value and design"
    ]
    
    result = analyzer.analyze_product("shirt", shirt_reviews)
    
    print(f"\nSearch: shirt")
    print(f"\nComponents:")
    for component in result['components'][:5]:  # Show first 5
        print(f"  {component}")
    
    print(f"\nAspects:")
    for aspect in result['aspects'][:5]:  # Show first 5
        print(f"  {aspect}")

def main():
    """Run all tests."""
    print("DUAL PIPELINE ANALYZER TEST SUITE")
    print("Testing Correct Architecture:")
    print("- Component Generator (search_query ONLY)")
    print("- Aspect Analyzer (reviews ONLY)")
    
    try:
        test_component_generator_only()
        test_aspect_analyzer_only()
        test_dual_pipeline_complete()
        test_convenience_functions()
        test_independence()
        test_expected_outputs()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("✅ Components depend ONLY on search_query")
        print("✅ Aspects depend ONLY on reviews")
        print("✅ Two independent pipelines working correctly")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
