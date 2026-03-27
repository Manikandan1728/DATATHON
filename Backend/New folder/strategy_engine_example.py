#!/usr/bin/env python3
"""
Example usage of the StrategyEngine module for generating product improvement suggestions.

This script demonstrates how to use the strategy_engine.py module to combine
competitive analysis and customer feedback into actionable strategic recommendations.
"""

from strategy_engine import StrategyEngine
import json

def main():
    """
    Main function demonstrating strategy engine usage.
    """
    print("🎯 Starting Strategic Recommendations Engine...")
    
    # Initialize the strategy engine
    engine = StrategyEngine()
    
    try:
        # Process strategic recommendations
        print("📊 Generating strategic recommendations...")
        strategic_recommendations = engine.process_strategy_engine(
            competitor_file='competitor_analysis.json',
            review_file='review_intelligence.json',
            output_file='strategic_recommendations.json'
        )
        
        print("\n✅ Strategic recommendations completed successfully!")
        
        # Display detailed results
        display_strategic_results(strategic_recommendations)
        
        # Show implementation roadmap
        show_implementation_roadmap(strategic_recommendations)
        
        # Generate competitive insights
        generate_competitive_insights(strategic_recommendations)
        
        # Create action plan
        create_action_plan(engine)
        
        # Validate strategy results
        validate_strategy_recommendations()
        
    except FileNotFoundError:
        print("❌ Error: Required input files not found!")
        print("💡 Please run the previous pipeline steps first to generate the required data files.")
        
    except Exception as e:
        print(f"❌ Error during strategic recommendations: {e}")
        print("🔧 Please check your input data and try again.")

def display_strategic_results(strategic_recommendations):
    """
    Display detailed results of the strategic recommendations.
    
    Args:
        strategic_recommendations: The strategic recommendations results
    """
    print("\n" + "="*60)
    print("🎯 DETAILED STRATEGIC RECOMMENDATIONS")
    print("="*60)
    
    summary = strategic_recommendations.get('strategic_summary', {})
    component_recommendations = strategic_recommendations.get('component_recommendations', {})
    
    total_recommendations = summary.get('total_recommendations', 0)
    priority_breakdown = summary.get('priority_breakdown', {})
    
    print(f"\n📈 OVERVIEW:")
    print(f"   Total Recommendations: {total_recommendations}")
    print(f"   High Priority: {priority_breakdown.get('high', 0)}")
    print(f"   Medium Priority: {priority_breakdown.get('medium', 0)}")
    print(f"   Low Priority: {priority_breakdown.get('low', 0)}")
    
    # Show top recommendations
    print(f"\n🚨 TOP STRATEGIC RECOMMENDATIONS:")
    top_recommendations = summary.get('top_recommendations', [])
    
    for i, rec in enumerate(top_recommendations[:15], 1):
        emoji = "🔥" if i <= 3 else "⚡" if i <= 8 else "💡"
        print(f"   {emoji} {i:2d}. {rec['key_recommendation']}")
        print(f"       Component: {rec['component'].title()} | Priority: {rec['priority']}")
        print(f"       Impact Score: {rec['impact_score']} | Products: {rec['affected_products']}")
    
    # Show component-specific details
    print(f"\n📁 COMPONENT-SPECIFIC RECOMMENDATIONS:")
    
    # Group by priority
    high_priority_components = []
    medium_priority_components = []
    low_priority_components = []
    
    for component, data in component_recommendations.items():
        priority = data.get('priority', 'low')
        if priority == 'high':
            high_priority_components.append((component, data))
        elif priority == 'medium':
            medium_priority_components.append((component, data))
        else:
            low_priority_components.append((component, data))
    
    print(f"\n🔥 HIGH PRIORITY COMPONENTS:")
    for component, data in high_priority_components:
        print(f"   📱 {component.title()}:")
        print(f"      Intensity Score: {data.get('intensity_score', 0):.1f}")
        print(f"      Affected Products: {data.get('affected_products', 0)}")
        
        base_recs = data.get('base_recommendations', [])
        if base_recs:
            print(f"      Key Actions:")
            for rec in base_recs[:2]:
                print(f"        • {rec}")
        
        customer_complaints = data.get('customer_complaints', [])
        if customer_complaints:
            print(f"      Customer Issues: {', '.join(customer_complaints[:2])}")
    
    print("="*60)

def show_implementation_roadmap(strategic_recommendations):
    """
    Show implementation roadmap for recommendations.
    
    Args:
        strategic_recommendations: The strategic recommendations results
    """
    print("\n" + "="*60)
    print("🗺️  IMPLEMENTATION ROADMAP")
    print("="*60)
    
    timeline = strategic_recommendations.get('implementation_timeline', {})
    
    print(f"\n⏰ PHASE-BASED IMPLEMENTATION:")
    
    phase_descriptions = {
        'immediate': "Immediate Actions (0-3 months)",
        'short_term': "Short-term Initiatives (3-6 months)",
        'medium_term': "Medium-term Projects (6-12 months)",
        'long_term': "Long-term Strategy (12+ months)"
    }
    
    for phase, components in timeline.items():
        phase_name = phase_descriptions.get(phase, phase.replace('_', ' ').title())
        print(f"\n📅 {phase_name}:")
        
        if components:
            component_recommendations = strategic_recommendations.get('component_recommendations', {})
            
            for component in components:
                comp_data = component_recommendations.get(component, {})
                priority = comp_data.get('priority', 'medium')
                intensity = comp_data.get('intensity_score', 0)
                
                print(f"   🎯 {component.title()}:")
                print(f"      Priority: {priority} | Impact: {intensity:.1f}")
                
                # Show top recommendation
                base_recs = comp_data.get('base_recommendations', [])
                if base_recs:
                    print(f"      Action: {base_recs[0]}")
        else:
            print(f"   No components in this phase")
    
    # Resource allocation suggestions
    print(f"\n💰 RESOURCE ALLOCATION RECOMMENDATIONS:")
    
    total_components = sum(len(components) for components in timeline.values())
    if total_components > 0:
        immediate_ratio = len(timeline.get('immediate', [])) / total_components
        short_term_ratio = len(timeline.get('short_term', [])) / total_components
        
        print(f"   🔥 Immediate Focus: {immediate_ratio*100:.1f}% of resources")
        print(f"   ⚡ Short-term Focus: {short_term_ratio*100:.1f}% of resources")
        print(f"   📊 Medium/Long-term: {(1-immediate_ratio-short_term_ratio)*100:.1f}% of resources")
    
    print("="*60)

def generate_competitive_insights(strategic_recommendations):
    """
    Generate competitive insights from strategic recommendations.
    
    Args:
        strategic_recommendations: The strategic recommendations results
    """
    print("\n" + "="*60)
    print("🏆 COMPETITIVE INSIGHTS & OPPORTUNITIES")
    print("="*60)
    
    competitive_gaps = strategic_recommendations.get('competitive_gaps', {})
    component_recommendations = strategic_recommendations.get('component_recommendations', {})
    
    print(f"\n🎯 COMPETITIVE OPPORTUNITIES:")
    
    opportunities = []
    for component, data in component_recommendations.items():
        if data.get('competitive_opportunity'):
            opportunities.append((component, data))
    
    # Sort by intensity score
    opportunities.sort(key=lambda x: x[1].get('intensity_score', 0), reverse=True)
    
    for i, (component, data) in enumerate(opportunities[:5], 1):
        intensity = data.get('intensity_score', 0)
        affected_products = data.get('affected_products', 0)
        
        print(f"\n   {i}. {component.title()} Opportunity:")
        print(f"      Impact Score: {intensity:.1f}")
        print(f"      Products Affected: {affected_products}")
        print(f"      Strategic Value: High competitive advantage potential")
        
        # Show key recommendation
        base_recs = data.get('base_recommendations', [])
        if base_recs:
            print(f"      Key Action: {base_recs[0]}")
    
    # Market positioning insights
    print(f"\n📈 MARKET POSITIONING INSIGHTS:")
    
    # Analyze component dominance patterns
    category_analysis = competitive_gaps.get('category_analysis', {})
    
    weak_areas = []
    for category, data in competitive_gaps.items():
        weak_components = data.get('weak_components', [])
        if weak_components:
            weak_areas.extend([(comp['component'], comp['leader_score']) for comp in weak_components])
    
    if weak_areas:
        print(f"   🔍 Market Weaknesses Identified:")
        weak_areas.sort(key=lambda x: x[1])  # Sort by score (ascending = weaker)
        
        for component, score in weak_areas[:5]:
            print(f"      • {component.title()}: Competitor weakness (score: {score:.2f})")
            print(f"        Opportunity: Gain market share through superior {component}")
    
    # Strategic recommendations by competitive impact
    print(f"\n💡 STRATEGIC RECOMMENDATIONS BY COMPETITIVE IMPACT:")
    
    prioritized = strategic_recommendations.get('prioritized_recommendations', [])
    
    # Focus on recommendations with competitive opportunities
    competitive_recs = [rec for rec in prioritized if rec.get('competitive_opportunity')]
    
    for i, rec in enumerate(competitive_recs[:5], 1):
        print(f"   {i}. {rec['recommendations'][0] if rec['recommendations'] else 'Improve component'}")
        print(f"      Component: {rec['component'].title()}")
        print(f"      Competitive Advantage: High")
        print(f"      Customer Impact: {rec['affected_products']} products")
    
    print("="*60)

def create_action_plan(engine):
    """
    Create detailed action plan for implementation.
    
    Args:
        engine: The StrategyEngine instance
    """
    print("\n" + "="*60)
    print("📋 DETAILED ACTION PLAN")
    print("="*60)
    
    # Get quick wins
    quick_wins = engine.get_quick_wins()
    
    print(f"\n🚀 QUICK WINS (High Impact, Fast Implementation):")
    
    for i, win in enumerate(quick_wins, 1):
        print(f"\n   {i}. {win['recommendations'][0] if win['recommendations'] else 'Improve component'}")
        print(f"      Component: {win['component'].title()}")
        print(f"      Priority: {win['priority']}")
        print(f"      Impact Score: {win['priority_score']}")
        print(f"      Timeline: 0-3 months")
        print(f"      Resources: Cross-functional team required")
        print(f"      Success Metrics: Customer satisfaction score improvement")
    
    # Component-specific deep dive
    print(f"\n📱 COMPONENT DEEP DIVE:")
    
    strategic_recommendations = engine.strategic_recommendations
    component_recommendations = strategic_recommendations.get('component_recommendations', {})
    
    # Select top 3 components for detailed analysis
    prioritized = strategic_recommendations.get('prioritized_recommendations', [])
    top_components = [rec['component'] for rec in prioritized[:3]]
    
    for component in top_components:
        comp_data = component_recommendations.get(component, {})
        
        print(f"\n   🎯 {component.title()} Improvement Plan:")
        print(f"      Current Priority: {comp_data.get('priority', 'unknown')}")
        print(f"      Customer Impact: {comp_data.get('intensity_score', 0):.1f}")
        print(f"      Affected Products: {comp_data.get('affected_products', 0)}")
        
        print(f"      Recommended Actions:")
        all_recs = comp_data.get('base_recommendations', []) + comp_data.get('contextual_recommendations', [])
        for i, rec in enumerate(all_recs[:3], 1):
            print(f"        {i}. {rec}")
        
        print(f"      Success Metrics:")
        print(f"        • Reduce customer complaints by 25%")
        print(f"        • Improve component satisfaction score by 0.5 points")
        print(f"        • Gain market share in competitive segments")
        
        print(f"      Required Resources:")
        print(f"        • R&D team for technical improvements")
        print(f"        • Marketing for communication of improvements")
        print(f"        • Customer support for feedback collection")
    
    # Risk assessment
    print(f"\n⚠️  RISK ASSESSMENT:")
    
    print(f"   📊 Implementation Risks:")
    print(f"      • Technical complexity may delay timeline")
    print(f"      • Resource constraints may impact quality")
    print(f"      • Market conditions may change priorities")
    
    print(f"   🛡️  Mitigation Strategies:")
    print(f"      • Phased implementation approach")
    print(f"      • Regular progress reviews and adjustments")
    print(f"      • Contingency planning for critical components")
    
    print("="*60)

def validate_strategy_recommendations():
    """
    Validate that strategy recommendations meet expectations.
    """
    print("\n" + "="*60)
    print("✅ STRATEGY RECOMMENDATIONS VALIDATION")
    print("="*60)
    
    try:
        with open('strategic_recommendations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📋 VALIDATION RESULTS:")
        
        # Check required sections
        required_sections = [
            'strategic_summary', 'component_recommendations', 
            'prioritized_recommendations', 'implementation_timeline'
        ]
        missing_sections = [section for section in required_sections if section not in data]
        
        if not missing_sections:
            print(f"   ✅ All required sections present")
        else:
            print(f"   ❌ Missing sections: {missing_sections}")
        
        # Validate strategic summary
        summary = data.get('strategic_summary', {})
        total_recs = summary.get('total_recommendations', 0)
        priority_breakdown = summary.get('priority_breakdown', {})
        
        print(f"   ✅ Total recommendations: {total_recs}")
        print(f"   ✅ Priority breakdown: {priority_breakdown}")
        
        # Validate component recommendations
        component_recs = data.get('component_recommendations', {})
        print(f"   ✅ Components analyzed: {len(component_recs)}")
        
        # Check for proper structure in component recommendations
        valid_components = 0
        for component, rec_data in component_recs.items():
            required_keys = ['priority', 'intensity_score', 'base_recommendations', 'contextual_recommendations']
            if all(key in rec_data for key in required_keys):
                valid_components += 1
        
        print(f"   ✅ Valid component structures: {valid_components}/{len(component_recs)}")
        
        # Validate prioritized recommendations
        prioritized = data.get('prioritized_recommendations', [])
        if prioritized:
            print(f"   ✅ Prioritized recommendations: {len(prioritized)}")
            
            # Check priority scores
            scores = [rec.get('priority_score', 0) for rec in prioritized]
            avg_score = sum(scores) / len(scores) if scores else 0
            print(f"   📊 Average priority score: {avg_score:.1f}")
            
            # Check for proper sorting
            sorted_scores = sorted(scores, reverse=True)
            is_sorted = scores == sorted_scores
            print(f"   ✅ Properly sorted by priority: {is_sorted}")
        
        # Validate implementation timeline
        timeline = data.get('implementation_timeline', {})
        if timeline:
            total_timeline_components = sum(len(components) for components in timeline.values())
            print(f"   ✅ Timeline components: {total_timeline_components}")
            
            for phase, components in timeline.items():
                print(f"   📅 {phase}: {len(components)} components")
        
        print(f"\n🎯 QUALITY CHECKS:")
        
        # Check for actionable recommendations
        actionable_count = 0
        for component, rec_data in component_recs.items():
            all_recs = rec_data.get('base_recommendations', []) + rec_data.get('contextual_recommendations', [])
            if all_recs and len(all_recs[0]) > 10:  # Reasonable length
                actionable_count += 1
        
        print(f"   ✅ Actionable recommendations: {actionable_count}/{len(component_recs)}")
        
        # Check for competitive opportunities
        competitive_opportunities = sum(1 for rec in prioritized if rec.get('competitive_opportunity'))
        print(f"   🏆 Competitive opportunities: {competitive_opportunities}")
        
        print("="*60)
        
    except FileNotFoundError:
        print("❌ strategic_recommendations.json not found for validation")
    except Exception as e:
        print(f"❌ Error during validation: {e}")

def export_strategy_report():
    """
    Export comprehensive strategy report.
    """
    print("\n" + "="*60)
    print("📄 EXPORTING STRATEGY REPORT")
    print("="*60)
    
    try:
        with open('strategic_recommendations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Export to text report
        with open('strategy_report.txt', 'w', encoding='utf-8') as f:
            f.write("PRODUCT IMPROVEMENT STRATEGY REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            summary = data.get('strategic_summary', {})
            top_recs = summary.get('top_recommendations', [])
            
            f.write("STRATEGIC RECOMMENDATIONS:\n")
            f.write("-" * 30 + "\n")
            
            for rec in top_recs:
                f.write(f"{rec['rank']}. {rec['key_recommendation']}\n")
                f.write(f"   Component: {rec['component']} | Priority: {rec['priority']}\n")
                f.write(f"   Impact Score: {rec['impact_score']} | Products: {rec['affected_products']}\n\n")
            
            f.write("\nIMPLEMENTATION TIMELINE:\n")
            f.write("-" * 30 + "\n")
            
            timeline = data.get('implementation_timeline', {})
            phase_names = {
                'immediate': 'Immediate (0-3 months)',
                'short_term': 'Short-term (3-6 months)',
                'medium_term': 'Medium-term (6-12 months)',
                'long_term': 'Long-term (12+ months)'
            }
            
            for phase, components in timeline.items():
                f.write(f"\n{phase_names.get(phase, phase)}:\n")
                for component in components:
                    f.write(f"  • {component}\n")
            
            f.write("\n\nCOMPONENT-SPECIFIC ACTIONS:\n")
            f.write("-" * 30 + "\n")
            
            component_recs = data.get('component_recommendations', {})
            for component, comp_data in component_recs.items():
                f.write(f"\n{component.upper()}:\n")
                f.write(f"  Priority: {comp_data.get('priority', 'unknown')}\n")
                f.write(f"  Intensity Score: {comp_data.get('intensity_score', 0):.1f}\n")
                
                all_recs = comp_data.get('base_recommendations', []) + comp_data.get('contextual_recommendations', [])
                for rec in all_recs[:3]:
                    f.write(f"  • {rec}\n")
        
        print("✅ Strategy report exported to strategy_report.txt")
        
        # Export to CSV for tracking
        with open('strategy_tracker.csv', 'w', encoding='utf-8') as f:
            f.write("Component,Priority,IntensityScore,AffectedProducts,CompetitiveOpportunity,TopRecommendation\n")
            
            component_recs = data.get('component_recommendations', {})
            for component, comp_data in component_recs.items():
                top_rec = comp_data.get('base_recommendations', [''])[0] if comp_data.get('base_recommendations') else ''
                competitive_opp = comp_data.get('competitive_opportunity', False)
                
                f.write(f"{component},{comp_data.get('priority', '')},{comp_data.get('intensity_score', 0)},"
                       f"{comp_data.get('affected_products', 0)},{competitive_opp},\"{top_rec}\"\n")
        
        print("✅ Strategy tracker exported to strategy_tracker.csv")
        
    except FileNotFoundError:
        print("❌ strategic_recommendations.json not found for export")
    except Exception as e:
        print(f"❌ Error during export: {e}")

if __name__ == "__main__":
    # Run main strategy engine
    main()
    
    # Export strategy report
    export_strategy_report()
