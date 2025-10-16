"""
Phase 6 Integration Test
Tests Logging, CSV Reporting, and Analytics

Tests the monitoring and reporting features:
- Enhanced logging system
- CSV report generation
- Analytics tracking
- Performance metrics

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import sys
from pathlib import Path
import tempfile
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.enhanced_logging import setup_enhanced_logging, EnhancedLogger
from src.utils.csv_reporter import CSVReporter
from src.utils.analytics_tracker import AnalyticsTracker


def test_enhanced_logging():
    """Test enhanced logging system."""
    print("=" * 60)
    print("Test 1: Enhanced Logging")
    print("=" * 60)
    
    try:
        # Create temporary log directory
        temp_dir = Path(tempfile.gettempdir()) / "test_logs"
        
        # Setup logging
        logger = setup_enhanced_logging(log_dir=str(temp_dir))
        
        print(f"✅ Logging system initialized")
        print(f"   Log directory: {temp_dir}")
        
        # Test performance tracking
        logger.track_operation("test_operation", success=True, duration=1.5)
        logger.track_operation("test_operation", success=True, duration=2.0)
        logger.track_operation("test_operation", success=False, duration=0.5)
        
        print(f"✅ Performance tracking tested")
        
        # Test error logging
        try:
            raise ValueError("Test error")
        except Exception as e:
            logger.log_error(e, context={'test': 'context'})
        
        print(f"✅ Error logging tested")
        
        # Get statistics
        perf_summary = logger.get_performance_summary()
        error_summary = logger.get_error_summary()
        
        print(f"\n📊 Statistics:")
        print(f"   Operations tracked: {perf_summary.get('test_operation', {}).get('total_operations', 0)}")
        print(f"   Errors logged: {error_summary['total_errors']}")
        
        # Cleanup - Close all handlers first to release file locks
        import logging
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        
        # Wait a moment for Windows to release file handles
        import time
        time.sleep(0.1)
        
        # Cleanup
        import shutil
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                print("⚠️  Note: Log files left in temp directory (Windows file lock)")
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ Logging test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_csv_reporting():
    """Test CSV report generation."""
    print("\n" + "=" * 60)
    print("Test 2: CSV Reporting")
    print("=" * 60)
    
    try:
        # Create temporary reports directory
        temp_dir = Path(tempfile.gettempdir()) / "test_reports"
        
        # Create CSV reporter
        reporter = CSVReporter(reports_dir=str(temp_dir))
        
        print(f"✅ CSV reporter initialized")
        print(f"   Reports directory: {temp_dir}")
        
        # Test campaign results export
        test_results = [
            {
                'timestamp': '2025-10-16T14:30:00',
                'business_name': 'Test Business 1',
                'phone': '+1234567890',
                'message_type': 'creation',
                'status': 'success',
                'error': '',
                'message_preview': 'Hello, this is a test message...',
            },
            {
                'timestamp': '2025-10-16T14:31:00',
                'business_name': 'Test Business 2',
                'phone': '+1234567891',
                'message_type': 'enhancement',
                'status': 'failed',
                'error': 'Network error',
                'message_preview': 'Hello, I saw your website...',
            },
        ]
        
        results_file = reporter.export_campaign_results(test_results)
        print(f"✅ Campaign results exported: {Path(results_file).name}")
        
        # Test campaign summary export
        campaign_data = {
            'campaign_info': {
                'excel_file': 'data/test.xlsx',
                'dry_run': False,
                'start_time': '2025-10-16T14:00:00',
                'end_time': '2025-10-16T14:30:00',
            },
            'summary': {
                'total_businesses': 10,
                'processed': 10,
                'sent': 8,
                'failed': 2,
                'skipped': 0,
            },
            'rate_limiting': {
                'total_sent': 8,
                'sent_today': 8,
                'sent_this_hour': 8,
                'daily_limit': 50,
                'hourly_limit': 15,
            },
        }
        
        summary_file = reporter.export_campaign_summary(campaign_data)
        print(f"✅ Campaign summary exported: {Path(summary_file).name}")
        
        # Verify files exist
        assert Path(results_file).exists(), "Results file not created"
        assert Path(summary_file).exists(), "Summary file not created"
        
        print(f"\n✅ All CSV files generated successfully")
        
        # Cleanup
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ CSV reporting test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_analytics_tracking():
    """Test analytics tracking."""
    print("\n" + "=" * 60)
    print("Test 3: Analytics Tracking")
    print("=" * 60)
    
    try:
        # Create temporary analytics directory
        temp_dir = Path(tempfile.gettempdir()) / "test_analytics"
        
        # Create analytics tracker
        tracker = AnalyticsTracker(analytics_dir=str(temp_dir))
        
        print(f"✅ Analytics tracker initialized")
        
        # Start campaign
        tracker.start_campaign(total_businesses=5)
        
        # Track some messages
        tracker.track_message_sent(
            business_name="Business 1",
            phone="+1234567890",
            message_type="creation",
            has_website=False,
            duration=2.5,
            retry_count=0
        )
        
        tracker.track_message_sent(
            business_name="Business 2",
            phone="+1234567891",
            message_type="enhancement",
            has_website=True,
            duration=3.0,
            retry_count=1
        )
        
        tracker.track_message_failed(
            business_name="Business 3",
            phone="+1234567892",
            message_type="creation",
            has_website=False,
            error="Network timeout",
            duration=1.0,
            retry_count=3
        )
        
        tracker.track_message_skipped(
            business_name="Business 4",
            phone="+1234567893",
            reason="Rate limit reached"
        )
        
        tracker.track_rate_limit_hit()
        tracker.track_batch_delay()
        
        print(f"✅ Messages tracked")
        
        # End campaign
        tracker.end_campaign()
        
        # Get metrics
        metrics = tracker.get_current_metrics()
        
        print(f"\n📊 Campaign Metrics:")
        print(f"   Total: {metrics['total_businesses']}")
        print(f"   Sent: {metrics['messages_sent']}")
        print(f"   Failed: {metrics['messages_failed']}")
        print(f"   Skipped: {metrics['messages_skipped']}")
        print(f"   Success Rate: {metrics['success_rate']}")
        
        # Get message distribution
        distribution = tracker.get_message_type_distribution()
        print(f"\n📝 Message Distribution:")
        print(f"   Creation: {distribution['creation']} ({distribution['creation_percentage']:.1f}%)")
        print(f"   Enhancement: {distribution['enhancement']} ({distribution['enhancement_percentage']:.1f}%)")
        
        # Export analytics
        analytics_file = tracker.export_analytics()
        print(f"\n✅ Analytics exported: {Path(analytics_file).name}")
        
        # Verify file exists
        assert Path(analytics_file).exists(), "Analytics file not created"
        
        # Cleanup
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics tracking test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_campaign():
    """Test integration with campaign manager."""
    print("\n" + "=" * 60)
    print("Test 4: Campaign Manager Integration")
    print("=" * 60)
    
    try:
        from src.core.campaign_manager import CampaignManager
        from src.core.delay_manager import create_test_delay_manager
        
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
        print(f"   CSV Reporter: {campaign.csv_reporter is not None}")
        print(f"   Analytics Tracker: {campaign.analytics_tracker is not None}")
        
        # Run campaign
        print(f"\n📨 Running campaign...")
        success = campaign.run_campaign(headless=True)
        
        if success:
            print(f"\n✅ Campaign completed successfully")
            
            # Verify reports were generated
            reports_dir = Path("data/reports")
            analytics_dir = Path("data/analytics")
            
            if reports_dir.exists():
                csv_files = list(reports_dir.glob("*.csv"))
                print(f"\n📄 CSV Reports generated: {len(csv_files)}")
                for file in csv_files[:3]:  # Show first 3
                    print(f"   - {file.name}")
            
            if analytics_dir.exists():
                json_files = list(analytics_dir.glob("*.json"))
                print(f"\n📊 Analytics files generated: {len(json_files)}")
                for file in json_files[:3]:  # Show first 3
                    print(f"   - {file.name}")
            
            return True
        else:
            print(f"\n❌ Campaign failed")
            return False
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 6 tests."""
    print("\n" + "=" * 60)
    print("PHASE 6 INTEGRATION TEST SUITE")
    print("Logging, CSV Reporting & Analytics")
    print("=" * 60)
    
    tests = [
        ("Enhanced Logging", test_enhanced_logging),
        ("CSV Reporting", test_csv_reporting),
        ("Analytics Tracking", test_analytics_tracking),
        ("Campaign Integration", test_integration_with_campaign),
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
        print("✅ ALL PHASE 6 TESTS PASSED!")
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
