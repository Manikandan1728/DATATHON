#!/usr/bin/env python3
"""
Example usage of the ExecutiveReport module for generating executive-level analysis.

This script demonstrates how to use the executive_report.py module to transform
complex competitive intelligence data into clear, actionable executive reports.
"""

from executive_report import ExecutiveReport
import json

def main():
    """
    Main function demonstrating executive report generation.
    """
    print("📊 Starting Executive Intelligence Analysis...")
    
    # Initialize the executive report generator
    executive = ExecutiveReport()
    
    try:
        # Process executive reports
        print("📊 Generating executive-level analysis...")
        reports = executive.process_executive_reports(
            competitor_file='competitor_analysis.json',
            review_file='review_intelligence.json',
            strategy_file='strategic_recommendations.json',
            output_file='executive_reports.json'
        )
        
        print("\n✅ Executive reports generated successfully!")
        
        # Display sample reports
        display_sample_reports(executive)
        
        # Show executive insights
        show_executive_insights(executive)
        
        # Generate actionable executive summary
        generate_executive_summary(executive)
        
        # Create board presentation outline
        create_board_presentation_outline(executive)
        
        # Validate executive reports
        validate_executive_reports()
        
    except FileNotFoundError:
        print("❌ Error: Required input files not found!")
        print("💡 Please run the previous pipeline steps first to generate the required data files.")
        
    except Exception as e:
        print(f"❌ Error during executive report generation: {e}")
        print("🔧 Please check your input data and try again.")

def display_sample_reports(executive):
    """
    Display sample executive reports.
    
    Args:
        executive: The ExecutiveReport instance
    """
    print("\n" + "="*60)
    print("📋 SAMPLE EXECUTIVE REPORTS")
    print("="*60)
    
    # Overall market report
    print(f"\n🌍 OVERALL MARKET INTELLIGENCE:")
    overall_report = executive.get_overall_market_report()
    if overall_report:
        # Show first few lines of overall report
        lines = overall_report.split('\n')
        for line in lines[:15]:
            print(f"   {line}")
        print("   ...")
    else:
        print("   Overall market report not available")
    
    # Brand-specific reports
    print(f"\n🏢 BRAND-SPECIFIC INTELLIGENCE:")
    
    # Get available brand reports
    brand_reports = {k: v for k, v in executive.executive_reports.items() if k != 'overall_market'}
    
    for i, (report_key, report_content) in enumerate(brand_reports.items(), 1):
        if i > 2:  # Show only first 3 brand reports
            break
            
        # Extract brand and category from key
        parts = report_key.split('_')
        brand = parts[0].title()
        category = ' '.join(parts[1:]).title()
        
        print(f"\n   📊 {brand} {category}:")
        
        # Show key sections of the report
        lines = report_content.split('\n')
        in_section = False
        section_lines = []
        
        for line in lines:
            if line.startswith('Market Position:'):
                in_section = True
                section_lines = [line]
            elif in_section and line.startswith('Critical Weaknesses:'):
                section_lines.append(line)
                break
            elif in_section:
                section_lines.append(line)
        
        for line in section_lines:
            print(f"      {line}")
    
    print("="*60)

def show_executive_insights(executive):
    """
    Show key executive insights from the analysis.
    
    Args:
        executive: The ExecutiveReport instance
    """
    print("\n" + "="*60)
    print("🧠 KEY EXECUTIVE INSIGHTS")
    print("="*60)
    
    # Market leadership analysis
    competitor_analysis = executive.competitor_analysis
    cross_analysis = competitor_analysis.get('cross_category_analysis', {})
    overall_ranking = cross_analysis.get('overall_ranking', [])
    
    print(f"\n🏆 MARKET LEADERSHIP ANALYSIS:")
    
    if overall_ranking:
        print(f"   Market Leaders:")
        for i, (brand, stats) in enumerate(overall_ranking[:3], 1):
            categories = ', '.join(stats.get('categories', [])[:2])
            print(f"   {i}. {brand}: {stats['total_wins']} component wins")
            print(f"      Categories: {categories}")
        
        # Market concentration
        if len(overall_ranking) >= 3:
            top_3_wins = sum(brand[1]['total_wins'] for brand in overall_ranking[:3])
            total_wins = sum(brand[1]['total_wins'] for brand in overall_ranking)
            concentration = (top_3_wins / total_wins) * 100
            
            print(f"\n📊 Market Concentration: {concentration:.1f}%")
            if concentration > 60:
                print(f"   Status: Highly concentrated market - top 3 brands dominate")
            elif concentration > 40:
                print(f"   Status: Moderately concentrated - competitive but clear leaders")
            else:
                print(f"   Status: Fragmented market - opportunities for new players")
    
    # Critical market issues
    print(f"\n⚠️  CRITICAL MARKET ISSUES:")
    
    review_intel = executive.review_intelligence.get('component_breakdown', {})
    
    if review_intel:
        # Find most severe issues
        sorted_issues = sorted(review_intel.items(), 
                            key=lambda x: x[1].get('severity_score', 0), 
                            reverse=True)
        
        for i, (component, data) in enumerate(sorted_issues[:5], 1):
            severity = data.get('severity_score', 0)
            review_count = data.get('review_count', 0)
            product_count = data.get('product_count', 0)
            
            priority = "🔴 Critical" if severity > 50 else "🟡 High" if severity > 25 else "🟢 Medium"
            
            print(f"   {priority} {component.title()}:")
            print(f"      Severity: {severity:.1f} | Reviews: {review_count} | Products: {product_count}")
            
            # Show top complaint
            top_phrases = data.get('top_phrases', [])
            if top_phrases:
                print(f"      Main Issue: {top_phrases[0][0].title()}")
    
    # Strategic opportunities
    print(f"\n💡 STRATEGIC OPPORTUNITIES:")
    
    # Find components with high customer dissatisfaction but low competitive performance
    strategic_recs = executive.strategic_recommendations.get('component_recommendations', {})
    
    opportunities = []
    for component, data in strategic_recs.items():
        priority = data.get('priority', 'low')
        intensity = data.get('intensity_score', 0)
        competitive_opp = data.get('competitive_opportunity', False)
        
        if priority == 'high' and competitive_opp:
            opportunities.append((component, intensity, competitive_opp))
    
    # Sort by intensity
    opportunities.sort(key=lambda x: x[1], reverse=True)
    
    for i, (component, intensity, comp_opp) in enumerate(opportunities[:5], 1):
        print(f"   {i}. {component.title()}:")
        print(f"      Customer Impact: {intensity:.1f}")
        print(f"      Competitive Opportunity: {'Yes' if comp_opp else 'No'}")
        print(f"      Strategic Value: High")
    
    print("="*60)

def generate_executive_summary(executive):
    """
    Generate a concise executive summary.
    
    Args:
        executive: The ExecutiveReport instance
    """
    print("\n" + "="*60)
    print("📄 EXECUTIVE SUMMARY FOR BOARD PRESENTATION")
    print("="*60)
    
    competitor_analysis = executive.competitor_analysis
    cross_analysis = competitor_analysis.get('cross_category_analysis', {})
    overall_ranking = cross_analysis.get('overall_ranking', [])
    
    # Market overview
    total_brands = len(overall_ranking)
    total_categories = len(competitor_analysis.get('category_analysis', {}))
    
    print(f"\n📊 MARKET OVERVIEW:")
    print(f"   • Total Brands Analyzed: {total_brands}")
    print(f"   • Product Categories: {total_categories}")
    
    if overall_ranking:
        market_leader = overall_ranking[0]
        print(f"   • Market Leader: {market_leader[0]} ({market_leader[1]['total_wins']} component wins)")
    
    # Key findings
    print(f"\n🔍 KEY FINDINGS:")
    
    # Finding 1: Market concentration
    if len(overall_ranking) >= 3:
        top_3_wins = sum(brand[1]['total_wins'] for brand in overall_ranking[:3])
        total_wins = sum(brand[1]['total_wins'] for brand in overall_ranking)
        concentration = (top_3_wins / total_wins) * 100
        
        print(f"   1. Market Concentration: {concentration:.1f}% controlled by top 3 brands")
    
    # Finding 2: Most critical issues
    review_intel = executive.review_intelligence.get('component_breakdown', {})
    if review_intel:
        sorted_issues = sorted(review_intel.items(), 
                            key=lambda x: x[1].get('severity_score', 0), 
                            reverse=True)
        
        if sorted_issues:
            worst_component = sorted_issues[0]
            severity = worst_component[1].get('severity_score', 0)
            print(f"   2. Critical Issue: {worst_component[0].title()} (severity: {severity:.1f})")
    
    # Finding 3: Strategic opportunities
    strategic_recs = executive.strategic_recommendations.get('strategic_summary', {})
    top_recs = strategic_recs.get('top_recommendations', [])
    
    if top_recs:
        top_rec = top_recs[0]
        print(f"   3. Top Priority: {top_rec.get('key_recommendation', 'Unknown')}")
    
    # Strategic recommendations
    print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
    
    # Top 3 strategic priorities
    for i, rec in enumerate(top_recs[:3], 1):
        component = rec.get('component', 'Unknown')
        impact = rec.get('impact_score', 0)
        print(f"   {i}. Focus on {component.title()} (Impact Score: {impact})")
    
    # Investment priorities
    priority_breakdown = strategic_recs.get('priority_breakdown', {})
    if priority_breakdown:
        high_priority = priority_breakdown.get('high', 0)
        total_recs = sum(priority_breakdown.values())
        
        print(f"\n💰 INVESTMENT PRIORITIES:")
        print(f"   • High Priority Initiatives: {high_priority}/{total_recs}")
        print(f"   • Recommended Investment: Focus on high-impact components first")
    
    # Risk assessment
    print(f"\n⚠️  RISK ASSESSMENT:")
    
    # Market risks
    if concentration > 60:
        print(f"   • Market Risk: High concentration creates barriers to entry")
    
    # Customer satisfaction risks
    if review_intel:
        total_negative = executive.review_intelligence.get('total_negative_reviews', 0)
        if total_negative > 1000:
            print(f"   • Customer Risk: {total_negative} negative reviews indicate satisfaction issues")
    
    # Competitive risks
    if overall_ranking and len(overall_ranking) > 1:
        leader_score = overall_ranking[0][1]['total_wins']
        second_score = overall_ranking[1][1]['total_wins']
        gap = leader_score - second_score
        
        if gap < 3:
            print(f"   • Competitive Risk: Tight competition at top ({gap} win gap)")
    
    print("="*60)

def create_board_presentation_outline(executive):
    """
    Create a board presentation outline based on executive analysis.
    
    Args:
        executive: The ExecutiveReport instance
    """
    print("\n" + "="*60)
    print("📽️  BOARD PRESENTATION OUTLINE")
    print("="*60)
    
    print(f"\n🎯 TITLE: Competitive Intelligence & Strategic Recommendations")
    print(f"📅 Date: {datetime.now().strftime('%B %d, %Y')}")
    
    print(f"\n📋 AGENDA:")
    
    print(f"\n1. MARKET OVERVIEW (5 minutes)")
    print(f"   • Total market size and competitive landscape")
    print(f"   • Key players and market positioning")
    print(f"   • Market trends and dynamics")
    
    print(f"\n2. COMPETITIVE ANALYSIS (10 minutes)")
    print(f"   • Brand performance rankings")
    print(f"   • Component-level competitive gaps")
    print(f"   • Market leader analysis")
    
    print(f"\n3. CUSTOMER INTELLIGENCE (10 minutes)")
    print(f"   • Customer satisfaction analysis")
    print(f"   • Critical pain points by component")
    print(f"   • Complaint trends and patterns")
    
    print(f"\n4. STRATEGIC RECOMMENDATIONS (15 minutes)")
    print(f"   • High-priority improvement areas")
    print(f"   • Investment opportunities")
    print(f"   • Competitive advantage strategies")
    
    print(f"\n5. IMPLEMENTATION ROADMAP (10 minutes)")
    print(f"   • Short-term initiatives (0-6 months)")
    print(f"   • Medium-term projects (6-12 months)")
    print(f"   • Long-term strategic initiatives")
    
    print(f"\n6. FINANCIAL IMPLICATIONS (5 minutes)")
    print(f"   • Investment requirements")
    print(f"   • ROI projections")
    print(f"   • Risk mitigation strategies")
    
    print(f"\n7. Q&A AND DISCUSSION (15 minutes)")
    
    print(f"\n📊 KEY SLIDES TO PREPARE:")
    
    # Market leadership slide
    cross_analysis = executive.competitor_analysis.get('cross_category_analysis', {})
    overall_ranking = cross_analysis.get('overall_ranking', [])
    
    if overall_ranking:
        print(f"\n   Slide 1: Market Leadership")
        print(f"   • Top 5 brands with component wins")
        print(f"   • Market concentration analysis")
        print(f"   • Competitive positioning map")
    
    # Critical issues slide
    review_intel = executive.review_intelligence.get('component_breakdown', {})
    if review_intel:
        print(f"\n   Slide 2: Critical Customer Issues")
        print(f"   • Top 5 customer complaint categories")
        print(f"   • Severity and impact analysis")
        print(f"   • Affected product lines")
    
    # Strategic recommendations slide
    strategic_recs = executive.strategic_recommendations.get('strategic_summary', {})
    top_recs = strategic_recs.get('top_recommendations', [])
    
    if top_recs:
        print(f"\n   Slide 3: Strategic Priorities")
        print(f"   • Top 5 improvement recommendations")
        print(f"   • Impact vs. effort matrix")
        print(f"   • Competitive advantage opportunities")
    
    # Implementation timeline slide
    timeline = executive.strategic_recommendations.get('implementation_timeline', {})
    if timeline:
        print(f"\n   Slide 4: Implementation Timeline")
        print(f"   • Phase-based rollout plan")
        print(f"   • Resource allocation")
        print(f"   • Success metrics and KPIs")
    
    print(f"\n🎯 PRESENTATION TIPS:")
    print(f"   • Focus on actionable insights, not just data")
    print(f"   • Use visual aids to show competitive gaps")
    print(f"   • Emphasize ROI and business impact")
    print(f"   • Prepare for questions about investment justification")
    print(f"   • Have backup data ready for deep dives")
    
    print("="*60)

def validate_executive_reports():
    """
    Validate that executive reports meet quality standards.
    """
    print("\n" + "="*60)
    print("✅ EXECUTIVE REPORTS VALIDATION")
    print("="*60)
    
    try:
        with open('executive_reports.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📋 VALIDATION RESULTS:")
        
        # Check required sections
        if 'overall_market' in data:
            print(f"   ✅ Overall market report present")
        else:
            print(f"   ❌ Overall market report missing")
        
        # Check brand reports
        brand_reports = {k: v for k, v in data.items() if k != 'overall_market'}
        print(f"   ✅ Brand-specific reports: {len(brand_reports)}")
        
        # Validate report format
        valid_reports = 0
        for report_key, report_content in brand_reports.items():
            if isinstance(report_content, str) and len(report_content) > 500:
                # Check for key sections
                if ('Market Position:' in report_content and 
                    'Critical Weaknesses:' in report_content and 
                    'Competitive Advantages:' in report_content):
                    valid_reports += 1
        
        print(f"   ✅ Properly formatted reports: {valid_reports}/{len(brand_reports)}")
        
        # Check for executive-level content
        executive_keywords = ['strategic', 'competitive', 'market', 'priority', 'investment', 'risk']
        keyword_count = 0
        
        for report_content in data.values():
            if isinstance(report_content, str):
                for keyword in executive_keywords:
                    if keyword.lower() in report_content.lower():
                        keyword_count += 1
        
        print(f"   📊 Executive keywords found: {keyword_count}")
        
        # Validate report quality
        avg_report_length = 0
        if brand_reports:
            total_length = sum(len(content) for content in brand_reports.values() if isinstance(content, str))
            avg_report_length = total_length / len(brand_reports)
        
        print(f"   📏 Average report length: {avg_report_length:.0f} characters")
        
        if avg_report_length > 1000:
            print(f"   ✅ Report length: Comprehensive")
        elif avg_report_length > 500:
            print(f"   ⚠️  Report length: Adequate")
        else:
            print(f"   ❌ Report length: Too brief")
        
        print("="*60)
        
    except FileNotFoundError:
        print("❌ executive_reports.json not found for validation")
    except Exception as e:
        print(f"❌ Error during validation: {e}")

def export_executive_presentation():
    """
    Export executive presentation materials.
    """
    print("\n" + "="*60)
    print("📄 EXPORTING EXECUTIVE PRESENTATION MATERIALS")
    print("="*60)
    
    try:
        with open('executive_reports.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Export to presentation-ready format
        with open('executive_presentation.txt', 'w', encoding='utf-8') as f:
            f.write("EXECUTIVE INTELLIGENCE PRESENTATION\n")
            f.write("=" * 60 + "\n\n")
            
            # Overall market report
            if 'overall_market' in data:
                f.write("OVERALL MARKET ANALYSIS\n")
                f.write("-" * 30 + "\n")
                f.write(data['overall_market'])
                f.write("\n\n")
            
            # Brand reports
            brand_reports = {k: v for k, v in data.items() if k != 'overall_market'}
            
            f.write("BRAND-SPECIFIC ANALYSIS\n")
            f.write("-" * 30 + "\n")
            
            for report_key, report_content in brand_reports.items():
                parts = report_key.split('_')
                brand = parts[0].title()
                category = ' '.join(parts[1:]).title()
                
                f.write(f"\n{brand} {category}\n")
                f.write("=" * 40 + "\n")
                f.write(report_content)
                f.write("\n\n")
        
        print("✅ Executive presentation exported to executive_presentation.txt")
        
        # Export summary for quick reference
        with open('executive_summary.txt', 'w', encoding='utf-8') as f:
            f.write("EXECUTIVE SUMMARY - KEY INSIGHTS\n")
            f.write("=" * 40 + "\n\n")
            
            # Extract key insights from reports
            if 'overall_market' in data:
                overall = data['overall_market']
                lines = overall.split('\n')
                
                for line in lines:
                    if any(keyword in line for keyword in ['Market Overview:', 'Top Performing:', 'Key Market']):
                        f.write(line + "\n")
            
            f.write("\nTOP BRAND INSIGHTS\n")
            f.write("-" * 20 + "\n")
            
            for report_key, report_content in list(brand_reports.items())[:3]:
                parts = report_key.split('_')
                brand = parts[0].title()
                category = ' '.join(parts[1:]).title()
                
                f.write(f"\n{brand} {category}:\n")
                
                lines = report_content.split('\n')
                for line in lines:
                    if line.startswith('Market Position:'):
                        f.write(f"  {line}\n")
                    elif line.startswith('Top Priority:'):
                        f.write(f"  {line}\n")
                    elif line.startswith('Critical Weaknesses:'):
                        f.write(f"  {line}\n")
                        break
        
        print("✅ Executive summary exported to executive_summary.txt")
        
    except FileNotFoundError:
        print("❌ executive_reports.json not found for export")
    except Exception as e:
        print(f"❌ Error during export: {e}")

if __name__ == "__main__":
    # Run main executive report generation
    main()
    
    # Export presentation materials
    export_executive_presentation()
