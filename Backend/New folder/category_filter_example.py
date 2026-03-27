#!/usr/bin/env python3
"""
Example usage of the CategoryFilter module for filtering electronics products.

This script demonstrates how to use the category_filter.py module to filter
processed product data into key categories for competitive intelligence analysis.
"""

from category_filter import CategoryFilter
import json

def main():
    """
    Main function demonstrating category filtering.
    """
    print("🔍 Starting Category Filtering for Electronics Products...")
    
    # Initialize the category filter
    filter = CategoryFilter()
    
    try:
        # Process categories with custom parameters
        print("📊 Filtering categories...")
        filtered_data = filter.process_categories(
            input_file='processed_product_reviews.json',
            output_file='category_products.json',
            min_brands=2,           # Keep at least 2 brands per category
            max_brands=5,           # Maximum 5 brands per category
            max_products_per_brand=3  # Top 3 products per brand
        )
        
        print("\n✅ Category filtering completed successfully!")
        
        # Display detailed results
        display_filtered_results(filtered_data)
        
        # Analyze brand diversity
        analyze_brand_diversity(filtered_data)
        
        # Show sample products from each category
        show_sample_products(filtered_data)
        
    except FileNotFoundError:
        print("❌ Error: processed_product_reviews.json not found!")
        print("💡 Please run the dataset_loader.py first to generate the processed data file.")
        
    except Exception as e:
        print(f"❌ Error during category filtering: {e}")
        print("🔧 Please check your input data and try again.")

def display_filtered_results(filtered_data):
    """
    Display detailed results of the filtering process.
    
    Args:
        filtered_data: The filtered category data
    """
    print("\n" + "="*60)
    print("📊 DETAILED FILTERING RESULTS")
    print("="*60)
    
    total_categories = len(filtered_data)
    total_products = sum(len(products) for products in filtered_data.values())
    all_brands = set()
    
    for category, products in filtered_data.items():
        brands = set(info['brand'] for info in products.values())
        all_brands.update(brands)
        
        print(f"\n📁 {category.upper()}")
        print(f"   📦 Products: {len(products)}")
        print(f"   🏷️  Brands: {len(brands)}")
        print(f"   🏷️  Brand List: {', '.join(sorted(brands))}")
        
        # Calculate category statistics
        total_reviews = sum(len(info.get('reviews', [])) for info in products.values())
        avg_reviews_per_product = total_reviews / len(products) if products else 0
        
        print(f"   📝 Total Reviews: {total_reviews}")
        print(f"   📈 Avg Reviews/Product: {avg_reviews_per_product:.1f}")
    
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"   Categories: {total_categories}")
    print(f"   Products: {total_products}")
    print(f"   Unique Brands: {len(all_brands)}")
    print("="*60)

def analyze_brand_diversity(filtered_data):
    """
    Analyze brand diversity across categories.
    
    Args:
        filtered_data: The filtered category data
    """
    print("\n" + "="*60)
    print("🏢 BRAND DIVERSITY ANALYSIS")
    print("="*60)
    
    # Track brands across categories
    brand_categories = {}
    category_brands = {}
    
    for category, products in filtered_data.items():
        brands = set(info['brand'] for info in products.values())
        category_brands[category] = brands
        
        for brand in brands:
            if brand not in brand_categories:
                brand_categories[brand] = set()
            brand_categories[brand].add(category)
    
    # Brands appearing in multiple categories
    multi_category_brands = {brand: cats for brand, cats in brand_categories.items() if len(cats) > 1}
    
    print(f"\n🏢 BRANDS ACROSS MULTIPLE CATEGORIES:")
    for brand, categories in sorted(multi_category_brands.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   {brand}: {', '.join(sorted(categories))}")
    
    # Category-specific brands
    print(f"\n🎯 CATEGORY-SPECIFIC BRANDS:")
    for category, brands in category_brands.items():
        specific_brands = [brand for brand in brands if len(brand_categories[brand]) == 1]
        if specific_brands:
            print(f"   {category}: {', '.join(sorted(specific_brands))}")
    
    print("="*60)

def show_sample_products(filtered_data):
    """
    Show sample products from each category.
    
    Args:
        filtered_data: The filtered category data
    """
    print("\n" + "="*60)
    print("🔍 SAMPLE PRODUCTS BY CATEGORY")
    print("="*60)
    
    for category, products in filtered_data.items():
        print(f"\n📁 {category.upper()} - TOP PRODUCTS:")
        
        # Sort products by review count
        sorted_products = sorted(
            products.items(),
            key=lambda x: len(x[1].get('reviews', [])),
            reverse=True
        )
        
        for i, (product_name, product_info) in enumerate(sorted_products[:3], 1):
            brand = product_info.get('brand', 'Unknown')
            reviews = product_info.get('reviews', [])
            review_count = len(reviews)
            
            # Calculate average rating
            avg_rating = 0
            if reviews:
                ratings = [r.get('rating', 0) for r in reviews if r.get('rating')]
                if ratings:
                    avg_rating = sum(ratings) / len(ratings)
            
            print(f"   {i}. {brand} {product_name}")
            print(f"      📝 Reviews: {review_count}")
            print(f"      ⭐ Avg Rating: {avg_rating:.1f}")
            
            # Show sample review text
            if reviews:
                sample_review = reviews[0].get('review_text', '')
                if sample_review:
                    preview = sample_review[:100] + "..." if len(sample_review) > 100 else sample_review
                    print(f"      💬 Sample: '{preview}'")
    
    print("="*60)

def validate_filtering_results():
    """
    Validate that filtering results meet requirements.
    """
    print("\n" + "="*60)
    print("✅ FILTERING VALIDATION")
    print("="*60)
    
    try:
        with open('category_products.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_categories = {'Headphones', 'Smartphones', 'Laptops', 'Smartwatches', 'Speakers'}
        found_categories = set(data.keys())
        
        print(f"\n📋 CATEGORY VALIDATION:")
        print(f"   Required: {required_categories}")
        print(f"   Found: {found_categories}")
        
        missing = required_categories - found_categories
        if missing:
            print(f"   ❌ Missing categories: {missing}")
        else:
            print(f"   ✅ All required categories present")
        
        print(f"\n🏷️ BRAND VALIDATION:")
        for category in required_categories:
            if category in data:
                brands = set(info['brand'] for info in data[category].values())
                brand_count = len(brands)
                
                if brand_count >= 2:
                    print(f"   ✅ {category}: {brand_count} brands ({', '.join(sorted(brands))})")
                else:
                    print(f"   ❌ {category}: Only {brand_count} brand(s) - needs at least 2")
            else:
                print(f"   ❌ {category}: Category not found")
        
        print("="*60)
        
    except FileNotFoundError:
        print("❌ category_products.json not found for validation")
    except Exception as e:
        print(f"❌ Error during validation: {e}")

if __name__ == "__main__":
    # Run main filtering process
    main()
    
    # Validate results
    validate_filtering_results()
