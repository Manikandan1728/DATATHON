#!/usr/bin/env python3
"""
Example usage of the TrendAnalysis module for detecting emerging product issues.

This script demonstrates how to use the trend_analysis.py module to identify
trends in customer complaints and sentiment over time.
"""

from trend_analysis import TrendAnalysis
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Main function demonstrating trend analysis capabilities.
    """
    print("📈 Starting Trend Analysis for Emerging Product Issues...")
    
    try:
        # Initialize trend analyzer
        analyzer = TrendAnalysis()
        
        # Process trend analysis
        print("🔍 Analyzing temporal patterns in customer feedback...")
        results = analyzer.process_trend_analysis(
            component_file='component_reviews.json',
            sentiment_file='component_sentiment_scores.json',
            review_file='review_intelligence.json',
            output_file='trend_alerts.json'
        )
        
        print("\n✅ Trend analysis completed successfully!")
        
        # Display trend results
        display_trend_results(results, analyzer)
        
        # Show top alerts
        show_top_alerts(analyzer)
        
        # Analyze specific components
        analyze_component_trends(analyzer)
        
        # Generate trend summary
        generate_trend_summary(analyzer)
        
        # Validate trend analysis
        validate_trend_analysis()
        
    except FileNotFoundError:
        print("❌ Error: Required input files not found!")
        print("💡 Please run the main pipeline first to generate the required data files.")
        
    except Exception as e:
        print(f"❌ Error during trend analysis: {e}")
        print("🔧 Please check your input data and try again.")

def display_trend_results(results, analyzer):
    """
    Display comprehensive trend analysis results.
    
    Args:
        results: Trend analysis results
        analyzer: TrendAnalysis instance
    """
    print("\n" + "="*60)
    print("📊 TREND ANALYSIS RESULTS")
    print("="*60)
    
    temporal_data = results.get('temporal_data', {})
    trend_metrics = results.get('trend_metrics', {})
    trend_alerts = results.get('trend_alerts', {})
    
    # Display temporal data summary
    print(f"\n📅 TEMPORAL DATA SUMMARY:")
    
    component_mentions = temporal_data.get('component_mentions', {})
    print(f"   Components tracked: {len(component_mentions)}")
    
    # Show components with most data
    if component_mentions:
        component_counts = [(comp, len(months)) for comp, months in component_mentions.items()]
        component_counts.sort(key=lambda x: x[1], reverse=True)
        
        print(f"   Components with most temporal data:")
        for comp, count in component_counts[:5]:
            total_mentions = sum(component_mentions[comp].values())
            print(f"      {comp.title()}: {count} months, {total_mentions} total mentions")
    
    complaint_patterns = temporal_data.get('complaint_patterns', {})
    print(f"   Complaint patterns tracked: {len(complaint_patterns)}")
    
    # Display trend metrics summary
    print(f"\n📈 TREND METRICS SUMMARY:")
    
    component_trends = trend_metrics.get('component_trends', {})
    print(f"   Component trends analyzed: {len(component_trends)}")
    
    # Show components with biggest changes
    if component_trends:
        component_changes = []
        for comp, trend in component_trends.items():
            if trend:
                component_changes.append((comp, trend.get('percentage_change', 0), trend.get('trend_direction', 'stable')))
        
        component_changes.sort(key=lambda x: abs(x[1]), reverse=True)
        
        print(f"   Components with largest percentage changes:")
        for comp, change, direction in component_changes[:5]:
            print(f"      {comp.title()}: {change:+.1f}% ({direction})")
    
    sentiment_trends = trend_metrics.get('sentiment_trends', {})
    print(f"   Sentiment trends analyzed: {len(sentiment_trends)}")
    
    # Show sentiment changes
    if sentiment_trends:
        sentiment_changes = []
        for comp, trend in sentiment_trends.items():
            if trend:
                sentiment_changes.append((comp, trend.get('percentage_change', 0), trend.get('current_sentiment', 0)))
        
        sentiment_changes.sort(key=lambda x: abs(x[1]), reverse=True)
        
        print(f"   Components with largest sentiment changes:")
        for comp, change, current in sentiment_changes[:5]:
            print(f"      {comp.title()}: {change:+.1f}% (current: {current:.3f})")
    
    # Display emerging issues
    emerging_issues = trend_metrics.get('emerging_issues', [])
    print(f"\n🚨 EMERGING ISSUES IDENTIFIED: {len(emerging_issues)}")
    
    for i, issue in enumerate(emerging_issues[:3], 1):
        issue_type = issue.get('type', 'unknown')
        if issue_type == 'emerging_complaint':
            print(f"   {i}. {issue['issue'].title()} complaints")
            print(f"      Growth: {issue.get('growth_rate', 0):+.1f}% | Recent mentions: {issue.get('recent_mentions', 0)}")
        elif issue_type == 'sentiment_decline':
            print(f"   {i}. {issue['issue'].title()} sentiment decline")
            print(f"      Change: {issue.get('sentiment_change', 0):+.1f}% | Current: {issue.get('current_sentiment', 0):.3f}")
            print(f"      Concern level: {issue.get('concern_level', 'medium')}")
    
    # Display alerts summary
    alerts_summary = trend_alerts.get('summary', {})
    print(f"\n📋 ALERTS SUMMARY:")
    print(f"   Total alerts: {alerts_summary.get('total_alerts', 0)}")
    print(f"   Critical: {alerts_summary.get('critical_count', 0)}")
    print(f"   Warning: {alerts_summary.get('warning_count', 0)}")
    print(f"   Emerging: {alerts_summary.get('emerging_count', 0)}")
    print(f"   Positive: {alerts_summary.get('positive_count', 0)}")
    
    print("="*60)

def show_top_alerts(analyzer):
    """
    Show top trend alerts.
    
    Args:
        analyzer: TrendAnalysis instance
    """
    print("\n" + "="*60)
    print("🚨 TOP TREND ALERTS")
    print("="*60)
    
    # Get critical alerts
    critical_alerts = analyzer.get_top_alerts(alert_type='critical', limit=5)
    if critical_alerts:
        print(f"\n🔴 CRITICAL ALERTS:")
        for i, alert in enumerate(critical_alerts, 1):
            print(f"   {i}. {alert['message']}")
            print(f"      Severity: {alert['severity'].upper()}")
            print(f"      Recommendation: {alert['recommendation']}")
            
            # Show additional details
            if 'percentage_change' in alert:
                print(f"      Change: {alert['percentage_change']:+.1f}%")
            if 'consistency' in alert:
                print(f"      Consistency: {alert['consistency']:.2f}")
            print()
    
    # Get warning alerts
    warning_alerts = analyzer.get_top_alerts(alert_type='warning', limit=5)
    if warning_alerts:
        print(f"🟡 WARNING ALERTS:")
        for i, alert in enumerate(warning_alerts, 1):
            print(f"   {i}. {alert['message']}")
            print(f"      Severity: {alert['severity'].upper()}")
            print(f"      Recommendation: {alert['recommendation']}")
            
            if 'percentage_change' in alert:
                print(f"      Change: {alert['percentage_change']:+.1f}%")
            print()
    
    # Get emerging alerts
    emerging_alerts = analyzer.get_top_alerts(alert_type='emerging', limit=5)
    if emerging_alerts:
        print(f"🟠 EMERGING ALERTS:")
        for i, alert in enumerate(emerging_alerts, 1):
            print(f"   {i}. {alert['message']}")
            print(f"      Severity: {alert['severity'].upper()}")
            print(f"      Recommendation: {alert['recommendation']}")
            
            if 'growth_rate' in alert:
                print(f"      Growth rate: {alert['growth_rate']:+.1f}%")
            print()
    
    # Get positive trends
    positive_alerts = analyzer.get_top_alerts(alert_type='positive', limit=3)
    if positive_alerts:
        print(f"🟢 POSITIVE TRENDS:")
        for i, alert in enumerate(positive_alerts, 1):
            print(f"   {i}. {alert['message']}")
            print(f"      Recommendation: {alert['recommendation']}")
            
            if 'percentage_change' in alert:
                print(f"      Improvement: {alert['percentage_change']:+.1f}%")
            print()
    
    print("="*60)

def analyze_component_trends(analyzer):
    """
    Analyze trends for specific components.
    
    Args:
        analyzer: TrendAnalysis instance
    """
    print("\n" + "="*60)
    print("🔧 COMPONENT-SPECIFIC TREND ANALYSIS")
    print("="*60)
    
    # Get components with trend data
    trend_metrics = analyzer.trend_metrics
    component_trends = trend_metrics.get('component_trends', {})
    
    # Select top components for detailed analysis
    components_to_analyze = ['battery', 'sound', 'camera', 'display', 'performance']
    
    for component in components_to_analyze:
        if component in component_trends:
            print(f"\n📱 {component.title()} Trend Analysis:")
            
            # Get component trend summary
            summary = analyzer.get_component_trend_summary(component)
            if summary:
                mention_trend = summary.get('mention_trend', {})
                sentiment_trend = summary.get('sentiment_trend', {})
                
                # Display mention trend
                if mention_trend:
                    print(f"   📊 Mention Trend:")
                    print(f"      Direction: {mention_trend.get('trend_direction', 'unknown')}")
                    print(f"      Change: {mention_trend.get('percentage_change', 0):+.1f}%")
                    print(f"      Recent avg: {mention_trend.get('recent_average', 0):.1f}")
                    print(f"      Total mentions: {mention_trend.get('total_mentions', 0)}")
                    
                    if mention_trend.get('percentage_change', 0) > 20:
                        print(f"      ⚠️  Significant increase detected!")
                
                # Display sentiment trend
                if sentiment_trend:
                    print(f"   💭 Sentiment Trend:")
                    print(f"      Direction: {sentiment_trend.get('trend_direction', 'unknown')}")
                    print(f"      Change: {sentiment_trend.get('percentage_change', 0):+.1f}%")
                    print(f"      Current sentiment: {sentiment_trend.get('current_sentiment', 0):.3f}")
                    
                    if sentiment_trend.get('percentage_change', 0) < -20:
                        print(f"      ⚠️  Significant sentiment decline!")
                
                # Display related alerts
                related_alerts = summary.get('related_alerts', [])
                if related_alerts:
                    print(f"   🚨 Related Alerts:")
                    for alert in related_alerts[:2]:
                        print(f"      • {alert['message']}")
    
    print("="*60)

def generate_trend_summary(analyzer):
    """
    Generate comprehensive trend summary.
    
    Args:
        analyzer: TrendAnalysis instance
    """
    print("\n" + "="*60)
    print("📋 COMPREHENSIVE TREND SUMMARY")
    print("="*60)
    
    trend_metrics = analyzer.trend_metrics
    trend_alerts = analyzer.trend_alerts
    
    print(f"\n🎯 KEY FINDINGS:")
    
    # Most critical issues
    critical_alerts = analyzer.get_top_alerts(alert_type='critical', limit=3)
    if critical_alerts:
        print(f"\n🔴 Most Critical Issues:")
        for i, alert in enumerate(critical_alerts, 1):
            print(f"   {i}. {alert['message']}")
            print(f"      Impact: {alert.get('percentage_change', 0):+.1f}% change")
    
    # Fastest growing issues
    component_trends = trend_metrics.get('component_trends', {})
    growing_issues = []
    
    for comp, trend in component_trends.items():
        if trend and trend.get('percentage_change', 0) > 0:
            growing_issues.append((comp, trend.get('percentage_change', 0), trend.get('total_mentions', 0)))
    
    growing_issues.sort(key=lambda x: x[1], reverse=True)
    
    if growing_issues:
        print(f"\n📈 Fastest Growing Issues:")
        for i, (comp, change, mentions) in enumerate(growing_issues[:3], 1):
            print(f"   {i}. {comp.title()}: +{change:.1f}% ({mentions} mentions)")
    
    # Biggest sentiment improvements
    sentiment_trends = trend_metrics.get('sentiment_trends', {})
    improving_sentiments = []
    
    for comp, trend in sentiment_trends.items():
        if trend and trend.get('percentage_change', 0) > 0:
            improving_sentiments.append((comp, trend.get('percentage_change', 0), trend.get('current_sentiment', 0)))
    
    improving_sentiments.sort(key=lambda x: x[1], reverse=True)
    
    if improving_sentiments:
        print(f"\n🟢 Biggest Sentiment Improvements:")
        for i, (comp, change, current) in enumerate(improving_sentiments[:3], 1):
            print(f"   {i}. {comp.title()}: +{change:.1f}% (current: {current:.3f})")
    
    # Emerging concerns
    emerging_issues = trend_metrics.get('emerging_issues', [])
    if emerging_issues:
        print(f"\n🟠 Emerging Concerns:")
        for i, issue in enumerate(emerging_issues[:3], 1):
            if issue.get('type') == 'emerging_complaint':
                print(f"   {i}. {issue['issue'].title()}: {issue.get('growth_rate', 0):+.1f}% growth")
            elif issue.get('type') == 'sentiment_decline':
                print(f"   {i}. {issue['issue'].title()}: {abs(issue.get('sentiment_change', 0)):.1f}% decline")
    
    # Recommendations
    print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
    
    # Based on critical alerts
    if critical_alerts:
        print(f"\n   Immediate Actions Required:")
        for alert in critical_alerts[:2]:
            print(f"   • {alert['recommendation']}")
    
    # Based on emerging issues
    if emerging_issues:
        print(f"\n   Monitor These Emerging Issues:")
        for issue in emerging_issues[:2]:
            if issue.get('type') == 'emerging_complaint':
                print(f"   • Track {issue['issue']} trend (growing {issue.get('growth_rate', 0):.1f}%)")
            elif issue.get('type') == 'sentiment_decline':
                print(f"   • Monitor {issue['issue']} satisfaction (declining {abs(issue.get('sentiment_change', 0)):.1f}%)")
    
    # Based on positive trends
    positive_alerts = analyzer.get_top_alerts(alert_type='positive', limit=2)
    if positive_alerts:
        print(f"\n   Continue Successful Initiatives:")
        for alert in positive_alerts:
            print(f"   • {alert['recommendation']}")
    
    print("="*60)

def validate_trend_analysis():
    """
    Validate trend analysis results.
    """
    print("\n" + "="*60)
    print("✅ TREND ANALYSIS VALIDATION")
    print("="*60)
    
    try:
        with open('trend_alerts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📋 VALIDATION RESULTS:")
        
        # Check required sections
        required_sections = ['generated_at', 'analysis_period', 'thresholds_used', 'alerts']
        missing_sections = [section for section in required_sections if section not in data]
        
        if not missing_sections:
            print(f"   ✅ All required sections present")
        else:
            print(f"   ❌ Missing sections: {missing_sections}")
        
        # Validate alerts structure
        alerts = data.get('alerts', {})
        alert_types = ['critical_alerts', 'warning_alerts', 'emerging_alerts', 'positive_trends', 'summary']
        
        valid_alerts = 0
        for alert_type in alert_types:
            if alert_type in alerts:
                valid_alerts += 1
        
        print(f"   ✅ Valid alert sections: {valid_alerts}/{len(alert_types)}")
        
        # Check for proper alert structure
        all_alerts = []
        for alert_type in ['critical_alerts', 'warning_alerts', 'emerging_alerts', 'positive_trends']:
            all_alerts.extend(alerts.get(alert_type, []))
        
        properly_structured = 0
        for alert in all_alerts:
            required_fields = ['type', 'severity', 'message', 'recommendation']
            if all(field in alert for field in required_fields):
                properly_structured += 1
        
        if all_alerts:
            print(f"   ✅ Properly structured alerts: {properly_structured}/{len(all_alerts)}")
        
        # Check for trend metrics
        if 'trend_metrics' in locals() and trend_metrics:
            metrics_count = len(trend_metrics)
            print(f"   ✅ Trend metrics calculated: {metrics_count} categories")
        
        # Validate thresholds
        thresholds = data.get('thresholds_used', {})
        expected_thresholds = ['significant_increase', 'critical_increase', 'emerging_threshold', 'trend_consistency']
        
        threshold_valid = sum(1 for t in expected_thresholds if t in thresholds)
        print(f"   ✅ Valid thresholds: {threshold_valid}/{len(expected_thresholds)}")
        
        # Check for actionable insights
        actionable_alerts = 0
        for alert in all_alerts:
            if 'recommendation' in alert and len(alert['recommendation']) > 10:
                actionable_alerts += 1
        
        if all_alerts:
            actionable_rate = (actionable_alerts / len(all_alerts)) * 100
            print(f"   📊 Actionable alerts: {actionable_rate:.1f}%")
        
        print("="*60)
        
    except FileNotFoundError:
        print("❌ trend_alerts.json not found for validation")
    except Exception as e:
        print(f"❌ Error during validation: {e}")

def export_trend_report():
    """
    Export trend analysis report.
    """
    print("\n" + "="*60)
    print("📤 EXPORTING TREND ANALYSIS REPORT")
    print("="*60)
    
    try:
        with open('trend_alerts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Export to text report
        with open('trend_report.txt', 'w', encoding='utf-8') as f:
            f.write("TREND ANALYSIS REPORT\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Generated: {data.get('generated_at', 'Unknown')}\n")
            f.write(f"Analysis Period: {data.get('analysis_period', 'Unknown')}\n\n")
            
            alerts = data.get('alerts', {})
            
            # Critical alerts
            critical_alerts = alerts.get('critical_alerts', [])
            if critical_alerts:
                f.write("CRITICAL ALERTS\n")
                f.write("-" * 20 + "\n")
                for i, alert in enumerate(critical_alerts, 1):
                    f.write(f"{i}. {alert['message']}\n")
                    f.write(f"   Recommendation: {alert['recommendation']}\n")
                    f.write(f"   Change: {alert.get('percentage_change', 0):+.1f}%\n\n")
            
            # Warning alerts
            warning_alerts = alerts.get('warning_alerts', [])
            if warning_alerts:
                f.write("WARNING ALERTS\n")
                f.write("-" * 20 + "\n")
                for i, alert in enumerate(warning_alerts, 1):
                    f.write(f"{i}. {alert['message']}\n")
                    f.write(f"   Recommendation: {alert['recommendation']}\n")
                    f.write(f"   Change: {alert.get('percentage_change', 0):+.1f}%\n\n")
            
            # Emerging alerts
            emerging_alerts = alerts.get('emerging_alerts', [])
            if emerging_alerts:
                f.write("EMERGING ALERTS\n")
                f.write("-" * 20 + "\n")
                for i, alert in enumerate(emerging_alerts, 1):
                    f.write(f"{i}. {alert['message']}\n")
                    f.write(f"   Recommendation: {alert['recommendation']}\n\n")
            
            # Summary
            summary = alerts.get('summary', {})
            f.write("SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total alerts: {summary.get('total_alerts', 0)}\n")
            f.write(f"Critical: {summary.get('critical_count', 0)}\n")
            f.write(f"Warning: {summary.get('warning_count', 0)}\n")
            f.write(f"Emerging: {summary.get('emerging_count', 0)}\n")
        
        print("✅ Trend report exported to trend_report.txt")
        
        # Export to CSV for tracking
        with open('trend_alerts.csv', 'w', encoding='utf-8') as f:
            import csv
            
            fieldnames = ['type', 'severity', 'message', 'percentage_change', 'recommendation', 'component', 'complaint']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            
            for alert_type in ['critical_alerts', 'warning_alerts', 'emerging_alerts', 'positive_trends']:
                for alert in alerts.get(alert_type, []):
                    writer.writerow({
                        'type': alert.get('type', ''),
                        'severity': alert.get('severity', ''),
                        'message': alert.get('message', ''),
                        'percentage_change': alert.get('percentage_change', ''),
                        'recommendation': alert.get('recommendation', ''),
                        'component': alert.get('component', ''),
                        'complaint': alert.get('complaint', '')
                    })
        
        print("✅ Trend alerts exported to trend_alerts.csv")
        
    except FileNotFoundError:
        print("❌ trend_alerts.json not found for export")
    except Exception as e:
        print(f"❌ Error during export: {e}")

if __name__ == "__main__":
    # Run main trend analysis
    main()
    
    # Export trend report
    export_trend_report()
