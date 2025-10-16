"""
Unit Tests for Delay Manager

Tests rate limiting, delays, and statistics tracking.

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import pytest
import time
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json

from src.core.delay_manager import (
    DelayManager,
    RateLimitConfig,
    SendingStats,
    create_default_delay_manager,
    create_test_delay_manager,
)


class TestRateLimitConfig:
    """Test RateLimitConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = RateLimitConfig()
        
        assert config.min_message_delay == 20
        assert config.max_message_delay == 90
        assert config.messages_per_batch == (10, 20)
        assert config.min_batch_delay == 300
        assert config.max_batch_delay == 900
        assert config.max_messages_per_day == 50
        assert config.max_messages_per_hour == 15
        assert config.enable_delays is True
        assert config.enable_daily_limit is True
        assert config.enable_hourly_limit is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = RateLimitConfig(
            min_message_delay=5,
            max_message_delay=10,
            max_messages_per_day=100,
            enable_delays=False,
        )
        
        assert config.min_message_delay == 5
        assert config.max_message_delay == 10
        assert config.max_messages_per_day == 100
        assert config.enable_delays is False


class TestSendingStats:
    """Test SendingStats dataclass."""
    
    def test_default_stats(self):
        """Test default statistics values."""
        stats = SendingStats()
        
        assert stats.total_sent == 0
        assert stats.sent_today == 0
        assert stats.sent_this_hour == 0
        assert stats.last_message_time is None
        assert stats.messages_since_batch_delay == 0
        assert stats.current_date is None
        assert len(stats.hourly_counts) == 0
        assert len(stats.daily_counts) == 0


class TestDelayManager:
    """Test DelayManager functionality."""
    
    @pytest.fixture
    def temp_stats_file(self):
        """Create temporary stats file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        yield str(temp_path)
        
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
    
    @pytest.fixture
    def test_manager(self, temp_stats_file):
        """Create test delay manager with fast settings."""
        config = RateLimitConfig(
            min_message_delay=1,
            max_message_delay=2,
            messages_per_batch=(3, 5),
            min_batch_delay=2,
            max_batch_delay=3,
            max_messages_per_day=10,
            max_messages_per_hour=5,
            enable_delays=True,
            enable_daily_limit=True,
            enable_hourly_limit=True,
        )
        
        return DelayManager(config=config, stats_file=temp_stats_file)
    
    def test_initialization(self, test_manager):
        """Test delay manager initialization."""
        assert test_manager.config is not None
        assert test_manager.stats is not None
        assert test_manager.stats.total_sent == 0
    
    def test_can_send_message_initially(self, test_manager):
        """Test that messages can be sent initially."""
        can_send, reason = test_manager.can_send_message()
        
        assert can_send is True
        assert reason is None
    
    def test_daily_limit(self, test_manager):
        """Test daily message limit."""
        # Send messages up to daily limit
        for i in range(test_manager.config.max_messages_per_day):
            test_manager.record_message_sent()
        
        # Should now be at limit
        can_send, reason = test_manager.can_send_message()
        
        assert can_send is False
        assert "Daily limit" in reason
    
    def test_hourly_limit(self, test_manager):
        """Test hourly message limit."""
        # Send messages up to hourly limit
        for i in range(test_manager.config.max_messages_per_hour):
            test_manager.record_message_sent()
        
        # Should now be at limit
        can_send, reason = test_manager.can_send_message()
        
        assert can_send is False
        assert "Hourly limit" in reason
    
    def test_record_message_sent(self, test_manager):
        """Test recording sent messages."""
        initial_total = test_manager.stats.total_sent
        initial_today = test_manager.stats.sent_today
        
        test_manager.record_message_sent()
        
        assert test_manager.stats.total_sent == initial_total + 1
        assert test_manager.stats.sent_today == initial_today + 1
        assert test_manager.stats.last_message_time is not None
    
    def test_batch_delay_tracking(self, test_manager):
        """Test batch delay threshold tracking."""
        initial_threshold = test_manager.stats.next_batch_delay_at
        
        # Should be between min and max from config
        assert 3 <= initial_threshold <= 5
        
        # Send messages
        for i in range(2):
            test_manager.record_message_sent()
        
        assert test_manager.stats.messages_since_batch_delay == 2
    
    def test_wait_between_messages_disabled(self):
        """Test that delays can be disabled."""
        config = RateLimitConfig(enable_delays=False)
        manager = DelayManager(config=config)
        
        start = time.time()
        manager.wait_between_messages()
        elapsed = time.time() - start
        
        # Should be nearly instant
        assert elapsed < 0.5
    
    def test_wait_between_messages_enabled(self, test_manager):
        """Test message delay timing."""
        start = time.time()
        test_manager.wait_between_messages()
        elapsed = time.time() - start
        
        # Should delay between min and max
        assert test_manager.config.min_message_delay <= elapsed <= test_manager.config.max_message_delay + 1
    
    def test_get_statistics(self, test_manager):
        """Test statistics retrieval."""
        test_manager.record_message_sent()
        
        stats = test_manager.get_statistics()
        
        assert 'total_sent' in stats
        assert 'sent_today' in stats
        assert 'sent_this_hour' in stats
        assert 'can_send_more' in stats
        assert stats['total_sent'] == 1
    
    def test_reset_daily_stats(self, test_manager):
        """Test resetting daily statistics."""
        test_manager.record_message_sent()
        assert test_manager.stats.sent_today == 1
        
        test_manager.reset_daily_stats()
        assert test_manager.stats.sent_today == 0
    
    def test_reset_hourly_stats(self, test_manager):
        """Test resetting hourly statistics."""
        test_manager.record_message_sent()
        assert test_manager.stats.sent_this_hour == 1
        
        test_manager.reset_hourly_stats()
        assert test_manager.stats.sent_this_hour == 0
    
    def test_stats_persistence(self, temp_stats_file):
        """Test saving and loading statistics."""
        # Create manager and send some messages
        manager1 = DelayManager(
            config=RateLimitConfig(),
            stats_file=temp_stats_file
        )
        
        manager1.record_message_sent()
        manager1.record_message_sent()
        
        total_sent = manager1.stats.total_sent
        
        # Create new manager with same stats file
        manager2 = DelayManager(
            config=RateLimitConfig(),
            stats_file=temp_stats_file
        )
        
        # Should load previous stats
        assert manager2.stats.total_sent == total_sent
    
    def test_date_change_resets_daily_counter(self, test_manager):
        """Test that daily counter resets on date change."""
        test_manager.record_message_sent()
        assert test_manager.stats.sent_today == 1
        
        # Simulate date change
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        test_manager.stats.current_date = yesterday
        
        # Check if can send (should reset daily counter)
        can_send, _ = test_manager.can_send_message()
        
        assert can_send is True
        assert test_manager.stats.sent_today == 0
    
    def test_hour_change_resets_hourly_counter(self, test_manager):
        """Test that hourly counter resets on hour change."""
        test_manager.record_message_sent()
        assert test_manager.stats.sent_this_hour == 1
        
        # Simulate hour change
        current_hour = datetime.now().hour
        previous_hour = (current_hour - 1) % 24
        test_manager.stats.current_hour = previous_hour
        
        # Check if can send (should reset hourly counter)
        can_send, _ = test_manager.can_send_message()
        
        assert can_send is True
        assert test_manager.stats.sent_this_hour == 0


class TestDelayManagerFactories:
    """Test factory functions for creating delay managers."""
    
    def test_create_default_delay_manager(self):
        """Test default delay manager creation."""
        manager = create_default_delay_manager(stats_file="test_stats.json")
        
        assert manager.config.max_messages_per_day == 50
        assert manager.config.enable_delays is True
        
        # Cleanup
        Path("test_stats.json").unlink(missing_ok=True)
    
    def test_create_test_delay_manager(self):
        """Test test delay manager creation."""
        manager = create_test_delay_manager()
        
        # Should have fast delays
        assert manager.config.min_message_delay < 5
        assert manager.config.max_message_delay < 10
        
        # Should have high limits
        assert manager.config.max_messages_per_day >= 1000
        assert manager.config.enable_daily_limit is False


class TestRateLimitingScenarios:
    """Test realistic rate limiting scenarios."""
    
    def test_sending_within_limits(self):
        """Test sending messages within all limits."""
        config = RateLimitConfig(
            max_messages_per_day=10,
            max_messages_per_hour=5,
            enable_delays=False,
        )
        manager = DelayManager(config=config)
        
        # Send 3 messages (within all limits)
        for i in range(3):
            can_send, reason = manager.can_send_message()
            assert can_send is True
            manager.record_message_sent()
        
        # Should still be able to send
        can_send, _ = manager.can_send_message()
        assert can_send is True
    
    def test_hitting_hourly_limit_before_daily(self):
        """Test scenario where hourly limit is hit before daily."""
        config = RateLimitConfig(
            max_messages_per_day=100,
            max_messages_per_hour=5,
            enable_delays=False,
        )
        manager = DelayManager(config=config)
        
        # Send up to hourly limit
        for i in range(5):
            manager.record_message_sent()
        
        # Should be blocked by hourly limit
        can_send, reason = manager.can_send_message()
        assert can_send is False
        assert "Hourly limit" in reason
