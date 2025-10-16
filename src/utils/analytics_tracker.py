"""
Analytics Tracker

Tracks and analyzes campaign performance:
- Real-time metrics tracking
- Success/failure analysis
- Message type distribution
- Performance trends
- Conversion tracking

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class CampaignMetrics:
    """Metrics for a campaign."""
    
    # Basic counts
    total_businesses: int = 0
    messages_sent: int = 0
    messages_failed: int = 0
    messages_skipped: int = 0
    
    # Message type distribution
    creation_messages: int = 0
    enhancement_messages: int = 0
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    
    # Performance
    average_message_time: float = 0.0
    success_rate: float = 0.0
    
    # Rate limiting
    rate_limit_hits: int = 0
    batch_delays_triggered: int = 0


@dataclass
class BusinessAnalytics:
    """Analytics for individual business."""
    
    business_name: str
    phone: str
    has_website: bool
    message_type: str
    status: str
    timestamp: str
    duration: float = 0.0
    retry_count: int = 0
    error: Optional[str] = None


class AnalyticsTracker:
    """
    Track and analyze campaign performance in real-time.
    
    Features:
    - Real-time metrics tracking
    - Success/failure analysis
    - Message type distribution
    - Hourly/daily statistics
    - Error categorization
    """
    
    def __init__(self, analytics_dir: str = "data/analytics"):
        """
        Initialize analytics tracker.
        
        Args:
            analytics_dir: Directory for analytics data
        """
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        
        # Current campaign metrics
        self.current_campaign = CampaignMetrics()
        
        # Business-level analytics
        self.business_analytics: List[BusinessAnalytics] = []
        
        # Time-based tracking
        self.hourly_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            'sent': 0,
            'failed': 0,
            'skipped': 0,
        })
        
        # Error tracking
        self.error_categories: Dict[str, int] = defaultdict(int)
        
        logger.info(f"Analytics tracker initialized: {self.analytics_dir}")
    
    def start_campaign(self, total_businesses: int):
        """
        Start tracking a new campaign.
        
        Args:
            total_businesses: Total number of businesses in campaign
        """
        self.current_campaign = CampaignMetrics(
            total_businesses=total_businesses,
            start_time=datetime.now()
        )
        
        logger.info(f"Campaign started: {total_businesses} businesses")
    
    def track_message_sent(
        self,
        business_name: str,
        phone: str,
        message_type: str,
        has_website: bool,
        duration: float = 0.0,
        retry_count: int = 0
    ):
        """
        Track a successfully sent message.
        
        Args:
            business_name: Name of business
            phone: Phone number
            message_type: Type of message ('creation' or 'enhancement')
            has_website: Whether business has website
            duration: Time taken to send (seconds)
            retry_count: Number of retries needed
        """
        self.current_campaign.messages_sent += 1
        
        if message_type == 'creation':
            self.current_campaign.creation_messages += 1
        else:
            self.current_campaign.enhancement_messages += 1
        
        # Track hourly
        hour_key = datetime.now().strftime("%Y-%m-%d %H:00")
        self.hourly_stats[hour_key]['sent'] += 1
        
        # Store business analytics
        analytics = BusinessAnalytics(
            business_name=business_name,
            phone=phone,
            has_website=has_website,
            message_type=message_type,
            status='success',
            timestamp=datetime.now().isoformat(),
            duration=duration,
            retry_count=retry_count,
        )
        self.business_analytics.append(analytics)
        
        logger.debug(f"Message tracked: {business_name} ({message_type})")
    
    def track_message_failed(
        self,
        business_name: str,
        phone: str,
        message_type: str,
        has_website: bool,
        error: str,
        duration: float = 0.0,
        retry_count: int = 0
    ):
        """
        Track a failed message.
        
        Args:
            business_name: Name of business
            phone: Phone number
            message_type: Type of message
            has_website: Whether business has website
            error: Error message
            duration: Time taken before failure (seconds)
            retry_count: Number of retries attempted
        """
        self.current_campaign.messages_failed += 1
        
        # Track hourly
        hour_key = datetime.now().strftime("%Y-%m-%d %H:00")
        self.hourly_stats[hour_key]['failed'] += 1
        
        # Categorize error
        self._categorize_error(error)
        
        # Store business analytics
        analytics = BusinessAnalytics(
            business_name=business_name,
            phone=phone,
            has_website=has_website,
            message_type=message_type,
            status='failed',
            timestamp=datetime.now().isoformat(),
            duration=duration,
            retry_count=retry_count,
            error=error,
        )
        self.business_analytics.append(analytics)
        
        logger.debug(f"Failure tracked: {business_name} - {error}")
    
    def track_message_skipped(
        self,
        business_name: str,
        phone: str,
        reason: str
    ):
        """
        Track a skipped message.
        
        Args:
            business_name: Name of business
            phone: Phone number
            reason: Reason for skipping
        """
        self.current_campaign.messages_skipped += 1
        
        # Track hourly
        hour_key = datetime.now().strftime("%Y-%m-%d %H:00")
        self.hourly_stats[hour_key]['skipped'] += 1
        
        # Store business analytics
        analytics = BusinessAnalytics(
            business_name=business_name,
            phone=phone,
            has_website=False,
            message_type='unknown',
            status='skipped',
            timestamp=datetime.now().isoformat(),
            error=reason,
        )
        self.business_analytics.append(analytics)
        
        logger.debug(f"Skip tracked: {business_name} - {reason}")
    
    def track_rate_limit_hit(self):
        """Track rate limit being hit."""
        self.current_campaign.rate_limit_hits += 1
        logger.info("Rate limit hit tracked")
    
    def track_batch_delay(self):
        """Track batch delay being triggered."""
        self.current_campaign.batch_delays_triggered += 1
        logger.info("Batch delay tracked")
    
    def end_campaign(self):
        """End campaign tracking and calculate final metrics."""
        self.current_campaign.end_time = datetime.now()
        
        if self.current_campaign.start_time:
            duration = self.current_campaign.end_time - self.current_campaign.start_time
            self.current_campaign.total_duration = duration.total_seconds()
        
        # Calculate success rate
        total_attempted = self.current_campaign.messages_sent + self.current_campaign.messages_failed
        if total_attempted > 0:
            self.current_campaign.success_rate = (
                self.current_campaign.messages_sent / total_attempted
            ) * 100
        
        # Calculate average message time
        successful_timings = [
            ba.duration for ba in self.business_analytics
            if ba.status == 'success' and ba.duration > 0
        ]
        if successful_timings:
            self.current_campaign.average_message_time = sum(successful_timings) / len(successful_timings)
        
        logger.info("Campaign ended and metrics calculated")
    
    def _categorize_error(self, error: str):
        """Categorize error for tracking."""
        error_lower = error.lower()
        
        if 'network' in error_lower or 'connection' in error_lower:
            self.error_categories['network'] += 1
        elif 'timeout' in error_lower:
            self.error_categories['timeout'] += 1
        elif 'element' in error_lower or 'not found' in error_lower:
            self.error_categories['element_not_found'] += 1
        elif 'rate limit' in error_lower:
            self.error_categories['rate_limit'] += 1
        elif 'phone' in error_lower or 'number' in error_lower:
            self.error_categories['invalid_phone'] += 1
        else:
            self.error_categories['other'] += 1
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get current campaign metrics.
        
        Returns:
            Dict with current metrics
        """
        return {
            'total_businesses': self.current_campaign.total_businesses,
            'messages_sent': self.current_campaign.messages_sent,
            'messages_failed': self.current_campaign.messages_failed,
            'messages_skipped': self.current_campaign.messages_skipped,
            'creation_messages': self.current_campaign.creation_messages,
            'enhancement_messages': self.current_campaign.enhancement_messages,
            'success_rate': f"{self.current_campaign.success_rate:.2f}%",
            'average_message_time': f"{self.current_campaign.average_message_time:.2f}s",
            'rate_limit_hits': self.current_campaign.rate_limit_hits,
            'batch_delays': self.current_campaign.batch_delays_triggered,
        }
    
    def get_hourly_breakdown(self) -> Dict[str, Dict[str, int]]:
        """
        Get hourly statistics breakdown.
        
        Returns:
            Dict mapping hour to statistics
        """
        return dict(self.hourly_stats)
    
    def get_error_breakdown(self) -> Dict[str, int]:
        """
        Get error breakdown by category.
        
        Returns:
            Dict mapping error category to count
        """
        return dict(self.error_categories)
    
    def get_message_type_distribution(self) -> Dict[str, Any]:
        """
        Get distribution of message types.
        
        Returns:
            Dict with message type statistics
        """
        total = self.current_campaign.creation_messages + self.current_campaign.enhancement_messages
        
        if total == 0:
            return {
                'creation': 0,
                'enhancement': 0,
                'creation_percentage': 0.0,
                'enhancement_percentage': 0.0,
            }
        
        return {
            'creation': self.current_campaign.creation_messages,
            'enhancement': self.current_campaign.enhancement_messages,
            'creation_percentage': (self.current_campaign.creation_messages / total) * 100,
            'enhancement_percentage': (self.current_campaign.enhancement_messages / total) * 100,
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive performance summary.
        
        Returns:
            Dict with complete performance data
        """
        return {
            'campaign_metrics': self.get_current_metrics(),
            'message_distribution': self.get_message_type_distribution(),
            'error_breakdown': self.get_error_breakdown(),
            'hourly_stats': self.get_hourly_breakdown(),
            'top_errors': self._get_top_errors(5),
            'timing_analysis': self._get_timing_analysis(),
        }
    
    def _get_top_errors(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top N most common errors."""
        failed_analytics = [
            ba for ba in self.business_analytics
            if ba.status == 'failed' and ba.error
        ]
        
        # Count error occurrences
        error_counts: Dict[str, int] = defaultdict(int)
        for ba in failed_analytics:
            error_counts[ba.error] += 1
        
        # Sort by count
        sorted_errors = sorted(
            error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {'error': error, 'count': count}
            for error, count in sorted_errors
        ]
    
    def _get_timing_analysis(self) -> Dict[str, Any]:
        """Analyze timing statistics."""
        successful_analytics = [
            ba for ba in self.business_analytics
            if ba.status == 'success' and ba.duration > 0
        ]
        
        if not successful_analytics:
            return {
                'min_time': 0.0,
                'max_time': 0.0,
                'avg_time': 0.0,
                'total_time': 0.0,
            }
        
        durations = [ba.duration for ba in successful_analytics]
        
        return {
            'min_time': min(durations),
            'max_time': max(durations),
            'avg_time': sum(durations) / len(durations),
            'total_time': sum(durations),
            'sample_size': len(durations),
        }
    
    def print_summary(self):
        """Print analytics summary to console."""
        print("\n" + "=" * 60)
        print("📊 CAMPAIGN ANALYTICS")
        print("=" * 60)
        
        metrics = self.get_current_metrics()
        
        print(f"\n📈 Overall Performance:")
        print(f"   Total Businesses: {metrics['total_businesses']}")
        print(f"   Messages Sent: {metrics['messages_sent']}")
        print(f"   Messages Failed: {metrics['messages_failed']}")
        print(f"   Messages Skipped: {metrics['messages_skipped']}")
        print(f"   Success Rate: {metrics['success_rate']}")
        print(f"   Average Time: {metrics['average_message_time']}")
        
        msg_dist = self.get_message_type_distribution()
        print(f"\n📝 Message Types:")
        print(f"   Creation: {msg_dist['creation']} ({msg_dist['creation_percentage']:.1f}%)")
        print(f"   Enhancement: {msg_dist['enhancement']} ({msg_dist['enhancement_percentage']:.1f}%)")
        
        if self.error_categories:
            print(f"\n❌ Error Categories:")
            for category, count in sorted(self.error_categories.items(), key=lambda x: x[1], reverse=True):
                print(f"   {category}: {count}")
        
        print(f"\n⚡ Rate Limiting:")
        print(f"   Rate Limit Hits: {metrics['rate_limit_hits']}")
        print(f"   Batch Delays: {metrics['batch_delays']}")
        
        print("=" * 60)
    
    def export_analytics(self, filename: Optional[str] = None) -> str:
        """
        Export analytics to JSON file.
        
        Args:
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analytics_{timestamp}.json"
        
        output_path = self.analytics_dir / filename
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'performance_summary': self.get_performance_summary(),
            'business_analytics': [
                {
                    'business_name': ba.business_name,
                    'phone': ba.phone,
                    'has_website': ba.has_website,
                    'message_type': ba.message_type,
                    'status': ba.status,
                    'timestamp': ba.timestamp,
                    'duration': ba.duration,
                    'retry_count': ba.retry_count,
                    'error': ba.error,
                }
                for ba in self.business_analytics
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analytics exported: {output_path}")
        return str(output_path)
