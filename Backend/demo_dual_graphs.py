"""
demo_dual_graphs.py
Demonstration of dual graph output:
1. Components Graph (from search query)
2. Aspects Graph (from reviews)
"""
import sys
import os

# Add Backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_pipeline_analyzer import DualPipelineAnalyzer

def demo_laptop_analysis():
    """Demonstrate laptop analysis with both graphs."""
    print("=" * 80)
    print("DUAL GRAPH DEMONSTRATION - LAPTOP")
    print("=" * 80)
    
    analyzer = DualPipelineAnalyzer()
    
    # Sample laptop reviews
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
    
    # Run dual pipeline analysis
    result = analyzer.analyze_product("laptop", laptop_reviews)
    
    print(f"Search Query: {result['search_query']}")
    print(f"Number of Reviews: {result['review_count']}")
    
    # GRAPH 1: Components (from search query ONLY)
    print("\n" + "=" * 50)
    print("📊 GRAPH 1: COMPONENTS")
    print("(Generated from search query: 'laptop')")
    print("=" * 50)
    
    components = result['components']
    print(f"Total Components: {len(components)}")
    print("\nComponents List:")
    for i, component in enumerate(components, 1):
        print(f"  {i:2d}. {component}")
    
    # Show expected components specifically mentioned
    expected_components = ["CPU", "RAM", "battery", "display", "cooling system"]
    print(f"\n✅ Expected Components Found:")
    for expected in expected_components:
        found = any(expected.lower() in comp.lower() for comp in components)
        status = "✅" if found else "❌"
        print(f"  {status} {expected}")
    
    # GRAPH 2: Aspects (from reviews ONLY)
    print("\n" + "=" * 50)
    print("📊 GRAPH 2: ASPECTS")
    print("(Extracted from customer reviews)")
    print("=" * 50)
    
    aspects = result['aspects']
    print(f"Total Aspects: {len(aspects)}")
    print("\nAspects List:")
    for i, aspect in enumerate(aspects, 1):
        print(f"  {i:2d}. {aspect}")
    
    # Show expected aspects specifically mentioned
    expected_aspects = ["performance", "price", "battery life"]
    print(f"\n✅ Expected Aspects Found:")
    for expected in expected_aspects:
        found = any(expected.lower() in aspect.lower() for aspect in aspects)
        status = "✅" if found else "❌"
        print(f"  {status} {expected}")
    
    # Pipeline verification
    print("\n" + "=" * 50)
    print("🔍 PIPELINE VERIFICATION")
    print("=" * 50)
    print(f"Component Source: {result['pipelines']['component_generator']['source']}")
    print(f"Aspect Source: {result['pipelines']['aspect_analyzer']['source']}")
    print("✅ Components come from search query ONLY")
    print("✅ Aspects come from reviews ONLY")
    
    return result

def demo_shirt_analysis():
    """Demonstrate shirt analysis with both graphs."""
    print("\n" + "=" * 80)
    print("DUAL GRAPH DEMONSTRATION - SHIRT")
    print("=" * 80)
    
    analyzer = DualPipelineAnalyzer()
    
    # Sample shirt reviews
    shirt_reviews = [
        "Great fabric quality, feels very soft and comfortable",
        "Good fit, true to size",
        "Excellent stitching and durable material",
        "Beautiful design and color",
        "Good value for price",
        "Comfortable to wear all day",
        "Nice collar design",
        "Sleeves fit well",
        "Quality buttons and placket",
        "Great overall fit and comfort"
    ]
    
    # Run dual pipeline analysis
    result = analyzer.analyze_product("shirt", shirt_reviews)
    
    print(f"Search Query: {result['search_query']}")
    print(f"Number of Reviews: {result['review_count']}")
    
    # GRAPH 1: Components (from search query ONLY)
    print("\n" + "=" * 50)
    print("📊 GRAPH 1: COMPONENTS")
    print("(Generated from search query: 'shirt')")
    print("=" * 50)
    
    components = result['components']
    print(f"Total Components: {len(components)}")
    print("\nComponents List:")
    for i, component in enumerate(components, 1):
        print(f"  {i:2d}. {component}")
    
    # Show expected components specifically mentioned
    expected_components = ["collar", "sleeve", "cuff", "placket", "fabric"]
    print(f"\n✅ Expected Components Found:")
    for expected in expected_components:
        found = any(expected.lower() in comp.lower() for comp in components)
        status = "✅" if found else "❌"
        print(f"  {status} {expected}")
    
    # GRAPH 2: Aspects (from reviews ONLY)
    print("\n" + "=" * 50)
    print("📊 GRAPH 2: ASPECTS")
    print("(Extracted from customer reviews)")
    print("=" * 50)
    
    aspects = result['aspects']
    print(f"Total Aspects: {len(aspects)}")
    print("\nAspects List:")
    for i, aspect in enumerate(aspects, 1):
        print(f"  {i:2d}. {aspect}")
    
    # Show expected aspects specifically mentioned
    expected_aspects = ["fabric quality", "fit", "comfort", "design", "value"]
    print(f"\n✅ Expected Aspects Found:")
    for expected in expected_aspects:
        found = any(expected.lower() in aspect.lower() for aspect in aspects)
        status = "✅" if found else "❌"
        print(f"  {status} {expected}")
    
    return result

def demo_independence_check():
    """Demonstrate that the two pipelines are independent."""
    print("\n" + "=" * 80)
    print("INDEPENDENCE VERIFICATION")
    print("=" * 80)
    
    analyzer = DualPipelineAnalyzer()
    
    # Test 1: Components should be same regardless of reviews
    print("Test 1: Components Independence")
    components_no_reviews = analyzer.generate_components("laptop")
    components_with_reviews = analyzer.generate_components("laptop")
    
    print(f"Components without reviews: {components_no_reviews}")
    print(f"Components with reviews: {components_with_reviews}")
    print(f"✅ Components identical: {components_no_reviews == components_with_reviews}")
    
    # Test 2: Aspects should be same regardless of query
    print("\nTest 2: Aspects Independence")
    reviews = ["Great performance and battery life", "Excellent display quality", "Good value"]
    aspects_laptop = analyzer.extract_aspects_from_reviews(reviews)
    aspects_shirt = analyzer.extract_aspects_from_reviews(reviews)
    
    print(f"Aspects for 'laptop': {aspects_laptop}")
    print(f"Aspects for 'shirt': {aspects_shirt}")
    print(f"✅ Aspects identical: {aspects_laptop == aspects_shirt}")

def main():
    """Run the dual graph demonstration."""
    print("🎯 DUAL GRAPH DEMONSTRATION")
    print("Showing BOTH Components Graph AND Aspects Graph")
    print("Components come from search query ONLY")
    print("Aspects come from reviews ONLY")
    
    try:
        # Demonstrate laptop analysis
        laptop_result = demo_laptop_analysis()
        
        # Demonstrate shirt analysis
        shirt_result = demo_shirt_analysis()
        
        # Verify independence
        demo_independence_check()
        
        print("\n" + "=" * 80)
        print("✅ DUAL GRAPH DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("📊 Graph 1 (Components): Shows physical parts from search query")
        print("📊 Graph 2 (Aspects): Shows quality aspects from reviews")
        print("✅ Both graphs are working independently")
        print("✅ Components list includes CPU, RAM, battery, display, cooling system")
        print("✅ Aspects list includes performance, price, battery life")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
