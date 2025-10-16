"""
Phase 8: End-to-End Integration Test Suite
Tests the complete campaign workflow from start to finish.

This test suite validates:
1. Complete campaign workflow (dry-run mode)
2. Data flow through all components
3. File generation and content validation
4. Error handling and recovery
5. State persistence and resume functionality

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import pytest
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.campaign_manager import CampaignManager
from src.core.delay_manager import create_test_delay_manager
from src.core.excel_handler import ExcelDataHandler
from src.core.message_composer import MessageComposer
from src.utils.csv_reporter import CSVReporter
from src.utils.analytics_tracker import AnalyticsTracker


class TestEndToEndWorkflow:
    """Test complete campaign workflow end-to-end."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create directory structure
        (temp_dir / 'data').mkdir()
        (temp_dir / 'data' / 'reports').mkdir()
        (temp_dir / 'data' / 'analytics').mkdir()
        (temp_dir / 'logs').mkdir()
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def sample_excel(self, temp_workspace):
        """Create sample Excel file for testing."""
        excel_path = temp_workspace / 'data' / 'test_data.xlsx'
        
        data = {
            'Business Name': [
                'Coffee Shop',
                'Tech Startup',
                'Local Restaurant',
                'Fitness Center',
                'Book Store'
            ],
            'Description': [
                'Local coffee shop',
                'Software company',
                'Family restaurant',
                'Gym and fitness',
                'Independent bookstore'
            ],
            'Website': [
                '',
                'https://techstartup.com',
                '',
                'https://fitness.com',
                ''
            ],
            'Phone': [
                '+1234567890',
                '+1234567891',
                '+1234567892',
                '+1234567893',
                '+1234567894'
            ],
            'Google Maps Link': [
                'https://maps.google.com/1',
                'https://maps.google.com/2',
                'https://maps.google.com/3',
                'https://maps.google.com/4',
                'https://maps.google.com/5'
            ]
        }
        
        df = pd.DataFrame(data)
        df.to_excel(excel_path, index=False)
        
        return excel_path
    
    def test_complete_campaign_workflow(self, sample_excel, temp_workspace):
        """Test complete campaign from start to finish."""
        print("\n" + "=" * 70)
        print("TEST 1: Complete Campaign Workflow")
        print("=" * 70)
        
        # Setup
        profile_dir = temp_workspace / 'chrome_profile'
        delay_manager = create_test_delay_manager(
            stats_file=str(temp_workspace / 'delay_stats.json')
        )
        
        # Create campaign manager
        campaign = CampaignManager(
            excel_file=str(sample_excel),
            chrome_profile=str(profile_dir),
            delay_manager=delay_manager,
            dry_run=True  # Important: dry-run mode for testing
        )
        
        print(f"\n✅ Campaign manager created")
        print(f"   Excel: {sample_excel}")
        print(f"   Profile: {profile_dir}")
        print(f"   Dry Run: True")
        
        # Run campaign
        print(f"\n🚀 Running campaign...")
        success = campaign.run_campaign(headless=True)
        
        assert success, "Campaign should complete successfully"
        print(f"✅ Campaign completed successfully")
        
        # Verify results
        results = campaign.results
        print(f"\n📊 Campaign Results:")
        print(f"   Total: {len(results)}")
        print(f"   Success: {sum(1 for r in results if r['status'] == 'success')}")
        print(f"   Failed: {sum(1 for r in results if r['status'] == 'failed')}")
        
        # Assertions
        assert len(results) == 5, "Should process 5 businesses"
        assert all(r['status'] == 'success' for r in results), "All should succeed in dry-run"
        
        # Check message types
        creation_count = sum(1 for r in results if r['message_type'] == 'creation')
        enhancement_count = sum(1 for r in results if r['message_type'] == 'enhancement')
        
        print(f"\n📝 Message Distribution:")
        print(f"   Creation: {creation_count}")
        print(f"   Enhancement: {enhancement_count}")
        
        assert creation_count == 3, "Should have 3 creation messages"
        assert enhancement_count == 2, "Should have 2 enhancement messages"
        
        print(f"\n✅ Test 1 PASSED")
    
    def test_file_generation(self, sample_excel, temp_workspace):
        """Test that all required files are generated."""
        print("\n" + "=" * 70)
        print("TEST 2: File Generation Validation")
        print("=" * 70)
        
        # Setup
        delay_manager = create_test_delay_manager()
        
        campaign = CampaignManager(
            excel_file=str(sample_excel),
            chrome_profile=str(temp_workspace / 'chrome_profile'),
            delay_manager=delay_manager,
            dry_run=True
        )
        
        # Run campaign
        campaign.run_campaign(headless=True)
        
        # Check report files
        reports_dir = Path('data/reports')
        analytics_dir = Path('data/analytics')
        campaign_reports_dir = Path('data/campaign_reports')
        
        print(f"\n📁 Checking generated files...")
        
        # Should have CSV reports
        csv_files = list(reports_dir.glob('campaign_*.csv'))
        print(f"   CSV reports: {len(csv_files)} files")
        assert len(csv_files) >= 2, "Should generate campaign CSV reports"
        
        # Should have analytics files
        analytics_files = list(analytics_dir.glob('analytics_*.json'))
        print(f"   Analytics files: {len(analytics_files)} files")
        assert len(analytics_files) >= 1, "Should generate analytics JSON"
        
        # Should have campaign report
        campaign_files = list(campaign_reports_dir.glob('campaign_*.json'))
        print(f"   Campaign reports: {len(campaign_files)} files")
        assert len(campaign_files) >= 1, "Should generate campaign report JSON"
        
        print(f"\n✅ Test 2 PASSED")
    
    def test_data_integrity(self, sample_excel):
        """Test data flows correctly through all components."""
        print("\n" + "=" * 70)
        print("TEST 3: Data Integrity Throughout Pipeline")
        print("=" * 70)
        
        # Load data
        handler = ExcelDataHandler(str(sample_excel))
        businesses, validation_summary = handler.load_businesses()
        
        print(f"\n📋 Excel Data Loaded:")
        print(f"   Total rows: {validation_summary['total_rows']}")
        print(f"   Valid: {validation_summary['valid_count']}")
        print(f"   Invalid: {validation_summary['invalid_count']}")
        
        assert len(businesses) == 5, "Should load 5 businesses"
        assert validation_summary['valid_count'] == 5, "All should be valid"
        
        # Test message composition
        composer = MessageComposer()
        
        print(f"\n✉️  Testing Message Composition:")
        
        for business in businesses:
            message_type, message, whatsapp_url = composer.compose_message(business)
            
            print(f"   {business.name}: {message_type}")
            
            # Verify message type matches website presence
            if business.website:
                assert message_type == 'enhancement', f"{business.name} should get enhancement"
            else:
                assert message_type == 'creation', f"{business.name} should get creation"
            
            # Verify message contains business name
            assert business.name in message, "Message should contain business name"
            
            # Verify URL is properly formatted
            assert 'https://wa.me/' in whatsapp_url, "Should generate WhatsApp URL"
            assert business.phone.replace('+', '') in whatsapp_url, "URL should contain phone"
        
        print(f"\n✅ Test 3 PASSED")
    
    def test_error_handling(self, temp_workspace):
        """Test error handling with invalid data."""
        print("\n" + "=" * 70)
        print("TEST 4: Error Handling & Recovery")
        print("=" * 70)
        
        # Create Excel with some invalid data
        excel_path = temp_workspace / 'data' / 'invalid_data.xlsx'
        
        data = {
            'Business Name': ['Valid Shop', '', 'Another Shop'],
            'Description': ['Good', 'Bad', 'Good'],
            'Website': ['', '', ''],
            'Phone': ['+1234567890', 'invalid', '+1234567892'],
            'Google Maps Link': ['', '', '']
        }
        
        df = pd.DataFrame(data)
        df.to_excel(excel_path, index=False)
        
        print(f"\n📋 Testing with invalid data...")
        
        # Load and validate
        handler = ExcelDataHandler(str(excel_path))
        businesses, validation_summary = handler.load_businesses()
        
        print(f"   Total rows: {validation_summary['total_rows']}")
        print(f"   Valid: {validation_summary['valid_count']}")
        print(f"   Invalid: {validation_summary['invalid_count']}")
        
        # Should filter out invalid rows
        assert validation_summary['valid_count'] == 2, "Should have 2 valid businesses"
        assert validation_summary['invalid_count'] == 1, "Should have 1 invalid business"
        
        # Campaign should still work with valid data
        delay_manager = create_test_delay_manager()
        
        campaign = CampaignManager(
            excel_file=str(excel_path),
            chrome_profile=str(temp_workspace / 'chrome_profile'),
            delay_manager=delay_manager,
            dry_run=True
        )
        
        success = campaign.run_campaign(headless=True)
        
        assert success, "Campaign should succeed with partial valid data"
        assert len(campaign.results) == 2, "Should process only valid businesses"
        
        print(f"\n✅ Test 4 PASSED - Error handling works correctly")
    
    def test_resume_capability(self, sample_excel, temp_workspace):
        """Test campaign resume functionality."""
        print("\n" + "=" * 70)
        print("TEST 5: Campaign Resume Capability")
        print("=" * 70)
        
        progress_file = temp_workspace / 'progress.json'
        delay_manager = create_test_delay_manager()
        
        # First campaign - simulate interruption after 2 messages
        print(f"\n🚀 Running partial campaign (2 messages)...")
        
        campaign1 = CampaignManager(
            excel_file=str(sample_excel),
            chrome_profile=str(temp_workspace / 'chrome_profile'),
            delay_manager=delay_manager,
            progress_file=str(progress_file),
            dry_run=True
        )
        
        # Manually process first 2 businesses
        handler = ExcelDataHandler(str(sample_excel))
        businesses, _ = handler.load_businesses()
        
        for i, business in enumerate(businesses[:2]):
            campaign1._process_business(business, i+1, len(businesses))
        
        # Save progress
        campaign1._save_progress()
        
        print(f"   Processed: 2 businesses")
        print(f"   Progress saved to: {progress_file}")
        
        assert progress_file.exists(), "Progress file should be created"
        
        # Load progress and verify
        with open(progress_file) as f:
            progress = json.load(f)
        
        print(f"   Last processed index: {progress['last_processed_index']}")
        assert progress['last_processed_index'] == 1, "Should save correct index"
        
        # Resume campaign
        print(f"\n🔄 Resuming campaign...")
        
        campaign2 = CampaignManager(
            excel_file=str(sample_excel),
            chrome_profile=str(temp_workspace / 'chrome_profile'),
            delay_manager=delay_manager,
            progress_file=str(progress_file),
            dry_run=True
        )
        
        success = campaign2.run_campaign(headless=True)
        
        assert success, "Resumed campaign should succeed"
        
        # Should process remaining businesses
        assert len(campaign2.results) == 3, "Should process remaining 3 businesses"
        
        print(f"   Remaining processed: {len(campaign2.results)} businesses")
        print(f"\n✅ Test 5 PASSED - Resume works correctly")


class TestPerformanceAndRateLimiting:
    """Test performance and rate limiting functionality."""
    
    def test_rate_limiting_enforcement(self):
        """Test that rate limits are properly enforced."""
        print("\n" + "=" * 70)
        print("TEST 6: Rate Limiting Enforcement")
        print("=" * 70)
        
        from src.core.delay_manager import DelayManager, RateLimitConfig
        
        # Create strict rate limits
        config = RateLimitConfig(
            max_messages_per_day=10,
            max_messages_per_hour=5,
            enable_daily_limit=True,
            enable_hourly_limit=True,
            min_message_delay=1,
            max_message_delay=2
        )
        
        manager = DelayManager(config, stats_file=None)
        
        print(f"\n⚙️  Rate Limits:")
        print(f"   Daily: {config.max_messages_per_day}")
        print(f"   Hourly: {config.max_messages_per_hour}")
        
        # Test daily limit
        print(f"\n📊 Testing daily limit...")
        for i in range(10):
            can_send = manager.can_send_message()
            if not can_send:
                print(f"   ✓ Daily limit enforced at message {i+1}")
                break
            manager.record_message_sent()
        
        assert not manager.can_send_message(), "Should enforce daily limit"
        
        print(f"\n✅ Test 6 PASSED")
    
    def test_delay_calculations(self):
        """Test delay calculations are within expected ranges."""
        print("\n" + "=" * 70)
        print("TEST 7: Delay Calculations")
        print("=" * 70)
        
        from src.core.delay_manager import DelayManager, RateLimitConfig
        import time
        
        config = RateLimitConfig(
            min_message_delay=1,
            max_message_delay=3,
            min_batch_delay=5,
            max_batch_delay=10,
            messages_per_batch=(3, 5)
        )
        
        manager = DelayManager(config, stats_file=None)
        
        print(f"\n⏱️  Testing message delays...")
        
        delays = []
        for i in range(5):
            delay = manager.get_message_delay()
            delays.append(delay)
            print(f"   Message {i+1}: {delay}s")
        
        # Verify delays are within range
        assert all(1 <= d <= 3 for d in delays), "Delays should be in configured range"
        
        print(f"   Average: {sum(delays)/len(delays):.2f}s")
        print(f"\n✅ Test 7 PASSED")


class TestAnalyticsAndReporting:
    """Test analytics tracking and CSV reporting."""
    
    def test_analytics_tracking(self):
        """Test analytics tracker records metrics correctly."""
        print("\n" + "=" * 70)
        print("TEST 8: Analytics Tracking")
        print("=" * 70)
        
        tracker = AnalyticsTracker(analytics_dir='test_analytics')
        
        # Start campaign
        tracker.start_campaign(total_businesses=10)
        
        print(f"\n📊 Tracking events...")
        
        # Track various events
        tracker.track_message_sent('creation', duration=1.5)
        tracker.track_message_sent('enhancement', duration=2.0)
        tracker.track_message_sent('creation', duration=1.8)
        tracker.track_message_failed('Network error', duration=3.0)
        tracker.track_message_skipped('Rate limit')
        
        # End campaign
        tracker.end_campaign()
        
        # Get metrics
        metrics = tracker.get_metrics()
        
        print(f"\n📈 Metrics:")
        print(f"   Total: {metrics['total_businesses']}")
        print(f"   Sent: {metrics['messages_sent']}")
        print(f"   Failed: {metrics['messages_failed']}")
        print(f"   Skipped: {metrics['messages_skipped']}")
        print(f"   Success Rate: {metrics['success_rate']:.2f}%")
        
        # Assertions
        assert metrics['messages_sent'] == 3, "Should track 3 sent messages"
        assert metrics['messages_failed'] == 1, "Should track 1 failure"
        assert metrics['messages_skipped'] == 1, "Should track 1 skip"
        assert metrics['success_rate'] == 75.0, "Success rate should be 75%"
        
        # Check message distribution
        distribution = tracker.get_message_distribution()
        print(f"\n📝 Distribution:")
        print(f"   Creation: {distribution.get('creation', 0)}")
        print(f"   Enhancement: {distribution.get('enhancement', 0)}")
        
        assert distribution['creation'] == 2, "Should have 2 creation messages"
        assert distribution['enhancement'] == 1, "Should have 1 enhancement message"
        
        print(f"\n✅ Test 8 PASSED")
        
        # Cleanup
        shutil.rmtree('test_analytics', ignore_errors=True)
    
    def test_csv_export(self):
        """Test CSV reporter generates correct files."""
        print("\n" + "=" * 70)
        print("TEST 9: CSV Export Functionality")
        print("=" * 70)
        
        temp_dir = Path(tempfile.mkdtemp())
        reporter = CSVReporter(reports_dir=str(temp_dir))
        
        # Sample campaign results
        results = [
            {
                'business_name': 'Shop 1',
                'phone': '+1234567890',
                'website': '',
                'message_type': 'creation',
                'status': 'success',
                'error': '',
                'timestamp': datetime.now().isoformat()
            },
            {
                'business_name': 'Shop 2',
                'phone': '+1234567891',
                'website': 'https://shop2.com',
                'message_type': 'enhancement',
                'status': 'success',
                'error': '',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        print(f"\n📄 Exporting campaign results...")
        
        # Export campaign summary
        summary_data = {
            'total_businesses': 2,
            'messages_sent': 2,
            'messages_failed': 0,
            'messages_skipped': 0,
            'success_rate': 100.0,
            'duration': '00:00:30',
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat()
        }
        
        summary_file = reporter.export_campaign_summary(summary_data)
        results_file = reporter.export_message_log(results)
        
        print(f"   Summary: {summary_file.name}")
        print(f"   Results: {results_file.name}")
        
        # Verify files exist
        assert summary_file.exists(), "Summary file should exist"
        assert results_file.exists(), "Results file should exist"
        
        # Verify content
        df_summary = pd.read_csv(summary_file)
        df_results = pd.read_csv(results_file)
        
        print(f"\n📊 File Contents:")
        print(f"   Summary rows: {len(df_summary)}")
        print(f"   Results rows: {len(df_results)}")
        
        assert len(df_summary) == 1, "Summary should have 1 row"
        assert len(df_results) == 2, "Results should have 2 rows"
        
        print(f"\n✅ Test 9 PASSED")
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """Run all Phase 8 tests with detailed reporting."""
    print("\n" + "=" * 70)
    print("PHASE 8 TEST SUITE - TESTING & QUALITY ASSURANCE")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Run with pytest
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-s'  # Show print statements
    ])


if __name__ == "__main__":
    run_all_tests()
