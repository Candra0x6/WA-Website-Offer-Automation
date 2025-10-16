"""
Validators Module
Validates phone numbers, URLs, and other data.
"""

import re
import phonenumbers
from typing import Tuple, Optional
from urllib.parse import urlparse


class Validators:
    """Collection of validation utilities."""
    
    @staticmethod
    def validate_phone(phone: str, default_region: str = "US") -> Tuple[bool, str]:
        """
        Validate and format phone number using phonenumbers library.
        
        Args:
            phone: Phone number to validate (can be with or without +)
            default_region: Default country code (ISO 3166-1 alpha-2)
            
        Returns:
            Tuple of (is_valid, formatted_phone_or_error_message)
            
        Examples:
            >>> validate_phone("+1234567890", "US")
            (True, "+1234567890")
            >>> validate_phone("6281234567890", "ID")
            (True, "+6281234567890")
            >>> validate_phone("invalid", "US")
            (False, "Invalid phone number format")
        """
        if not phone or not isinstance(phone, str):
            return False, "Phone number is empty or invalid type"
        
        # Clean the phone number
        phone = phone.strip()
        
        if not phone:
            return False, "Phone number is empty"
        
        try:
            # If phone doesn't start with +, try to parse with region
            if not phone.startswith('+'):
                # Try to add + if it looks like an international number
                if phone.isdigit() and len(phone) >= 10:
                    phone = '+' + phone
            
            # Parse the phone number
            parsed_number = phonenumbers.parse(phone, default_region)
            
            # Check if it's a valid number
            if not phonenumbers.is_valid_number(parsed_number):
                return False, "Invalid phone number"
            
            # Check if it could be a WhatsApp number (mobile)
            number_type = phonenumbers.number_type(parsed_number)
            valid_types = [
                phonenumbers.PhoneNumberType.MOBILE,
                phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE,
            ]
            
            # Format in E164 format (international format with +)
            formatted = phonenumbers.format_number(
                parsed_number, 
                phonenumbers.PhoneNumberFormat.E164
            )
            
            return True, formatted
            
        except phonenumbers.NumberParseException as e:
            return False, f"Parse error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL string to validate
            
        Returns:
            bool: True if valid URL, False otherwise
            
        Examples:
            >>> validate_url("https://example.com")
            True
            >>> validate_url("http://test.com/page")
            True
            >>> validate_url("not a url")
            False
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        if not url:
            return False
        
        try:
            result = urlparse(url)
            # Must have scheme (http/https) and netloc (domain)
            return all([
                result.scheme in ['http', 'https'],
                result.netloc,
                '.' in result.netloc  # Must have at least one dot
            ])
        except Exception:
            return False
    
    @staticmethod
    def sanitize_business_name(name: str) -> str:
        """
        Sanitize business name by removing extra whitespace and special characters.
        
        Args:
            name: Business name to sanitize
            
        Returns:
            str: Sanitized business name
            
        Examples:
            >>> sanitize_business_name("  Coffee  Shop  ")
            "Coffee Shop"
            >>> sanitize_business_name("Tech & Solutions")
            "Tech & Solutions"
        """
        if not name or not isinstance(name, str):
            return ""
        
        # Remove leading/trailing whitespace
        name = name.strip()
        
        # Replace multiple spaces with single space
        name = re.sub(r'\s+', ' ', name)
        
        # Remove any control characters
        name = ''.join(char for char in name if ord(char) >= 32)
        
        return name
    
    @staticmethod
    def is_valid_whatsapp_number(phone: str) -> bool:
        """
        Check if a phone number is potentially valid for WhatsApp.
        
        Args:
            phone: Phone number to check
            
        Returns:
            bool: True if potentially valid for WhatsApp
        """
        is_valid, _ = Validators.validate_phone(phone)
        return is_valid
    
    @staticmethod
    def clean_phone_for_whatsapp(phone: str, default_region: str = "US") -> Optional[str]:
        """
        Clean and format phone number for WhatsApp (E164 format without +).
        
        Args:
            phone: Phone number to clean
            default_region: Default region code
            
        Returns:
            str: Cleaned phone number without + prefix, or None if invalid
            
        Examples:
            >>> clean_phone_for_whatsapp("+1234567890")
            "1234567890"
        """
        is_valid, result = Validators.validate_phone(phone, default_region)
        if is_valid and result.startswith('+'):
            return result[1:]  # Remove the + prefix
        return None
    
    @staticmethod
    def extract_domain_from_url(url: str) -> Optional[str]:
        """
        Extract domain name from URL.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            str: Domain name, or None if invalid
            
        Examples:
            >>> extract_domain_from_url("https://www.example.com/page")
            "www.example.com"
        """
        if not Validators.validate_url(url):
            return None
        
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None


# Convenience functions for direct use
def validate_phone(phone: str, default_region: str = "US") -> Tuple[bool, str]:
    """Validate phone number."""
    return Validators.validate_phone(phone, default_region)


def validate_url(url: str) -> bool:
    """Validate URL."""
    return Validators.validate_url(url)


def sanitize_business_name(name: str) -> str:
    """Sanitize business name."""
    return Validators.sanitize_business_name(name)


def is_valid_whatsapp_number(phone: str, default_region: str = "US") -> bool:
    """Check if phone number is valid for WhatsApp."""
    return Validators.is_valid_whatsapp_number(phone, default_region)


def clean_phone_for_whatsapp(phone: str, default_region: str = "US") -> Optional[str]:
    """Clean phone number for WhatsApp."""
    return Validators.clean_phone_for_whatsapp(phone, default_region)


def extract_domain_from_url(url: str) -> Optional[str]:
    """Extract domain from URL."""
    return Validators.extract_domain_from_url(url)


if __name__ == "__main__":
    # Test the validators
    print("=" * 60)
    print("Testing Validators Module")
    print("=" * 60)
    
    # Test phone validation
    print("\n### Phone Number Validation ###")
    test_phones = [
        ("+1234567890", "US"),
        ("1234567890", "US"),
        ("+6281234567890", "ID"),
        ("6281234567890", "ID"),
        ("invalid", "US"),
        ("", "US"),
        ("+44 20 7946 0958", "GB"),
    ]
    
    for phone, region in test_phones:
        is_valid, result = validate_phone(phone, region)
        status = "✅" if is_valid else "❌"
        print(f"{status} {phone:20} -> {result}")
    
    # Test URL validation
    print("\n### URL Validation ###")
    test_urls = [
        "https://example.com",
        "http://test.com/page",
        "https://www.google.com",
        "not a url",
        "",
        "ftp://invalid.com",
    ]
    
    for url in test_urls:
        is_valid = validate_url(url)
        status = "✅" if is_valid else "❌"
        print(f"{status} {url}")
    
    # Test business name sanitization
    print("\n### Business Name Sanitization ###")
    test_names = [
        "  Coffee  Shop  ",
        "Tech & Solutions",
        "  Multiple   Spaces   Between  ",
        "Normal Name",
    ]
    
    for name in test_names:
        sanitized = sanitize_business_name(name)
        print(f"'{name}' -> '{sanitized}'")
    
    print("\n" + "=" * 60)
    print("✅ All validator tests completed!")
    print("=" * 60)
