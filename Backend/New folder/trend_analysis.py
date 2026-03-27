import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendAnalysis:
    """
    Detect emerging product issues and trends over time.
    Analyzes temporal patterns in customer complaints and sentiment data.
    """
    
    def __init__(self):
        """Initialize the trend analysis engine."""
        self.trend_data = {}
        self.trend_alerts = {}
        self.time_windows = {
            '1_month': 30,
            '3_months': 90,
            '6_months': 180,
            '1_year': 365
        }
        
        # Trend detection thresholds
        self.thresholds = {
            'significant_increase': 20.0,  # 20% increase
            'critical_increase': 50.0,     # 50% increase
            'emerging_threshold': 10,       # Minimum mentions for emerging issues
            'trend_consistency': 0.7        # Minimum consistency score
        }
        
        logger.info("Trend analysis engine initialized")
    
    def load_component_reviews(self, component_file: str = 'component_reviews.json') -> None:
        """
        Load component reviews data for trend analysis.
        
        Args:
            component_file: Path to component reviews JSON file
        """
        try:
            with open(component_file, 'r', encoding='utf-8') as f:
                self.component_reviews = json.load(f)
            logger.info(f"Successfully loaded component reviews from {component_file}")
        except Exception as e:
            logger.error(f"Error loading component reviews: {e}")
            raise
    
    def load_sentiment_scores(self, sentiment_file: str = 'component_sentiment_scores.json') -> None:
        """
        Load sentiment scores data for trend analysis.
        
        Args:
            sentiment_file: Path to sentiment scores JSON file
        """
        try:
            with open(sentiment_file, 'r', encoding='utf-8') as f:
                self.sentiment_scores = json.load(f)
            logger.info(f"Successfully loaded sentiment scores from {sentiment_file}")
        except Exception as e:
            logger.error(f"Error loading sentiment scores: {e}")
            raise
    
    def load_review_intelligence(self, review_file: str = 'review_intelligence.json') -> None:
        """
        Load review intelligence data for trend analysis.
        
        Args:
            review_file: Path to review intelligence JSON file
        """
        try:
            with open(review_file, 'r', encoding='utf-8') as f:
                self.review_intelligence = json.load(f)
            logger.info(f"Successfully loaded review intelligence from {review_file}")
        except Exception as e:
            logger.error(f"Error loading review intelligence: {e}")
            raise
    
    def extract_temporal_data(self) -> Dict[str, Any]:
        """
        Extract temporal data from reviews for trend analysis.
        
        Returns:
            Dictionary containing temporal data organized by time periods
        """
        temporal_data = {
            'monthly_data': defaultdict(lambda: defaultdict(list)),
            'component_mentions': defaultdict(lambda: defaultdict(int)),
            'sentiment_trends': defaultdict(lambda: defaultdict(list)),
            'complaint_patterns': defaultdict(lambda: defaultdict(list))
        }
        
        try:
            # Process component reviews
            for category, products in self.component_reviews.items():
                for product, components in products.items():
                    for component, reviews in components.items():
                        for review in reviews:
                            # Extract date information
                            review_date = self._extract_review_date(review)
                            if review_date:
                                month_key = review_date.strftime('%Y-%m')
                                
                                # Store component mentions over time
                                temporal_data['component_mentions'][component][month_key] += 1
                                
                                # Store sentiment data
                                sentiment = self._extract_sentiment(review)
                                if sentiment is not None:
                                    temporal_data['sentiment_trends'][component][month_key].append(sentiment)
                                
                                # Store complaint patterns
                                complaint_keywords = self._extract_complaint_keywords(review)
                                for keyword in complaint_keywords:
                                    temporal_data['complaint_patterns'][keyword][month_key].append(review_date.isoformat())
            
            # Process review intelligence for additional patterns
            component_breakdown = self.review_intelligence.get('component_breakdown', {})
            for component, data in component_breakdown.items():
                top_phrases = data.get('top_phrases', [])
                for phrase, count in top_phrases:
                    # Extract keywords from phrases
                    keywords = self._extract_keywords_from_phrase(phrase[0])
                    for keyword in keywords:
                        # Distribute phrase counts across recent months (simplified)
                        current_month = datetime.now().strftime('%Y-%m')
                        for i in range(3):  # Distribute across last 3 months
                            month_key = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m')
                            temporal_data['complaint_patterns'][keyword][month_key].extend([None] * (phrase[1] // 3))
            
            logger.info("Temporal data extraction completed")
            return temporal_data
            
        except Exception as e:
            logger.error(f"Error extracting temporal data: {e}")
            raise
    
    def _extract_review_date(self, review: Dict[str, Any]) -> Optional[datetime]:
        """Extract date from review data."""
        try:
            # Try different date fields
            date_fields = ['date', 'review_date', 'timestamp', 'created_at']
            
            for field in date_fields:
                if field in review:
                    date_str = review[field]
                    if isinstance(date_str, str):
                        # Parse various date formats
                        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                            try:
                                return datetime.strptime(date_str, fmt)
                            except ValueError:
                                continue
            
            # If no explicit date, use current time (placeholder)
            return datetime.now()
            
        except Exception:
            return None
    
    def _extract_sentiment(self, review: Dict[str, Any]) -> Optional[float]:
        """Extract sentiment from review data."""
        try:
            # Try different sentiment fields
            sentiment_fields = ['sentiment', 'rating', 'score', 'polarity']
            
            for field in sentiment_fields:
                if field in review:
                    sentiment = review[field]
                    if isinstance(sentiment, (int, float)):
                        return float(sentiment)
            
            return None
            
        except Exception:
            return None
    
    def _extract_complaint_keywords(self, review: Dict[str, Any]) -> List[str]:
        """Extract complaint keywords from review text."""
        keywords = []
        
        try:
            # Get review text
            text_fields = ['review_text', 'text', 'content', 'body']
            review_text = ""
            
            for field in text_fields:
                if field in review:
                    review_text = str(review[field])
                    break
            
            # Define complaint patterns
            complaint_patterns = {
                'battery': ['battery', 'charge', 'power', 'drain', 'battery life', 'charging'],
                'sound': ['sound', 'audio', 'speaker', 'volume', 'noise', 'quality'],
                'camera': ['camera', 'picture', 'photo', 'video', 'focus', 'lens'],
                'display': ['screen', 'display', 'resolution', 'brightness', 'pixel'],
                'performance': ['slow', 'lag', 'performance', 'speed', 'freeze', 'crash'],
                'build': ['build', 'quality', 'material', 'durability', 'sturdy'],
                'comfort': ['comfortable', 'fit', 'wear', 'uncomfortable', 'tight'],
                'connectivity': ['bluetooth', 'wifi', 'connection', 'pairing', 'network'],
                'software': ['software', 'app', 'update', 'bug', 'interface', 'os'],
                'price': ['price', 'cost', 'expensive', 'cheap', 'value', 'money']
            }
            
            # Extract keywords from text
            review_text_lower = review_text.lower()
            
            for category, patterns in complaint_patterns.items():
                for pattern in patterns:
                    if pattern in review_text_lower:
                        keywords.append(category)
                        break
            
            return list(set(keywords))  # Remove duplicates
            
        except Exception:
            return []
    
    def _extract_keywords_from_phrase(self, phrase: str) -> List[str]:
        """Extract keywords from complaint phrase."""
        keywords = []
        
        try:
            # Simple keyword extraction
            words = re.findall(r'\b\w+\b', phrase.lower())
            
            # Filter out common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
            
            keywords = [word for word in words if word not in stop_words and len(word) > 2]
            
            return keywords[:5]  # Limit to top 5 keywords
            
        except Exception:
            return []
    
    def calculate_trend_metrics(self, temporal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate trend metrics for components and issues.
        
        Args:
            temporal_data: Temporal data extracted from reviews
            
        Returns:
            Dictionary containing trend metrics
        """
        trend_metrics = {
            'component_trends': {},
            'complaint_trends': {},
            'sentiment_trends': {},
            'emerging_issues': {}
        }
        
        try:
            # Calculate component mention trends
            for component, monthly_data in temporal_data['component_mentions'].items():
                trend_metrics['component_trends'][component] = self._calculate_component_trend(monthly_data)
            
            # Calculate complaint trend metrics
            for complaint, monthly_data in temporal_data['complaint_patterns'].items():
                trend_metrics['complaint_trends'][complaint] = self._calculate_complaint_trend(monthly_data)
            
            # Calculate sentiment trends
            for component, monthly_data in temporal_data['sentiment_trends'].items():
                trend_metrics['sentiment_trends'][component] = self._calculate_sentiment_trend(monthly_data)
            
            # Identify emerging issues
            trend_metrics['emerging_issues'] = self._identify_emerging_issues(temporal_data)
            
            logger.info("Trend metrics calculation completed")
            return trend_metrics
            
        except Exception as e:
            logger.error(f"Error calculating trend metrics: {e}")
            raise
    
    def _calculate_component_trend(self, monthly_data: Dict[str, int]) -> Dict[str, Any]:
        """Calculate trend metrics for a specific component."""
        if not monthly_data:
            return {}
        
        # Sort months chronologically
        sorted_months = sorted(monthly_data.keys())
        
        if len(sorted_months) < 2:
            return {}
        
        # Calculate trend metrics
        values = [monthly_data[month] for month in sorted_months]
        
        # Recent vs older comparison
        recent_months = sorted_months[-3:] if len(sorted_months) >= 3 else sorted_months[-1:]
        older_months = sorted_months[:-3] if len(sorted_months) >= 6 else sorted_months[:-1]
        
        recent_avg = statistics.mean([monthly_data[month] for month in recent_months])
        older_avg = statistics.mean([monthly_data[month] for month in older_months]) if older_months else recent_avg
        
        # Calculate percentage change
        if older_avg > 0:
            percentage_change = ((recent_avg - older_avg) / older_avg) * 100
        else:
            percentage_change = 0 if recent_avg == 0 else 100
        
        # Calculate trend direction and consistency
        trend_direction = 'increasing' if percentage_change > 5 else 'decreasing' if percentage_change < -5 else 'stable'
        
        # Calculate trend consistency (how consistent is the trend)
        if len(values) >= 3:
            consistency = self._calculate_trend_consistency(values)
        else:
            consistency = 0.5
        
        return {
            'monthly_data': monthly_data,
            'recent_average': recent_avg,
            'older_average': older_avg,
            'percentage_change': percentage_change,
            'trend_direction': trend_direction,
            'consistency_score': consistency,
            'total_mentions': sum(values),
            'peak_month': sorted_months[-1] if values[-1] == max(values) else sorted_months[values.index(max(values))]
        }
    
    def _calculate_complaint_trend(self, monthly_data: Dict[str, List]) -> Dict[str, Any]:
        """Calculate trend metrics for a specific complaint."""
        if not monthly_data:
            return {}
        
        # Sort months chronologically
        sorted_months = sorted(monthly_data.keys())
        
        if len(sorted_months) < 2:
            return {}
        
        # Calculate monthly counts
        monthly_counts = {}
        for month in sorted_months:
            monthly_counts[month] = len([x for x in monthly_data[month] if x is not None])
        
        # Calculate trend metrics
        values = list(monthly_counts.values())
        
        # Recent vs older comparison
        recent_months = sorted_months[-3:] if len(sorted_months) >= 3 else sorted_months[-1:]
        older_months = sorted_months[:-3] if len(sorted_months) >= 6 else sorted_months[:-1]
        
        recent_avg = statistics.mean([monthly_counts[month] for month in recent_months])
        older_avg = statistics.mean([monthly_counts[month] for month in older_months]) if older_months else recent_avg
        
        # Calculate percentage change
        if older_avg > 0:
            percentage_change = ((recent_avg - older_avg) / older_avg) * 100
        else:
            percentage_change = 0 if recent_avg == 0 else 100
        
        # Calculate trend direction
        trend_direction = 'increasing' if percentage_change > 5 else 'decreasing' if percentage_change < -5 else 'stable'
        
        # Calculate trend consistency
        if len(values) >= 3:
            consistency = self._calculate_trend_consistency(values)
        else:
            consistency = 0.5
        
        return {
            'monthly_counts': monthly_counts,
            'recent_average': recent_avg,
            'older_average': older_avg,
            'percentage_change': percentage_change,
            'trend_direction': trend_direction,
            'consistency_score': consistency,
            'total_complaints': sum(values),
            'peak_month': sorted_months[-1] if values[-1] == max(values) else sorted_months[values.index(max(values))]
        }
    
    def _calculate_sentiment_trend(self, monthly_data: Dict[str, List]) -> Dict[str, Any]:
        """Calculate sentiment trend for a specific component."""
        if not monthly_data:
            return {}
        
        # Sort months chronologically
        sorted_months = sorted(monthly_data.keys())
        
        if len(sorted_months) < 2:
            return {}
        
        # Calculate monthly sentiment averages
        monthly_averages = {}
        for month in sorted_months:
            sentiments = monthly_data[month]
            if sentiments:
                monthly_averages[month] = statistics.mean(sentiments)
            else:
                monthly_averages[month] = 0.0
        
        # Calculate trend metrics
        values = list(monthly_averages.values())
        
        # Recent vs older comparison
        recent_months = sorted_months[-3:] if len(sorted_months) >= 3 else sorted_months[-1:]
        older_months = sorted_months[:-3] if len(sorted_months) >= 6 else sorted_months[:-1]
        
        recent_avg = statistics.mean([monthly_averages[month] for month in recent_months])
        older_avg = statistics.mean([monthly_averages[month] for month in older_months]) if older_months else recent_avg
        
        # Calculate percentage change
        if older_avg != 0:
            percentage_change = ((recent_avg - older_avg) / abs(older_avg)) * 100
        else:
            percentage_change = 0 if recent_avg == 0 else 100
        
        # Calculate trend direction
        trend_direction = 'improving' if percentage_change > 5 else 'declining' if percentage_change < -5 else 'stable'
        
        # Calculate trend consistency
        if len(values) >= 3:
            consistency = self._calculate_trend_consistency(values)
        else:
            consistency = 0.5
        
        return {
            'monthly_averages': monthly_averages,
            'recent_average': recent_avg,
            'older_average': older_avg,
            'percentage_change': percentage_change,
            'trend_direction': trend_direction,
            'consistency_score': consistency,
            'current_sentiment': recent_avg,
            'peak_month': sorted_months[-1] if values[-1] == max(values) else sorted_months[values.index(max(values))]
        }
    
    def _calculate_trend_consistency(self, values: List[float]) -> float:
        """Calculate how consistent a trend is (0-1 scale)."""
        if len(values) < 3:
            return 0.5
        
        try:
            # Calculate correlation with expected trend direction
            expected_direction = 1 if values[-1] > values[0] else -1
            
            # Calculate trend line
            x_values = list(range(len(values)))
            correlation = self._calculate_correlation(x_values, values)
            
            # Convert to consistency score
            consistency = abs(correlation) if correlation * expected_direction > 0 else abs(correlation) * 0.5
            
            return max(0, min(1, consistency))
            
        except Exception:
            return 0.5
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient between two lists."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        try:
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi * xi for xi in x)
            sum_y2 = sum(yi * yi for yi in y)
            
            denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            correlation = (n * sum_xy - sum_x * sum_y) / denominator
            return correlation
            
        except Exception:
            return 0.0
    
    def _identify_emerging_issues(self, temporal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify emerging issues from temporal data."""
        emerging_issues = []
        
        try:
            # Look for new complaint patterns
            for complaint, monthly_data in temporal_data['complaint_patterns'].items():
                if len(monthly_data) < 2:
                    continue
                
                sorted_months = sorted(monthly_data.keys())
                recent_counts = [len([x for x in monthly_data[month] if x is not None]) for month in sorted_months[-3:]]
                
                # Check if issue is emerging (recent activity with low historical baseline)
                if sum(recent_counts) >= self.thresholds['emerging_threshold']:
                    # Calculate growth rate
                    if len(recent_counts) >= 2:
                        growth_rate = ((recent_counts[-1] - recent_counts[0]) / max(recent_counts[0], 1)) * 100
                        
                        if growth_rate > self.thresholds['significant_increase']:
                            emerging_issues.append({
                                'issue': complaint,
                                'type': 'emerging_complaint',
                                'recent_mentions': sum(recent_counts),
                                'growth_rate': growth_rate,
                                'trend_direction': 'increasing' if growth_rate > 0 else 'decreasing',
                                'months_active': len(sorted_months),
                                'peak_month': sorted_months[-1]
                            })
            
            # Look for declining sentiment in components
            for component, monthly_data in temporal_data['sentiment_trends'].items():
                if len(monthly_data) < 2:
                    continue
                
                sorted_months = sorted(monthly_data.keys())
                recent_sentiments = [statistics.mean(monthly_data[month]) if monthly_data[month] else 0 for month in sorted_months[-3:]]
                
                # Check for significant sentiment decline
                if len(recent_sentiments) >= 2:
                    sentiment_change = ((recent_sentiments[-1] - recent_sentiments[0]) / max(abs(recent_sentiments[0]), 0.1)) * 100
                    
                    if sentiment_change < -self.thresholds['significant_increase']:
                        emerging_issues.append({
                            'issue': component,
                            'type': 'sentiment_decline',
                            'sentiment_change': sentiment_change,
                            'current_sentiment': recent_sentiments[-1],
                            'trend_direction': 'declining',
                            'months_analyzed': len(sorted_months),
                            'concern_level': 'high' if sentiment_change < -self.thresholds['critical_increase'] else 'medium'
                        })
            
            # Sort by severity
            emerging_issues.sort(key=lambda x: (
                x.get('growth_rate', 0) if x.get('growth_rate', 0) > 0 else abs(x.get('sentiment_change', 0)),
                x.get('recent_mentions', 0)
            ), reverse=True)
            
            return emerging_issues[:10]  # Return top 10 emerging issues
            
        except Exception as e:
            logger.error(f"Error identifying emerging issues: {e}")
            return []
    
    def generate_trend_alerts(self, trend_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trend alerts based on analysis results.
        
        Args:
            trend_metrics: Calculated trend metrics
            
        Returns:
            Dictionary containing trend alerts
        """
        alerts = {
            'critical_alerts': [],
            'warning_alerts': [],
            'emerging_alerts': [],
            'positive_trends': [],
            'summary': {
                'total_alerts': 0,
                'critical_count': 0,
                'warning_count': 0,
                'emerging_count': 0,
                'positive_count': 0
            }
        }
        
        try:
            # Generate alerts for component trends
            for component, trend in trend_metrics.get('component_trends', {}).items():
                if not trend:
                    continue
                
                percentage_change = trend.get('percentage_change', 0)
                consistency = trend.get('consistency_score', 0)
                
                if percentage_change >= self.thresholds['critical_increase'] and consistency >= self.thresholds['trend_consistency']:
                    alerts['critical_alerts'].append({
                        'type': 'component_spike',
                        'component': component,
                        'severity': 'critical',
                        'message': f"{component.title()} complaints increased {percentage_change:.1f}% in recent months",
                        'percentage_change': percentage_change,
                        'consistency': consistency,
                        'total_mentions': trend.get('total_mentions', 0),
                        'recommendation': f"Investigate {component} issues immediately"
                    })
                elif percentage_change >= self.thresholds['significant_increase'] and consistency >= 0.5:
                    alerts['warning_alerts'].append({
                        'type': 'component_increase',
                        'component': component,
                        'severity': 'warning',
                        'message': f"{component.title()} complaints increased {percentage_change:.1f}% in recent months",
                        'percentage_change': percentage_change,
                        'consistency': consistency,
                        'total_mentions': trend.get('total_mentions', 0),
                        'recommendation': f"Monitor {component} trends closely"
                    })
            
            # Generate alerts for complaint trends
            for complaint, trend in trend_metrics.get('complaint_trends', {}).items():
                if not trend:
                    continue
                
                percentage_change = trend.get('percentage_change', 0)
                consistency = trend.get('consistency_score', 0)
                
                if percentage_change >= self.thresholds['critical_increase'] and consistency >= self.thresholds['trend_consistency']:
                    alerts['critical_alerts'].append({
                        'type': 'complaint_spike',
                        'complaint': complaint,
                        'severity': 'critical',
                        'message': f"{complaint.title()} issues increased {percentage_change:.1f}% in recent months",
                        'percentage_change': percentage_change,
                        'consistency': consistency,
                        'total_complaints': trend.get('total_complaints', 0),
                        'recommendation': f"Urgent: Address {complaint} issues"
                    })
                elif percentage_change >= self.thresholds['significant_increase'] and consistency >= 0.5:
                    alerts['warning_alerts'].append({
                        'type': 'complaint_increase',
                        'complaint': complaint,
                        'severity': 'warning',
                        'message': f"{complaint.title()} issues increased {percentage_change:.1f}% in recent months",
                        'percentage_change': percentage_change,
                        'consistency': consistency,
                        'total_complaints': trend.get('total_complaints', 0),
                        'recommendation': f"Monitor {complaint} trends"
                    })
            
            # Generate alerts for sentiment trends
            for component, trend in trend_metrics.get('sentiment_trends', {}).items():
                if not trend:
                    continue
                
                percentage_change = trend.get('percentage_change', 0)
                consistency = trend.get('consistency_score', 0)
                
                if percentage_change <= -self.thresholds['critical_increase'] and consistency >= self.thresholds['trend_consistency']:
                    alerts['critical_alerts'].append({
                        'type': 'sentiment_decline',
                        'component': component,
                        'severity': 'critical',
                        'message': f"{component.title()} sentiment declined {abs(percentage_change):.1f}% in recent months",
                        'percentage_change': percentage_change,
                        'consistency': consistency,
                        'current_sentiment': trend.get('current_sentiment', 0),
                        'recommendation': f"Critical: Improve {component} customer satisfaction"
                    })
                elif percentage_change <= -self.thresholds['significant_increase'] and consistency >= 0.5:
                    alerts['warning_alerts'].append({
                        'type': 'sentiment_warning',
                        'component': component,
                        'severity': 'warning',
                        'message': f"{component.title()} sentiment declined {abs(percentage_change):.1f}% in recent months",
                        'percentage_change': percentage_change,
                        'consistency': consistency,
                        'current_sentiment': trend.get('current_sentiment', 0),
                        'recommendation': f"Address {component} satisfaction issues"
                    })
                elif percentage_change >= self.thresholds['significant_increase'] and consistency >= 0.5:
                    alerts['positive_trends'].append({
                        'type': 'sentiment_improvement',
                        'component': component,
                        'severity': 'positive',
                        'message': f"{component.title()} sentiment improved {percentage_change:.1f}% in recent months",
                        'percentage_change': percentage_change,
                        'consistency': consistency,
                        'current_sentiment': trend.get('current_sentiment', 0),
                        'recommendation': f"Continue {component} improvement efforts"
                    })
            
            # Add emerging issues alerts
            for issue in trend_metrics.get('emerging_issues', []):
                if issue.get('type') == 'emerging_complaint':
                    alerts['emerging_alerts'].append({
                        'type': 'emerging_issue',
                        'issue': issue['issue'],
                        'severity': 'emerging',
                        'message': f"Emerging issue: {issue['issue'].title()} ({issue['growth_rate']:.1f}% growth)",
                        'growth_rate': issue.get('growth_rate', 0),
                        'recent_mentions': issue.get('recent_mentions', 0),
                        'recommendation': f"Monitor {issue['issue']} trend for escalation"
                    })
                elif issue.get('type') == 'sentiment_decline':
                    alerts['emerging_alerts'].append({
                        'type': 'emerging_sentiment',
                        'issue': issue['issue'],
                        'severity': 'emerging',
                        'message': f"Emerging sentiment decline: {issue['issue'].title()} ({abs(issue['sentiment_change']):.1f}% decline)",
                        'sentiment_change': issue.get('sentiment_change', 0),
                        'current_sentiment': issue.get('current_sentiment', 0),
                        'concern_level': issue.get('concern_level', 'medium'),
                        'recommendation': f"Monitor {issue['issue']} satisfaction closely"
                    })
            
            # Update summary
            alerts['summary']['total_alerts'] = len(alerts['critical_alerts']) + len(alerts['warning_alerts']) + len(alerts['emerging_alerts'])
            alerts['summary']['critical_count'] = len(alerts['critical_alerts'])
            alerts['summary']['warning_count'] = len(alerts['warning_alerts'])
            alerts['summary']['emerging_count'] = len(alerts['emerging_alerts'])
            alerts['summary']['positive_count'] = len(alerts['positive_trends'])
            
            logger.info(f"Generated {alerts['summary']['total_alerts']} trend alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating trend alerts: {e}")
            raise
    
    def save_trend_alerts(self, alerts: Dict[str, Any], output_file: str = 'trend_alerts.json') -> None:
        """
        Save trend alerts to JSON file.
        
        Args:
            alerts: Trend alerts dictionary
            output_file: Output filename
        """
        try:
            # Add metadata
            output_data = {
                'generated_at': datetime.now().isoformat(),
                'analysis_period': 'Last 6 months',
                'thresholds_used': self.thresholds,
                'alerts': alerts
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Trend alerts saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving trend alerts: {e}")
            raise
    
    def process_trend_analysis(self, component_file: str = 'component_reviews.json',
                            sentiment_file: str = 'component_sentiment_scores.json',
                            review_file: str = 'review_intelligence.json',
                            output_file: str = 'trend_alerts.json') -> Dict[str, Any]:
        """
        Complete trend analysis pipeline.
        
        Args:
            component_file: Component reviews JSON file
            sentiment_file: Sentiment scores JSON file
            review_file: Review intelligence JSON file
            output_file: Output trend alerts JSON file
            
        Returns:
            Complete trend analysis results
        """
        try:
            # Load input data
            self.load_component_reviews(component_file)
            self.load_sentiment_scores(sentiment_file)
            self.load_review_intelligence(review_file)
            
            # Extract temporal data
            temporal_data = self.extract_temporal_data()
            
            # Calculate trend metrics
            trend_metrics = self.calculate_trend_metrics(temporal_data)
            
            # Generate trend alerts
            alerts = self.generate_trend_alerts(trend_metrics)
            
            # Save alerts
            self.save_trend_alerts(alerts, output_file)
            
            # Store results
            self.trend_data = temporal_data
            self.trend_metrics = trend_metrics
            self.trend_alerts = alerts
            
            logger.info("Trend analysis pipeline completed successfully!")
            
            return {
                'temporal_data': temporal_data,
                'trend_metrics': trend_metrics,
                'trend_alerts': alerts
            }
            
        except Exception as e:
            logger.error(f"Error in trend analysis pipeline: {e}")
            raise
    
    def get_top_alerts(self, alert_type: str = 'all', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top alerts by type.
        
        Args:
            alert_type: Type of alerts ('critical', 'warning', 'emerging', 'positive', 'all')
            limit: Maximum number of alerts to return
            
        Returns:
            List of top alerts
        """
        if not self.trend_alerts:
            return []
        
        alerts = []
        
        if alert_type == 'all' or alert_type == 'critical':
            alerts.extend(self.trend_alerts.get('critical_alerts', []))
        if alert_type == 'all' or alert_type == 'warning':
            alerts.extend(self.trend_alerts.get('warning_alerts', []))
        if alert_type == 'all' or alert_type == 'emerging':
            alerts.extend(self.trend_alerts.get('emerging_alerts', []))
        if alert_type == 'all' or alert_type == 'positive':
            alerts.extend(self.trend_alerts.get('positive_trends', []))
        
        # Sort by severity (critical first) then by percentage change
        severity_order = {'critical': 3, 'warning': 2, 'emerging': 1, 'positive': 0}
        
        alerts.sort(key=lambda x: (
            severity_order.get(x.get('severity', 'positive'), 0),
            abs(x.get('percentage_change', 0)) or x.get('growth_rate', 0) or 0
        ), reverse=True)
        
        return alerts[:limit]
    
    def get_component_trend_summary(self, component: str) -> Optional[Dict[str, Any]]:
        """
        Get trend summary for a specific component.
        
        Args:
            component: Component name
            
        Returns:
            Component trend summary
        """
        if not self.trend_metrics:
            return None
        
        component_trends = self.trend_metrics.get('component_trends', {}).get(component, {})
        sentiment_trends = self.trend_metrics.get('sentiment_trends', {}).get(component, {})
        
        if not component_trends and not sentiment_trends:
            return None
        
        return {
            'component': component,
            'mention_trend': component_trends,
            'sentiment_trend': sentiment_trends,
            'related_alerts': [alert for alert in self.get_top_alerts() if alert.get('component') == component]
        }

# Example usage
if __name__ == "__main__":
    # Initialize trend analysis
    analyzer = TrendAnalysis()
    
    # Process trend analysis
    results = analyzer.process_trend_analysis(
        component_file='component_reviews.json',
        sentiment_file='component_sentiment_scores.json',
        review_file='review_intelligence.json',
        output_file='trend_alerts.json'
    )
    
    print(f"✅ Trend analysis completed!")
    
    # Display top alerts
    top_alerts = analyzer.get_top_alerts(limit=5)
    print(f"\n🚨 TOP TREND ALERTS:")
    for i, alert in enumerate(top_alerts, 1):
        print(f"   {i}. {alert['message']}")
        print(f"      Severity: {alert['severity']}")
        print(f"      Recommendation: {alert['recommendation']}")
