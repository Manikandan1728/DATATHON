"""
test_product_analyzers.py
Test script for PRODUCT COMPONENT ANALYZER and PRODUCT ASPECT ANALYZER
"""
import sys
import os

# Add the Backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from product_component_analyzer import ProductComponentAnalyzer, extract_product_components
from product_aspect_analyzer import ProductAspectAnalyzer, extract_product_aspects

def test_component_analyzer():
    """Test the Product Component Analyzer."""
    print("=" * 60)
    print("TESTING PRODUCT COMPONENT ANALYZER")
    print("=" * 60)
    
    # Sample product data
    title = "Dell XPS 15 Laptop Intel i7 16GB RAM 512GB SSD"
    description = "High-performance laptop with stunning 4K display and powerful Intel Core i7 processor"
    specifications = """
    - Processor: Intel Core i7-12700H 2.3 GHz
    - Memory: 16GB DDR4 RAM
    - Storage: 512GB NVMe SSD
    - Display: 15.6" 4K UHD Touch Display
    - Graphics: NVIDIA GeForce RTX 3050
    - Operating System: Windows 11 Pro
    - Connectivity: WiFi 6, Bluetooth 5.2, USB-C, HDMI 2.1
    - Battery: 86Whr
    - Weight: 4.2 lbs
    """
    reviews = [
        "The Intel i7 processor is incredibly fast and handles all my tasks smoothly",
        "16GB RAM is perfect for multitasking and running multiple applications",
        "The 512GB SSD provides lightning-fast boot times and file access",
        "4K display is absolutely stunning with vibrant colors",
        "NVIDIA graphics card performs well for gaming and video editing",
        "Battery life lasts about 8 hours with normal usage",
        "Keyboard feels comfortable and backlit keys are helpful",
        "Trackpad is responsive and accurate",
        "Build quality is solid with premium aluminum chassis",
        "WiFi 6 connectivity provides fast and stable internet connection"
    ]
    
    # Test the analyzer
    analyzer = ProductComponentAnalyzer(top_n=10)
    components = analyzer.extract_components(title, description, specifications, reviews)
    
    print(f"Extracted {len(components)} components:")
    for i, component in enumerate(components, 1):
        print(f"{i:2d}. {component}")
    
    # Test with product data dictionary
    product_data = {
        "title": title,
        "description": description,
        "specifications": specifications,
        "reviews": reviews
    }
    
    result = analyzer.analyze_product(product_data)
    print(f"\nDetailed Analysis:")
    print(f"Product: {result['product_title']}")
    print(f"Components: {result['components']}")
    print(f"Sources Used: {result['sources_used']}")
    
    return components

def test_aspect_analyzer():
    """Test the Product Aspect Analyzer."""
    print("\n" + "=" * 60)
    print("TESTING PRODUCT ASPECT ANALYZER")
    print("=" * 60)
    
    # Sample reviews focused on aspects
    reviews = [
        "Great performance, the Intel i7 processor handles everything smoothly",
        "Excellent battery life, lasts all day with normal usage",
        "Beautiful design with premium aluminum build quality",
        "Amazing display quality, colors are vibrant and sharp",
        "Good value for money considering the specifications",
        "Easy to use right out of the box, setup was simple",
        "Fast charging time, fully charges in about 2 hours",
        "Quiet operation, fan noise is minimal even under load",
        "Comfortable keyboard, typing experience is excellent",
        "Responsive trackpad, gestures work perfectly",
        "Solid build quality, feels very durable and premium",
        "Great connectivity options with WiFi 6 and USB-C",
        "Outstanding gaming performance on this laptop",
        "Perfect color accuracy for photo editing work",
        "Impressive sound quality from the speakers",
        "Excellent customer support when I had questions",
        "Good warranty coverage for peace of mind",
        "Effective heat management, stays cool during intensive tasks",
        "Compact size makes it highly portable",
        "Intuitive software features enhance the user experience"
    ]
    
    # Test the analyzer
    analyzer = ProductAspectAnalyzer(top_n=12)
    aspects = analyzer.extract_aspects(reviews)
    
    print(f"Extracted {len(aspects)} aspects:")
    for i, aspect in enumerate(aspects, 1):
        print(f"{i:2d}. {aspect}")
    
    # Test with product data dictionary
    product_data = {
        "title": "Dell XPS 15 Laptop",
        "reviews": reviews
    }
    
    result = analyzer.analyze_product_aspects(product_data)
    print(f"\nDetailed Analysis:")
    print(f"Product: {result['product_title']}")
    print(f"Aspects: {result['aspects']}")
    print(f"Review Count: {result['review_count']}")
    print(f"Extraction Methods: {result['extraction_methods']}")
    
    return aspects

def test_convenience_functions():
    """Test the convenience functions."""
    print("\n" + "=" * 60)
    print("TESTING CONVENIENCE FUNCTIONS")
    print("=" * 60)
    
    # Quick component extraction
    components = extract_product_components(
        title="iPhone 14 Pro 128GB Space Gray",
        description="Latest iPhone with A16 Bionic chip and Pro camera system",
        specifications="A16 Bionic chip, 128GB storage, 6.1 display, 48MP camera",
        reviews=["Great camera quality", "Fast performance", "Excellent battery life"],
        top_n=8
    )
    
    print("Quick Component Extraction:")
    for i, comp in enumerate(components, 1):
        print(f"{i}. {comp}")
    
    # Quick aspect extraction
    reviews = [
        "Amazing camera quality with detailed photos",
        "Performance is incredibly fast and smooth",
        "Battery life lasts all day with heavy usage",
        "Premium design feels great in hand",
        "Price is high but worth it for the quality",
        "Easy to use interface is intuitive"
    ]
    
    aspects = extract_product_aspects(reviews, top_n=8)
    
    print("\nQuick Aspect Extraction:")
    for i, aspect in enumerate(aspects, 1):
        print(f"{i}. {aspect}")

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "=" * 60)
    print("TESTING EDGE CASES")
    print("=" * 60)
    
    # Test with minimal data
    print("Test 1: Minimal Data")
    components = extract_product_components()
    aspects = extract_product_aspects([])
    print(f"Components with no data: {components}")
    print(f"Aspects with no reviews: {aspects}")
    
    # Test with generic content
    print("\nTest 2: Generic Content")
    generic_reviews = [
        "This is a good product",
        "I like this item",
        "Great purchase overall",
        "Nice thing to have"
    ]
    aspects = extract_product_aspects(generic_reviews)
    print(f"Aspects from generic reviews: {aspects}")
    
    # Test with technical specifications
    print("\nTest 3: Technical Specifications Only")
    tech_specs = "Intel i7-12700H 2.3GHz 16GB DDR4 512GB NVMe SSD RTX 3050 4K USB-C WiFi-6"
    components = extract_product_components(specifications=tech_specs)
    print(f"Components from specs only: {components}")

def main():
    """Run all tests."""
    print("PRODUCT ANALYZERS TEST SUITE")
    print("Testing Component and Aspect Analyzers")
    
    try:
        # Run main tests
        test_component_analyzer()
        test_aspect_analyzer()
        test_convenience_functions()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
