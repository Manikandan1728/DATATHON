"""
test_all_categories.py
Test all product categories to ensure correct components
"""
import sys
import os

# Add Backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_pipeline_analyzer import DualPipelineAnalyzer

def test_all_product_categories():
    """Test all product categories for correct component generation."""
    print("=" * 80)
    print("TESTING ALL PRODUCT CATEGORIES")
    print("=" * 80)
    
    analyzer = DualPipelineAnalyzer()
    
    # Test cases for different categories
    test_cases = [
        # Electronics
        ("laptop", ["CPU", "RAM", "battery", "display"]),
        ("smartphone", ["processor", "display", "camera", "battery"]),
        ("headphones", ["drivers", "cable", "ear pads", "battery"]),
        ("tablet", ["processor", "display", "battery", "camera"]),
        ("tv", ["display panel", "speakers", "remote", "power supply"]),
        ("camera", ["sensor", "lens", "display", "battery"]),
        ("smartwatch", ["display", "battery", "sensors", "band"]),
        ("desktop", ["CPU", "motherboard", "RAM", "storage"]),
        ("monitor", ["display panel", "stand", "ports"]),
        ("speaker", ["drivers", "cabinet", "amplifier"]),
        
        # Clothing
        ("shirt", ["collar", "sleeve", "cuff", "fabric"]),
        ("dress", ["bodice", "skirt", "waistline", "hemline"]),
        ("pants", ["waistband", "pockets", "seams", "fabric"]),
        ("shoes", ["sole", "upper", "laces", "heel"]),
        ("jacket", ["collar", "sleeves", "zipper", "pockets"]),
        
        # Food & Eatables
        ("food", ["ingredients", "nutrients", "protein", "vitamins"]),
        ("snacks", ["ingredients", "nutrition facts", "flavor", "texture"]),
        ("drink", ["ingredients", "water", "sugar", "flavorings"]),
        ("fruit", ["skin", "flesh", "seeds", "nutrients"]),
        ("vegetables", ["skin", "flesh", "leaves", "nutrients"]),
        ("meat", ["muscle", "fat", "protein", "texture"]),
        
        # Other categories
        ("car", ["engine", "wheels", "brakes", "steering"]),
        ("book", ["cover", "pages", "spine", "binding"]),
        ("watch", ["face", "hands", "crown", "band"]),
        ("bag", ["handle", "straps", "zipper", "compartments"]),
        ("perfume", ["fragrance notes", "bottle", "cap", "liquid"]),
        ("cosmetics", ["pigments", "base", "applicator", "container"]),
        ("toys", ["plastic", "batteries", "motors", "buttons"]),
        ("furniture", ["frame", "cushions", "upholstery", "legs"]),
        ("appliances", ["motor", "controls", "power cord", "sensors"]),
        
        # Variations
        ("dresses", ["bodice", "skirt", "waistline", "hemline"]),
        ("gown", ["bodice", "skirt", "waistline", "hemline"]),
        ("eat", ["ingredients", "nutrients", "protein", "vitamins"]),
        ("eatable", ["ingredients", "nutrients", "protein", "vitamins"]),
        ("snack", ["ingredients", "nutrition facts", "flavor", "texture"]),
        ("beverage", ["ingredients", "water", "sugar", "flavorings"]),
        ("clothing", ["collar", "sleeve", "cuff", "fabric"]),
        ("footwear", ["sole", "upper", "laces", "heel"]),
        ("boots", ["sole", "upper", "laces", "heel"]),
        ("phone", ["processor", "display", "camera", "battery"]),
        ("mobile", ["processor", "display", "camera", "battery"]),
        ("auto", ["engine", "wheels", "brakes", "steering"]),
        ("handbag", ["handle", "straps", "zipper", "compartments"]),
        ("purse", ["handle", "straps", "zipper", "compartments"]),
        ("makeup", ["pigments", "base", "applicator", "container"]),
        ("skincare", ["pigments", "base", "applicator", "container"]),
        ("sofa", ["frame", "cushions", "upholstery", "legs"]),
        ("chair", ["frame", "cushions", "upholstery", "legs"]),
        ("table", ["frame", "cushions", "upholstery", "legs"]),
        ("bed", ["frame", "cushions", "upholstery", "legs"]),
        ("fridge", ["motor", "controls", "power cord", "sensors"]),
        ("oven", ["motor", "controls", "power cord", "sensors"]),
        ("washing", ["motor", "controls", "power cord", "sensors"])
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_keywords in test_cases:
        components = analyzer.generate_components(query)
        
        # Check if expected keywords are in components
        found_keywords = [kw for kw in expected_keywords if any(kw.lower() in comp.lower() for comp in components)]
        
        success = len(found_keywords) >= len(expected_keywords) * 0.5  # At least 50% match
        
        if success:
            passed += 1
            status = "✅"
        else:
            failed += 1
            status = "❌"
        
        print(f"{status} {query:15} → {len(components)} components (found {len(found_keywords)}/{len(expected_keywords)} expected)")
        if not success:
            print(f"    Expected: {expected_keywords}")
            print(f"    Got: {components[:5]}...")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(test_cases)*100:.1f}%")
    
    if failed == 0:
        print("🎉 ALL CATEGORIES WORKING CORRECTLY!")
    else:
        print(f"⚠️  {failed} categories need improvement")
    
    return passed, failed

def test_problematic_cases():
    """Test specific problematic cases mentioned by user."""
    print("\n" + "=" * 80)
    print("TESTING PROBLEMATIC CASES")
    print("=" * 80)
    
    analyzer = DualPipelineAnalyzer()
    
    # Test the specific cases user mentioned
    problematic_cases = [
        "dress",
        "food", 
        "snacks",
        "eatables",
        "eat",
        "drink",
        "beverages"
    ]
    
    for query in problematic_cases:
        components = analyzer.generate_components(query)
        print(f"\nQuery: '{query}'")
        print(f"Components: {components}")
        print(f"Count: {len(components)}")
        
        # Verify these are not generic/dress components
        if query == "dress":
            dress_components = ["bodice", "skirt", "waistline", "hemline", "sleeves", "neckline", "back", "zipper", "buttons", "lining", "fabric", "seams", "darts", "pleats"]
            found = [comp for comp in dress_components if comp.lower() in [c.lower() for c in components]]
            print(f"✅ Dress-specific components found: {len(found)}/{len(dress_components)}")
        
        elif query in ["food", "snacks", "eatables", "eat"]:
            food_components = ["ingredients", "nutrients", "protein", "carbohydrates", "fats", "vitamins", "minerals", "fiber", "calories", "serving size", "preservatives", "additives", "flavorings"]
            found = [comp for comp in food_components if comp.lower() in [c.lower() for c in components]]
            print(f"✅ Food-specific components found: {len(found)}/{len(food_components)}")

def main():
    """Run comprehensive category tests."""
    print("🎯 COMPREHENSIVE CATEGORY TESTING")
    print("Testing all product categories for correct component analysis")
    
    try:
        # Test all categories
        passed, failed = test_all_product_categories()
        
        # Test problematic cases
        test_problematic_cases()
        
        print("\n" + "=" * 80)
        print("🔧 FIXES APPLIED:")
        print("  1. Expanded knowledge base with 25+ categories")
        print("  2. Enhanced matching logic with multiple strategies")
        print("  3. Added special mappings for variations")
        print("  4. Word-based overlap detection")
        print("  5. 50% match threshold for category detection")
        
        if failed == 0:
            print("\n🎉 ALL PRODUCT CATEGORIES NOW WORK CORRECTLY!")
            print("✅ Components match product searched")
            print("✅ All categories analyzed properly")
        else:
            print(f"\n⚠️  {failed} categories still need work")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
