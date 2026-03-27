#!/usr/bin/env python3
"""
Example usage of the CompetitorIntelligence module for competitive analysis.

This script demonstrates how to use the competitor_intelligence.py module to analyze
brand performance across categories and generate competitive intelligence reports.
"""

from competitor_intelligence import CompetitorIntelligence
import json

def main():
    """
    Main function demonstrating competitor intelligence analysis.
    """
    print("🏆 Starting Competitive Intelligence Analysis...")
    
    # Initialize the competitor intelligence engine
    intelligence = CompetitorIntelligence()
    
    try:
        # Process competitor intelligence
        print("📊 Analyzing competitor performance...")
        analysis_results = intelligence.process_competitor_intelligence(
            input_file='component_sentiment_scores.json',
            output_file='competitor_analysis.json'
        )
        
        print("\n✅ Competitor intelligence analysis completed successfully!")
        
        # Display detailed results
        display_competitor_results(analysis_results)
        
        # Show cross-category insights
        show_cross_category_insights(intelligence)
        
        # Generate brand comparisons
        generate_brand_comparisons(intelligence)
        
        # Create strategic insights
        create_strategic_insights(intelligence)
        
        # Validate analysis results
        validate_competitor_analysis()
        
    except FileNotFoundError:
        print("❌ Error: component_sentiment_scores.json not found!")
        print("💡 Please run the previous pipeline steps first to generate the required data files.")
        
    except Exception as e:
        print(f"❌ Error during competitor intelligence analysis: {e}")
        print("🔧 Please check your input data and try again.")

def display_competitor_results(analysis_results):
    """
    Display detailed results of the competitor intelligence analysis.
    
    Args:
        analysis_results: The competitor analysis results
    """
    print("\n" + "="*60)
    print("📊 DETAILED COMPETITOR INTELLIGENCE RESULTS")
    print("="*60)
    
    total_categories = len(analysis_results)
    total_components = sum(analysis['total_components'] for analysis in analysis_results.values())
    
    print(f"\n📈 OVERVIEW:")
    print(f"   Categories analyzed: {total_categories}")
    print(f"   Total components: {total_components}")
    
    # Show performance summary for each category
    print(f"\n📁 CATEGORY PERFORMANCE SUMMARY:")
    for category, analysis in analysis_results.items():
        brand_wins = analysis['brand_wins']
        total_components = analysis['total_components']
        
        print(f"\n📂 {category.upper()}:")
        print(f"   Components: {total_components}")
        print(f"   Brand Wins: {brand_wins}")
        
        # Show top brand
        if brand_wins:
            top_brand = max(brand_wins.items(), key=lambda x: x[1])
            dominance = (top_brand[1] / total_components) * 100
            print(f"   Leader: {top_brand[0]} ({dominance:.1f}% dominance)")
    
    print("="*60)

def show_cross_category_insights(intelligence):
    """
    Show cross-category competitive insights.
    
    Args:
        intelligence: The CompetitorIntelligence instance
    """
    print("\n" + "="*60)
    print("🌍 CROSS-CATEGORY COMPETITIVE INSIGHTS")
    print("="*60)
    
    cross_analysis = intelligence.generate_cross_category_analysis()
    market_leaders = intelligence.identify_market_leaders()
    
    print(f"\n🏆 OVERALL BRAND RANKINGS:")
    for i, (brand, stats) in enumerate(cross_analysis['overall_ranking'][:10], 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        categories_str = ", ".join(stats['categories'])
        print(f"   {emoji} {i:2d}. {brand}")
        print(f"       Wins: {stats['total_wins']} | Categories: {stats['category_count']} | Avg Score: {stats['average_score']:.3f}")
        print(f"       Categories: {categories_str}")
    
    print(f"\n👑 MARKET LEADERSHIP:")
    if market_leaders['overall_winner']:
        winner = market_leaders['overall_winner']
        print(f"   Overall Champion: {winner[0]} with {winner[1]['total_wins']} component wins")
    
    if market_leaders['highest_average_score']:
        best_avg = market_leaders['highest_average_score']
        print(f"   Quality Leader: {best_avg[0]} with {best_avg[1]['average_score']:.3f} average score")
    
    if market_leaders['most_categories']:
        most_cats = market_leaders['most_categories']
        print(f"   Broadest Presence: {most_cats[0]} in {most_cats[1]['category_count']} categories")
    
    if market_leaders['most_consistent']:
        consistent = market_leaders['most_consistent']
        print(f"   Most Consistent: {consistent[0]} (score variance: {consistent[1]:.3f})")
    
    print(f"\n📁 CATEGORY DOMINANCE:")
    for category, dominant in market_leaders['dominant_categories'].items():
        dominance_pct = (dominant['wins'] / dominant['total_components']) * 100
        print(f"   {category}: {dominant['brand']} dominates with {dominance_pct:.1f}% of component wins")

def generate_brand_comparisons(intelligence):
    """
    Generate detailed brand-to-brand comparisons.
    
    Args:
        intelligence: The CompetitorIntelligence instance
    """
    print("\n" + "="*60)
    print("🥊 BRAND-TO-BRAND COMPARISONS")
    print("="*60)
    
    cross_analysis = intelligence.generate_cross_category_analysis()
    top_brands = cross_analysis['overall_ranking'][:5]  # Top 5 brands
    
    if len(top_brands) < 2:
        print("   Not enough brands for comparison")
        return
    
    print(f"\n🔥 TOP BRAND RIVALRIES:")
    
    # Compare top brands
    for i in range(min(3, len(top_brands) - 1)):
        brand1 = top_brands[i][0]
        brand2 = top_brands[i + 1][0]
        
        print(f"\n🥊 {brand1} vs {brand2}:")
        comparison = intelligence.get_brand_comparison(brand1, brand2)
        
        print(f"   Overall Winner: {comparison['overall_winner']}")
        
        # Show head-to-head record
        brand1_wins = sum(1 for cat_data in comparison['head_to_head'].values() 
                         for comp_data in cat_data['components'].values() 
                         if comp_data['winner'] == brand1)
        brand2_wins = sum(1 for cat_data in comparison['head_to_head'].values() 
                         for comp_data in cat_data['components'].values() 
                         if comp_data['winner'] == brand2)
        total_comparisons = brand1_wins + brand2_wins
        
        if total_comparisons > 0:
            print(f"   Head-to-Head: {brand1} {brand1_wins} - {brand2_wins} {brand2}")
            print(f"   Win Rate: {brand1} {brand1_wins/total_comparisons*100:.1f}% | {brand2} {brand2_wins/total_comparisons*100:.1f}%")
        
        # Show category breakdown
        print(f"   Category Battles:")
        for category, cat_data in comparison['head_to_head'].items():
            category_winner = cat_data['winner']
            component_count = len(cat_data['components'])
            print(f"     {category}: {category_winner} wins ({component_count} components)")

def create_strategic_insights(intelligence):
    """
    Create strategic insights from the competitive analysis.
    
    Args:
        intelligence: The CompetitorIntelligence instance
    """
    print("\n" + "="*60)
    print("🧠 STRATEGIC COMPETITIVE INSIGHTS")
    print("="*60)
    
    cross_analysis = intelligence.generate_cross_category_analysis()
    market_leaders = intelligence.identify_market_leaders()
    
    print(f"\n🎯 COMPETITIVE POSITIONING:")
    
    # Identify competitive patterns
    brand_stats = cross_analysis['brand_statistics']
    
    # Categorize brands by their competitive strategy
    leaders = []      # High wins, multiple categories
    specialists = []  # High performance in few categories
    challengers = []  # Moderate performance across categories
    followers = []    # Low performance
    
    for brand, stats in brand_stats.items():
        win_rate = stats['total_wins'] / (stats['category_count'] * 6)  # Assuming ~6 components per category
        avg_score = stats['average_score']
        
        if win_rate > 0.4 and stats['category_count'] >= 3:
            leaders.append((brand, stats))
        elif win_rate > 0.3 and stats['category_count'] <= 2:
            specialists.append((brand, stats))
        elif win_rate > 0.2:
            challengers.append((brand, stats))
        else:
            followers.append((brand, stats))
    
    print(f"\n👑 MARKET LEADERS (Broad Dominance):")
    for brand, stats in leaders[:3]:
        print(f"   🏆 {brand}: {stats['total_wins']} wins across {stats['category_count']} categories")
    
    print(f"\n🎯 CATEGORY SPECIALISTS (Focused Excellence):")
    for brand, stats in specialists[:3]:
        categories_str = ", ".join(stats['categories'])
        print(f"   🎯 {brand}: Specializes in {categories_str}")
    
    print(f"\n🚀 CHALLENGERS (Growing Presence):")
    for brand, stats in challengers[:3]:
        print(f"   🚀 {brand}: {stats['total_wins']} wins, {stats['average_score']:.3f} avg score")
    
    print(f"\n📊 MARKET OPPORTUNITIES:")
    
    # Identify under-served components
    component_analysis = defaultdict(lambda: defaultdict(list))
    for category, analysis in intelligence.competitor_analysis.items():
        for component, data in analysis['performance_data'].items():
            for brand, score in data['brand_scores'].items():
                component_analysis[component][brand].append(score)
    
    # Find components with low average scores (opportunities for improvement)
    opportunities = []
    for component, brand_scores in component_analysis.items():
        all_scores = []
        for scores in brand_scores.values():
            all_scores.extend(scores)
        
        if all_scores:
            avg_score = sum(all_scores) / len(all_scores)
            if avg_score < 0.3:  # Low satisfaction
                opportunities.append((component, avg_score, len(brand_scores)))
    
    opportunities.sort(key=lambda x: x[1])  # Sort by lowest average score
    
    print(f"   🔧 Components Needing Improvement:")
    for component, avg_score, brand_count in opportunities[:5]:
        print(f"     - {component}: {avg_score:.3f} average score ({brand_count} brands competing)")
    
    print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
    
    if leaders:
        top_leader = leaders[0][0]
        print(f"   🎯 For competitors: Focus on differentiating against {top_leader}'s strengths")
    
    if specialists:
        top_specialist = specialists[0][0]
        specialist_cats = ", ".join(specialists[0][1]['categories'])
        print(f"   🎯 For {top_specialist}: Consider expanding beyond {specialist_cats}")
    
    if opportunities:
        print(f"   🎯 For all brands: {opportunities[0][0]} component shows clear improvement opportunities")
    
    print("="*60)

def validate_competitor_analysis():
    """
    Validate that competitor analysis results meet expectations.
    """
    print("\n" + "="*60)
    print("✅ COMPETITOR ANALYSIS VALIDATION")
    print("="*60)
    
    try:
        with open('competitor_analysis.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📋 VALIDATION RESULTS:")
        
        # Check structure
        required_sections = ['category_analysis', 'cross_category_analysis', 'market_leaders', 'metadata']
        missing_sections = [section for section in required_sections if section not in data]
        
        if not missing_sections:
            print(f"   ✅ All required sections present")
        else:
            print(f"   ❌ Missing sections: {missing_sections}")
        
        # Validate category analysis
        category_analysis = data.get('category_analysis', {})
        if category_analysis:
            print(f"   ✅ Category analysis: {len(category_analysis)} categories")
            
            for category, analysis in category_analysis.items():
                required_keys = ['performance_table', 'brand_wins', 'summary', 'total_components']
                missing_keys = [key for key in required_keys if key not in analysis]
                
                if missing_keys:
                    print(f"   ⚠️  {category} missing keys: {missing_keys}")
        
        # Validate cross-category analysis
        cross_analysis = data.get('cross_category_analysis', {})
        if cross_analysis:
            brand_stats = cross_analysis.get('brand_statistics', {})
            overall_ranking = cross_analysis.get('overall_ranking', [])
            
            print(f"   ✅ Cross-category analysis: {len(brand_stats)} brands analyzed")
            print(f"   ✅ Overall ranking: {len(overall_ranking)} brands ranked")
            
            if overall_ranking:
                top_brand = overall_ranking[0]
                print(f"   🏆 Top brand: {top_brand[0]} with {top_brand[1]['total_wins']} wins")
        
        # Validate market leaders
        market_leaders = data.get('market_leaders', {})
        if market_leaders:
            print(f"   ✅ Market leaders analysis complete")
            
            if market_leaders.get('overall_winner'):
                winner = market_leaders['overall_winner']
                print(f"   👑 Overall winner: {winner[0]}")
            
            if market_leaders.get('dominant_categories'):
                dominant = market_leaders['dominant_categories']
                print(f"   📁 Dominant categories: {len(dominant)}")
        
        print(f"\n📊 SUMMARY STATISTICS:")
        print(f"   Categories: {len(category_analysis)}")
        print(f"   Brands: {len(brand_stats)}")
        print(f"   Rankings: {len(overall_ranking)}")
        
        print("="*60)
        
    except FileNotFoundError:
        print("❌ competitor_analysis.json not found for validation")
    except Exception as e:
        print(f"❌ Error during validation: {e}")

def export_performance_tables():
    """
    Export performance tables to a readable format.
    """
    print("\n" + "="*60)
    print("📄 EXPORTING PERFORMANCE TABLES")
    print("="*60)
    
    try:
        with open('competitor_analysis.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Export to text file
        with open('performance_tables.txt', 'w', encoding='utf-8') as f:
            f.write("COMPETITIVE INTELLIGENCE PERFORMANCE TABLES\n")
            f.write("=" * 60 + "\n\n")
            
            category_analysis = data.get('category_analysis', {})
            for category, analysis in category_analysis.items():
                f.write(f"{analysis['performance_table']}\n")
                f.write(f"{analysis['summary']}\n\n")
        
        print("✅ Performance tables exported to performance_tables.txt")
        
        # Export summary to CSV
        with open('brand_summary.csv', 'w', encoding='utf-8') as f:
            f.write("Brand,Total_Wins,Category_Count,Average_Score,Best_Category,Worst_Category\n")
            
            brand_stats = data.get('cross_category_analysis', {}).get('brand_statistics', {})
            for brand, stats in brand_stats.items():
                best_cat = stats.get('best_category', {}).get('name', 'N/A')
                worst_cat = stats.get('worst_category', {}).get('name', 'N/A')
                
                f.write(f"{brand},{stats['total_wins']},{stats['category_count']},"
                       f"{stats['average_score']:.3f},{best_cat},{worst_cat}\n")
        
        print("✅ Brand summary exported to brand_summary.csv")
        
    except FileNotFoundError:
        print("❌ competitor_analysis.json not found for export")
    except Exception as e:
        print(f"❌ Error during export: {e}")

if __name__ == "__main__":
    # Run main competitor intelligence analysis
    main()
    
    # Export performance tables
    export_performance_tables()
