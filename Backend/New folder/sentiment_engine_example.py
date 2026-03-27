#!/usr/bin/env python3
"""
Example usage of the SentimentEngine module for calculating component sentiment scores.

This script demonstrates how to use the sentiment_engine.py module to analyze
sentiment of product component reviews for competitive intelligence analysis.
"""

from sentiment_engine import SentimentEngine
import json
import statistics

def main():
    """
    Main function demonstrating sentiment analysis.
    """
    print("😊 Starting Sentiment Analysis for Product Components...")
    
    # Initialize the sentiment engine
    engine = SentimentEngine(model_type='auto')
    
    try:
        # Process sentiments with custom parameters
        print("📊 Analyzing sentiment of component reviews...")
        sentiment_scores = engine.process_sentiments(
            input_file='component_reviews.json',
            output_file='component_sentiment_scores.json',
            model_type='auto',
            enhance_analysis=True
        )
        
        print("\n✅ Sentiment analysis completed successfully!")
        
        # Display detailed results
        display_sentiment_results(sentiment_scores)
        
        # Analyze sentiment by category
        analyze_sentiment_by_category(sentiment_scores)
        
        # Show top and worst performers
        show_performers(engine)
        
        # Generate sentiment insights
        generate_sentiment_insights(sentiment_scores, engine)
        
        # Validate sentiment results
        validate_sentiment_analysis()
        
    except FileNotFoundError:
        print("❌ Error: component_reviews.json not found!")
        print("💡 Please run the dataset_loader.py, category_filter.py, and component_extractor.py first to generate the required data files.")
        
    except Exception as e:
        print(f"❌ Error during sentiment analysis: {e}")
        print("🔧 Please check your input data and try again.")

def display_sentiment_results(sentiment_scores):
    """
    Display detailed results of the sentiment analysis.
    
    Args:
        sentiment_scores: The calculated sentiment scores
    """
    print("\n" + "="*60)
    print("😊 DETAILED SENTIMENT ANALYSIS RESULTS")
    print("="*60)
    
    total_categories = len(sentiment_scores)
    total_components = sum(len(components) for components in sentiment_scores.values())
    total_brand_components = sum(len(brands) for components in sentiment_scores.values() for brands in components.values())
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Categories analyzed: {total_categories}")
    print(f"   Components analyzed: {total_components}")
    print(f"   Brand-component pairs: {total_brand_components}")
    
    # Sentiment distribution
    all_scores = []
    for category, components in sentiment_scores.items():
        for component, brands in components.items():
            all_scores.extend(brands.values())
    
    if all_scores:
        positive_count = sum(1 for score in all_scores if score > 0.1)
        neutral_count = sum(1 for score in all_scores if -0.1 <= score <= 0.1)
        negative_count = sum(1 for score in all_scores if score < -0.1)
        
        total = len(all_scores)
        print(f"\n😊 SENTIMENT DISTRIBUTION:")
        print(f"   Positive: {positive_count} ({positive_count/total*100:.1f}%)")
        print(f"   Neutral: {neutral_count} ({neutral_count/total*100:.1f}%)")
        print(f"   Negative: {negative_count} ({negative_count/total*100:.1f}%)")
        
        avg_sentiment = statistics.mean(all_scores)
        print(f"   Overall Average: {avg_sentiment:.3f}")
    
    print("="*60)

def analyze_sentiment_by_category(sentiment_scores):
    """
    Analyze sentiment scores by product category.
    
    Args:
        sentiment_scores: The calculated sentiment scores
    """
    print("\n" + "="*60)
    print("📁 SENTIMENT ANALYSIS BY CATEGORY")
    print("="*60)
    
    for category, components in sentiment_scores.items():
        print(f"\n📂 {category.upper()}:")
        
        component_scores = []
        for component, brands in components.items():
            component_scores.extend(brands.values())
        
        if component_scores:
            avg_sentiment = statistics.mean(component_scores)
            print(f"   Average Sentiment: {avg_sentiment:.3f}")
            
            # Find best and worst components in this category
            best_component = max(components.items(), key=lambda x: statistics.mean(x[1].values()))
            worst_component = min(components.items(), key=lambda x: statistics.mean(x[1].values()))
            
            best_avg = statistics.mean(best_component[1].values())
            worst_avg = statistics.mean(worst_component[1].values())
            
            print(f"   Best Component: {best_component[0]} ({best_avg:.3f})")
            print(f"   Worst Component: {worst_component[0]} ({worst_avg:.3f})")
            
            # Show component breakdown
            print(f"   Component Breakdown:")
            for component, brands in components.items():
                component_avg = statistics.mean(brands.values())
                print(f"     - {component}: {component_avg:.3f}")
        else:
            print(f"   No sentiment data available")

def show_performers(engine):
    """
    Show top and worst performing components.
    
    Args:
        engine: The SentimentEngine instance
    """
    print("\n" + "="*60)
    print("🏆 PERFORMANCE LEADERBOARD")
    print("="*60)
    
    print(f"\n🥇 TOP 10 PERFORMING COMPONENTS:")
    top_components = engine.get_top_performing_components(10)
    for i, (category, component, brand, score) in enumerate(top_components, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"   {emoji} {i:2d}. {brand} {component} ({category}): {score:.3f}")
    
    print(f"\n⚠️  WORST 10 PERFORMING COMPONENTS:")
    worst_components = engine.get_worst_performing_components(10)
    for i, (category, component, brand, score) in enumerate(worst_components, 1):
        emoji = "🔴" if i == 1 else "🟠" if i == 2 else "🟡" if i == 3 else "  "
        print(f"   {emoji} {i:2d}. {brand} {component} ({category}): {score:.3f}")

def generate_sentiment_insights(sentiment_scores, engine):
    """
    Generate insights from sentiment analysis.
    
    Args:
        sentiment_scores: The calculated sentiment scores
        engine: The SentimentEngine instance
    """
    print("\n" + "="*60)
    print("🧠 SENTIMENT INSIGHTS")
    print("="*60)
    
    # Component performance analysis
    component_performance = {}
    for category, components in sentiment_scores.items():
        for component, brands in components.items():
            scores = list(brands.values())
            if scores:
                component_performance[f"{category}_{component}"] = {
                    'category': category,
                    'component': component,
                    'avg_score': statistics.mean(scores),
                    'score_range': max(scores) - min(scores),
                    'brand_count': len(brands)
                }
    
    print(f"\n📈 COMPONENT PERFORMANCE ANALYSIS:")
    
    # Most consistent components (low score range)
    consistent_components = sorted(component_performance.items(), 
                                 key=lambda x: x[1]['score_range'])
    print(f"\n🎯 MOST CONSISTENT COMPONENTS:")
    for i, (key, data) in enumerate(consistent_components[:5], 1):
        print(f"   {i}. {data['component']} ({data['category']}): "
              f"Range {data['score_range']:.3f}, {data['brand_count']} brands")
    
    # Most polarizing components (high score range)
    polarizing_components = sorted(component_performance.items(), 
                                 key=lambda x: x[1]['score_range'], reverse=True)
    print(f"\n⚖️  MOST POLARIZING COMPONENTS:")
    for i, (key, data) in enumerate(polarizing_components[:5], 1):
        print(f"   {i}. {data['component']} ({data['category']}): "
              f"Range {data['score_range']:.3f}, {data['brand_count']} brands")
    
    # Brand sentiment analysis
    brand_sentiments = {}
    for category, components in sentiment_scores.items():
        for component, brands in components.items():
            for brand, score in brands.items():
                if brand not in brand_sentiments:
                    brand_sentiments[brand] = []
                brand_sentiments[brand].append(score)
    
    print(f"\n🏢 BRAND SENTIMENT OVERVIEW:")
    brand_averages = {brand: statistics.mean(scores) for brand, scores in brand_sentiments.items()}
    sorted_brands = sorted(brand_averages.items(), key=lambda x: x[1], reverse=True)
    
    for i, (brand, avg_score) in enumerate(sorted_brands[:10], 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"   {emoji} {i:2d}. {brand}: {avg_score:.3f} ({len(brand_sentiments[brand])} components)")
    
    print("="*60)

def validate_sentiment_analysis():
    """
    Validate that sentiment analysis results meet expectations.
    """
    print("\n" + "="*60)
    print("✅ SENTIMENT ANALYSIS VALIDATION")
    print("="*60)
    
    try:
        with open('component_sentiment_scores.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📋 VALIDATION RESULTS:")
        
        # Check data structure
        expected_structure = True
        for category, components in data.items():
            if not isinstance(components, dict):
                expected_structure = False
                break
            for component, brands in components.items():
                if not isinstance(brands, dict):
                    expected_structure = False
                    break
                for brand, score in brands.items():
                    if not isinstance(score, (int, float)):
                        expected_structure = False
                        break
        
        if expected_structure:
            print(f"   ✅ Data structure is correct")
        else:
            print(f"   ❌ Data structure is incorrect")
        
        # Check score ranges
        all_scores = []
        for category, components in data.items():
            for component, brands in components.items():
                all_scores.extend(brands.values())
        
        if all_scores:
            min_score = min(all_scores)
            max_score = max(all_scores)
            
            if -1.0 <= min_score <= max_score <= 1.0:
                print(f"   ✅ Score range is valid ({min_score:.3f} to {max_score:.3f})")
            else:
                print(f"   ❌ Score range is invalid ({min_score:.3f} to {max_score:.3f})")
            
            # Check for reasonable distribution
            positive_count = sum(1 for score in all_scores if score > 0.1)
            neutral_count = sum(1 for score in all_scores if -0.1 <= score <= 0.1)
            negative_count = sum(1 for score in all_scores if score < -0.1)
            
            print(f"   📊 Sentiment distribution: {positive_count} positive, {neutral_count} neutral, {negative_count} negative")
        
        print(f"   📁 Categories: {len(data)}")
        print(f"   🔧 Components: {sum(len(components) for components in data.values())}")
        print(f"   🏢 Brands: {sum(len(brands) for components in data.values() for brands in components.values())}")
        
        print("="*60)
        
    except FileNotFoundError:
        print("❌ component_sentiment_scores.json not found for validation")
    except Exception as e:
        print(f"❌ Error during validation: {e}")

def compare_sentiment_models():
    """
    Compare different sentiment analysis models (if available).
    """
    print("\n" + "="*60)
    print("🔬 SENTIMENT MODEL COMPARISON")
    print("="*60)
    
    models_to_test = ['vader', 'huggingface', 'fallback']
    results = {}
    
    for model_type in models_to_test:
        try:
            print(f"\n🧪 Testing {model_type} model...")
            engine = SentimentEngine(model_type=model_type)
            
            # Load a small sample for testing
            with open('component_reviews.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process first product only for comparison
            sample_data = {}
            first_product = list(data.keys())[0]
            sample_data[first_product] = data[first_product]
            
            # Temporarily replace component data
            engine.component_data = sample_data
            engine.calculate_component_sentiments()
            
            # Calculate average score
            all_scores = []
            for category, components in engine.sentiment_scores.items():
                for component, brands in components.items():
                    all_scores.extend(brands.values())
            
            if all_scores:
                avg_score = statistics.mean(all_scores)
                results[model_type] = avg_score
                print(f"   ✅ {model_type}: Average score {avg_score:.3f}")
            else:
                print(f"   ❌ {model_type}: No scores calculated")
                
        except Exception as e:
            print(f"   ❌ {model_type}: Error - {e}")
    
    if results:
        print(f"\n📊 MODEL COMPARISON RESULTS:")
        for model, score in results.items():
            print(f"   {model}: {score:.3f}")
    
    print("="*60)

if __name__ == "__main__":
    # Run main sentiment analysis
    main()
    
    # Optional: Compare different models
    # compare_sentiment_models()
