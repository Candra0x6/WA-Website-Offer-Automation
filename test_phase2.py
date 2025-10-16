"""
Test script for Phase 2 modules
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.excel_handler import ExcelDataHandler
from src.utils.validators import Validators

def test_validators():
    """Test the validators module."""
    print("\n" + "=" * 60)
    print("Testing Validators Module")
    print("=" * 60)
    
    # Test phone validation
    print("\n### Phone Number Validation ###")
    test_phones = [
        ("+12025551001", "US"),
        ("12025551002", "US"),
        ("+6281234567890", "ID"),
        ("invalid", "US"),
    ]
    
    for phone, region in test_phones:
        is_valid, result = Validators.validate_phone(phone, region)
        status = "✅" if is_valid else "❌"
        print(f"{status} {phone:20} -> {result}")
    
    # Test URL validation
    print("\n### URL Validation ###")
    test_urls = [
        "https://example.com",
        "http://test.com/page",
        "not a url",
        "",
    ]
    
    for url in test_urls:
        is_valid = Validators.validate_url(url)
        status = "✅" if is_valid else "❌"
        print(f"{status} {url}")
    
    print("\n✅ Validators test completed!")


def test_excel_handler():
    """Test the Excel handler module."""
    print("\n" + "=" * 60)
    print("Testing Excel Data Handler")
    print("=" * 60)
    
    # Try to load sample data
    sample_file = project_root / 'data' / 'data.xlsx'
    
    if sample_file.exists():
        try:
            handler = ExcelDataHandler(str(sample_file))
            businesses = handler.get_businesses()
            
            handler.print_stats()
            handler.print_errors()
            
            # Display first few businesses
            print("\n📋 Sample Businesses:")
            print("-" * 60)
            for i, business in enumerate(businesses[:5], 1):
                website_status = "✅ Has website" if business.has_website() else "❌ No website"
                print(f"{i}. {business.business_name}")
                print(f"   Phone: {business.phone}")
                print(f"   {website_status}")
                if business.website:
                    print(f"   Website: {business.website}")
                print()
            
            if len(businesses) > 5:
                print(f"... and {len(businesses) - 5} more businesses")
            
            print("-" * 60)
            print("✅ Excel handler test completed!")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"⚠️  Sample file not found: {sample_file}")
        print("   Run: python data/create_sample_data.py")
    

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Phase 2 Module Testing")
    print("=" * 60)
    
    test_validators()
    test_excel_handler()
    
    print("\n" + "=" * 60)
    print("✅ All Phase 2 tests completed!")
    print("=" * 60 + "\n")
