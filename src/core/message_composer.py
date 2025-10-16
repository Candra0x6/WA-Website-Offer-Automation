"""
Message Composer
Composes personalized messages based on business data.
"""

from urllib.parse import quote
from typing import Dict, Any
from ..models.business import Business
from ..config.templates import MessageTemplates
from ..utils.validators import extract_domain_from_url


class MessageComposer:
    """Handles message composition and personalization."""
    
    def __init__(self):
        """Initialize message composer."""
        self.templates = MessageTemplates()
    
    def compose_message(self, business: Business, url_encode: bool = False) -> str:
        """
        Compose a personalized message for a business.
        
        Args:
            business: Business object with business information
            url_encode: Whether to URL-encode the message for WhatsApp Web
            
        Returns:
            str: Personalized message, optionally URL-encoded
        """
        # Detect message type based on website presence
        message_type = self.detect_message_type(business)
        
        # Get appropriate template
        template = self.templates.get_template_by_type(message_type)
        
        # Personalize the message
        message = self._personalize_template(template, business)
        
        # URL-encode if requested
        if url_encode:
            message = self._url_encode_message(message)
        
        return message
    
    def detect_message_type(self, business: Business) -> str:
        """
        Detect whether to use creation or enhancement template.
        
        Args:
            business: Business object
            
        Returns:
            str: 'creation' if no website, 'enhancement' if has website
        """
        return 'enhancement' if business.has_website() else 'creation'
    
    def _personalize_template(self, template: str, business: Business) -> str:
        """
        Replace placeholders in template with actual business data.
        
        Args:
            template: Message template with placeholders
            business: Business object with data
            
        Returns:
            str: Personalized message
        """
        # Build replacement dictionary
        replacements = self._build_replacements(business)
        
        # Replace all placeholders
        message = template
        for placeholder, value in replacements.items():
            message = message.replace(f"{{{placeholder}}}", value)
        
        return message
    
    def _build_replacements(self, business: Business) -> Dict[str, str]:
        """
        Build dictionary of placeholder replacements.
        
        Args:
            business: Business object
            
        Returns:
            dict: Placeholder to value mapping
        """
        replacements = {
            'business_name': business.business_name,
            'name': business.business_name,  # Alias
        }
        
        # Add optional fields if available
        if business.description:
            replacements['description'] = business.description
        
        if business.website:
            replacements['website'] = business.website
            # Also add domain
            domain = extract_domain_from_url(business.website)
            if domain:
                replacements['domain'] = domain
        
        if business.google_maps_link:
            replacements['maps_link'] = business.google_maps_link
            replacements['google_maps'] = business.google_maps_link  # Alias
        
        return replacements
    
    def _url_encode_message(self, message: str) -> str:
        """
        URL-encode message for WhatsApp Web API.
        
        Args:
            message: Plain text message
            
        Returns:
            str: URL-encoded message
        """
        # URL-encode the message, preserving spaces as %20
        return quote(message, safe='')
    
    def compose_whatsapp_url(self, business: Business) -> str:
        """
        Compose complete WhatsApp Web URL with message.
        
        Args:
            business: Business object
            
        Returns:
            str: Complete WhatsApp Web URL
        """
        # Clean phone for WhatsApp (remove + and spaces)
        phone = business.phone.replace('+', '').replace(' ', '').replace('-', '')
        
        # Compose and encode message
        message = self.compose_message(business, url_encode=True)
        
        # Build WhatsApp Web URL
        return f"https://web.whatsapp.com/send?phone={phone}&text={message}"
    
    def get_message_preview(self, business: Business, max_length: int = 100) -> str:
        """
        Get a preview of the message (first N characters).
        
        Args:
            business: Business object
            max_length: Maximum length of preview
            
        Returns:
            str: Message preview
        """
        message = self.compose_message(business)
        
        if len(message) <= max_length:
            return message
        
        return message[:max_length] + "..."
    
    def get_message_stats(self, business: Business) -> Dict[str, Any]:
        """
        Get statistics about the composed message.
        
        Args:
            business: Business object
            
        Returns:
            dict: Message statistics
        """
        message = self.compose_message(business)
        message_type = self.detect_message_type(business)
        
        return {
            'message_type': message_type,
            'length': len(message),
            'word_count': len(message.split()),
            'has_website': business.has_website(),
            'business_name': business.business_name,
        }


# Convenience function
def compose_message(business: Business, url_encode: bool = False) -> str:
    """
    Convenience function to compose a message.
    
    Args:
        business: Business object
        url_encode: Whether to URL-encode the message
        
    Returns:
        str: Personalized message
    """
    composer = MessageComposer()
    return composer.compose_message(business, url_encode)


if __name__ == "__main__":
    # Test message composition
    print("=" * 60)
    print("Testing Message Composer")
    print("=" * 60)
    
    # Create test businesses
    test_businesses = [
        Business(
            business_name="Coffee Haven",
            phone="+12025551001",
            description="Local coffee shop",
            website="",
            google_maps_link="https://maps.google.com/..."
        ),
        Business(
            business_name="Tech Solutions",
            phone="+12025551002",
            description="IT consulting",
            website="https://techsolutions.com",
            google_maps_link=""
        ),
    ]
    
    composer = MessageComposer()
    
    for i, business in enumerate(test_businesses, 1):
        print(f"\n{'='*60}")
        print(f"Business {i}: {business.business_name}")
        print(f"{'='*60}")
        
        # Detect message type
        msg_type = composer.detect_message_type(business)
        print(f"Message Type: {msg_type.upper()}")
        
        # Compose message
        message = composer.compose_message(business)
        print(f"\nMessage:\n{message}")
        
        # Get stats
        stats = composer.get_message_stats(business)
        print(f"\nStats:")
        print(f"  Length: {stats['length']} characters")
        print(f"  Words: {stats['word_count']}")
        
        # WhatsApp URL
        url = composer.compose_whatsapp_url(business)
        print(f"\nWhatsApp URL:\n{url[:100]}...")
    
    print(f"\n{'='*60}")
    print("✅ Message composer test completed!")
    print("=" * 60)
