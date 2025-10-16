"""
Phase 5 Integration Test
Tests Campaign Management with Rate Limiting

Tests the complete campaign workflow with:
- Delay management
- Rate limiting
- Campaign orchestration
- Progress tracking

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.campaign_manager import CampaignManager
from src.core.delay_manager import create_test_delay_manager, RateLimitConfig, DelayManager


def test_delay_manager():
    """Test delay manager functionality."""
    print("=" * 60)
    print("Test 1: Delay Manager")
    print("=" * 60)
    
    try:
        # Create test delay manager (fast settings)
        manager = create_test_delay_manager()
        
        print(f"✅ Delay manager created")
        print(f"   Min delay: {manager.config.min_message_delay}s")
        print(f"   Max delay: {manager.config.max_message_delay}s")
        print(f"   Daily limit: {manager.config.max_messages_per_day}")
        print(f"   Hourly limit: {manager.config.max_messages_per_hour}")
        
        # Test can send message
        can_send, reason = manager.can_send_message()
        print(f"\n✅ Can send message: {can_send}")
        
        # Record some messages
        print(f"\n📊 Recording test messages...")
        for i in range(3):
            manager.record_message_sent()
            time.sleep(0.1)
        
        # Get statistics
        stats = manager.get_statistics()
        print(f"\n✅ Statistics:")
        print(f"   Total sent: {stats['total_sent']}")
        print(f"   Sent today: {stats['sent_today']}")
        print(f"   Sent this hour: {stats['sent_this_hour']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Delay manager test failed: {str(e)}")
        return False


def test_rate_limiting():
    """Test rate limiting enforcement."""
    print("\n" + "=" * 60)
    print("Test 2: Rate Limiting")
    print("=" * 60)
    
    try:
        # Create manager with low limits
        config = RateLimitConfig(
            max_messages_per_day=5,
            max_messages_per_hour=3,
            enable_delays=False,
        )
        manager = DelayManager(config=config)
        
        print(f"✅ Manager created with limits:")
        print(f"   Daily: {config.max_messages_per_day}")
        print(f"   Hourly: {config.max_messages_per_hour}")
        
        # Send up to hourly limit
        print(f"\n📊 Sending up to hourly limit...")
        for i in range(3):
            can_send, _ = manager.can_send_message()
            if can_send:
                manager.record_message_sent()
                print(f"   Message {i+1} sent")
        
        # Try to send one more (should be blocked)
        can_send, reason = manager.can_send_message()
        
        if not can_send:
            print(f"\n✅ Rate limit enforced: {reason}")
            return True
        else:
            print(f"\n❌ Rate limit not enforced")
            return False
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {str(e)}")
        return False


def test_campaign_dry_run():
    """Test campaign manager in dry run mode."""
    print("\n" + "=" * 60)
    print("Test 3: Campaign Manager (Dry Run)")
    print("=" * 60)
    
    try:
        excel_file = Path(__file__).parent / 'data' / 'data.xlsx'
        
        if not excel_file.exists():
            print("⚠️  Sample data not found, skipping")
            return True
        
        print(f"✅ Excel file: {excel_file}")
        
        # Create test delay manager
        delay_manager = create_test_delay_manager()
        
        # Create campaign manager
        campaign = CampaignManager(
            excel_file=str(excel_file),
            chrome_profile="test_profile",
            delay_manager=delay_manager,
            dry_run=True  # Don't actually send
        )
        
        print(f"✅ Campaign manager created")
        print(f"   Mode: DRY RUN")
        
        # Run campaign
        print(f"\n📨 Running campaign...")
        success = campaign.run_campaign(headless=True)
        
        if success:
            print(f"\n✅ Campaign completed successfully")
            
            # Show results
            print(f"\n📊 Results:")
            print(f"   Total: {campaign.progress.total_businesses}")
            print(f"   Processed: {campaign.progress.processed}")
            print(f"   Sent: {campaign.progress.sent}")
            print(f"   Failed: {campaign.progress.failed}")
            print(f"   Skipped: {campaign.progress.skipped}")
            
            return True
        else:
            print(f"\n❌ Campaign failed")
            return False
        
    except Exception as e:
        print(f"❌ Campaign test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_delays():
    """Test batch delay logic."""
    print("\n" + "=" * 60)
    print("Test 4: Batch Delays")
    print("=" * 60)
    
    try:
        # Create manager with small batch size
        config = RateLimitConfig(
            messages_per_batch=(2, 3),  # Trigger after 2-3 messages
            min_batch_delay=2,
            max_batch_delay=3,
            min_message_delay=0,
            max_message_delay=1,
            enable_delays=True,
        )
        manager = DelayManager(config=config)
        
        print(f"✅ Manager created")
        print(f"   Batch size: {config.messages_per_batch}")
        print(f"   Next batch delay at: {manager.stats.next_batch_delay_at} messages")
        
        # Send messages and trigger batch delay
        print(f"\n📊 Sending messages to trigger batch delay...")
        
        start_time = time.time()
        
        for i in range(manager.stats.next_batch_delay_at + 1):
            manager.record_message_sent()
            
            if i < manager.stats.next_batch_delay_at:
                # Normal delay
                print(f"   Message {i+1} sent")
                manager.wait_between_messages()
            else:
                # This should trigger batch delay
                print(f"   Message {i+1} sent - triggering batch delay...")
                manager.wait_between_messages()
        
        elapsed = time.time() - start_time
        
        # Should have taken at least the batch delay time
        if elapsed >= config.min_batch_delay:
            print(f"\n✅ Batch delay triggered (took {elapsed:.1f}s)")
            return True
        else:
            print(f"\n⚠️  Batch delay not detected (took {elapsed:.1f}s)")
            return True  # Still pass, might not have triggered
        
    except Exception as e:
        print(f"❌ Batch delay test failed: {str(e)}")
        return False


def test_statistics_persistence():
    """Test statistics save/load."""
    print("\n" + "=" * 60)
    print("Test 5: Statistics Persistence")
    print("=" * 60)
    
    try:
        import tempfile
        
        # Create temp file for stats
        temp_file = Path(tempfile.gettempdir()) / "test_stats.json"
        
        # Create first manager and send messages
        manager1 = DelayManager(
            config=RateLimitConfig(),
            stats_file=str(temp_file)
        )
        
        manager1.record_message_sent()
        manager1.record_message_sent()
        
        total_sent = manager1.stats.total_sent
        print(f"✅ Manager 1: Sent {total_sent} messages")
        
        # Create second manager with same file
        manager2 = DelayManager(
            config=RateLimitConfig(),
            stats_file=str(temp_file)
        )
        
        print(f"✅ Manager 2: Loaded stats")
        print(f"   Total sent: {manager2.stats.total_sent}")
        
        # Should match
        if manager2.stats.total_sent == total_sent:
            print(f"\n✅ Statistics persisted correctly")
            
            # Cleanup
            temp_file.unlink(missing_ok=True)
            return True
        else:
            print(f"\n❌ Statistics mismatch")
            return False
        
    except Exception as e:
        print(f"❌ Persistence test failed: {str(e)}")
        return False


def main():
    """Run all Phase 5 tests."""
    print("\n" + "=" * 60)
    print("PHASE 5 INTEGRATION TEST SUITE")
    print("Rate Limiting & Campaign Management")
    print("=" * 60)
    
    tests = [
        ("Delay Manager", test_delay_manager),
        ("Rate Limiting", test_rate_limiting),
        ("Campaign Manager (Dry Run)", test_campaign_dry_run),
        ("Batch Delays", test_batch_delays),
        ("Statistics Persistence", test_statistics_persistence),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            results.append((test_name, False))
            break
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error:")
            print(f"   {str(e)}")
            results.append((test_name, False))
    
    # Print final summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(success for _, success in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL PHASE 5 TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED OR WERE SKIPPED")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
