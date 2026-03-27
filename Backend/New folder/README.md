# Dataset Loader for AI Competitive Intelligence System

This Python module provides comprehensive functionality to load, process, and merge Amazon electronics datasets for competitive intelligence analysis.

## Features

- **Multi-dataset loading**: Supports loading three Amazon datasets simultaneously
- **Smart column detection**: Automatically detects and renames columns to standard names
- **Data cleaning**: Removes invalid reviews and handles missing data
- **Brand normalization**: Standardizes brand names (Sony, SONY → Sony)
- **Category extraction**: Identifies product categories using keyword matching
- **Structured output**: Produces nested JSON structure for easy analysis

## Supported Datasets

1. `amazon_electronics_master_dataset`
2. `amazon_electronics_reviews_cleaned`
3. `amazon_reviews_cleaned_4M`

## Product Categories

- Headphones
- Smartphones
- Laptops
- Speakers
- Smartwatches
- Other (fallback category)

## Usage

```python
from main_pipeline import MainPipeline

# Run the complete competitive intelligence pipeline
pipeline = MainPipeline()
results = pipeline.run_complete_pipeline()

# Access results
processed_data = results["processed_data"]
competitor_analysis = results["competitor_data"]
strategic_recommendations = results["strategy_data"]
```

### Individual Module Usage

```python
from dataset_loader import DatasetLoader
from category_filter import CategoryFilter
from component_extractor import ComponentExtractor
from sentiment_engine import SentimentEngine
from competitor_intelligence import CompetitorIntelligence
from review_intelligence import ReviewIntelligence
from strategy_engine import StrategyEngine
from executive_report import ExecutiveReport
from web_scraper import WebScraper

# Initialize and process datasets
loader = DatasetLoader()
file_paths = {
    'amazon_electronics_master_dataset': 'path/to/amazon_electronics_master_dataset.csv',
    'amazon_electronics_reviews_cleaned': 'path/to/amazon_electronics_reviews_cleaned.csv',
    'amazon_reviews_cleaned_4M': 'path/to/amazon_reviews_cleaned_4M.csv'
}
processed_data = loader.process_all_datasets(file_paths)

# Filter categories
filter = CategoryFilter()
filtered_data = filter.process_categories(
    input_file='processed_product_reviews.json',
    output_file='category_products.json',
    min_brands=2,
    max_brands=5,
    max_products_per_brand=3
)

# Extract components from reviews
extractor = ComponentExtractor()
component_data = extractor.process_components(
    input_file='category_products.json',
    output_file='component_reviews.json',
    min_reviews_per_component=5,
    enhance_detection=True
)

# Analyze sentiment for components
engine = SentimentEngine(model_type='auto')
sentiment_scores = engine.process_sentiments(
    input_file='component_reviews.json',
    output_file='component_sentiment_scores.json',
    model_type='auto',
    enhance_analysis=True
)

# Generate competitor intelligence
intelligence = CompetitorIntelligence()
competitor_analysis = intelligence.process_competitor_intelligence(
    input_file='component_sentiment_scores.json',
    output_file='competitor_analysis.json'
)

# Analyze customer complaints
review_intel = ReviewIntelligence()
complaint_analysis = review_intel.process_review_intelligence(
    component_file='component_reviews.json',
    sentiment_file='component_sentiment_scores.json',
    output_file='review_intelligence.json'
)

# Generate strategic recommendations
strategy_engine = StrategyEngine()
strategic_recommendations = strategy_engine.process_strategy_engine(
    competitor_file='competitor_analysis.json',
    review_file='review_intelligence.json',
    output_file='strategic_recommendations.json'
)

# Generate executive reports
executive = ExecutiveReport()
executive_reports = executive.process_executive_reports(
    competitor_file='competitor_analysis.json',
    review_file='review_intelligence.json',
    strategy_file='strategic_recommendations.json',
    output_file='executive_reports.json'
)

# Scrape latest Amazon data
with WebScraper(use_selenium=False) as scraper:
    scraped_data = scraper.scrape_product_data(
        search_query="Sony WH-1000XM4 headphones",
        max_products=3,
        max_reviews_per_product=10
    )

# Access executive report for a specific brand
sony_report = executive.get_brand_report('Sony', 'Headphones')
print(sony_report)
```

## Output Structure

The processed data is saved as `processed_product_reviews.json` with the following structure:

```json
{
  "Headphones": {
    "Sony WH-1000XM4": {
      "brand": "Sony",
      "reviews": [
        {
          "review_text": "Excellent noise cancellation...",
          "rating": 5,
          "review_date": "2023-01-15"
        }
      ]
    }
  },
  "Smartphones": {
    "iPhone 14 Pro": {
      "brand": "Apple",
      "reviews": [...]
    }
  }
}
```

The filtered data is saved as `category_products.json` with the same structure but containing only the 5 target categories and at least 2 brands per category:

```json
{
  "Headphones": {
    "Sony WH-1000XM4": {
      "brand": "Sony",
      "reviews": [...]
    },
    "Bose QuietComfort": {
      "brand": "Bose", 
      "reviews": [...]
    }
  },
  "Smartphones": {
    "Samsung Galaxy S23": {
      "brand": "Samsung",
      "reviews": [...]
    },
    "Apple iPhone 14": {
      "brand": "Apple",
      "reviews": [...]
    }
  }
}
```

The component data is saved as `component_reviews.json` with the following structure:

```json
{
  "Sony WH-1000XM4": {
    "sound": [
      "The sound quality is amazing with deep bass...",
      "Crystal clear audio with excellent noise cancellation..."
    ],
    "battery": [
      "Battery lasts about 30 hours with noise cancellation on...",
      "Quick charging is a great feature..."
    ],
    "comfort": [
      "Very comfortable for long listening sessions...",
      "The ear cushions are soft and don't cause pressure..."
    ]
  },
  "Apple iPhone 14": {
    "camera": [
      "The camera takes stunning photos in low light...",
      "Video quality is exceptional with smooth stabilization..."
    ],
    "battery": [
      "Battery life improved significantly from previous models...",
      "All-day battery life with moderate usage..."
    ]
  }
}
```

The sentiment scores are saved as `component_sentiment_scores.json` with the following structure:

```json
{
  "Headphones": {
    "sound": {
      "Sony": 0.85,
      "Bose": 0.78,
      "JBL": 0.42
    },
    "battery": {
      "Sony": 0.91,
      "Bose": 0.65,
      "JBL": -0.12
    },
    "comfort": {
      "Sony": 0.73,
      "Bose": 0.89,
      "JBL": 0.34
    }
  },
  "Smartphones": {
    "camera": {
      "Apple": 0.92,
      "Samsung": 0.87,
      "Google": 0.81
    },
    "battery": {
      "Apple": 0.45,
      "Samsung": 0.67,
      "Google": 0.38
    }
  }
}
```

The competitor analysis is saved as `competitor_analysis.json` with comprehensive competitive intelligence:

```json
{
  "category_analysis": {
    "Headphones": {
      "performance_table": "HEADPHONES PERFORMANCE TABLE\nsound           Sony: 0.85 | Bose: 0.78 | Winner: Sony",
      "brand_wins": {"Sony": 2, "Bose": 1},
      "summary": "HEADPHONES SUMMARY:\nSony: 2 component wins\nBose: 1 component wins"
    }
  },
  "cross_category_analysis": {
    "brand_statistics": {
      "Sony": {"total_wins": 4, "categories": ["Headphones", "Smartphones"], "average_score": 0.78}
    },
    "overall_ranking": [["Sony", {"total_wins": 4}], ["Bose", {"total_wins": 2}]]
  },
  "market_leaders": {
    "overall_winner": ["Sony", {"total_wins": 4}],
    "dominant_categories": {"Headphones": {"brand": "Sony", "wins": 2}}
  }
}
```

The review intelligence is saved as `review_intelligence.json` with customer complaint analysis:

```json
{
  "total_negative_reviews": 1247,
  "total_complaint_categories": 8,
  "top_customer_issues": [
    {
      "rank": 1,
      "issue": "battery drains quickly",
      "component": "battery",
      "frequency": 342,
      "products_affected": 12
    },
    {
      "rank": 2,
      "issue": "poor sound quality",
      "component": "sound",
      "frequency": 287,
      "products_affected": 8
    }
  ],
  "component_breakdown": {
    "battery": {
      "review_count": 342,
      "product_count": 12,
      "severity_score": 45.2,
      "top_phrases": [["battery drains quickly", 156], ["poor battery life", 89]]
    },
    "sound": {
      "review_count": 287,
      "product_count": 8,
      "severity_score": 38.7,
      "top_phrases": [["poor sound quality", 134], ["audio distortion", 76]]
    }
  }
}
```

The strategic recommendations are saved as `strategic_recommendations.json` with actionable improvement suggestions:

```json
{
  "strategic_summary": {
    "total_recommendations": 15,
    "priority_breakdown": {
      "high": 6,
      "medium": 7,
      "low": 2
    },
    "top_recommendations": [
      {
        "rank": 1,
        "component": "battery",
        "priority": "high",
        "key_recommendation": "Implement advanced battery optimization algorithms",
        "impact_score": 85,
        "affected_products": 12
      },
      {
        "rank": 2,
        "component": "sound",
        "priority": "high",
        "key_recommendation": "Upgrade audio drivers and sound processing chips",
        "impact_score": 78,
        "affected_products": 8
      }
    ],
    "strategic_focus_areas": [
      {
        "area": "battery",
        "rationale": "High customer dissatisfaction (342.0 intensity)",
        "expected_impact": "Significant improvement in customer satisfaction"
      }
    ]
  },
  "component_recommendations": {
    "battery": {
      "priority": "high",
      "intensity_score": 342.0,
      "base_recommendations": [
        "Implement advanced battery optimization algorithms",
        "Upgrade to higher capacity battery cells"
      ],
      "contextual_recommendations": [
        "Address customer complaints about battery drains quickly"
      ]
    }
  },
  "implementation_timeline": {
    "immediate": ["battery", "sound"],
    "short_term": ["camera", "display"],
    "medium_term": ["performance", "build_quality"],
    "long_term": ["software", "price"]
  }
}
```

The executive reports are saved as `executive_reports.json` with board-ready analysis:

```json
{
  "overall_market": "EXECUTIVE INTELLIGENCE ANALYSIS - OVERALL MARKET\n\nMarket Overview: Analyzed 8 brands across 5 product categories...",
  "sony_headphones": "============================================================\nEXECUTIVE INTELLIGENCE ANALYSIS - SONY HEADPHONES\n============================================================\n\nMarket Position:\nRanked #5 overall, strong in noise cancellation but weak in battery and sound.\n\nProducts Analyzed: 54\nCategories: headphones\n\nTop Priority:\nAddress battery and audio performance gaps vs competitors.\n\nCritical Weaknesses:\nSound Performance: 50% deficit vs Bose\nBattery Performance: 72% deficit vs Bose\n\nCompetitive Advantages:\nNoise Cancellation: 33% superiority over Bose\nDesign: 72% superiority over Bose\n\nStrategic Recommendations:\n1. Urgent: Improve sound performance to close 50% competitive gap\n2. Urgent: Improve battery performance to close 72% competitive gap\n3. Strengthen noise cancellation advantage in marketing and product development\n\nMarket Share Opportunity: High\n\nRisk Assessment: High risk - Market share loss due to sound underperformance, Competitive pressure from top-performing brands\n\nInvestment Priority: Immediate"
}
```

The web scraped data is saved as `scraped_reviews.json` with fresh Amazon data:

```json
{
  "search_query": "Sony WH-1000XM4 headphones",
  "scraped_at": "2024-01-15T10:30:00",
  "products": [
    {
      "title": "Sony WH-1000XM4 Wireless Premium Noise Canceling Overhead Headphones",
      "url": "https://www.amazon.com/dp/B08HV3ZQZ3",
      "price": 278.99,
      "rating": 4.6,
      "num_reviews": 45231,
      "image": "https://m.media-amazon.com/images/I/...",
      "reviews": [
        {
          "rating": 5,
          "title": "Best headphones I've ever owned",
          "review_text": "The noise cancellation is incredible and the sound quality is amazing...",
          "date": "2024-01-10T00:00:00",
          "reviewer": "John D.",
          "verified_purchase": true,
          "scraped_at": "2024-01-15T10:30:00"
        }
      ],
      "scraped_at": "2024-01-15T10:30:00"
    }
  ],
  "total_reviews": 10
}
```

## Requirements

- Python 3.7+
- pandas
- nltk (for VADER sentiment analysis)
- transformers (for HuggingFace sentiment models)
- requests (for web scraping)
- beautifulsoup4 (for HTML parsing)
- selenium (for dynamic content scraping)
- Standard library modules: json, re, typing, logging, statistics

## Installation

```bash
pip install pandas nltk transformers requests beautifulsoup4 selenium
# Download NLTK VADER data
python -c "import nltk; nltk.download('vader_lexicon')"
# For Selenium: Download ChromeDriver and add to PATH
```

## Methods

### DatasetLoader()

Initialize the dataset loader with default configurations.

### load_datasets(file_paths)

Load the three datasets using pandas.

### inspect_columns()

Inspect columns and detect required columns in all datasets.

### detect_and_rename_columns()

Automatically detect and rename columns to standard names.

### clean_data()

Remove invalid or empty reviews and perform basic data cleaning.

### normalize_brand_names()

Normalize brand names to consistent format.

### extract_product_categories()

Extract product categories using keyword matching.

### merge_product_reviews()

Merge product metadata with reviews and structure the output.

### save_processed_data(output_file)

Save processed data as JSON file.

### process_all_datasets(file_paths, output_file)

Complete pipeline to process all datasets from start to finish.

---

## CategoryFilter Methods

### CategoryFilter()

Initialize the category filter with target categories.

### load_processed_data(input_file)

Read processed_product_reviews.json file.

### identify_target_categories()

Identify products belonging to the 5 target categories.

### filter_brands_per_category(category_data, min_brands, max_brands)

Filter products to keep at least the specified number of brands per category.

### select_top_products_per_brand(category_data, max_products_per_brand)

Select top products per brand based on review count and ratings.

### save_filtered_data(output_file)

Save filtered category data as JSON file.

### process_categories(input_file, output_file, min_brands, max_brands, max_products_per_brand)

Complete pipeline to filter and process categories.

---

## ComponentExtractor Methods

### ComponentExtractor()

Initialize the component extractor with category-specific component keywords.

### load_category_data(input_file)

Read category_products.json file.

### extract_components_from_review(review_text, category)

Extract components mentioned in a review text using keyword matching.

### scan_reviews_for_components()

Scan all reviews and assign them to components.

### enhance_keyword_detection()

Enhance keyword detection with regex patterns and variations.

### filter_component_reviews(min_reviews_per_component)

Filter components to keep only those with sufficient reviews.

### save_component_data(output_file)

Save component data as JSON file.

### process_components(input_file, output_file, min_reviews_per_component, enhance_detection)

Complete pipeline to extract components from reviews.

---

## SentimentEngine Methods

### SentimentEngine(model_type)

Initialize the sentiment engine with model selection ('auto', 'vader', 'huggingface', 'fallback').

### load_component_data(input_file)

Read component_reviews.json file.

### analyze_sentiment(text)

Analyze sentiment of a single text using the selected model.

### calculate_component_sentiments()

Calculate sentiment scores for all components and average by brand.

### analyze_sentiment_vader(text)

Analyze sentiment using NLTK VADER.

### analyze_sentiment_huggingface(text)

Analyze sentiment using HuggingFace transformers.

### save_sentiment_scores(output_file)

Save sentiment scores as JSON file.

### process_sentiments(input_file, output_file, model_type, enhance_analysis)

Complete pipeline to calculate sentiment scores.

### get_top_performing_components(top_n)

Get top performing components by sentiment score.

### get_worst_performing_components(top_n)

Get worst performing components by sentiment score.

---

## CompetitorIntelligence Methods

### CompetitorIntelligence()

Initialize the competitor intelligence engine.

### load_sentiment_scores(input_file)

Read component_sentiment_scores.json file.

### compare_component_scores(category, component)

Compare sentiment scores for a specific component within a category.

### generate_performance_table(category)

Generate performance table for a category with winning brand identification.

### analyze_all_categories()

Analyze all categories and generate performance tables.

### generate_cross_category_analysis()

Generate cross-category competitive analysis and brand rankings.

### identify_market_leaders()

Identify market leaders and competitive trends.

### save_competitor_analysis(output_file)

Save competitor analysis as JSON file.

### process_competitor_intelligence(input_file, output_file)

Complete pipeline to process competitor intelligence.

### get_brand_comparison(brand1, brand2)

Get detailed head-to-head comparison between two brands.

---

## ReviewIntelligence Methods

### ReviewIntelligence()

Initialize the review intelligence engine for complaint analysis.

### load_component_data(component_file)

Read component_reviews.json file.

### load_sentiment_scores(sentiment_file)

Read component_sentiment_scores.json file for reference.

### is_negative_review(review_text, sentiment_threshold)

Determine if a review is negative based on sentiment indicators.

### extract_negative_reviews()

Extract negative reviews from component data.

### normalize_complaint_text(text)

Normalize complaint text for better clustering and analysis.

### identify_complaint_component(review_text)

Identify which component the complaint is about.

### extract_complaint_phrases(review_text, component)

Extract specific complaint phrases from review text.

### cluster_complaints_by_component()

Cluster negative reviews by component and extract common complaints.

### rank_complaint_frequencies(clustered_complaints)

Rank complaints by frequency and importance.

### generate_complaint_summary(ranked_complaints)

Generate comprehensive complaint summary with actionable insights.

### save_complaint_analysis(output_file)

Save complaint analysis as JSON file.

### process_review_intelligence(component_file, sentiment_file, output_file, sentiment_threshold)

Complete pipeline to process review intelligence.

### get_complaint_trends()

Analyze complaint trends and patterns.

### get_product_specific_complaints(product_name)

Get complaints specific to a particular product.

---

## StrategyEngine Methods

### StrategyEngine()

Initialize the strategy engine for generating product improvement suggestions.

### load_competitor_analysis(competitor_file)

Read competitor_analysis.json file.

### load_review_intelligence(review_file)

Read review_intelligence.json file.

### analyze_competitive_gaps()

Analyze competitive gaps and opportunities across categories.

### analyze_customer_pain_points()

Analyze customer pain points from review intelligence data.

### generate_component_recommendations(component, competitive_gap, pain_point)

Generate specific recommendations for a component based on analysis.

### generate_strategic_recommendations()

Generate comprehensive strategic recommendations combining all analyses.

### save_strategic_recommendations(output_file)

Save strategic recommendations as JSON file.

### process_strategy_engine(competitor_file, review_file, output_file)

Complete pipeline to process strategic recommendations.

### get_component_strategy(component)

Get detailed strategy for a specific component.

### get_quick_wins()

Get quick win opportunities (high impact, low effort).

---

## ExecutiveReport Methods

### ExecutiveReport()

Initialize the executive report generator for board-level analysis.

### load_competitor_analysis(competitor_file)

Read competitor_analysis.json file.

### load_review_intelligence(review_file)

Read review_intelligence.json file.

### load_strategic_recommendations(strategy_file)

Read strategic_recommendations.json file.

### analyze_brand_market_position(brand, category)

Analyze market position for a specific brand in a category.

### identify_critical_weaknesses(market_position)

Identify critical weaknesses for a brand based on competitive gaps.

### identify_competitive_advantages(market_position)

Identify competitive advantages for a brand.

### generate_brand_priority_recommendations(brand, category, market_position)

Generate priority recommendations for a brand.

### generate_brand_executive_report(brand, category)

Generate formatted executive report for a specific brand and category.

### generate_overall_market_report()

Generate overall market intelligence report.

### save_executive_reports(output_file)

Save executive reports as JSON file.

### process_executive_reports(competitor_file, review_file, strategy_file, output_file)

Complete pipeline to process executive reports.

### get_brand_report(brand, category)

Get executive report for a specific brand and category.

### get_overall_market_report()

Get overall market executive report.

---

## WebScraper Methods

### WebScraper(use_selenium=False, headless=True)

Initialize the web scraper for Amazon data extraction.

### search_amazon_product(search_query, max_results=10)

Search for products on Amazon and return basic product information.

### get_product_reviews(product_url, max_reviews=50)

Extract reviews for a specific Amazon product.

### save_scraped_data(data, filename='scraped_reviews.json')

Save scraped data to JSON file.

### append_to_dataset(scraped_data, existing_file='scraped_reviews.json')

Append scraped data to existing dataset.

### scrape_product_data(search_query, max_products=5, max_reviews_per_product=20)

Complete scraping pipeline for product data and reviews.

### close()

Clean up resources (close browser, session).

---

## Usage Notes

### Web Scraping Best Practices:
- Use random delays between requests (2-5 seconds)
- Respect robots.txt and terms of service
- Use appropriate User-Agent headers
- Handle errors gracefully and retry failed requests
- Consider rate limiting to avoid being blocked

### Selenium vs BeautifulSoup:
- **Requests + BeautifulSoup**: Faster, good for static content
- **Selenium**: Handles dynamic content, slower but more robust
- Choose based on website complexity and requirements

### Data Appending:
- Scraped data is automatically appended to existing datasets
- Maintains historical data for trend analysis
- Supports incremental updates without overwriting

### Trend Analysis:
- Detects emerging issues over time using temporal analysis
- Identifies significant changes in complaint patterns
- Generates alerts for critical trend developments
- Provides component-specific trend insights

---

## MainPipeline Methods

### MainPipeline(config_file='pipeline_config.json')

Initialize the complete competitive intelligence pipeline.

### run_complete_pipeline()

Run the entire pipeline from data loading to executive reports.

### save_pipeline_config(config_file='pipeline_config.json')

Save current pipeline configuration to JSON file.

### get_results()

Get complete pipeline results dictionary.

---

## Pipeline Configuration

The pipeline uses `pipeline_config.json` for configuration:

```json
{
  "input_files": {
    "amazon_electronics_master_dataset": "amazon_electronics_master_dataset.csv",
    "amazon_electronics_reviews_cleaned": "amazon_electronics_reviews_cleaned.csv",
    "amazon_reviews_cleaned_4M": "amazon_reviews_cleaned_4M.csv"
  },
  "output_files": {
    "processed_data": "processed_product_reviews.json",
    "category_products": "category_products.json",
    "component_reviews": "component_reviews.json",
    "sentiment_scores": "component_sentiment_scores.json",
    "competitor_analysis": "competitor_analysis.json",
    "review_intelligence": "review_intelligence.json",
    "strategic_recommendations": "strategic_recommendations.json",
    "executive_reports": "executive_reports.json"
  },
  "parameters": {
    "min_brands": 2,
    "max_brands": 5,
    "max_products_per_brand": 3,
    "min_reviews_per_component": 5,
    "sentiment_model": "auto",
    "max_reviews_per_product": 20
  }
}
```

---

## Pipeline Output

The main pipeline produces formatted terminal output:

```
================================================================================
MULTI CATEGORY PRODUCT INTELLIGENCE PLATFORM
================================================================================

📊 STEP 1: LOADING DATASETS
--------------------------------------------------
✅ Datasets loaded successfully

🏷️  STEP 2: FILTERING CATEGORIES
--------------------------------------------------
✅ Categories filtered: 3
   Categories found: headphones, smartphones, laptops

🔧 STEP 3: EXTRACTING COMPONENTS
--------------------------------------------------
   headphones: 8 components
   smartphones: 10 components
   laptops: 9 components
✅ Components extracted: 27 total

💭 STEP 4: SENTIMENT ANALYSIS
--------------------------------------------------
   headphones: 24 component analyses
   smartphones: 30 component analyses
   laptops: 27 component analyses
✅ Sentiment analysis completed: 81 total

🏆 STEP 5: COMPETITOR ANALYSIS
--------------------------------------------------

📈 ANALYZING CATEGORY: HEADPHONES

HEADPHONES PERFORMANCE TABLE
+--------+--------+--------+--------+--------+--------+
| Brand  | Battery| Sound  | Camera | Display| Overall|
+--------+--------+--------+--------+--------+--------+
| Sony   |  0.45  |  0.62  |  0.38  |  0.71  |  0.54  |
+--------+--------+--------+--------+--------+--------+
| Bose   |  0.78  |  0.85  |  0.42  |  0.65  |  0.68  |
+--------+--------+--------+--------+--------+--------+

Sony vs Bose

📈 ANALYZING CATEGORY: SMARTPHONES

SMARTPHONES PERFORMANCE TABLE
+--------+--------+--------+--------+--------+--------+
| Brand  | Battery| Camera | Display| Sound  | Overall|
+--------+--------+--------+--------+--------+--------+
| Apple  |  0.82  |  0.91  |  0.88  |  0.75  |  0.84  |
+--------+--------+--------+--------+--------+--------+
| Samsung|  0.76  |  0.85  |  0.92  |  0.78  |  0.83  |
+--------+--------+--------+--------+--------+--------+

Apple vs Samsung

✅ Competitor analysis completed

⚠️  STEP 6: REVIEW INTELLIGENCE
--------------------------------------------------
🚨 TOP CUSTOMER ISSUES:
   1. battery drains quickly (battery)
      Frequency: 342 | Products: 12
   2. poor sound quality (sound)
      Frequency: 287 | Products: 8

📋 COMPONENT ISSUE BREAKDOWN:
   Battery: Severity 45.2 | 342 reviews
   Sound: Severity 38.7 | 287 reviews

✅ Review intelligence completed

💡 STEP 7: STRATEGY ENGINE
--------------------------------------------------
🚀 TOP STRATEGIC RECOMMENDATIONS:
   1. Implement advanced battery optimization algorithms
      Component: battery | Priority: high
      Impact Score: 85 | Products: 12
   2. Upgrade audio drivers and sound processing chips
      Component: sound | Priority: high
      Impact Score: 78 | Products: 8

📊 PRIORITY BREAKDOWN:
   High: 6 recommendations
   Medium: 7 recommendations
   Low: 2 recommendations

✅ Strategy engine completed

📋 STEP 8: EXECUTIVE REPORT
--------------------------------------------------
📄 EXECUTIVE INTELLIGENCE REPORT
   EXECUTIVE INTELLIGENCE ANALYSIS - OVERALL MARKET
   Market Overview: Analyzed 8 brands across 5 product categories...
   ...

📊 Sony Headphones Executive Summary:
   Market Position: Ranked #5 overall, strong in noise cancellation but weak in battery and sound.
   Top Priority: Address battery and audio performance gaps vs competitors.

✅ Executive reports completed

================================================================================
MULTI CATEGORY SUMMARY
================================================================================

📊 CATEGORIES ANALYZED: 3
   Headphones: 3 brands (Sony, Bose, Apple)
   Smartphones: 2 brands (Apple, Samsung)
   Laptops: 2 brands (Dell, HP)

💭 SENTIMENT OVERVIEW:
   Headphones: 0.542 avg sentiment
   Smartphones: 0.635 avg sentiment
   Laptops: 0.578 avg sentiment

🏆 OVERALL MARKET LEADERS:
   1. Apple: 12 component wins
      Categories: headphones, smartphones
   2. Samsung: 8 component wins
      Categories: smartphones, laptops
   3. Bose: 6 component wins
      Categories: headphones

⚠️  MARKET-WIDE CRITICAL ISSUES:
   1. battery drains quickly (battery)
      Affects 12 products
   2. poor sound quality (sound)
      Affects 8 products

🎯 STRATEGIC PRIORITIES:
   High: 6 recommendations (40.0%)
   Medium: 7 recommendations (46.7%)
   Low: 2 recommendations (13.3%)

================================================================================
PIPELINE EXECUTION SUMMARY
================================================================================

⏱️  Execution Time: 45.67 seconds
📅 Started: 2024-01-15 10:30:00
📅 Completed: 2024-01-15 10:30:45

📁 OUTPUT FILES GENERATED:
   ✅ processed_data: processed_product_reviews.json (2,345,678 bytes)
   ✅ category_products: category_products.json (567,890 bytes)
   ✅ component_reviews: component_reviews.json (1,234,567 bytes)
   ✅ sentiment_scores: component_sentiment_scores.json (345,678 bytes)
   ✅ competitor_analysis: competitor_analysis.json (234,567 bytes)
   ✅ review_intelligence: review_intelligence.json (456,789 bytes)
   ✅ strategic_recommendations: strategic_recommendations.json (123,456 bytes)
   ✅ executive_reports: executive_reports.json (789,012 bytes)
   ✅ trend_alerts: trend_alerts.json (345,678 bytes)

The trend alerts are saved as `trend_alerts.json` with emerging issue detection:

```json
{
  "generated_at": "2024-01-15T10:30:00",
  "analysis_period": "Last 6 months",
  "thresholds_used": {
    "significant_increase": 20.0,
    "critical_increase": 50.0,
    "emerging_threshold": 10,
    "trend_consistency": 0.7
  },
  "alerts": {
    "critical_alerts": [
      {
        "type": "component_spike",
        "component": "battery",
        "severity": "critical",
        "message": "Battery complaints increased 52.3% in recent months",
        "percentage_change": 52.3,
        "consistency": 0.85,
        "total_mentions": 342,
        "recommendation": "Investigate battery issues immediately"
      }
    ],
    "warning_alerts": [
      {
        "type": "complaint_increase",
        "complaint": "sound",
        "severity": "warning",
        "message": "Sound issues increased 28.7% in recent months",
        "percentage_change": 28.7,
        "consistency": 0.72,
        "total_complaints": 287,
        "recommendation": "Monitor sound trends closely"
      }
    ],
    "emerging_alerts": [
      {
        "type": "emerging_issue",
        "issue": "connectivity",
        "severity": "emerging",
        "message": "Emerging issue: Connectivity (35.2% growth)",
        "growth_rate": 35.2,
        "recent_mentions": 45,
        "recommendation": "Monitor connectivity trend for escalation"
      }
    ],
    "positive_trends": [
      {
        "type": "sentiment_improvement",
        "component": "display",
        "severity": "positive",
        "message": "Display sentiment improved 18.4% in recent months",
        "percentage_change": 18.4,
        "consistency": 0.68,
        "current_sentiment": 0.742,
        "recommendation": "Continue display improvement efforts"
      }
    ],
    "summary": {
      "total_alerts": 4,
      "critical_count": 1,
      "warning_count": 1,
      "emerging_count": 1,
      "positive_count": 1
    }
  }
}
```

🎯 PIPELINE STATUS: COMPLETED SUCCESSFULLY
================================================================================
