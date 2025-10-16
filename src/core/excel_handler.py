"""
Excel Data Handler
Loads and processes business data from Excel files.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import pandas as pd
from ..models.business import Business
from ..utils.validators import Validators


class ExcelDataHandler:
    """Handles loading and processing Excel data."""
    
    # Required columns
    REQUIRED_COLUMNS = ['Business Name', 'Phone']
    
    # Optional columns
    OPTIONAL_COLUMNS = ['Description', 'Website', 'Google Maps Link']
    
    # All expected columns
    ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
    
    def __init__(self, file_path: str):
        """
        Initialize Excel data handler.
        
        Args:
            file_path: Path to the Excel file
            
        Raises:
            FileNotFoundError: If Excel file doesn't exist
        """
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")
        
        if not self.file_path.suffix in ['.xlsx', '.xls']:
            raise ValueError(f"File must be Excel format (.xlsx or .xls): {self.file_path}")
        
        self.df: Optional[pd.DataFrame] = None
        self.businesses: List[Business] = []
        self.errors: List[Dict[str, Any]] = []
        self.skipped_count: int = 0
    
    def load_data(self) -> pd.DataFrame:
        """
        Load Excel data into a pandas DataFrame.
        
        Returns:
            pd.DataFrame: Loaded data
            
        Raises:
            Exception: If file cannot be loaded
        """
        try:
            self.df = pd.read_excel(self.file_path)
            return self.df
        except Exception as e:
            raise Exception(f"Failed to load Excel file: {str(e)}")
    
    def validate_columns(self, df: Optional[pd.DataFrame] = None) -> bool:
        """
        Validate that required columns exist in the DataFrame.
        
        Args:
            df: DataFrame to validate (uses self.df if None)
            
        Returns:
            bool: True if all required columns exist
            
        Raises:
            ValueError: If required columns are missing
        """
        if df is None:
            df = self.df
        
        if df is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        # Check for required columns
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        return True
    
    def _clean_string_value(self, value: Any) -> Optional[str]:
        """
        Clean and convert value to string, handling NaN and None.
        
        Args:
            value: Value to clean
            
        Returns:
            str or None: Cleaned string or None if empty
        """
        if pd.isna(value):
            return None
        
        if value is None:
            return None
        
        # Convert to string and strip whitespace
        str_value = str(value).strip()
        
        # Return None if empty after stripping
        if not str_value or str_value.lower() in ['nan', 'none', '']:
            return None
        
        return str_value
    
    def _parse_business_row(self, row: pd.Series, row_index: int) -> Optional[Business]:
        """
        Parse a single row into a Business object.
        
        Args:
            row: DataFrame row
            row_index: Row index for error reporting
            
        Returns:
            Business object or None if row should be skipped
        """
        # Extract and clean required fields
        business_name = self._clean_string_value(row.get('Business Name'))
        phone = self._clean_string_value(row.get('Phone'))
        
        # Skip if required fields are missing
        if not business_name:
            self.errors.append({
                'row': row_index + 2,  # +2 for 1-indexed and header
                'error': 'Missing Business Name',
                'severity': 'skip'
            })
            self.skipped_count += 1
            return None
        
        if not phone:
            self.errors.append({
                'row': row_index + 2,
                'business_name': business_name,
                'error': 'Missing Phone number',
                'severity': 'skip'
            })
            self.skipped_count += 1
            return None
        
        # Validate and format phone number
        is_valid_phone, formatted_phone = Validators.validate_phone(phone)
        if not is_valid_phone:
            self.errors.append({
                'row': row_index + 2,
                'business_name': business_name,
                'phone': phone,
                'error': f'Invalid phone number: {formatted_phone}',
                'severity': 'skip'
            })
            self.skipped_count += 1
            return None
        
        # Sanitize business name
        business_name = Validators.sanitize_business_name(business_name)
        
        # Extract optional fields
        description = self._clean_string_value(row.get('Description'))
        website = self._clean_string_value(row.get('Website'))
        google_maps_link = self._clean_string_value(row.get('Google Maps Link'))
        
        # Validate website URL if provided
        if website:
            if not Validators.validate_url(website):
                self.errors.append({
                    'row': row_index + 2,
                    'business_name': business_name,
                    'error': f'Invalid website URL: {website} (treating as no website)',
                    'severity': 'warning'
                })
                website = None  # Treat as no website
        
        # Create Business object
        return Business(
            business_name=business_name,
            phone=formatted_phone,
            description=description,
            website=website,
            google_maps_link=google_maps_link
        )
    
    def get_businesses(self) -> List[Business]:
        """
        Get list of Business objects from Excel data.
        
        Returns:
            List[Business]: List of valid Business objects
            
        Raises:
            ValueError: If data not loaded or columns invalid
        """
        # Load data if not already loaded
        if self.df is None:
            self.load_data()
        
        # Validate columns
        self.validate_columns()
        
        # Clear previous results
        self.businesses = []
        self.errors = []
        self.skipped_count = 0
        
        # Parse each row
        for index, row in self.df.iterrows():
            business = self._parse_business_row(row, index)
            if business:
                self.businesses.append(business)
        
        return self.businesses
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get validation summary for reporting.
        
        Returns:
            Dict with validation summary
        """
        total_rows = len(self.df) if self.df is not None else 0
        valid_rows = len(self.businesses)
        invalid_rows = total_rows - valid_rows
        
        return {
            'total_rows': total_rows,
            'valid_rows': valid_rows,
            'invalid_rows': invalid_rows,
            'success_rate': (valid_rows / total_rows * 100) if total_rows > 0 else 0,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded data.
        
        Returns:
            Dict with statistics
        """
        total_rows = len(self.df) if self.df is not None else 0
        
        return {
            'total_rows': total_rows,
            'valid_businesses': len(self.businesses),
            'skipped': self.skipped_count,
            'errors': len(self.errors),
            'success_rate': (len(self.businesses) / total_rows * 100) if total_rows > 0 else 0,
            'businesses_with_website': sum(1 for b in self.businesses if b.has_website()),
            'businesses_without_website': sum(1 for b in self.businesses if not b.has_website())
        }
    
    def print_stats(self):
        """Print statistics in a formatted way."""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print("Excel Data Processing Statistics")
        print("=" * 60)
        print(f"Total rows:                {stats['total_rows']}")
        print(f"Valid businesses:          {stats['valid_businesses']}")
        print(f"Skipped:                   {stats['skipped']}")
        print(f"Errors:                    {stats['errors']}")
        print(f"Success rate:              {stats['success_rate']:.1f}%")
        print(f"\nBusinesses with website:   {stats['businesses_with_website']}")
        print(f"Businesses without website: {stats['businesses_without_website']}")
        print("=" * 60)
    
    def print_errors(self, severity: Optional[str] = None):
        """
        Print errors encountered during processing.
        
        Args:
            severity: Filter by severity ('skip', 'warning', or None for all)
        """
        if not self.errors:
            print("\n✅ No errors!")
            return
        
        filtered_errors = self.errors
        if severity:
            filtered_errors = [e for e in self.errors if e.get('severity') == severity]
        
        if not filtered_errors:
            print(f"\n✅ No {severity} errors!")
            return
        
        print(f"\n⚠️  Errors ({len(filtered_errors)}):")
        print("-" * 60)
        
        for error in filtered_errors:
            row_num = error.get('row', 'Unknown')
            business = error.get('business_name', 'Unknown')
            message = error.get('error', 'Unknown error')
            severity_icon = "⏭️" if error.get('severity') == 'skip' else "⚠️"
            
            print(f"{severity_icon} Row {row_num}: {business} - {message}")
        
        print("-" * 60)


def load_businesses_from_excel(file_path: str) -> List[Business]:
    """
    Convenience function to load businesses from Excel file.
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        List[Business]: List of valid businesses
    """
    handler = ExcelDataHandler(file_path)
    businesses = handler.get_businesses()
    handler.print_stats()
    handler.print_errors()
    return businesses


if __name__ == "__main__":
    # Test the Excel handler
    print("=" * 60)
    print("Testing Excel Data Handler")
    print("=" * 60)
    
    # Try to load sample data
    sample_file = Path(__file__).parent.parent.parent / 'data' / 'data.xlsx'
    
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
    else:
        print(f"⚠️  Sample file not found: {sample_file}")
        print("   Create data/data.xlsx to test the handler")
    
    print("=" * 60)
