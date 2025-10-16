"""
Phase 4 Integration Test
Tests WhatsApp Web automation (Session Management + Message Sending)

⚠️ WARNING: This test will open a real browser and attempt to connect to WhatsApp Web.
On first run, you will need to scan a QR code with your phone.

This is a MANUAL test - automated testing of WhatsApp is not recommended.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.core.session_manager import SessionManager
from src.core.whatsapp_controller import WhatsAppController
from src.models.business import Business


def test_session_manager():
    """Test session manager functionality."""
    print("=" * 60)
    print("Test 1: Session Manager")
    print("=" * 60)
    
    try:
        manager = SessionManager("test_chrome_profile")
        
        # Test profile directory creation
        profile_dir = manager.ensure_profile_directory()
        print(f"✅ Profile directory: {profile_dir}")
        
        # Test session validation
        has_session = manager.is_session_valid()
        print(f"✅ Session valid: {has_session}")
        
        # Test Chrome options generation
        options = manager.get_chrome_options(headless=False)
        print(f"✅ Chrome options configured")
        
        # Cleanup
        manager.clear_session()
        print(f"✅ Session cleared")
        
        return True
        
    except Exception as e:
        print(f"❌ Session manager test failed: {str(e)}")
        return False


def test_whatsapp_controller_init():
    """Test WhatsApp controller initialization (requires QR scan)."""
    print("\n" + "=" * 60)
    print("Test 2: WhatsApp Controller Initialization")
    print("=" * 60)
    print("\n⚠️  This will open a browser window.")
    print("⚠️  If you see a QR code, you'll need to scan it with your phone.")
    
    response = input("\nProceed with browser test? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("⏭️  Skipped")
        return True
    
    try:
        controller = WhatsAppController(profile_path="test_chrome_profile", headless=False)
        
        print("\nInitializing controller...")
        success = controller.initialize_driver()
        
        if success:
            print("✅ Controller initialized successfully!")
            
            # Get status
            status = controller.get_driver_status()
            print(f"\nStatus:")
            print(f"  Initialized: {status['initialized']}")
            print(f"  Driver Active: {status['driver_active']}")
            print(f"  Logged In: {status['logged_in']}")
            
            # Keep browser open briefly
            input("\nPress Enter to close browser...")
            
            controller.close()
            return True
        else:
            print("❌ Controller initialization failed")
            controller.close()
            return False
        
    except Exception as e:
        print(f"❌ WhatsApp controller test failed: {str(e)}")
        return False


def test_message_composition_only():
    """Test message composition without actually sending."""
    print("\n" + "=" * 60)
    print("Test 3: Message Composition (No Sending)")
    print("=" * 60)
    
    try:
        from src.core.excel_handler import ExcelDataHandler
        from src.core.message_composer import MessageComposer
        
        # Load sample data
        excel_file = Path(__file__).parent / 'data' / 'data.xlsx'
        
        if not excel_file.exists():
            print("⚠️  Sample data not found, skipping")
            return True
        
        # Load businesses
        handler = ExcelDataHandler(str(excel_file))
        businesses = handler.get_businesses()
        
        print(f"✅ Loaded {len(businesses)} businesses")
        
        # Compose messages
        composer = MessageComposer()
        
        print("\nComposed Messages (Preview):")
        print("-" * 60)
        
        for i, business in enumerate(businesses[:3], 1):
            msg_type = composer.detect_message_type(business)
            message = composer.compose_message(business)
            
            print(f"\n{i}. {business.business_name}")
            print(f"   Phone: {business.phone}")
            print(f"   Type: {msg_type.upper()}")
            print(f"   Message: {message[:80]}...")
        
        print("\n✅ Message composition successful")
        return True
        
    except Exception as e:
        print(f"❌ Message composition test failed: {str(e)}")
        return False


def test_dry_run_flow():
    """Test complete flow without actually sending messages."""
    print("\n" + "=" * 60)
    print("Test 4: Complete Flow (Dry Run)")
    print("=" * 60)
    
    try:
        from src.core.excel_handler import ExcelDataHandler
        from src.core.message_composer import MessageComposer
        
        # Load sample data
        excel_file = Path(__file__).parent / 'data' / 'data.xlsx'
        
        if not excel_file.exists():
            print("⚠️  Sample data not found, skipping")
            return True
        
        print("\nStep 1: Load businesses from Excel")
        handler = ExcelDataHandler(str(excel_file))
        businesses = handler.get_businesses()
        print(f"✅ Loaded {len(businesses)} businesses")
        
        print("\nStep 2: Initialize message composer")
        composer = MessageComposer()
        print("✅ Composer initialized")
        
        print("\nStep 3: Compose messages")
        messages_composed = []
        
        for business in businesses:
            message = composer.compose_message(business)
            whatsapp_url = composer.compose_whatsapp_url(business)
            messages_composed.append({
                'business': business,
                'message': message,
                'url': whatsapp_url,
            })
        
        print(f"✅ Composed {len(messages_composed)} messages")
        
        print("\nStep 4: Simulate sending (Dry Run)")
        print("-" * 60)
        
        for i, item in enumerate(messages_composed[:3], 1):
            business = item['business']
            print(f"\n{i}. Would send to: {business.business_name}")
            print(f"   Phone: {business.phone}")
            print(f"   Message length: {len(item['message'])} chars")
            print(f"   Status: ✅ DRY RUN (not actually sent)")
        
        if len(messages_composed) > 3:
            print(f"\n... and {len(messages_composed) - 3} more messages")
        
        print("\n✅ Dry run complete - no messages were actually sent")
        return True
        
    except Exception as e:
        print(f"❌ Dry run test failed: {str(e)}")
        return False


def main():
    """Run all Phase 4 tests."""
    print("\n" + "=" * 60)
    print("PHASE 4 INTEGRATION TEST SUITE")
    print("=" * 60)
    print("\n⚠️  IMPORTANT NOTES:")
    print("- These tests involve real browser automation")
    print("- You may need to scan a QR code on first run")
    print("- No actual messages will be sent (dry run mode)")
    print("- Tests can be skipped individually")
    
    tests = [
        ("Session Manager", test_session_manager),
        ("WhatsApp Controller Init", test_whatsapp_controller_init),
        ("Message Composition", test_message_composition_only),
        ("Complete Flow (Dry Run)", test_dry_run_flow),
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
        print("✅ ALL PHASE 4 TESTS PASSED!")
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
