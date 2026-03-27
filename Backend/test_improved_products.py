"""
test_improved_products.py
Test the products that were previously failing
"""
import sys
import os

# Add Backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_pipeline_analyzer import DualPipelineAnalyzer

def test_improved_products():
    """Test products that were previously failing."""
    print("=" * 80)
    print("🔧 TESTING PREVIOUSLY FAILING PRODUCTS")
    print("=" * 80)
    print("Testing products that were getting default components...")
    print()
    
    analyzer = DualPipelineAnalyzer()
    
    # Test products that were failing before
    failing_products = [
        "stapler", "paper clips", "binders", "file folders", "pens", "markers", 
        "highlighters", "scissors", "calculator", "phone case", "screen protector", 
        "charger", "power bank", "wireless charger", "luggage", "suitcase", 
        "travel pillow", "travel organizer", "toiletry bag", "passport holder",
        "christmas lights", "decorations", "holiday ornaments", "wreath", 
        "garland", "bag", "handbag", "purse", "wallet", "watch", "timepiece"
    ]
    
    success_count = 0
    total_count = len(failing_products)
    
    for i, product in enumerate(failing_products, 1):
        components = analyzer.generate_components(product)
        
        # Check if we got meaningful components (not just defaults)
        if components and len(components) > 5:  # Most products should have more than 5 components
            success_count += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{i:2d}. {status} {product:25} → {len(components):2d} components")
        
        # Show first few components for verification
        if components:
            preview = ", ".join(components[:3])
            if len(components) > 3:
                preview += "..."
            print(f"      {preview}")
    
    print()
    print("=" * 80)
    print(f"📊 RESULTS: {success_count}/{total_count} products now working correctly ({success_count/total_count*100:.1f}%)")
    print("=" * 80)
    
    if success_count == total_count:
        print("🎉 ALL PREVIOUSLY FAILING PRODUCTS NOW WORK!")
    else:
        print(f"⚠️  {total_count - success_count} products still need work")
    
    print()
    print("🎯 IMPROVEMENT SUMMARY:")
    print("   ✅ Added office supplies components")
    print("   ✅ Added bags and accessories components") 
    print("   ✅ Added electronics accessories components")
    print("   ✅ Added travel accessories components")
    print("   ✅ Added seasonal & holiday components")
    print("   ✅ Added watch components")

if __name__ == "__main__":
    test_improved_products()
