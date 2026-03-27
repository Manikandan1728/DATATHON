"""
test_specific_products.py
Test the specific products mentioned by user
"""
import sys
import os

# Add Backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dual_pipeline_analyzer import DualPipelineAnalyzer

def test_specific_products():
    """Test the specific products mentioned by user."""
    print("=" * 80)
    print("🎯 TESTING SPECIFIC PRODUCTS MENTIONED BY USER")
    print("=" * 80)
    print("Testing: desk, water bottle, cupboard, wardrobe, toothbrush, noodles, cooker, broom stick")
    print()
    
    analyzer = DualPipelineAnalyzer()
    
    # Test the problematic products
    test_products = [
        "desk",
        "water bottle", 
        "cupboard",
        "wardrobe",
        "toothbrush",
        "noodles",
        "cooker",
        "broom stick"
    ]
    
    for product in test_products:
        components = analyzer.generate_components(product)
        print(f"📦 {product:20} → {len(components)} components")
        print(f"   {', '.join(components[:10])}{'...' if len(components) > 10 else ''}")
        print()
    
    print("=" * 80)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_specific_products()
