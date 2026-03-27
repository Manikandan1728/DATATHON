"""
test_ai_component_generator.py
Test script for AI-based component generation
"""
import sys
import os

# Add the Backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_component_generator import AIComponentGenerator, generate_ai_components

def test_fallback_knowledge_base():
    """Test the fallback knowledge base without LLM."""
    print("=" * 60)
    print("TESTING FALLBACK KNOWLEDGE BASE")
    print("=" * 60)
    
    generator = AIComponentGenerator()
    
    # Test different product categories
    test_queries = [
        "laptop",
        "smartphone", 
        "headphones",
        "tablet",
        "tv",
        "camera",
        "smartwatch",
        "desktop",
        "monitor",
        "speaker",
        "gaming laptop",
        "wireless earbuds"
    ]
    
    for query in test_queries:
        result = generator.analyze_product(query, use_llm=False)
        print(f"\nQuery: '{query}'")
        print(f"Components ({len(result['components'])}): {result['components']}")
        print(f"Category inferred: {generator._infer_product_category(query)}")

def test_with_reviews():
    """Test AI component generation with review-based aspect analysis."""
    print("\n" + "=" * 60)
    print("TESTING WITH REVIEW-BASED ASPECT ANALYSIS")
    print("=" * 60)
    
    generator = AIComponentGenerator()
    
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
        "Responsive trackpad, gestures work perfectly",
        "Solid build quality, feels very durable and premium",
        "Great connectivity options with WiFi 6 and USB-C",
        "Outstanding gaming performance on this laptop",
        "Perfect color accuracy for photo editing work",
        "Impressive sound quality from the speakers"
    ]
    
    # Test laptop analysis
    result = generator.analyze_product("laptop", laptop_reviews, use_llm=False)
    
    print(f"Search Query: {result['search_query']}")
    print(f"\nComponents (AI-generated):")
    for i, component in enumerate(result['components'], 1):
        print(f"  {i:2d}. {component}")
    
    print(f"\nAspects (from reviews):")
    for i, aspect in enumerate(result['aspects'], 1):
        print(f"  {i:2d}. {aspect}")
    
    print(f"\nSummary:")
    print(f"  Components: {result['component_count']}")
    print(f"  Aspects: {result['aspect_count']}")
    print(f"  Reviews: {result['review_count']}")
    print(f"  Generation Method: {result['generation_method']}")

def test_smartphone_analysis():
    """Test smartphone analysis with reviews."""
    print("\n" + "=" * 60)
    print("TESTING SMARTPHONE ANALYSIS")
    print("=" * 60)
    
    generator = AIComponentGenerator()
    
    # Sample reviews for smartphone
    phone_reviews = [
        "Amazing camera quality, photos are sharp and detailed",
        "Fast performance with the new A16 chip",
        "Battery life is excellent, lasts all day",
        "Beautiful design and premium build quality",
        "Great display quality, colors are vibrant",
        "Good value for the price",
        "Easy to use interface is very intuitive",
        "Fast charging with the included adapter",
        "Great sound quality from speakers",
        "Solid build, feels very durable",
        "Excellent connectivity with 5G support",
        "Responsive touchscreen and smooth performance",
        "Impressive low-light camera performance",
        "Good storage capacity with 256GB",
        "Comfortable to hold and use"
    ]
    
    result = generator.analyze_product("smartphone", phone_reviews, use_llm=False)
    
    print(f"Search Query: {result['search_query']}")
    print(f"\nComponents (AI-generated):")
    for i, component in enumerate(result['components'], 1):
        print(f"  {i:2d}. {component}")
    
    print(f"\nAspects (from reviews):")
    for i, aspect in enumerate(result['aspects'], 1):
        print(f"  {i:2d}. {aspect}")

def test_convenience_function():
    """Test the convenience function."""
    print("\n" + "=" * 60)
    print("TESTING CONVENIENCE FUNCTION")
    print("=" * 60)
    
    # Quick test with convenience function
    reviews = [
        "Great performance and battery life",
        "Excellent display quality and design",
        "Good value for money",
        "Easy to use and setup"
    ]
    
    result = generate_ai_components("tablet", reviews)
    
    print("Quick Analysis Result:")
    print(f"Components: {result['components']}")
    print(f"Aspects: {result['aspects']}")

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "=" * 60)
    print("TESTING EDGE CASES")
    print("=" * 60)
    
    generator = AIComponentGenerator()
    
    # Test empty query
    print("Test 1: Empty Query")
    result = generator.analyze_product("", use_llm=False)
    print(f"Empty query components: {result['components']}")
    
    # Test unknown product
    print("\nTest 2: Unknown Product")
    result = generator.analyze_product("quantum computer", use_llm=False)
    print(f"Unknown product components: {result['components']}")
    
    # Test no reviews
    print("\nTest 3: No Reviews")
    result = generator.analyze_product("headphones", [], use_llm=False)
    print(f"No reviews aspects: {result['aspects']}")
    
    # Test single word query
    print("\nTest 4: Single Word Query")
    result = generator.analyze_product("tv", use_llm=False)
    print(f"Single word query: {result['components']}")

def test_llm_parsing():
    """Test LLM response parsing."""
    print("\n" + "=" * 60)
    print("TESTING LLM RESPONSE PARSING")
    print("=" * 60)
    
    generator = AIComponentGenerator()
    
    # Test different response formats
    test_responses = [
        """1. CPU
2. RAM
3. Storage
4. Display
5. Battery""",
        
        """- Processor
- Memory
- Graphics Card
- Motherboard
- Power Supply""",
        
        """CPU, RAM, Storage, Display, Battery, Keyboard, Trackpad""",
        
        """Processor
Memory
Storage
Display
Battery""",
        
        """The main components are:
1. Central Processing Unit (CPU)
2. Random Access Memory (RAM)
3. Storage Drive
4. Display Screen
5. Battery Pack"""
    ]
    
    for i, response in enumerate(test_responses, 1):
        parsed = generator._parse_llm_response(response)
        print(f"Test {i}: {parsed}")

def main():
    """Run all tests."""
    print("AI COMPONENT GENERATOR TEST SUITE")
    print("Testing AI-based component generation with review-based aspect analysis")
    
    try:
        # Run all tests
        test_fallback_knowledge_base()
        test_with_reviews()
        test_smartphone_analysis()
        test_convenience_function()
        test_edge_cases()
        test_llm_parsing()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
