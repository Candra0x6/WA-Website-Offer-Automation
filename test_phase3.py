"""
Phase 3 Integration Test
Tests the complete flow: Excel -> Businesses -> Composed Messages
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.core.excel_handler import ExcelDataHandler
from src.core.message_composer import MessageComposer
from src.models.business import Business


def test_complete_flow():
    """Test complete flow from Excel to composed messages."""
    print("=" * 60)
    print("Phase 3 Integration Test")
    print("Testing: Excel → Businesses → Composed Messages")
    print("=" * 60)
    
    # Step 1: Load businesses from Excel
    print("\n### Step 1: Loading businesses from Excel ###")
    excel_file = Path(__file__).parent / 'data' / 'data.xlsx'
    
    if not excel_file.exists():
        print(f"❌ Excel file not found: {excel_file}")
        return False
    
    handler = ExcelDataHandler(str(excel_file))
    businesses = handler.get_businesses()
    
    print(f"✅ Loaded {len(businesses)} valid businesses")
    handler.print_stats()
    
    # Step 2: Initialize message composer
    print("\n### Step 2: Initialize Message Composer ###")
    composer = MessageComposer()
    print("✅ Message composer initialized")
    
    # Step 3: Compose messages for each business
    print("\n### Step 3: Composing Messages ###")
    print("-" * 60)
    
    creation_count = 0
    enhancement_count = 0
    
    for i, business in enumerate(businesses[:5], 1):  # Show first 5
        print(f"\n{i}. {business.business_name}")
        print(f"   Phone: {business.phone}")
        
        # Detect message type
        msg_type = composer.detect_message_type(business)
        if msg_type == 'creation':
            creation_count += 1
        else:
            enhancement_count += 1
        
        print(f"   Type: {msg_type.upper()}")
        
        if business.website:
            print(f"   Website: {business.website}")
        
        # Compose message
        message = composer.compose_message(business)
        print(f"\n   Message Preview:")
        print(f"   \"{message[:100]}...\"")
        
        # Get stats
        stats = composer.get_message_stats(business)
        print(f"\n   Stats: {stats['length']} chars, {stats['word_count']} words")
        
        # WhatsApp URL
        url = composer.compose_whatsapp_url(business)
        print(f"   WhatsApp URL: {url[:80]}...")
    
    if len(businesses) > 5:
        print(f"\n... and {len(businesses) - 5} more businesses")
    
    # Count all message types
    print("\n### Summary ###")
    print("-" * 60)
    for business in businesses[5:]:
        msg_type = composer.detect_message_type(business)
        if msg_type == 'creation':
            creation_count += 1
        else:
            enhancement_count += 1
    
    print(f"Total businesses: {len(businesses)}")
    print(f"Creation messages: {creation_count}")
    print(f"Enhancement messages: {enhancement_count}")
    
    return True


def test_message_personalization():
    """Test that messages are properly personalized."""
    print("\n" + "=" * 60)
    print("Testing Message Personalization")
    print("=" * 60)
    
    composer = MessageComposer()
    
    # Test with business without website
    business1 = Business(
        business_name="Test Coffee Shop",
        phone="+12025551001",
        description="Great coffee"
    )
    
    message1 = composer.compose_message(business1)
    print(f"\n1. Creation Message:")
    print(f"   Business: {business1.business_name}")
    print(f"   Message: {message1}")
    
    assert "Test Coffee Shop" in message1, "Business name not in message"
    assert "{business_name}" not in message1, "Placeholder not replaced"
    print("   ✅ Personalization successful")
    
    # Test with business with website
    business2 = Business(
        business_name="Test Tech Co",
        phone="+12025551002",
        website="https://testtech.com"
    )
    
    message2 = composer.compose_message(business2)
    print(f"\n2. Enhancement Message:")
    print(f"   Business: {business2.business_name}")
    print(f"   Website: {business2.website}")
    print(f"   Message: {message2}")
    
    assert "Test Tech Co" in message2, "Business name not in message"
    assert "{business_name}" not in message2, "Placeholder not replaced"
    print("   ✅ Personalization successful")
    
    return True


def test_url_encoding():
    """Test URL encoding for WhatsApp."""
    print("\n" + "=" * 60)
    print("Testing URL Encoding")
    print("=" * 60)
    
    composer = MessageComposer()
    
    business = Business(
        business_name="Test Business",
        phone="+12025551001"
    )
    
    # Test without encoding
    message_plain = composer.compose_message(business, url_encode=False)
    print(f"\nPlain Message:")
    print(f"  {message_plain[:80]}...")
    
    # Test with encoding
    message_encoded = composer.compose_message(business, url_encode=True)
    print(f"\nURL-Encoded Message:")
    print(f"  {message_encoded[:80]}...")
    
    # Verify encoding
    assert ' ' not in message_encoded, "Spaces should be encoded"
    assert '%20' in message_encoded or '%' in message_encoded, "Should contain URL encoding"
    print("\n✅ URL encoding successful")
    
    # Test complete WhatsApp URL
    whatsapp_url = composer.compose_whatsapp_url(business)
    print(f"\nComplete WhatsApp URL:")
    print(f"  {whatsapp_url[:100]}...")
    
    assert whatsapp_url.startswith('https://web.whatsapp.com/send?'), "Invalid WhatsApp URL"
    assert 'phone=' in whatsapp_url, "Phone parameter missing"
    assert 'text=' in whatsapp_url, "Text parameter missing"
    print("✅ WhatsApp URL generation successful")
    
    return True


def main():
    """Run all Phase 3 tests."""
    print("\n" + "=" * 60)
    print("PHASE 3 INTEGRATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Complete Flow", test_complete_flow),
        ("Message Personalization", test_message_personalization),
        ("URL Encoding", test_url_encoding),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
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
        print("✅ ALL PHASE 3 TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
