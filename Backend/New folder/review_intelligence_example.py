#!/usr/bin/env python3
"""
Example usage of the ReviewIntelligence module for analyzing customer complaints.

This script demonstrates how to use the review_intelligence.py module to identify
most common product complaints and generate actionable insights for improvement.
"""

from review_intelligence import ReviewIntelligence
import json

def main():
    """
    Main function demonstrating review intelligence analysis.
    """
    print("🚨 Starting Review Intelligence Analysis...")
    
    # Initialize the review intelligence engine
    intelligence = ReviewIntelligence()
    
    try:
        # Process review intelligence
        print("📊 Analyzing customer complaints...")
        complaint_analysis = intelligence.process_review_intelligence(
            component_file='component_reviews.json',
            sentiment_file='component_sentiment_scores.json',
            output_file='review_intelligence.json'
        )
        
        print("\n✅ Review intelligence analysis completed successfully!")
        
        # Display detailed results
        display_complaint_results(complaint_analysis)
        
        # Show complaint trends
        analyze_complaint_trends(intelligence)
        
        # Generate actionable insights
        generate_actionable_insights(complaint_analysis, intelligence)
        
        # Create product-specific analysis
        create_product_specific_analysis(intelligence)
        
        # Validate analysis results
        validate_review_intelligence()
        
    except FileNotFoundError:
        print("❌ Error: Required input files not found!")
        print("💡 Please run the previous pipeline steps first to generate the required data files.")
        
    except Exception as e:
        print(f"❌ Error during review intelligence analysis: {e}")
        print("🔧 Please check your input data and try again.")

def display_complaint_results(complaint_analysis):
    """
    Display detailed results of the complaint analysis.
    
    Args:
        complaint_analysis: The complaint analysis results
    """
    print("\n" + "="*60)
    print("🚨 DETAILED COMPLAINT ANALYSIS RESULTS")
    print("="*60)
    
    total_negative_reviews = complaint_analysis.get('total_negative_reviews', 0)
    total_complaint_categories = complaint_analysis.get('total_complaint_categories', 0)
    
    print(f"\n📈 OVERVIEW:")
    print(f"   Total Negative Reviews: {total_negative_reviews}")
    print(f"   Complaint Categories: {total_complaint_categories}")
    
    # Show top customer issues
    print(f"\n🔍 TOP CUSTOMER ISSUES:")
    top_issues = complaint_analysis.get('top_customer_issues', [])
    
    for i, issue in enumerate(top_issues[:15], 1):
        emoji = "🚨" if i <= 3 else "⚠️" if i <= 8 else "📝"
        print(f"   {emoji} {i:2d}. {issue['issue'].title()}")
        print(f"       Component: {issue['component'].title()} | Frequency: {issue['frequency']} | Products: {issue['products_affected']}")
    
    # Show component breakdown
    component_breakdown = complaint_analysis.get('component_breakdown', {})
    
    print(f"\n📁 COMPONENT COMPLAINT BREAKDOWN:")
    sorted_components = sorted(component_breakdown.items(), 
                               key=lambda x: x[1]['severity_score'], reverse=True)
    
    for i, (component, data) in enumerate(sorted_components, 1):
        emoji = "🔥" if i <= 2 else "⚡" if i <= 4 else "📊"
        print(f"   {emoji} {component.title()}:")
        print(f"      Reviews: {data['review_count']} | Products: {data['product_count']} | Severity: {data['severity_score']}")
        
        if data['top_phrases']:
            print(f"      Top Complaints:")
            for phrase, count in data['top_phrases'][:3]:
                print(f"        • {phrase.title()} ({count} mentions)")
    
    print("="*60)

def analyze_complaint_trends(intelligence):
    """
    Analyze complaint trends and patterns.
    
    Args:
        intelligence: The ReviewIntelligence instance
    """
    print("\n" + "="*60)
    print("📈 COMPLAINT TRENDS ANALYSIS")
    print("="*60)
    
    trends = intelligence.get_complaint_trends()
    
    print(f"\n🔥 MOST PROBLEMATIC COMPONENTS:")
    if trends['most_problematic_component']:
        component, data = trends['most_problematic_component']
        print(f"   🥇 {component.title()}:")
        print(f"      Severity Score: {data['severity_score']}")
        print(f"      Review Count: {data['review_count']}")
        print(f"      Products Affected: {data['product_count']}")
        
        if data['top_phrases']:
            print(f"      Top Complaints:")
            for phrase, count in data['top_phrases'][:5]:
                print(f"        • {phrase.title()} ({count} mentions)")
    
    print(f"\n🔝 TOP COMPLAINT PHRASES OVERALL:")
    for phrase, count in trends['top_complaint_phrases'][:10]:
        print(f"   {count:3d} • {phrase.title()}")
    
    # Analyze complaint severity distribution
    component_breakdown = intelligence.complaint_analysis.get('component_breakdown', {})
    
    severity_levels = {'High': 0, 'Medium': 0, 'Low': 0}
    for data in component_breakdown.values():
        severity = data['severity_score']
        if severity >= 20:
            severity_levels['High'] += 1
        elif severity >= 10:
            severity_levels['Medium'] += 1
        else:
            severity_levels['Low'] += 1
    
    print(f"\n📊 SEVERITY DISTRIBUTION:")
    total = sum(severity_levels.values())
    for level, count in severity_levels.items():
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"   {level}: {count} components ({percentage:.1f}%)")
    
    print("="*60)

def generate_actionable_insights(complaint_analysis, intelligence):
    """
    Generate actionable insights from complaint analysis.
    
    Args:
        complaint_analysis: The complaint analysis results
        intelligence: The ReviewIntelligence instance
    """
    print("\n" + "="*60)
    print("💡 ACTIONABLE INSIGHTS & RECOMMENDATIONS")
    print("="*60)
    
    component_breakdown = complaint_analysis.get('component_breakdown', {})
    
    # Priority recommendations based on severity and frequency
    print(f"\n🎯 PRIORITY IMPROVEMENT AREAS:")
    
    # Sort by severity score
    sorted_components = sorted(component_breakdown.items(), 
                               key=lambda x: x[1]['severity_score'], reverse=True)
    
    for i, (component, data) in enumerate(sorted_components[:5], 1):
        print(f"\n   {i}. {component.title()} (Priority: {'High' if i <= 2 else 'Medium' if i <= 4 else 'Low'})")
        
        # Specific recommendations based on component
        recommendations = get_component_recommendations(component, data)
        for recommendation in recommendations:
            print(f"      • {recommendation}")
    
    # Cross-product issues
    print(f"\n🔗 CROSS-PRODUCT ISSUES:")
    
    # Find components affecting multiple products
    multi_product_issues = [(comp, data) for comp, data in component_breakdown.items() 
                           if data['product_count'] >= 3]
    
    multi_product_issues.sort(key=lambda x: x[1]['review_count'], reverse=True)
    
    for component, data in multi_product_issues[:3]:
        print(f"   📱 {component.title()}: Affects {data['product_count']} products")
        print(f"      Total Complaints: {data['review_count']}")
        print(f"      Recommendation: Focus on {component} quality control across product line")
    
    # Quality improvement suggestions
    print(f"\n🔧 QUALITY IMPROVEMENT SUGGESTIONS:")
    
    # Identify common complaint patterns
    all_phrases = []
    for data in component_breakdown.values():
        all_phrases.extend([(phrase, count, component) for component in component_breakdown.keys() 
                           for phrase, count in data['top_phrases']])
    
    # Group similar complaints
    quality_issues = {
        'reliability': [],
        'performance': [],
        'usability': [],
        'durability': []
    }
    
    for phrase, count, component in all_phrases[:20]:
        phrase_lower = phrase.lower()
        if any(word in phrase_lower for word in ['broken', 'failed', 'doesn\'t work', 'stopped']):
            quality_issues['reliability'].append((phrase, count, component))
        elif any(word in phrase_lower for word in ['slow', 'lag', 'performance', 'speed']):
            quality_issues['performance'].append((phrase, count, component))
        elif any(word in phrase_lower for word in ['uncomfortable', 'difficult', 'hard to']):
            quality_issues['usability'].append((phrase, count, component))
        elif any(word in phrase_lower for word in ['break', 'damage', 'weak', 'fragile']):
            quality_issues['durability'].append((phrase, count, component))
    
    for issue_type, issues in quality_issues.items():
        if issues:
            print(f"\n   📊 {issue_type.title()} Issues:")
            for phrase, count, component in issues[:3]:
                print(f"      • {phrase.title()} ({component}) - {count} mentions")
    
    print("="*60)

def get_component_recommendations(component, data):
    """
    Get specific recommendations for a component.
    
    Args:
        component: Component name
        data: Component data
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    component_recommendations = {
        'battery': [
            "Improve battery optimization and power management",
            "Consider higher capacity battery options",
            "Enhance charging efficiency and speed",
            "Implement better battery health monitoring"
        ],
        'sound': [
            "Upgrade audio drivers and sound processing",
            "Improve speaker and microphone quality",
            "Enhance noise cancellation technology",
            "Optimize audio equalization settings"
        ],
        'camera': [
            "Improve camera sensor quality and processing",
            "Enhance low-light performance",
            "Optimize camera software and algorithms",
            "Improve autofocus and image stabilization"
        ],
        'display': [
            "Upgrade display panel quality",
            "Improve touch responsiveness",
            "Enhance brightness and color accuracy",
            "Address screen durability issues"
        ],
        'performance': [
            "Optimize software performance and memory management",
            "Improve thermal management and cooling",
            "Enhance processor optimization",
            "Reduce system lag and improve responsiveness"
        ],
        'build_quality': [
            "Use higher quality materials",
            "Improve manufacturing quality control",
            "Enhance structural integrity and durability",
            "Better quality assurance testing"
        ],
        'comfort': [
            "Redesign ergonomics for better comfort",
            "Use lighter and more comfortable materials",
            "Improve fit and adjustability",
            "Enhance weight distribution"
        ],
        'connectivity': [
            "Improve wireless connection stability",
            "Enhance bluetooth and wifi performance",
            "Better signal strength and range",
            "Improve pairing and connection reliability"
        ],
        'software': [
            "Fix software bugs and stability issues",
            "Improve user interface and experience",
            "Enhance app compatibility",
            "Regular software updates and improvements"
        ],
        'price': [
            "Reassess pricing strategy and value proposition",
            "Improve product features to justify price",
            "Consider tiered pricing options",
            "Enhance perceived value through quality"
        ]
    }
    
    return component_recommendations.get(component, ["Improve overall product quality and user experience"])

def create_product_specific_analysis(intelligence):
    """
    Create product-specific complaint analysis.
    
    Args:
        intelligence: The ReviewIntelligence instance
    """
    print("\n" + "="*60)
    print("📱 PRODUCT-SPECIFIC COMPLAINT ANALYSIS")
    print("="*60)
    
    # Get a sample of products with most complaints
    product_complaint_counts = {}
    for product_name, components in intelligence.negative_reviews.items():
        total_complaints = sum(len(reviews) for reviews in components.values())
        product_complaint_counts[product_name] = total_complaints
    
    # Sort products by complaint count
    sorted_products = sorted(product_complaint_counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n📊 PRODUCTS WITH MOST COMPLAINTS:")
    for i, (product, count) in enumerate(sorted_products[:5], 1):
        print(f"   {i}. {product}: {count} negative reviews")
        
        # Get product-specific complaints
        product_complaints = intelligence.get_product_specific_complaints(product)
        
        if product_complaints:
            print(f"      Top Complaint Areas:")
            for component, reviews in product_complaints.items():
                print(f"        • {component.title()}: {len(reviews)} complaints")
                
                # Show a sample complaint
                if reviews:
                    sample = reviews[0][:100] + "..." if len(reviews[0]) > 100 else reviews[0]
                    print(f"          Sample: \"{sample}\"")
    
    print("="*60)

def validate_review_intelligence():
    """
    Validate that review intelligence results meet expectations.
    """
    print("\n" + "="*60)
    print("✅ REVIEW INTELLIGENCE VALIDATION")
    print("="*60)
    
    try:
        with open('review_intelligence.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📋 VALIDATION RESULTS:")
        
        # Check required sections
        required_sections = ['total_negative_reviews', 'top_customer_issues', 'component_breakdown']
        missing_sections = [section for section in required_sections if section not in data]
        
        if not missing_sections:
            print(f"   ✅ All required sections present")
        else:
            print(f"   ❌ Missing sections: {missing_sections}")
        
        # Validate data quality
        total_negative = data.get('total_negative_reviews', 0)
        top_issues = data.get('top_customer_issues', [])
        component_breakdown = data.get('component_breakdown', {})
        
        print(f"   ✅ Total negative reviews: {total_negative}")
        print(f"   ✅ Top issues identified: {len(top_issues)}")
        print(f"   ✅ Components analyzed: {len(component_breakdown)}")
        
        # Check for reasonable complaint distribution
        if top_issues:
            frequencies = [issue['frequency'] for issue in top_issues]
            avg_frequency = sum(frequencies) / len(frequencies)
            print(f"   📊 Average complaint frequency: {avg_frequency:.1f}")
        
        # Check component breakdown quality
        if component_breakdown:
            total_component_reviews = sum(data['review_count'] for data in component_breakdown.values())
            print(f"   📊 Total component reviews: {total_component_reviews}")
            
            # Check for severity scores
            severity_scores = [data['severity_score'] for data in component_breakdown.values()]
            avg_severity = sum(severity_scores) / len(severity_scores)
            print(f"   📊 Average severity score: {avg_severity:.1f}")
        
        print(f"\n🔍 DATA QUALITY CHECKS:")
        
        # Check for empty fields
        empty_fields = []
        for issue in top_issues[:5]:
            if not issue.get('issue') or not issue.get('component'):
                empty_fields.append(f"Issue {issue.get('rank', 'unknown')}")
        
        if empty_fields:
            print(f"   ⚠️  Issues with empty fields: {empty_fields}")
        else:
            print(f"   ✅ No empty fields detected in top issues")
        
        # Check for reasonable complaint phrases
        phrase_quality = 0
        for component, data in component_breakdown.items():
            top_phrases = data.get('top_phrases', [])
            if top_phrases:
                for phrase, count in top_phrases[:3]:
                    if len(phrase) > 10 and count > 0:
                        phrase_quality += 1
        
        print(f"   ✅ Quality complaint phrases: {phrase_quality}")
        
        print("="*60)
        
    except FileNotFoundError:
        print("❌ review_intelligence.json not found for validation")
    except Exception as e:
        print(f"❌ Error during validation: {e}")

def export_complaint_report():
    """
    Export a comprehensive complaint report.
    """
    print("\n" + "="*60)
    print("📄 EXPORTING COMPLAINT REPORT")
    print("="*60)
    
    try:
        with open('review_intelligence.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Export to text report
        with open('complaint_report.txt', 'w', encoding='utf-8') as f:
            f.write("CUSTOMER COMPLAINT INTELLIGENCE REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("TOP CUSTOMER ISSUES:\n")
            f.write("-" * 30 + "\n")
            
            top_issues = data.get('top_customer_issues', [])
            for issue in top_issues:
                f.write(f"{issue['rank']}. {issue['issue'].title()} ({issue['component']})\n")
                f.write(f"   Frequency: {issue['frequency']} | Products: {issue['products_affected']}\n\n")
            
            f.write("\nCOMPONENT BREAKDOWN:\n")
            f.write("-" * 30 + "\n")
            
            component_breakdown = data.get('component_breakdown', {})
            for component, comp_data in component_breakdown.items():
                f.write(f"\n{component.title()}:\n")
                f.write(f"  Reviews: {comp_data['review_count']} | Products: {comp_data['product_count']}\n")
                f.write(f"  Severity: {comp_data['severity_score']}\n")
                
                if comp_data.get('top_phrases'):
                    f.write(f"  Top Complaints:\n")
                    for phrase, count in comp_data['top_phrases'][:5]:
                        f.write(f"    - {phrase.title()} ({count})\n")
        
        print("✅ Complaint report exported to complaint_report.txt")
        
        # Export to CSV for analysis
        with open('complaint_data.csv', 'w', encoding='utf-8') as f:
            f.write("Component,Review_Count,Product_Count,Severity_Score,Top_Phrase\n")
            
            for component, comp_data in component_breakdown.items():
                top_phrase = comp_data.get('top_phrases', [['', 0]])[0][0]
                f.write(f"{component},{comp_data['review_count']},{comp_data['product_count']},"
                       f"{comp_data['severity_score']},\"{top_phrase}\"\n")
        
        print("✅ Complaint data exported to complaint_data.csv")
        
    except FileNotFoundError:
        print("❌ review_intelligence.json not found for export")
    except Exception as e:
        print(f"❌ Error during export: {e}")

if __name__ == "__main__":
    # Run main review intelligence analysis
    main()
    
    # Export complaint report
    export_complaint_report()
