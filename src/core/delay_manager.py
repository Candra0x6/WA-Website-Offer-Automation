"""
Delay Manager - Rate Limiting & Anti-Ban Features

Implements intelligent delay management to avoid WhatsApp bans:
- Random delays between messages (20-90 seconds)
- Batch delays after every 10-20 messages (5-15 minutes)
- Daily message limits (30-50 messages)
- Hourly caps for safe distribution
- Human-like behavior simulation

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import random
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    
    # Message delays (seconds)
    min_message_delay: int = 20
    max_message_delay: int = 90
    
    # Batch delays
    messages_per_batch: tuple = (10, 20)  # Random between 10-20
    min_batch_delay: int = 300  # 5 minutes
    max_batch_delay: int = 900  # 15 minutes
    
    # Daily limits
    max_messages_per_day: int = 50
    max_messages_per_hour: int = 15
    
    # Safety settings
    enable_delays: bool = True
    enable_daily_limit: bool = True
    enable_hourly_limit: bool = True


@dataclass
class SendingStats:
    """Statistics for message sending."""
    
    total_sent: int = 0
    sent_today: int = 0
    sent_this_hour: int = 0
    last_message_time: Optional[datetime] = None
    last_batch_delay_time: Optional[datetime] = None
    messages_since_batch_delay: int = 0
    next_batch_delay_at: int = 0
    
    # Daily tracking
    current_date: Optional[str] = None
    current_hour: Optional[int] = None
    
    # History
    hourly_counts: Dict[str, int] = field(default_factory=dict)
    daily_counts: Dict[str, int] = field(default_factory=dict)


class DelayManager:
    """
    Manages delays and rate limiting for WhatsApp message sending.
    
    Features:
    - Random delays between messages
    - Batch delays after N messages
    - Daily and hourly limits
    - Statistics tracking
    - Persistence across sessions
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None,
                 stats_file: Optional[str] = None):
        """
        Initialize delay manager.
        
        Args:
            config: Rate limiting configuration (uses defaults if None)
            stats_file: Path to stats file for persistence
        """
        self.config = config or RateLimitConfig()
        self.stats = SendingStats()
        self.stats_file = Path(stats_file) if stats_file else None
        
        # Load existing stats if available
        if self.stats_file and self.stats_file.exists():
            self._load_stats()
        
        # Set next batch delay threshold
        self._reset_batch_threshold()
        
        logger.info(f"DelayManager initialized with config: {self.config}")
    
    def _reset_batch_threshold(self):
        """Set random threshold for next batch delay."""
        min_msgs, max_msgs = self.config.messages_per_batch
        self.stats.next_batch_delay_at = random.randint(min_msgs, max_msgs)
        logger.debug(f"Next batch delay will occur after {self.stats.next_batch_delay_at} messages")
    
    def can_send_message(self) -> tuple[bool, Optional[str]]:
        """
        Check if a message can be sent based on rate limits.
        
        Returns:
            tuple: (can_send: bool, reason: str or None)
        """
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_hour = now.hour
        
        # Update date/hour tracking
        if self.stats.current_date != today:
            logger.info(f"New day detected: {today}. Resetting daily counters.")
            self.stats.current_date = today
            self.stats.sent_today = 0
        
        if self.stats.current_hour != current_hour:
            logger.debug(f"New hour detected: {current_hour}. Resetting hourly counter.")
            self.stats.current_hour = current_hour
            self.stats.sent_this_hour = 0
        
        # Check daily limit
        if self.config.enable_daily_limit:
            if self.stats.sent_today >= self.config.max_messages_per_day:
                reason = f"Daily limit reached ({self.config.max_messages_per_day} messages)"
                logger.warning(reason)
                return False, reason
        
        # Check hourly limit
        if self.config.enable_hourly_limit:
            if self.stats.sent_this_hour >= self.config.max_messages_per_hour:
                reason = f"Hourly limit reached ({self.config.max_messages_per_hour} messages)"
                logger.warning(reason)
                return False, reason
        
        return True, None
    
    def wait_between_messages(self, force: bool = False):
        """
        Wait appropriate delay between messages.
        
        Args:
            force: Force delay even if delays are disabled
        """
        if not self.config.enable_delays and not force:
            logger.debug("Delays disabled, skipping wait")
            return
        
        # Check if batch delay is needed
        if self.stats.messages_since_batch_delay >= self.stats.next_batch_delay_at:
            self._do_batch_delay()
            return
        
        # Normal message delay
        delay = random.randint(
            self.config.min_message_delay,
            self.config.max_message_delay
        )
        
        logger.info(f"Waiting {delay} seconds before next message...")
        self._sleep_with_countdown(delay)
    
    def _do_batch_delay(self):
        """Perform batch delay (longer rest after multiple messages)."""
        delay = random.randint(
            self.config.min_batch_delay,
            self.config.max_batch_delay
        )
        
        logger.info(
            f"🛑 Batch delay triggered after {self.stats.messages_since_batch_delay} messages. "
            f"Resting for {delay // 60} minutes ({delay} seconds)..."
        )
        
        self.stats.last_batch_delay_time = datetime.now()
        self._sleep_with_countdown(delay, show_minutes=True)
        
        # Reset batch counter and set new threshold
        self.stats.messages_since_batch_delay = 0
        self._reset_batch_threshold()
    
    def _sleep_with_countdown(self, seconds: int, show_minutes: bool = False):
        """
        Sleep with countdown display.
        
        Args:
            seconds: Number of seconds to sleep
            show_minutes: Show countdown in MM:SS format
        """
        start_time = time.time()
        end_time = start_time + seconds
        
        while time.time() < end_time:
            remaining = int(end_time - time.time())
            
            if remaining <= 0:
                break
            
            if show_minutes:
                mins, secs = divmod(remaining, 60)
                display = f"{mins:02d}:{secs:02d}"
            else:
                display = f"{remaining}s"
            
            # Update countdown every second
            if remaining % 5 == 0 or remaining <= 10:
                logger.debug(f"⏳ Time remaining: {display}")
            
            time.sleep(1)
    
    def record_message_sent(self):
        """Record that a message was successfully sent."""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        hour_key = now.strftime("%Y-%m-%d %H:00")
        
        # Update counters
        self.stats.total_sent += 1
        self.stats.sent_today += 1
        self.stats.sent_this_hour += 1
        self.stats.messages_since_batch_delay += 1
        self.stats.last_message_time = now
        
        # Update history
        self.stats.hourly_counts[hour_key] = self.stats.sent_this_hour
        self.stats.daily_counts[today] = self.stats.sent_today
        
        logger.info(
            f"📊 Message recorded: Total={self.stats.total_sent}, "
            f"Today={self.stats.sent_today}/{self.config.max_messages_per_day}, "
            f"This Hour={self.stats.sent_this_hour}/{self.config.max_messages_per_hour}"
        )
        
        # Save stats
        if self.stats_file:
            self._save_stats()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current sending statistics.
        
        Returns:
            dict: Statistics dictionary
        """
        now = datetime.now()
        
        stats_dict = {
            'total_sent': self.stats.total_sent,
            'sent_today': self.stats.sent_today,
            'sent_this_hour': self.stats.sent_this_hour,
            'daily_limit': self.config.max_messages_per_day,
            'hourly_limit': self.config.max_messages_per_hour,
            'messages_until_batch_delay': (
                self.stats.next_batch_delay_at - self.stats.messages_since_batch_delay
            ),
            'last_message_time': (
                self.stats.last_message_time.isoformat() 
                if self.stats.last_message_time else None
            ),
            'current_date': now.strftime("%Y-%m-%d"),
            'current_hour': now.hour,
        }
        
        # Add remaining capacity
        can_send, reason = self.can_send_message()
        stats_dict['can_send_more'] = can_send
        stats_dict['limit_reason'] = reason
        
        return stats_dict
    
    def reset_daily_stats(self):
        """Reset daily statistics (for testing or manual reset)."""
        logger.warning("Manually resetting daily statistics")
        self.stats.sent_today = 0
        self.stats.current_date = datetime.now().strftime("%Y-%m-%d")
        
        if self.stats_file:
            self._save_stats()
    
    def reset_hourly_stats(self):
        """Reset hourly statistics (for testing or manual reset)."""
        logger.warning("Manually resetting hourly statistics")
        self.stats.sent_this_hour = 0
        self.stats.current_hour = datetime.now().hour
        
        if self.stats_file:
            self._save_stats()
    
    def _save_stats(self):
        """Save statistics to file."""
        if not self.stats_file:
            return
        
        try:
            # Ensure directory exists
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            
            stats_data = {
                'total_sent': self.stats.total_sent,
                'sent_today': self.stats.sent_today,
                'sent_this_hour': self.stats.sent_this_hour,
                'last_message_time': (
                    self.stats.last_message_time.isoformat()
                    if self.stats.last_message_time else None
                ),
                'last_batch_delay_time': (
                    self.stats.last_batch_delay_time.isoformat()
                    if self.stats.last_batch_delay_time else None
                ),
                'messages_since_batch_delay': self.stats.messages_since_batch_delay,
                'next_batch_delay_at': self.stats.next_batch_delay_at,
                'current_date': self.stats.current_date,
                'current_hour': self.stats.current_hour,
                'hourly_counts': self.stats.hourly_counts,
                'daily_counts': self.stats.daily_counts,
            }
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2)
            
            logger.debug(f"Stats saved to {self.stats_file}")
            
        except Exception as e:
            logger.error(f"Failed to save stats: {str(e)}")
    
    def _load_stats(self):
        """Load statistics from file."""
        if not self.stats_file or not self.stats_file.exists():
            return
        
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                stats_data = json.load(f)
            
            self.stats.total_sent = stats_data.get('total_sent', 0)
            self.stats.sent_today = stats_data.get('sent_today', 0)
            self.stats.sent_this_hour = stats_data.get('sent_this_hour', 0)
            
            # Parse datetime fields
            if stats_data.get('last_message_time'):
                self.stats.last_message_time = datetime.fromisoformat(
                    stats_data['last_message_time']
                )
            
            if stats_data.get('last_batch_delay_time'):
                self.stats.last_batch_delay_time = datetime.fromisoformat(
                    stats_data['last_batch_delay_time']
                )
            
            self.stats.messages_since_batch_delay = stats_data.get(
                'messages_since_batch_delay', 0
            )
            self.stats.next_batch_delay_at = stats_data.get('next_batch_delay_at', 10)
            self.stats.current_date = stats_data.get('current_date')
            self.stats.current_hour = stats_data.get('current_hour')
            self.stats.hourly_counts = stats_data.get('hourly_counts', {})
            self.stats.daily_counts = stats_data.get('daily_counts', {})
            
            logger.info(f"Stats loaded from {self.stats_file}")
            logger.info(
                f"Loaded: Total={self.stats.total_sent}, "
                f"Today={self.stats.sent_today}, Hour={self.stats.sent_this_hour}"
            )
            
        except Exception as e:
            logger.error(f"Failed to load stats: {str(e)}")
    
    def print_statistics(self):
        """Print formatted statistics to console."""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print("📊 DELAY MANAGER STATISTICS")
        print("=" * 60)
        print(f"Total Messages Sent: {stats['total_sent']}")
        print(f"Sent Today: {stats['sent_today']}/{stats['daily_limit']}")
        print(f"Sent This Hour: {stats['sent_this_hour']}/{stats['hourly_limit']}")
        print(f"Messages Until Batch Delay: {stats['messages_until_batch_delay']}")
        
        if stats['last_message_time']:
            print(f"Last Message: {stats['last_message_time']}")
        
        if stats['can_send_more']:
            print("✅ Status: Can send more messages")
        else:
            print(f"🛑 Status: {stats['limit_reason']}")
        
        print("=" * 60 + "\n")


def create_default_delay_manager(stats_file: str = "data/delay_stats.json") -> DelayManager:
    """
    Create a delay manager with default safe settings.
    
    Args:
        stats_file: Path to statistics file
        
    Returns:
        DelayManager instance
    """
    config = RateLimitConfig(
        min_message_delay=20,
        max_message_delay=90,
        messages_per_batch=(10, 20),
        min_batch_delay=300,
        max_batch_delay=900,
        max_messages_per_day=50,
        max_messages_per_hour=15,
        enable_delays=True,
        enable_daily_limit=True,
        enable_hourly_limit=True,
    )
    
    return DelayManager(config=config, stats_file=stats_file)


def create_test_delay_manager(stats_file: Optional[str] = None) -> DelayManager:
    """
    Create a delay manager for testing (faster delays, no limits).
    
    Args:
        stats_file: Path to statistics file
        
    Returns:
        DelayManager instance configured for testing
    """
    config = RateLimitConfig(
        min_message_delay=1,
        max_message_delay=3,
        messages_per_batch=(3, 5),
        min_batch_delay=5,
        max_batch_delay=10,
        max_messages_per_day=1000,
        max_messages_per_hour=100,
        enable_delays=True,
        enable_daily_limit=False,
        enable_hourly_limit=False,
    )
    
    return DelayManager(config=config, stats_file=stats_file)
