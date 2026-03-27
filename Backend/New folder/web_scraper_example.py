#!/usr/bin/env python3
"""
Example usage of the WebScraper module for Amazon product data extraction.

This script demonstrates how to use the web_scraper.py module to fetch
latest reviews and pricing from Amazon for competitive intelligence analysis.
"""

from web_scraper import WebScraper
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Main function demonstrating web scraping capabilities.
    """
    print("🕷️  Starting Amazon Web Scraping...")
    
    try:
        # Initialize scraper (use Selenium for dynamic content)
        with WebScraper(use_selenium=False, headless=True) as scraper:
            
            # Example 1: Search for specific products
            print("\n" + "="*60)
            print("🔍 PRODUCT SEARCH EXAMPLE")
            print("="*60)
            
            search_queries = [
                "Sony WH-1000XM4 headphones",
                "Bose QuietComfort headphones",
                "Apple AirPods Pro",
                "Samsung Galaxy Buds"
            ]
            
            for query in search_queries[:2]:  # Limit to 2 for demo
                print(f"\n📱 Searching for: {query}")
                products = scraper.search_amazon_product(query, max_results=3)
                
                print(f"   Found {len(products)} products:")
                for i, product in enumerate(products, 1):
                    print(f"   {i}. {product['title'][:60]}...")
                    print(f"      Price: ${product.get('price', 'N/A')}")
                    print(f"      Rating: {product.get('rating', 'N/A')}")
                    print(f"      Reviews: {product.get('num_reviews', 'N/A')}")
            
            # Example 2: Scrape complete product data with reviews
            print(f"\n" + "="*60)
            print("📊 COMPLETE PRODUCT SCRAPING EXAMPLE")
            print("="*60)
            
            # Scrape data for a specific product
            scraped_data = scraper.scrape_product_data(
                search_query="Sony WH-1000XM4 headphones",
                max_products=2,
                max_reviews_per_product=5
            )
            
            print(f"\n📈 Scraping Results:")
            print(f"   Products scraped: {len(scraped_data['products'])}")
            print(f"   Total reviews: {scraped_data['total_reviews']}")
            print(f"   Scraped at: {scraped_data['scraped_at']}")
            
            # Display sample product data
            print(f"\n📱 Sample Product Data:")
            for i, product in enumerate(scraped_data['products'], 1):
                print(f"\n   Product {i}:")
                print(f"      Title: {product['title']}")
                print(f"      Price: ${product.get('price', 'N/A')}")
                print(f"      Rating: {product.get('rating', 'N/A')}")
                print(f"      Reviews: {len(product.get('reviews', []))}")
                print(f"      URL: {product.get('url', 'N/A')}")
                
                # Show sample reviews
                reviews = product.get('reviews', [])
                if reviews:
                    print(f"      Sample Review:")
                    sample_review = reviews[0]
                    print(f"         Rating: {sample_review.get('rating', 'N/A')}")
                    print(f"         Date: {sample_review.get('date', 'N/A')}")
                    print(f"         Reviewer: {sample_review.get('reviewer', 'N/A')}")
                    review_text = sample_review.get('review_text', '')
                    if review_text:
                        preview = review_text[:100] + "..." if len(review_text) > 100 else review_text
                        print(f"         Text: {preview}")
            
            # Example 3: Batch scraping for multiple products
            print(f"\n" + "="*60)
            print("🔄 BATCH SCRAPING EXAMPLE")
            print("="*60)
            
            batch_queries = [
                "noise cancelling headphones",
                "wireless earbuds"
            ]
            
            all_scraped_data = []
            
            for query in batch_queries:
                print(f"\n📦 Batch scraping: {query}")
                try:
                    batch_data = scraper.scrape_product_data(
                        search_query=query,
                        max_products=2,
                        max_reviews_per_product=3
                    )
                    all_scraped_data.append(batch_data)
                    print(f"   ✅ Scraped {len(batch_data['products'])} products")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            # Save batch results
            if all_scraped_data:
                batch_filename = 'batch_scraped_data.json'
                with open(batch_filename, 'w', encoding='utf-8') as f:
                    json.dump(all_scraped_data, f, indent=2, ensure_ascii=False)
                print(f"   💾 Batch data saved to {batch_filename}")
            
            print(f"\n✅ Web scraping completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during web scraping: {e}")
        print("💡 Make sure you have the required dependencies installed:")
        print("   pip install requests beautifulsoup4 selenium")
        print("   For Selenium: Download ChromeDriver and add to PATH")

def analyze_scraped_data():
    """
    Analyze scraped data for insights.
    """
    print("\n" + "="*60)
    print("📊 SCRAPED DATA ANALYSIS")
    print("="*60)
    
    try:
        # Load the most recent scraped data
        with open('scraped_reviews.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            # Get the most recent scraping session
            latest_data = data[-1] if data[-1].get('scraped_at') else data[0]
        else:
            latest_data = data
        
        print(f"\n📈 Data Overview:")
        print(f"   Search Query: {latest_data.get('search_query', 'Unknown')}")
        print(f"   Scraped At: {latest_data.get('scraped_at', 'Unknown')}")
        print(f"   Products: {len(latest_data.get('products', []))}")
        print(f"   Total Reviews: {latest_data.get('total_reviews', 0)}")
        
        # Analyze product prices
        products = latest_data.get('products', [])
        prices = [p.get('price') for p in products if p.get('price')]
        
        if prices:
            print(f"\n💰 Price Analysis:")
            print(f"   Price Range: ${min(prices):.2f} - ${max(prices):.2f}")
            print(f"   Average Price: ${sum(prices)/len(prices):.2f}")
        
        # Analyze ratings
        ratings = [p.get('rating') for p in products if p.get('rating')]
        
        if ratings:
            print(f"\n⭐ Rating Analysis:")
            print(f"   Rating Range: {min(ratings):.1f} - {max(ratings):.1f}")
            print(f"   Average Rating: {sum(ratings)/len(ratings):.1f}")
        
        # Analyze review content
        all_reviews = []
        for product in products:
            reviews = product.get('reviews', [])
            all_reviews.extend(reviews)
        
        if all_reviews:
            print(f"\n📝 Review Analysis:")
            print(f"   Total Reviews: {len(all_reviews)}")
            
            # Rating distribution
            review_ratings = [r.get('rating') for r in all_reviews if r.get('rating')]
            if review_ratings:
                rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                for rating in review_ratings:
                    rating_dist[int(rating)] += 1
                
                print(f"   Rating Distribution:")
                for stars, count in rating_dist.items():
                    percentage = (count / len(review_ratings)) * 100
                    print(f"      {stars} stars: {count} ({percentage:.1f}%)")
            
            # Verified purchase rate
            verified_reviews = [r for r in all_reviews if r.get('verified_purchase')]
            if verified_reviews:
                verified_rate = (len(verified_reviews) / len(all_reviews)) * 100
                print(f"   Verified Purchase Rate: {verified_rate:.1f}%")
        
        print("="*60)
        
    except FileNotFoundError:
        print("❌ scraped_reviews.json not found. Run scraping first.")
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")

def demonstrate_scraping_techniques():
    """
    Demonstrate different scraping techniques.
    """
    print("\n" + "="*60)
    print("🔧 SCRAPING TECHNIQUES DEMONSTRATION")
    print("="*60)
    
    # Technique 1: Requests + BeautifulSoup (faster, limited to static content)
    print(f"\n1️⃣ REQUESTS + BEAUTIFULULSOUP:")
    print(f"   ✅ Fast and lightweight")
    print(f"   ✅ Good for static content")
    print(f"   ❌ Limited with dynamic/JavaScript content")
    print(f"   ❌ May be blocked by anti-bot measures")
    
    try:
        with WebScraper(use_selenium=False) as scraper:
            start_time = time.time()
            products = scraper.search_amazon_product("headphones", max_results=2)
            end_time = time.time()
            
            print(f"   ⏱️  Scraped {len(products)} products in {end_time - start_time:.2f} seconds")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Technique 2: Selenium (slower, handles dynamic content)
    print(f"\n2️⃣ SELENIUM:")
    print(f"   ✅ Handles dynamic/JavaScript content")
    print(f"   ✅ More robust against anti-bot measures")
    print(f"   ✅ Can interact with page elements")
    print(f"   ❌ Slower performance")
    print(f"   ❌ Requires browser/driver setup")
    
    # Only demonstrate Selenium if available
    try:
        from selenium import webdriver
        selenium_available = True
    except ImportError:
        selenium_available = False
    
    if selenium_available:
        try:
            with WebScraper(use_selenium=True, headless=True) as scraper:
                start_time = time.time()
                products = scraper.search_amazon_product("headphones", max_results=2)
                end_time = time.time()
                
                print(f"   ⏱️  Scraped {len(products)} products in {end_time - start_time:.2f} seconds")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print(f"   ⚠️  Selenium not available - install with: pip install selenium")
    
    print(f"\n💡 RECOMMENDATION:")
    print(f"   • Use Requests + BeautifulSoup for simple, static content")
    print(f"   • Use Selenium for complex, dynamic content")
    print(f"   • Consider rate limiting and delays to avoid blocking")
    print(f"   • Respect robots.txt and terms of service")

def export_scraped_data():
    """
    Export scraped data in different formats.
    """
    print("\n" + "="*60)
    print("📤 EXPORTING SCRAPED DATA")
    print("="*60)
    
    try:
        # Load scraped data
        with open('scraped_reviews.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            latest_data = data[-1] if data[-1].get('scraped_at') else data[0]
        else:
            latest_data = data
        
        # Export to CSV (products only)
        import csv
        
        products = latest_data.get('products', [])
        
        if products:
            with open('scraped_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['title', 'price', 'rating', 'num_reviews', 'url', 'scraped_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for product in products:
                    writer.writerow({
                        'title': product.get('title', ''),
                        'price': product.get('price', ''),
                        'rating': product.get('rating', ''),
                        'num_reviews': product.get('num_reviews', ''),
                        'url': product.get('url', ''),
                        'scraped_at': product.get('scraped_at', '')
                    })
            
            print(f"✅ Products exported to scraped_products.csv")
        
        # Export reviews to separate CSV
        all_reviews = []
        for product in products:
            reviews = product.get('reviews', [])
            for review in reviews:
                review['product_title'] = product.get('title', '')
                all_reviews.append(review)
        
        if all_reviews:
            with open('scraped_reviews.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['product_title', 'rating', 'title', 'review_text', 'date', 'reviewer', 'verified_purchase', 'scraped_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for review in all_reviews:
                    writer.writerow(review)
            
            print(f"✅ Reviews exported to scraped_reviews.csv")
        
        # Export summary report
        with open('scraping_summary.txt', 'w', encoding='utf-8') as f:
            f.write("WEB SCRAPING SUMMARY REPORT\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Search Query: {latest_data.get('search_query', 'Unknown')}\n")
            f.write(f"Scraped At: {latest_data.get('scraped_at', 'Unknown')}\n")
            f.write(f"Products Found: {len(products)}\n")
            f.write(f"Total Reviews: {latest_data.get('total_reviews', 0)}\n\n")
            
            f.write("PRODUCTS:\n")
            f.write("-" * 20 + "\n")
            for i, product in enumerate(products, 1):
                f.write(f"{i}. {product.get('title', 'Unknown')}\n")
                f.write(f"   Price: ${product.get('price', 'N/A')}\n")
                f.write(f"   Rating: {product.get('rating', 'N/A')}\n")
                f.write(f"   Reviews: {len(product.get('reviews', []))}\n\n")
        
        print(f"✅ Summary report exported to scraping_summary.txt")
        
    except FileNotFoundError:
        print("❌ scraped_reviews.json not found. Run scraping first.")
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

def show_scraping_best_practices():
    """
    Display web scraping best practices and legal considerations.
    """
    print("\n" + "="*60)
    print("📚 WEB SCRAPING BEST PRACTICES")
    print("="*60)
    
    print(f"\n⚖️  LEGAL CONSIDERATIONS:")
    print(f"   • Always check website's robots.txt file")
    print(f"   • Respect terms of service and usage policies")
    print(f"   • Don't overload servers with too many requests")
    print(f"   • Consider copyright and data usage rights")
    print(f"   • Identify yourself with appropriate User-Agent")
    
    print(f"\n🔒 TECHNICAL BEST PRACTICES:")
    print(f"   • Use random delays between requests (2-5 seconds)")
    print(f"   • Rotate User-Agent strings if needed")
    print(f"   • Handle errors gracefully and retry failed requests")
    print(f"   • Use session management for connection pooling")
    print(f"   • Implement proper exception handling")
    
    print(f"\n🛡️  ANTI-BOT MITIGATION:")
    print(f"   • Mimic human browsing behavior")
    print(f"   • Use realistic headers and User-Agent")
    print(f"   • Avoid predictable request patterns")
    print(f"   • Handle CAPTCHAs if encountered")
    print(f"   • Consider proxy rotation for large-scale scraping")
    
    print(f"\n📊 DATA QUALITY:")
    print(f"   • Validate extracted data formats")
    print(f"   • Handle missing or malformed data")
    print(f"   • Log scraping errors and warnings")
    print(f"   • Implement data deduplication")
    print(f"   • Store metadata (scraping timestamp, source, etc.)")
    
    print(f"\n⚡ PERFORMANCE OPTIMIZATION:")
    print(f"   • Use connection pooling")
    print(f"   • Cache repeated requests when appropriate")
    print(f"   • Parallelize independent requests")
    print(f"   • Use efficient parsing libraries")
    print(f"   • Monitor memory usage for large datasets")
    
    print(f"\n🔧 MAINTENANCE:")
    print(f"   • Monitor for website structure changes")
    print(f"   • Update selectors when layouts change")
    print(f"   • Implement health checks for scraping pipeline")
    print(f"   • Log scraping statistics and success rates")
    print(f"   • Plan for API alternatives when available")

if __name__ == "__main__":
    import time
    
    # Run main scraping demonstration
    main()
    
    # Analyze scraped data
    analyze_scraped_data()
    
    # Demonstrate scraping techniques
    demonstrate_scraping_techniques()
    
    # Export scraped data
    export_scraped_data()
    
    # Show best practices
    show_scraping_best_practices()
