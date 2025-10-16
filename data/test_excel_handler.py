"""
Test script for Excel handler
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.excel_handler import ExcelDataHandler

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Excel Data Handler")
    print("=" * 60)
    
    # Try to load sample data
    sample_file = Path(__file__).parent / 'data.xlsx'
    
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
        print("   Run create_sample_data.py first")
    
    print("=" * 60)
