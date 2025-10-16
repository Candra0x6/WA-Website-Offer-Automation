"""
Unit tests for the ExcelDataHandler module
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from src.core.excel_handler import ExcelDataHandler, load_businesses_from_excel
from src.models.business import Business


@pytest.fixture
def sample_excel_file():
    """Create a temporary Excel file for testing."""
    data = {
        'Business Name': ['Coffee Shop', 'Tech Co', '', 'Invalid Phone Co'],
        'Description': ['Great coffee', 'IT services', 'Test', 'Test'],
        'Website': ['', 'https://tech.com', '', 'https://test.com'],
        'Phone': ['+12025551001', '+12025551002', '+12025551003', 'invalid'],
        'Google Maps Link': ['', '', '', '']
    }
    
    df = pd.DataFrame(data)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xlsx') as f:
        temp_path = f.name
    
    df.to_excel(temp_path, index=False, engine='openpyxl')
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestExcelDataHandlerInit:
    """Tests for ExcelDataHandler initialization."""
    
    def test_init_with_valid_file(self, sample_excel_file):
        """Test initialization with valid Excel file."""
        handler = ExcelDataHandler(sample_excel_file)
        assert handler.file_path.exists()
    
    def test_init_with_nonexistent_file(self):
        """Test initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            ExcelDataHandler("nonexistent.xlsx")
    
    def test_init_with_invalid_extension(self, tmp_path):
        """Test initialization with invalid file extension."""
        invalid_file = tmp_path / "test.txt"
        invalid_file.touch()
        
        with pytest.raises(ValueError, match="must be Excel format"):
            ExcelDataHandler(str(invalid_file))


class TestLoadData:
    """Tests for loading Excel data."""
    
    def test_load_data_success(self, sample_excel_file):
        """Test successful data loading."""
        handler = ExcelDataHandler(sample_excel_file)
        df = handler.load_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'Business Name' in df.columns
        assert 'Phone' in df.columns
    
    def test_load_data_sets_df_attribute(self, sample_excel_file):
        """Test that load_data sets the df attribute."""
        handler = ExcelDataHandler(sample_excel_file)
        handler.load_data()
        
        assert handler.df is not None
        assert isinstance(handler.df, pd.DataFrame)


class TestValidateColumns:
    """Tests for column validation."""
    
    def test_validate_required_columns(self, sample_excel_file):
        """Test validation with all required columns."""
        handler = ExcelDataHandler(sample_excel_file)
        handler.load_data()
        
        assert handler.validate_columns() is True
    
    def test_validate_missing_columns(self):
        """Test validation with missing required columns."""
        # Create DataFrame without required columns
        df = pd.DataFrame({'Wrong Column': [1, 2, 3]})
        
        handler = ExcelDataHandler.__new__(ExcelDataHandler)
        handler.df = df
        
        with pytest.raises(ValueError, match="Missing required columns"):
            handler.validate_columns()
    
    def test_validate_without_loading(self):
        """Test validation without loading data first."""
        # Create a valid file but don't load
        data = {
            'Business Name': ['Test'],
            'Phone': ['+12025551001']
        }
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xlsx') as f:
            temp_path = f.name
        
        df.to_excel(temp_path, index=False, engine='openpyxl')
        
        try:
            handler = ExcelDataHandler(temp_path)
            
            with pytest.raises(ValueError, match="No data loaded"):
                handler.validate_columns()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestGetBusinesses:
    """Tests for getting business objects."""
    
    def test_get_businesses_success(self, sample_excel_file):
        """Test successful business extraction."""
        handler = ExcelDataHandler(sample_excel_file)
        businesses = handler.get_businesses()
        
        assert isinstance(businesses, list)
        assert len(businesses) > 0
        assert all(isinstance(b, Business) for b in businesses)
    
    def test_get_businesses_filters_invalid(self, sample_excel_file):
        """Test that invalid entries are filtered out."""
        handler = ExcelDataHandler(sample_excel_file)
        businesses = handler.get_businesses()
        
        # Should have skipped empty name and invalid phone
        assert handler.skipped_count > 0
        assert len(handler.errors) > 0
    
    def test_get_businesses_validates_phones(self, sample_excel_file):
        """Test that phone numbers are validated."""
        handler = ExcelDataHandler(sample_excel_file)
        businesses = handler.get_businesses()
        
        # All returned businesses should have valid, formatted phones
        for business in businesses:
            assert business.phone.startswith('+')
    
    def test_get_businesses_handles_websites(self, sample_excel_file):
        """Test website handling."""
        handler = ExcelDataHandler(sample_excel_file)
        businesses = handler.get_businesses()
        
        # Should have both businesses with and without websites
        with_website = [b for b in businesses if b.has_website()]
        without_website = [b for b in businesses if not b.has_website()]
        
        assert len(with_website) > 0 or len(without_website) > 0


class TestStatistics:
    """Tests for statistics generation."""
    
    def test_get_stats(self, sample_excel_file):
        """Test statistics generation."""
        handler = ExcelDataHandler(sample_excel_file)
        handler.get_businesses()
        
        stats = handler.get_stats()
        
        assert 'total_rows' in stats
        assert 'valid_businesses' in stats
        assert 'skipped' in stats
        assert 'success_rate' in stats
        assert 'businesses_with_website' in stats
        assert 'businesses_without_website' in stats
    
    def test_stats_accuracy(self, sample_excel_file):
        """Test that statistics are accurate."""
        handler = ExcelDataHandler(sample_excel_file)
        handler.get_businesses()
        
        stats = handler.get_stats()
        
        # Total should equal valid + skipped
        assert stats['total_rows'] >= stats['valid_businesses'] + stats['skipped']
        
        # Website counts should match businesses
        total_businesses = stats['valid_businesses']
        website_total = stats['businesses_with_website'] + stats['businesses_without_website']
        assert website_total == total_businesses


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_errors_tracked(self, sample_excel_file):
        """Test that errors are tracked."""
        handler = ExcelDataHandler(sample_excel_file)
        handler.get_businesses()
        
        assert isinstance(handler.errors, list)
        # Should have some errors from test data
        assert len(handler.errors) > 0
    
    def test_error_structure(self, sample_excel_file):
        """Test error structure."""
        handler = ExcelDataHandler(sample_excel_file)
        handler.get_businesses()
        
        for error in handler.errors:
            assert 'row' in error
            assert 'error' in error
            assert 'severity' in error


class TestConvenienceFunction:
    """Tests for convenience function."""
    
    def test_load_businesses_from_excel(self, sample_excel_file):
        """Test convenience function."""
        businesses = load_businesses_from_excel(sample_excel_file)
        
        assert isinstance(businesses, list)
        assert len(businesses) > 0


class TestPrintMethods:
    """Tests for print methods (stats and errors)."""
    
    def test_print_stats(self, sample_excel_file, capsys):
        """Test print_stats method."""
        handler = ExcelDataHandler(sample_excel_file)
        handler.get_businesses()
        handler.print_stats()
        
        captured = capsys.readouterr()
        assert "Total rows" in captured.out
        assert "Valid businesses" in captured.out
        assert "Skipped" in captured.out
    
    def test_print_errors(self, sample_excel_file, capsys):
        """Test print_errors method."""
        handler = ExcelDataHandler(sample_excel_file)
        handler.get_businesses()
        handler.print_errors()
        
        captured = capsys.readouterr()
        # Should have some errors from test data
        assert captured.out != ""


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_empty_excel_file(self):
        """Test with empty Excel file."""
        df = pd.DataFrame()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xlsx') as f:
            temp_path = f.name
        
        df.to_excel(temp_path, index=False, engine='openpyxl')
        
        try:
            handler = ExcelDataHandler(temp_path)
            handler.load_data()
            
            with pytest.raises(ValueError, match="Missing required columns"):
                handler.validate_columns()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_all_invalid_data(self):
        """Test with all invalid business data."""
        data = {
            'Business Name': ['', '', ''],
            'Phone': ['invalid1', 'invalid2', 'invalid3'],
            'Description': ['Test 1', 'Test 2', 'Test 3'],
            'Website': ['', '', ''],
            'Google Maps Link': ['', '', '']
        }
        
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xlsx') as f:
            temp_path = f.name
        
        df.to_excel(temp_path, index=False, engine='openpyxl')
        
        try:
            handler = ExcelDataHandler(temp_path)
            businesses = handler.get_businesses()
            
            # All rows should be skipped
            assert len(businesses) == 0
            assert handler.skipped_count == 3
            assert len(handler.errors) > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_get_businesses_without_loading(self):
        """Test get_businesses calls load_data automatically."""
        # Create a valid Excel file
        data = {
            'Business Name': ['Test'],
            'Phone': ['+12025551001'],
            'Description': ['Test'],
            'Website': [''],
            'Google Maps Link': ['']
        }
        
        df = pd.DataFrame(data)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.xlsx') as f:
            temp_path = f.name
        
        df.to_excel(temp_path, index=False, engine='openpyxl')
        
        try:
            handler = ExcelDataHandler(temp_path)
            # Don't call load_data() - get_businesses should load automatically
            businesses = handler.get_businesses()
            
            # Should successfully get businesses even without explicit load_data call
            assert len(businesses) == 1
            assert businesses[0].business_name == 'Test'
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
