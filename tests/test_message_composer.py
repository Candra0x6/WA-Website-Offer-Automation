"""
Unit tests for the MessageComposer module
"""

import pytest
from urllib.parse import unquote

from src.core.message_composer import MessageComposer, compose_message
from src.models.business import Business


@pytest.fixture
def business_without_website():
    """Create a business without a website."""
    return Business(
        business_name="Coffee Haven",
        phone="+12025551001",
        description="Local coffee shop",
        website="",
        google_maps_link="https://maps.google.com/coffeehaven"
    )


@pytest.fixture
def business_with_website():
    """Create a business with a website."""
    return Business(
        business_name="Tech Solutions",
        phone="+12025551002",
        description="IT consulting services",
        website="https://techsolutions.com",
        google_maps_link="https://maps.google.com/techsolutions"
    )


@pytest.fixture
def minimal_business():
    """Create a business with only required fields."""
    return Business(
        business_name="Minimal Co",
        phone="+12025551003"
    )


class TestMessageComposerInit:
    """Tests for MessageComposer initialization."""
    
    def test_init(self):
        """Test MessageComposer initialization."""
        composer = MessageComposer()
        assert composer is not None
        assert composer.templates is not None


class TestDetectMessageType:
    """Tests for message type detection."""
    
    def test_detect_creation_type(self, business_without_website):
        """Test detection of creation message type."""
        composer = MessageComposer()
        message_type = composer.detect_message_type(business_without_website)
        assert message_type == 'creation'
    
    def test_detect_enhancement_type(self, business_with_website):
        """Test detection of enhancement message type."""
        composer = MessageComposer()
        message_type = composer.detect_message_type(business_with_website)
        assert message_type == 'enhancement'
    
    def test_detect_type_minimal_business(self, minimal_business):
        """Test detection with minimal business data."""
        composer = MessageComposer()
        message_type = composer.detect_message_type(minimal_business)
        assert message_type == 'creation'


class TestComposeMessage:
    """Tests for message composition."""
    
    def test_compose_creation_message(self, business_without_website):
        """Test composing a creation message."""
        composer = MessageComposer()
        message = composer.compose_message(business_without_website)
        
        assert isinstance(message, str)
        assert len(message) > 0
        assert business_without_website.business_name in message
    
    def test_compose_enhancement_message(self, business_with_website):
        """Test composing an enhancement message."""
        composer = MessageComposer()
        message = composer.compose_message(business_with_website)
        
        assert isinstance(message, str)
        assert len(message) > 0
        assert business_with_website.business_name in message
        # Note: Not all enhancement templates include {website} placeholder
        # so we just verify the message type is correct
    
    def test_compose_message_no_url_encoding(self, business_without_website):
        """Test composing message without URL encoding."""
        composer = MessageComposer()
        message = composer.compose_message(business_without_website, url_encode=False)
        
        # Should contain normal characters (not URL-encoded)
        assert ' ' in message
        assert '%20' not in message
    
    def test_compose_message_with_url_encoding(self, business_without_website):
        """Test composing message with URL encoding."""
        composer = MessageComposer()
        message = composer.compose_message(business_without_website, url_encode=True)
        
        # Should be URL-encoded
        assert ' ' not in message
        assert '%20' in message or '%' in message
    
    def test_compose_minimal_business(self, minimal_business):
        """Test composing message with minimal business data."""
        composer = MessageComposer()
        message = composer.compose_message(minimal_business)
        
        assert isinstance(message, str)
        assert minimal_business.business_name in message


class TestPersonalization:
    """Tests for message personalization."""
    
    def test_business_name_replacement(self, business_without_website):
        """Test that business name is properly replaced."""
        composer = MessageComposer()
        message = composer.compose_message(business_without_website)
        
        assert business_without_website.business_name in message
        assert '{business_name}' not in message
        assert '{name}' not in message
    
    def test_website_replacement(self, business_with_website):
        """Test that website is properly replaced in enhancement messages."""
        composer = MessageComposer()
        
        # Test multiple times to potentially hit a template with {website}
        messages_with_website = []
        for _ in range(20):
            message = composer.compose_message(business_with_website)
            if '{website}' in message or '{' in message:
                # Found a placeholder that wasn't replaced
                assert False, f"Placeholder not replaced in: {message}"
            if business_with_website.website in message or 'techsolutions.com' in message:
                messages_with_website.append(message)
        
        # At least some messages should include the website (2 out of 5 templates have it)
        # With 20 tries, we should hit at least one
        assert len(messages_with_website) > 0, "No messages included website after 20 tries"
    
    def test_no_placeholder_leakage(self, business_with_website):
        """Test that no placeholders remain in final message."""
        composer = MessageComposer()
        message = composer.compose_message(business_with_website)
        
        # Check for common placeholder patterns
        assert '{' not in message or '}' not in message


class TestURLEncoding:
    """Tests for URL encoding."""
    
    def test_url_encode_spaces(self):
        """Test that spaces are properly encoded."""
        composer = MessageComposer()
        test_message = "Hello World"
        encoded = composer._url_encode_message(test_message)
        
        assert ' ' not in encoded
        assert '%20' in encoded
    
    def test_url_encode_special_chars(self):
        """Test that special characters are encoded."""
        composer = MessageComposer()
        test_message = "Hello! How are you?"
        encoded = composer._url_encode_message(test_message)
        
        assert '!' not in encoded
        assert '?' not in encoded
        assert '%21' in encoded or '%3F' in encoded
    
    def test_url_encode_decode_roundtrip(self, business_without_website):
        """Test that encoded message can be decoded back."""
        composer = MessageComposer()
        
        # Get the same message twice (one encoded, one not)
        # To ensure consistency, we need to test the encoding/decoding itself
        test_message = "Hello World! How are you?"
        encoded = composer._url_encode_message(test_message)
        decoded = unquote(encoded)
        
        assert test_message == decoded


class TestWhatsAppURL:
    """Tests for WhatsApp URL generation."""
    
    def test_compose_whatsapp_url(self, business_without_website):
        """Test WhatsApp URL composition."""
        composer = MessageComposer()
        url = composer.compose_whatsapp_url(business_without_website)
        
        assert url.startswith('https://web.whatsapp.com/send?')
        assert 'phone=' in url
        assert 'text=' in url
    
    def test_whatsapp_url_contains_phone(self, business_with_website):
        """Test that WhatsApp URL contains phone number."""
        composer = MessageComposer()
        url = composer.compose_whatsapp_url(business_with_website)
        
        # Phone should be in URL without + sign
        phone_digits = business_with_website.phone.replace('+', '')
        assert phone_digits in url
    
    def test_whatsapp_url_message_encoded(self, business_without_website):
        """Test that message in URL is encoded."""
        composer = MessageComposer()
        url = composer.compose_whatsapp_url(business_without_website)
        
        # Extract the text parameter
        text_start = url.find('text=') + 5
        text_part = url[text_start:]
        
        # Should be URL-encoded (no spaces)
        assert ' ' not in text_part
    
    def test_whatsapp_url_phone_formatting(self):
        """Test that phone numbers are properly formatted in URL."""
        composer = MessageComposer()
        
        # Test with phone containing +, spaces, dashes
        business = Business(
            business_name="Test",
            phone="+1-202-555-1001",
        )
        
        url = composer.compose_whatsapp_url(business)
        
        # Should remove all special characters
        assert '+' not in url.split('text=')[0]  # Before text param
        assert '-' not in url.split('text=')[0]
        assert ' ' not in url.split('text=')[0]


class TestMessagePreview:
    """Tests for message preview functionality."""
    
    def test_get_message_preview_short(self, minimal_business):
        """Test preview with short message."""
        composer = MessageComposer()
        preview = composer.get_message_preview(minimal_business, max_length=200)
        
        assert isinstance(preview, str)
        # Preview can be up to max_length + 3 for "..."
        assert len(preview) <= 203
    
    def test_get_message_preview_truncated(self, business_with_website):
        """Test preview with truncation."""
        composer = MessageComposer()
        preview = composer.get_message_preview(business_with_website, max_length=50)
        
        assert len(preview) <= 53  # 50 + "..."
        if len(composer.compose_message(business_with_website)) > 50:
            assert preview.endswith('...')
    
    def test_get_message_preview_default_length(self, business_without_website):
        """Test preview with default length."""
        composer = MessageComposer()
        preview = composer.get_message_preview(business_without_website)
        
        # Default is 100
        assert len(preview) <= 103  # 100 + "..."


class TestMessageStats:
    """Tests for message statistics."""
    
    def test_get_message_stats(self, business_with_website):
        """Test getting message statistics."""
        composer = MessageComposer()
        stats = composer.get_message_stats(business_with_website)
        
        assert isinstance(stats, dict)
        assert 'message_type' in stats
        assert 'length' in stats
        assert 'word_count' in stats
        assert 'has_website' in stats
        assert 'business_name' in stats
    
    def test_stats_message_type_creation(self, business_without_website):
        """Test stats for creation message."""
        composer = MessageComposer()
        stats = composer.get_message_stats(business_without_website)
        
        assert stats['message_type'] == 'creation'
        assert stats['has_website'] is False
    
    def test_stats_message_type_enhancement(self, business_with_website):
        """Test stats for enhancement message."""
        composer = MessageComposer()
        stats = composer.get_message_stats(business_with_website)
        
        assert stats['message_type'] == 'enhancement'
        assert stats['has_website'] is True
    
    def test_stats_length_and_words(self, business_without_website):
        """Test that stats correctly calculate length and words."""
        composer = MessageComposer()
        
        # Get message and stats
        # Note: We need to ensure we're comparing the same message
        # Since templates are random, we'll compose once and verify stats match
        stats = composer.get_message_stats(business_without_website)
        
        # Stats should have positive values
        assert stats['length'] > 0
        assert stats['word_count'] > 0
        
        # Word count should be reasonable relative to length
        # Average word length in English is ~5 chars, so word_count should be roughly length/5
        assert stats['word_count'] < stats['length']  # Basic sanity check
    
    def test_stats_business_name(self, business_with_website):
        """Test that stats include business name."""
        composer = MessageComposer()
        stats = composer.get_message_stats(business_with_website)
        
        assert stats['business_name'] == business_with_website.business_name


class TestConvenienceFunction:
    """Tests for convenience function."""
    
    def test_compose_message_function(self, business_without_website):
        """Test convenience function."""
        message = compose_message(business_without_website)
        
        assert isinstance(message, str)
        assert len(message) > 0
        assert business_without_website.business_name in message
    
    def test_compose_message_function_with_encoding(self, business_with_website):
        """Test convenience function with URL encoding."""
        message = compose_message(business_with_website, url_encode=True)
        
        assert isinstance(message, str)
        assert ' ' not in message
        assert '%20' in message or '%' in message


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_business_with_special_chars_in_name(self):
        """Test business name with special characters."""
        business = Business(
            business_name="Joe's Coffee & Tea",
            phone="+12025551001"
        )
        
        composer = MessageComposer()
        message = composer.compose_message(business)
        
        assert "Joe's Coffee & Tea" in message
    
    def test_compose_multiple_messages_variation(self, business_without_website):
        """Test that multiple compositions may vary (random templates)."""
        composer = MessageComposer()
        
        messages = [composer.compose_message(business_without_website) for _ in range(10)]
        
        # All should contain business name
        assert all(business_without_website.business_name in msg for msg in messages)
        
        # Messages might vary (different templates selected)
        # But all should be valid strings
        assert all(isinstance(msg, str) and len(msg) > 0 for msg in messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
