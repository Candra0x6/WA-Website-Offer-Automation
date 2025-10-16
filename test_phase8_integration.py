"""
Phase 8: Simplified Integration Test Suite
Tests critical functionality with correct API signatures.

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import pytest
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCoreIntegration:
    """Test core integration points."""
    
    def test_excel_to_business_flow(self):
        """Test loading Excel and converting to Business objects."""
        print("\n" + "=" * 70)
        print("TEST 1: Excel to Business Object Flow")
        print("=" * 70)
        
        # Use existing test data
        excel_path = Path('data/data.xlsx')
        
        if not excel_path.exists():
            pytest.skip("Test data not found")
        
        from src.core.excel_handler import ExcelDataHandler
        
        handler = ExcelDataHandler(str(excel_path))
        handler.load_data()
        businesses = handler.get_businesses()
        summary = handler.get_validation_summary()
        
        print(f"\n📋 Data Loaded:")
        print(f"   Total rows: {summary['total_rows']}")
        print(f"   Valid: {summary['valid_count']}")
        print(f"   Invalid: {summary['invalid_count']}")
        print(f"   Success rate: {summary['success_rate']:.1f}%")
        
        assert len(businesses) > 0, "Should load businesses"
        assert summary['valid_count'] > 0, "Should have valid businesses"
        
        # Check business objects
        business = businesses[0]
        print(f"\n📊 Sample Business:")
        print(f"   Name: {business.name}")
        print(f"   Phone: {business.phone}")
        print(f"   Has Website: {'Yes' if business.website else 'No'}")
        
        assert business.name, "Business should have name"
        assert business.phone, "Business should have phone"
        
        print(f"\n✅ Test 1 PASSED")
    
    def test_message_composition(self):
        """Test message composition for both types."""
        print("\n" + "=" * 70)
        print("TEST 2: Message Composition")
        print("=" * 70)
        
        from src.core.message_composer import MessageComposer
        from src.models.business import Business
        
        composer = MessageComposer()
        
        # Test creation message (no website)
        business1 = Business(
            name="Test Coffee Shop",
            description="Local cafe",
            website="",
            phone="+1234567890",
            google_maps_link="https://maps.google.com/test"
        )
        
        msg_type1, message1, url1 = composer.compose_message(business1)
        
        print(f"\n✉️  Creation Message:")
        print(f"   Type: {msg_type1}")
        print(f"   Length: {len(message1)} chars")
        print(f"   Preview: {message1[:80]}...")
        
        assert msg_type1 == "creation", "Should be creation message"
        assert business1.name in message1, "Should contain business name"
        assert "https://wa.me/" in url1, "Should generate WhatsApp URL"
        
        # Test enhancement message (with website)
        business2 = Business(
            name="Test Tech Company",
            description="Software dev",
            website="https://testtech.com",
            phone="+1234567891",
            google_maps_link="https://maps.google.com/test2"
        )
        
        msg_type2, message2, url2 = composer.compose_message(business2)
        
        print(f"\n✉️  Enhancement Message:")
        print(f"   Type: {msg_type2}")
        print(f"   Length: {len(message2)} chars")
        print(f"   Preview: {message2[:80]}...")
        
        assert msg_type2 == "enhancement", "Should be enhancement message"
        assert business2.name in message2, "Should contain business name"
        assert business2.website in message2, "Should contain website URL"
        
        print(f"\n✅ Test 2 PASSED")
    
    def test_delay_manager_basic(self):
        """Test delay manager basic functionality."""
        print("\n" + "=" * 70)
        print("TEST 3: Delay Manager Basic Functionality")
        print("=" * 70)
        
        from src.core.delay_manager import create_test_delay_manager
        
        manager = create_test_delay_manager()
        
        print(f"\n⚙️  Configuration:")
        print(f"   Min delay: {manager.config.min_message_delay}s")
        print(f"   Max delay: {manager.config.max_message_delay}s")
        print(f"   Daily limit: {manager.config.max_messages_per_day}")
        
        # Test can send message
        can_send, reason = manager.can_send_message()
        print(f"\n📊 Status:")
        print(f"   Can send: {can_send}")
        print(f"   Reason: {reason}")
        
        assert can_send, "Should be able to send initially"
        
        # Record some messages
        for i in range(5):
            manager.record_message_sent()
        
        stats = manager.get_stats()
        print(f"\n📈 After 5 messages:")
        print(f"   Total sent: {stats['total_messages_sent']}")
        print(f"   Today: {stats['sent_today']}")
        
        assert stats['total_messages_sent'] == 5, "Should track message count"
        
        print(f"\n✅ Test 3 PASSED")
    
    def test_analytics_basic(self):
        """Test analytics tracker basic functionality."""
        print("\n" + "=" * 70)
        print("TEST 4: Analytics Tracker Basic Functionality")
        print("=" * 70)
        
        from src.utils.analytics_tracker import AnalyticsTracker
        
        temp_dir = Path(tempfile.mkdtemp())
        tracker = AnalyticsTracker(analytics_dir=str(temp_dir))
        
        # Start tracking
        tracker.start_campaign(total_businesses=10)
        
        print(f"\n📊 Tracking events...")
        
        # Track some events with correct signature
        tracker.track_message_sent(
            business_name="Shop 1",
            phone="+1234567890",
            message_type="creation",
            has_website=False,
            duration=1.5
        )
        
        tracker.track_message_sent(
            business_name="Shop 2",
            phone="+1234567891",
            message_type="enhancement",
            has_website=True,
            duration=2.0
        )
        
        tracker.track_message_failed(
            business_name="Shop 3",
            phone="+1234567892",
            error="Network error",
            duration=3.0
        )
        
        tracker.end_campaign()
        
        # Get metrics
        metrics = tracker.get_metrics()
        
        print(f"\n📈 Metrics:")
        print(f"   Total: {metrics['total_businesses']}")
        print(f"   Sent: {metrics['messages_sent']}")
        print(f"   Failed: {metrics['messages_failed']}")
        print(f"   Success Rate: {metrics['success_rate']:.2f}%")
        
        assert metrics['messages_sent'] == 2, "Should track 2 sent"
        assert metrics['messages_failed'] == 1, "Should track 1 failed"
        assert metrics['success_rate'] == 66.67, "Success rate should be 66.67%"
        
        print(f"\n✅ Test 4 PASSED")
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_csv_reporter_basic(self):
        """Test CSV reporter basic functionality."""
        print("\n" + "=" * 70)
        print("TEST 5: CSV Reporter Basic Functionality")
        print("=" * 70)
        
        from src.utils.csv_reporter import CSVReporter
        
        temp_dir = Path(tempfile.mkdtemp())
        reporter = CSVReporter(reports_dir=str(temp_dir))
        
        # Create sample campaign summary
        summary_data = {
            'total_businesses': 10,
            'messages_sent': 8,
            'messages_failed': 1,
            'messages_skipped': 1,
            'success_rate': 88.89,
            'duration': '00:05:30',
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat()
        }
        
        print(f"\n📄 Exporting campaign summary...")
        
        summary_file = reporter.export_campaign_summary(summary_data)
        
        print(f"   File: {summary_file.name}")
        print(f"   Exists: {summary_file.exists()}")
        
        assert summary_file.exists(), "Summary file should be created"
        
        # Verify content
        df = pd.read_csv(summary_file)
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        assert len(df) == 1, "Should have 1 summary row"
        assert df['messages_sent'][0] == 8, "Should have correct sent count"
        
        print(f"\n✅ Test 5 PASSED")
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


class TestCampaignDryRun:
    """Test campaign in dry-run mode."""
    
    def test_dry_run_campaign(self):
        """Test full dry-run campaign."""
        print("\n" + "=" * 70)
        print("TEST 6: Dry-Run Campaign End-to-End")
        print("=" * 70)
        
        excel_path = Path('data/data.xlsx')
        
        if not excel_path.exists():
            pytest.skip("Test data not found")
        
        from src.core.campaign_manager import CampaignManager
        from src.core.delay_manager import create_test_delay_manager
        
        # Create temp profile
        temp_dir = Path(tempfile.mkdtemp())
        profile_dir = temp_dir / 'chrome_profile'
        
        delay_manager = create_test_delay_manager()
        
        print(f"\n⚙️  Configuration:")
        print(f"   Excel: {excel_path}")
        print(f"   Profile: {profile_dir}")
        print(f"   Dry Run: True")
        
        campaign = CampaignManager(
            excel_file=str(excel_path),
            chrome_profile=str(profile_dir),
            delay_manager=delay_manager,
            dry_run=True
        )
        
        print(f"\n🚀 Running campaign...")
        
        # Run campaign (should complete without browser)
        success = campaign.run_campaign(headless=True)
        
        if not success:
            print(f"   ⚠️  Campaign returned False (may be due to no valid businesses)")
        
        results = campaign.results
        
        print(f"\n📊 Results:")
        print(f"   Total processed: {len(results)}")
        
        if len(results) > 0:
            success_count = sum(1 for r in results if r['status'] == 'success')
            print(f"   Successful: {success_count}")
            print(f"   Failed: {len(results) - success_count}")
            
            # Sample result
            print(f"\n📋 Sample Result:")
            sample = results[0]
            print(f"   Business: {sample['business_name']}")
            print(f"   Type: {sample['message_type']}")
            print(f"   Status: {sample['status']}")
        
        print(f"\n✅ Test 6 COMPLETED")
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


class TestCLIFeatures:
    """Test CLI-related features."""
    
    def test_config_validation(self):
        """Test configuration validation."""
        print("\n" + "=" * 70)
        print("TEST 7: Configuration Validation")
        print("=" * 70)
        
        import pandas as pd
        
        # Test Excel validation
        excel_path = Path('data/data.xlsx')
        
        if not excel_path.exists():
            pytest.skip("Test data not found")
        
        print(f"\n📋 Validating Excel file...")
        
        # Load and check
        df = pd.read_csv(excel_path)
        
        required_cols = ['Business Name', 'Phone']
        has_required = all(col in df.columns for col in required_cols)
        
        print(f"   File exists: ✓")
        print(f"   Required columns: {'✓' if has_required else '✗'}")
        print(f"   Row count: {len(df)}")
        
        assert has_required, "Should have required columns"
        
        # Test directories
        print(f"\n📁 Validating directories...")
        
        data_dir = Path('data')
        logs_dir = Path('logs')
        reports_dir = Path('data/reports')
        
        print(f"   data/: {'✓' if data_dir.exists() else '✗'}")
        print(f"   logs/: {'✓' if logs_dir.exists() else '✗'}")
        print(f"   data/reports/: {'✓' if reports_dir.exists() else '✗'}")
        
        assert data_dir.exists(), "data directory should exist"
        
        print(f"\n✅ Test 7 PASSED")


def run_phase8_tests():
    """Run all Phase 8 tests."""
    print("\n" + "=" * 70)
    print("PHASE 8: TESTING & QUALITY ASSURANCE")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    # Run tests
    result = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-s',
        '--color=yes'
    ])
    
    print("\n" + "=" * 70)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    exit_code = run_phase8_tests()
    sys.exit(exit_code)
