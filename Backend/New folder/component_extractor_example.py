#!/usr/bin/env python3
"""
Example usage of the ComponentExtractor module for extracting product components from reviews.

This script demonstrates how to use the component_extractor.py module to identify
product components mentioned in reviews for competitive intelligence analysis.
"""

from component_extractor import ComponentExtractor
import json

def main():
    """
    Main function demonstrating component extraction.
    """
    print("🔧 Starting Component Extraction from Product Reviews...")
    
    # Initialize the component extractor
    extractor = ComponentExtractor()
    
    try:
        # Process components with custom parameters
        print("📊 Extracting components from reviews...")
        component_data = extractor.process_components(
            input_file='category_products.json',
            output_file='component_reviews.json',
            min_reviews_per_component=3,  # Lower threshold for demo
            enhance_detection=True
        )
        
        print("\n✅ Component extraction completed successfully!")
        
        # Display detailed results
        display_component_results(component_data)
        
        # Analyze component coverage
        analyze_component_coverage(component_data)
        
        # Show sample component reviews
        show_sample_component_reviews(component_data)
        
        # Generate component insights
        generate_component_insights(component_data)
        
    except FileNotFoundError:
        print("❌ Error: category_products.json not found!")
        print("💡 Please run the dataset_loader.py and category_filter.py first to generate the required data files.")
        
    except Exception as e:
        print(f"❌ Error during component extraction: {e}")
        print("🔧 Please check your input data and try again.")

def display_component_results(component_data):
    """
    Display detailed results of the component extraction.
    
    Args:
        component_data: The extracted component data
    """
    print("\n" + "="*60)
    print("🔧 DETAILED COMPONENT EXTRACTION RESULTS")
    print("="*60)
    
    total_products = len(component_data)
    total_components = 0
    total_reviews = 0
    component_stats = {}
    
    for product_name, components in component_data.items():
        for component, reviews in components.items():
            total_components += 1
            total_reviews += len(reviews)
            
            if component not in component_stats:
                component_stats[component] = {'products': 0, 'reviews': 0}
            component_stats[component]['products'] += 1
            component_stats[component]['reviews'] += len(reviews)
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Products with component data: {total_products}")
    print(f"   Total component types: {total_components}")
    print(f"   Total component reviews: {total_reviews}")
    
    print(f"\n🔧 COMPONENT BREAKDOWN:")
    sorted_components = sorted(component_stats.items(), key=lambda x: x[1]['reviews'], reverse=True)
    for component, stats in sorted_components:
        print(f"   {component}: {stats['products']} products, {stats['reviews']} reviews")
    
    print("="*60)

def analyze_component_coverage(component_data):
    """
    Analyze component coverage across products and categories.
    
    Args:
        component_data: The extracted component data
    """
    print("\n" + "="*60)
    print("📈 COMPONENT COVERAGE ANALYSIS")
    print("="*60)
    
    # Load category data for context
    try:
        with open('category_products.json', 'r', encoding='utf-8') as f:
            category_data = json.load(f)
    except:
        print("❌ Could not load category_products.json for analysis")
        return
    
    # Analyze coverage by category
    category_component_coverage = {}
    
    for category, products in category_data.items():
        total_products = len(products)
        products_with_components = 0
        component_distribution = {}
        
        for product_name in products.keys():
            if product_name in component_data:
                products_with_components += 1
                
                for component in component_data[product_name].keys():
                    if component not in component_distribution:
                        component_distribution[component] = 0
                    component_distribution[component] += 1
        
        coverage_rate = (products_with_components / total_products) * 100 if total_products > 0 else 0
        category_component_coverage[category] = {
            'total_products': total_products,
            'products_with_components': products_with_components,
            'coverage_rate': coverage_rate,
            'component_distribution': component_distribution
        }
    
    print(f"\n📁 COVERAGE BY CATEGORY:")
    for category, coverage in category_component_coverage.items():
        print(f"\n📂 {category}:")
        print(f"   Coverage: {coverage['coverage_rate']:.1f}% ({coverage['products_with_components']}/{coverage['total_products']} products)")
        
        if coverage['component_distribution']:
            print(f"   Top Components:")
            sorted_components = sorted(coverage['component_distribution'].items(), 
                                     key=lambda x: x[1], reverse=True)
            for component, count in sorted_components[:5]:
                print(f"     - {component}: {count} products")
        else:
            print(f"   No components found")
    
    print("="*60)

def show_sample_component_reviews(component_data):
    """
    Show sample reviews for each component type.
    
    Args:
        component_data: The extracted component data
    """
    print("\n" + "="*60)
    print("💬 SAMPLE COMPONENT REVIEWS")
    print("="*60)
    
    # Collect all reviews by component
    component_reviews = {}
    
    for product_name, components in component_data.items():
        for component, reviews in components.items():
            if component not in component_reviews:
                component_reviews[component] = []
            
            for review in reviews:
                component_reviews[component].append({
                    'product': product_name,
                    'review': review
                })
    
    # Show samples for each component
    for component, reviews in component_reviews.items():
        print(f"\n🔧 {component.upper()} REVIEWS:")
        
        # Show top 3 reviews for this component
        for i, review_data in enumerate(reviews[:3], 1):
            product = review_data['product']
            review_text = review_data['review']
            
            # Truncate long reviews
            if len(review_text) > 150:
                review_text = review_text[:150] + "..."
            
            print(f"   {i}. [{product}] {review_text}")
        
        if len(reviews) > 3:
            print(f"   ... and {len(reviews) - 3} more reviews")
    
    print("="*60)

def generate_component_insights(component_data):
    """
    Generate insights from component analysis.
    
    Args:
        component_data: The extracted component data
    """
    print("\n" + "="*60)
    print("🧠 COMPONENT INSIGHTS")
    print("="*60)
    
    # Most discussed components
    component_review_counts = {}
    for product_name, components in component_data.items():
        for component, reviews in components.items():
            if component not in component_review_counts:
                component_review_counts[component] = 0
            component_review_counts[component] += len(reviews)
    
    print(f"\n🏆 MOST DISCUSSED COMPONENTS:")
    sorted_components = sorted(component_review_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (component, count) in enumerate(sorted_components[:5], 1):
        print(f"   {i}. {component}: {count} reviews")
    
    # Products with most component coverage
    product_component_counts = {}
    for product_name, components in component_data.items():
        product_component_counts[product_name] = len(components)
    
    print(f"\n📱 PRODUCTS WITH MOST COMPONENT COVERAGE:")
    sorted_products = sorted(product_component_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (product, count) in enumerate(sorted_products[:5], 1):
        print(f"   {i}. {product}: {count} components")
    
    # Component diversity analysis
    component_diversity = {}
    for product_name, components in component_data.items():
        total_reviews = sum(len(reviews) for reviews in components.values())
        component_diversity[product_name] = {
            'component_count': len(components),
            'total_reviews': total_reviews,
            'avg_reviews_per_component': total_reviews / len(components) if components else 0
        }
    
    print(f"\n🎯 COMPONENT DIVERSITY LEADERS:")
    diversity_sorted = sorted(component_diversity.items(), 
                           key=lambda x: x[1]['avg_reviews_per_component'], 
                           reverse=True)
    
    for i, (product, stats) in enumerate(diversity_sorted[:5], 1):
        print(f"   {i}. {product}: {stats['component_count']} components, "
              f"{stats['avg_reviews_per_component']:.1f} avg reviews/component")
    
    print("="*60)

def validate_component_extraction():
    """
    Validate that component extraction results meet expectations.
    """
    print("\n" + "="*60)
    print("✅ COMPONENT EXTRACTION VALIDATION")
    print("="*60)
    
    try:
        with open('component_reviews.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📋 VALIDATION RESULTS:")
        print(f"   Products with component data: {len(data)}")
        
        # Check for expected components
        expected_components = {
            'sound', 'battery', 'comfort', 'camera', 'display', 
            'processor', 'design', 'price', 'build_quality'
        }
        
        found_components = set()
        for product_name, components in data.items():
            found_components.update(components.keys())
        
        print(f"   Expected components: {len(expected_components)}")
        print(f"   Found components: {len(found_components)}")
        
        missing = expected_components - found_components
        if missing:
            print(f"   ⚠️  Missing components: {missing}")
        else:
            print(f"   ✅ All expected component types found")
        
        # Check review distribution
        total_reviews = sum(len(reviews) for components in data.values() for reviews in components.values())
        print(f"   Total component reviews: {total_reviews}")
        
        if total_reviews > 0:
            avg_reviews_per_product = total_reviews / len(data)
            print(f"   Average reviews per product: {avg_reviews_per_product:.1f}")
        
        print("="*60)
        
    except FileNotFoundError:
        print("❌ component_reviews.json not found for validation")
    except Exception as e:
        print(f"❌ Error during validation: {e}")

if __name__ == "__main__":
    # Run main extraction process
    main()
    
    # Validate results
    validate_component_extraction()
