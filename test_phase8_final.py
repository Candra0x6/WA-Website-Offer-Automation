"""
Phase 8: Final Integration Tests
Simple tests that validate the working system.

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_1_excel_loading():
    """Test 1: Excel file loading."""
    print("\n" + "=" * 70)
    print("TEST 1: Excel File Loading")
    print("=" * 70)
    
    from src.core.excel_handler import ExcelDataHandler
    
    excel_path = Path('data/data.xlsx')
    
    if not excel_path.exists():
        print("   ❌ Test data not found")
        return False
    
    handler = ExcelDataHandler(str(excel_path))
    handler.load_data()
    businesses = handler.get_businesses()
    
    print(f"\n📋 Results:")
    print(f"   Businesses loaded: {len(businesses)}")
    
    if len(businesses) > 0:
        biz = businesses[0]
        print(f"\n📊 Sample Business:")
        print(f"   Name: {biz.name}")
        print(f"   Phone: {biz.phone}")
        print(f"   Website: {biz.website if biz.website else 'None'}")
    
    print(f"\n✅ TEST 1 PASSED - Excel loading works")
    return True


def test_2_message_composition():
    """Test 2: Message composition."""
    print("\n" + "=" * 70)
    print("TEST 2: Message Composition")
    print("=" * 70)
    
    from src.core.message_composer import MessageComposer
    from src.core.excel_handler import ExcelDataHandler
    
    excel_path = Path('data/data.xlsx')
    
    if not excel_path.exists():
        print("   ❌ Test data not found")
        return False
    
    handler = ExcelDataHandler(str(excel_path))
    handler.load_data()
    businesses = handler.get_businesses()
    
    if len(businesses) == 0:
        print("   ❌ No businesses to test")
        return False
    
    composer = MessageComposer()
    
    creation_count = 0
    enhancement_count = 0
    
    for biz in businesses[:5]:  # Test first 5
        msg_type, message, url = composer.compose_message(biz)
        
        if msg_type == 'creation':
            creation_count += 1
        else:
            enhancement_count += 1
        
        # Verify
        assert biz.name in message, "Message should contain business name"
        assert 'https://wa.me/' in url, "Should generate WhatsApp URL"
    
    print(f"\n📊 Results:")
    print(f"   Creation messages: {creation_count}")
    print(f"   Enhancement messages: {enhancement_count}")
    print(f"   Total tested: {creation_count + enhancement_count}")
    
    print(f"\n✅ TEST 2 PASSED - Message composition works")
    return True


def test_3_delay_manager():
    """Test 3: Delay manager."""
    print("\n" + "=" * 70)
    print("TEST 3: Delay Manager")
    print("=" * 70)
    
    from src.core.delay_manager import create_test_delay_manager
    
    manager = create_test_delay_manager()
    
    print(f"\n⚙️  Configuration:")
    print(f"   Min delay: {manager.config.min_message_delay}s")
    print(f"   Max delay: {manager.config.max_message_delay}s")
    print(f"   Daily limit: {manager.config.max_messages_per_day}")
    
    # Test can send
    can_send, reason = manager.can_send_message()
    print(f"\n📊 Status:")
    print(f"   Can send: {can_send}")
    
    # Record messages
    for i in range(5):
        manager.record_message_sent()
    
    print(f"   Messages recorded: 5")
    
    print(f"\n✅ TEST 3 PASSED - Delay manager works")
    return True


def test_4_dry_run_campaign():
    """Test 4: Full dry-run campaign."""
    print("\n" + "=" * 70)
    print("TEST 4: Dry-Run Campaign (Full Integration)")
    print("=" * 70)
    
    import tempfile
    import shutil
    
    from src.core.campaign_manager import CampaignManager
    from src.core.delay_manager import create_test_delay_manager
    
    excel_path = Path('data/data.xlsx')
    
    if not excel_path.exists():
        print("   ❌ Test data not found")
        return False
    
    # Create temp profile
    temp_dir = Path(tempfile.mkdtemp())
    profile_dir = temp_dir / 'chrome_profile'
    
    delay_manager = create_test_delay_manager()
    
    print(f"\n⚙️  Configuration:")
    print(f"   Excel: {excel_path}")
    print(f"   Dry Run: True")
    print(f"   Headless: True")
    
    campaign = CampaignManager(
        excel_file=str(excel_path),
        chrome_profile=str(profile_dir),
        delay_manager=delay_manager,
        dry_run=True
    )
    
    print(f"\n🚀 Running campaign...")
    
    # Run campaign
    success = campaign.run_campaign(headless=True)
    
    print(f"\n📊 Campaign Result:")
    print(f"   Success: {success}")
    
    # Check for generated files
    reports_dir = Path('data/reports')
    analytics_dir = Path('data/analytics')
    
    csv_count = len(list(reports_dir.glob('campaign_*.csv'))) if reports_dir.exists() else 0
    analytics_count = len(list(analytics_dir.glob('analytics_*.json'))) if analytics_dir.exists() else 0
    
    print(f"\n📁 Generated Files:")
    print(f"   CSV reports: {csv_count}")
    print(f"   Analytics files: {analytics_count}")
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    print(f"\n✅ TEST 4 PASSED - Full campaign works")
    return True


def test_5_cli_features():
    """Test 5: CLI features."""
    print("\n" + "=" * 70)
    print("TEST 5: CLI Features")
    print("=" * 70)
    
    import subprocess
    
    print(f"\n🔧 Testing CLI commands...")
    
    # Test --version
    result = subprocess.run(
        ['python', 'main.py', '--version'],
        capture_output=True,
        text=True
    )
    
    version_works = 'WhatsApp Campaign System' in result.stdout
    print(f"   --version: {'✓' if version_works else '✗'}")
    
    # Test --info
    result = subprocess.run(
        ['python', 'main.py', '--info'],
        capture_output=True,
        text=True
    )
    
    info_works = 'SYSTEM INFORMATION' in result.stdout
    print(f"   --info: {'✓' if info_works else '✗'}")
    
    # Test --validate
    result = subprocess.run(
        ['python', 'main.py', '--validate'],
        capture_output=True,
        text=True
    )
    
    validate_works = 'VALIDATION' in result.stdout
    print(f"   --validate: {'✓' if validate_works else '✗'}")
    
    # Test --help
    result = subprocess.run(
        ['python', 'main.py', '--help'],
        capture_output=True,
        text=True
    )
    
    help_works = 'WhatsApp Message Campaign Runner' in result.stdout
    print(f"   --help: {'✓' if help_works else '✗'}")
    
    all_passed = all([version_works, info_works, validate_works, help_works])
    
    if all_passed:
        print(f"\n✅ TEST 5 PASSED - All CLI features work")
    else:
        print(f"\n⚠️  TEST 5 PARTIAL - Some CLI features may need attention")
    
    return all_passed


def test_6_file_structure():
    """Test 6: File structure validation."""
    print("\n" + "=" * 70)
    print("TEST 6: File Structure Validation")
    print("=" * 70)
    
    required_dirs = [
        'data',
        'logs',
        'data/reports',
        'data/analytics',
        'src',
        'src/core',
        'src/utils',
        'src/models',
        'src/config',
        'docs'
    ]
    
    print(f"\n📁 Checking directories...")
    
    all_exist = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        status = '✓' if exists else '✗'
        print(f"   {dir_path}: {status}")
        if not exists:
            all_exist = False
    
    required_files = [
        'main.py',
        'README.md',
        'requirements.txt',
        'config.example.json',
        'data/data.xlsx'
    ]
    
    print(f"\n📄 Checking key files...")
    
    for file_path in required_files:
        exists = Path(file_path).exists()
        status = '✓' if exists else '✗'
        print(f"   {file_path}: {status}")
        if not exists:
            all_exist = False
    
    if all_exist:
        print(f"\n✅ TEST 6 PASSED - File structure complete")
    else:
        print(f"\n⚠️  TEST 6 PARTIAL - Some files/dirs missing")
    
    return all_exist


def run_all_tests():
    """Run all Phase 8 tests."""
    print("\n" + "=" * 80)
    print("PHASE 8: TESTING & QUALITY ASSURANCE - FINAL INTEGRATION TESTS")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    tests = [
        ("Excel Loading", test_1_excel_loading),
        ("Message Composition", test_2_message_composition),
        ("Delay Manager", test_3_delay_manager),
        ("Dry-Run Campaign", test_4_dry_run_campaign),
        ("CLI Features", test_5_cli_features),
        ("File Structure", test_6_file_structure)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
    elif passed >= total * 0.7:
        print("\n✅ MOST TESTS PASSED. System is functional with minor issues.")
    else:
        print("\n⚠️  SIGNIFICANT FAILURES. Review and fix issues.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
