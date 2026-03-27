#!/usr/bin/env python3
"""
Example usage of the DatasetLoader module for AI Competitive Intelligence System.

This script demonstrates how to use the dataset_loader.py module to process
Amazon electronics datasets and generate structured competitive intelligence data.
"""

from dataset_loader import DatasetLoader
import json

def main():
    """
    Main function demonstrating dataset loading and processing.
    """
    print("🚀 Starting AI Competitive Intelligence Dataset Processing...")
    
    # Initialize the dataset loader
    loader = DatasetLoader()
    
    # Define your dataset file paths here
    # Replace these with your actual file paths
    file_paths = {
        'amazon_electronics_master_dataset': 'data/amazon_electronics_master_dataset.csv',
        'amazon_electronics_reviews_cleaned': 'data/amazon_electronics_reviews_cleaned.csv',
        'amazon_reviews_cleaned_4M': 'data/amazon_reviews_cleaned_4M.csv'
    }
    
    try:
        # Process all datasets
        print("📊 Processing datasets...")
        processed_data = loader.process_all_datasets(file_paths)
        
        # Display summary statistics
        print("\n✅ Processing completed successfully!")
        print("\n📈 Dataset Summary:")
        print(f"Total categories: {len(processed_data)}")
        
        total_products = 0
        total_reviews = 0
        
        for category, products in processed_data.items():
            product_count = len(products)
            review_count = sum(len(product_info['reviews']) for product_info in products.values())
            total_products += product_count
            total_reviews += review_count
            
            print(f"  📁 {category}: {product_count} products, {review_count} reviews")
        
        print(f"\n📊 Overall Statistics:")
        print(f"  Total Products: {total_products}")
        print(f"  Total Reviews: {total_reviews}")
        
        # Show sample data structure
        print("\n🔍 Sample Data Structure:")
        if processed_data:
            first_category = list(processed_data.keys())[0]
            category_data = processed_data[first_category]
            
            if category_data:
                first_product = list(category_data.keys())[0]
                product_info = category_data[first_product]
                
                print(f"Category: {first_category}")
                print(f"Product: {first_product}")
                print(f"Brand: {product_info['brand']}")
                print(f"Number of Reviews: {len(product_info['reviews'])}")
                
                if product_info['reviews']:
                    sample_review = product_info['reviews'][0]
                    print(f"Sample Review:")
                    print(f"  Rating: {sample_review['rating']}")
                    print(f"  Date: {sample_review['review_date']}")
                    print(f"  Text: {sample_review['review_text'][:100]}...")
        
        print(f"\n💾 Processed data saved to: processed_product_reviews.json")
        
        # Optional: Load and display the saved JSON file
        try:
            with open('processed_product_reviews.json', 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            print(f"✅ Verified: JSON file contains {len(saved_data)} categories")
        except Exception as e:
            print(f"⚠️  Warning: Could not verify saved JSON file: {e}")
            
    except FileNotFoundError as e:
        print(f"❌ Error: Dataset file not found - {e}")
        print("\n💡 Please ensure your dataset files are in the correct locations:")
        for dataset_name, path in file_paths.items():
            print(f"  - {dataset_name}: {path}")
        print("\n📝 Update the file_paths dictionary in this script with your actual file locations.")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        print("\n🔧 Please check your dataset files and try again.")

def analyze_competitive_intelligence(processed_data_file='processed_product_reviews.json'):
    """
    Additional function to analyze the processed competitive intelligence data.
    
    Args:
        processed_data_file: Path to the processed JSON file
    """
    try:
        with open(processed_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n🧠 Competitive Intelligence Analysis:")
        
        # Brand analysis by category
        for category, products in data.items():
            print(f"\n📊 {category} Market Analysis:")
            
            brand_counts = {}
            brand_rating_totals = {}
            brand_review_counts = {}
            
            for product_info in products.values():
                brand = product_info['brand']
                reviews = product_info['reviews']
                
                # Count products per brand
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
                
                # Calculate average rating per brand
                if reviews:
                    total_rating = sum(review['rating'] for review in reviews)
                    brand_rating_totals[brand] = brand_rating_totals.get(brand, 0) + total_rating
                    brand_review_counts[brand] = brand_review_counts.get(brand, 0) + len(reviews)
            
            # Display brand rankings
            sorted_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)
            
            print("  Brand Rankings (by product count):")
            for i, (brand, count) in enumerate(sorted_brands[:5], 1):
                avg_rating = 0
                if brand in brand_rating_totals and brand in brand_review_counts:
                    avg_rating = brand_rating_totals[brand] / brand_review_counts[brand]
                
                print(f"    {i}. {brand}: {count} products (avg rating: {avg_rating:.1f}⭐)")
                
    except FileNotFoundError:
        print(f"❌ Analysis file not found: {processed_data_file}")
        print("💡 Please run the main processing function first.")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    # Run the main processing
    main()
    
    # Optional: Run competitive intelligence analysis
    # analyze_competitive_intelligence()
