"""
Unit tests for the Validators module
"""

import pytest
from src.utils.validators import Validators, validate_phone, validate_url, sanitize_business_name


class TestPhoneValidation:
    """Tests for phone number validation."""
    
    def test_valid_us_phone_with_plus(self):
        """Test valid US phone number with + prefix."""
        is_valid, result = Validators.validate_phone("+12025551234", "US")
        assert is_valid is True
        assert result == "+12025551234"
    
    def test_valid_us_phone_without_plus(self):
        """Test valid US phone number without + prefix."""
        is_valid, result = Validators.validate_phone("12025551234", "US")
        assert is_valid is True
        assert result == "+12025551234"
    
    def test_valid_indonesian_phone(self):
        """Test valid Indonesian phone number."""
        is_valid, result = Validators.validate_phone("+6281234567890", "ID")
        assert is_valid is True
        assert result == "+6281234567890"
    
    def test_valid_uk_phone(self):
        """Test valid UK phone number."""
        is_valid, result = Validators.validate_phone("+442079460958", "GB")
        assert is_valid is True
        assert result == "+442079460958"
    
    def test_invalid_phone_format(self):
        """Test invalid phone number format."""
        is_valid, result = Validators.validate_phone("invalid", "US")
        assert is_valid is False
        assert "Parse error" in result or "Invalid" in result
    
    def test_empty_phone(self):
        """Test empty phone number."""
        is_valid, result = Validators.validate_phone("", "US")
        assert is_valid is False
        assert "empty" in result.lower()
    
    def test_none_phone(self):
        """Test None phone number."""
        is_valid, result = Validators.validate_phone(None, "US")
        assert is_valid is False
    
    def test_phone_with_spaces(self):
        """Test phone number with spaces."""
        is_valid, result = Validators.validate_phone("  +12025551234  ", "US")
        assert is_valid is True
        assert result == "+12025551234"


class TestURLValidation:
    """Tests for URL validation."""
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        assert Validators.validate_url("https://example.com") is True
    
    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        assert Validators.validate_url("http://test.com") is True
    
    def test_url_with_path(self):
        """Test URL with path."""
        assert Validators.validate_url("https://example.com/path/to/page") is True
    
    def test_url_with_query(self):
        """Test URL with query parameters."""
        assert Validators.validate_url("https://example.com?param=value") is True
    
    def test_invalid_url_no_scheme(self):
        """Test invalid URL without scheme."""
        assert Validators.validate_url("example.com") is False
    
    def test_invalid_url_wrong_scheme(self):
        """Test invalid URL with wrong scheme."""
        assert Validators.validate_url("ftp://example.com") is False
    
    def test_invalid_url_text(self):
        """Test invalid URL (plain text)."""
        assert Validators.validate_url("not a url") is False
    
    def test_empty_url(self):
        """Test empty URL."""
        assert Validators.validate_url("") is False
    
    def test_none_url(self):
        """Test None URL."""
        assert Validators.validate_url(None) is False
    
    def test_url_with_subdomain(self):
        """Test URL with subdomain."""
        assert Validators.validate_url("https://www.example.com") is True


class TestBusinessNameSanitization:
    """Tests for business name sanitization."""
    
    def test_trim_whitespace(self):
        """Test trimming leading/trailing whitespace."""
        assert Validators.sanitize_business_name("  Coffee Shop  ") == "Coffee Shop"
    
    def test_multiple_spaces(self):
        """Test collapsing multiple spaces."""
        assert Validators.sanitize_business_name("Coffee    Shop") == "Coffee Shop"
    
    def test_mixed_whitespace(self):
        """Test mixed whitespace."""
        assert Validators.sanitize_business_name("  Coffee   Shop   Bar  ") == "Coffee Shop Bar"
    
    def test_normal_name(self):
        """Test normal business name."""
        assert Validators.sanitize_business_name("Coffee Shop") == "Coffee Shop"
    
    def test_special_characters(self):
        """Test business name with special characters."""
        assert Validators.sanitize_business_name("Coffee & Tea") == "Coffee & Tea"
    
    def test_empty_string(self):
        """Test empty string."""
        assert Validators.sanitize_business_name("") == ""
    
    def test_none_value(self):
        """Test None value."""
        assert Validators.sanitize_business_name(None) == ""
    
    def test_whitespace_only(self):
        """Test whitespace-only string."""
        assert Validators.sanitize_business_name("   ") == ""


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_validate_phone_function(self):
        """Test validate_phone convenience function."""
        is_valid, result = validate_phone("+12025551234", "US")
        assert is_valid is True
    
    def test_validate_url_function(self):
        """Test validate_url convenience function."""
        assert validate_url("https://example.com") is True
    
    def test_sanitize_business_name_function(self):
        """Test sanitize_business_name convenience function."""
        assert sanitize_business_name("  Test  ") == "Test"


class TestWhatsAppHelpers:
    """Tests for WhatsApp-specific helper methods."""
    
    def test_is_valid_whatsapp_number(self):
        """Test WhatsApp number validation."""
        assert Validators.is_valid_whatsapp_number("+12025551234") is True
        assert Validators.is_valid_whatsapp_number("invalid") is False
    
    def test_clean_phone_for_whatsapp(self):
        """Test cleaning phone for WhatsApp (removes +)."""
        result = Validators.clean_phone_for_whatsapp("+12025551234")
        assert result == "12025551234"
    
    def test_clean_invalid_phone_for_whatsapp(self):
        """Test cleaning invalid phone for WhatsApp."""
        result = Validators.clean_phone_for_whatsapp("invalid")
        assert result is None
    
    def test_extract_domain_from_url(self):
        """Test extracting domain from URL."""
        domain = Validators.extract_domain_from_url("https://www.example.com/page")
        assert domain == "www.example.com"
    
    def test_extract_domain_from_invalid_url(self):
        """Test extracting domain from invalid URL."""
        domain = Validators.extract_domain_from_url("not a url")
        assert domain is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
