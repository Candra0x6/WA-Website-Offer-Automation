"""
Message Templates Module
Contains all message templates for website creation and enhancement offers.
"""

import random
from typing import List


class MessageTemplates:
    """Container for all message templates."""
    
    # Templates for businesses WITHOUT a website (Website Creation Offer)
    CREATION_TEMPLATES: List[str] = [
        "Hi {business_name}, your business sounds amazing! I help local brands like yours create professional websites that attract more customers online. Would you like me to send a free mockup idea?",
        
        "Hello {business_name}, I came across your business — it looks great! I specialize in creating simple, beautiful websites that make it easier for customers to find and contact you. Want to see a free demo?",
        
        "Hi {business_name}, we recently helped a similar business increase online leads by 40% after launching a modern website. I'd love to show you how a site could boost your visibility too. Shall I send you an example?",
        
        "Hey {business_name}! I noticed you don't have a website yet. In today's digital world, having an online presence can really help grow your business. I'd be happy to create a free concept for you. Interested?",
        
        "Hello {business_name}, I build affordable, professional websites for small businesses like yours. A website helps customers find you 24/7 and builds trust. Want to discuss your options?",
    ]
    
    # Templates for businesses WITH a website (Website Enhancement Offer)
    ENHANCEMENT_TEMPLATES: List[str] = [
        "Hey {business_name}, I checked out your website ({website}) — it's great! I specialize in modern redesigns that improve speed, mobile look, and Google ranking. Would you like a free concept preview?",
        
        "Hello {business_name}, I saw your website and think it could attract even more customers with a cleaner layout and better mobile performance. I can prepare a few enhancement ideas at no cost — interested?",
        
        "Hi {business_name}, your current site looks good, but a refreshed design could make it feel more premium and boost conversions. I can share a quick concept for free if you're open to it!",
        
        "Hey {business_name}, I took a look at {website} and see some opportunities to improve user experience and SEO. Would you be interested in a complimentary website audit and redesign proposal?",
        
        "Hello {business_name}, your website has potential! I help businesses modernize their sites to increase engagement and sales. Can I show you what an upgrade might look like?",
    ]
    
    @staticmethod
    def get_creation_template() -> str:
        """
        Get a random website creation template.
        
        Returns:
            str: A randomly selected creation template
        """
        return random.choice(MessageTemplates.CREATION_TEMPLATES)
    
    @staticmethod
    def get_enhancement_template() -> str:
        """
        Get a random website enhancement template.
        
        Returns:
            str: A randomly selected enhancement template
        """
        return random.choice(MessageTemplates.ENHANCEMENT_TEMPLATES)
    
    @staticmethod
    def get_template_by_type(message_type: str) -> str:
        """
        Get a random template based on message type.
        
        Args:
            message_type: Either 'creation' or 'enhancement'
            
        Returns:
            str: A randomly selected template
            
        Raises:
            ValueError: If message_type is not 'creation' or 'enhancement'
        """
        if message_type.lower() == 'creation':
            return MessageTemplates.get_creation_template()
        elif message_type.lower() == 'enhancement':
            return MessageTemplates.get_enhancement_template()
        else:
            raise ValueError(f"Invalid message_type: {message_type}. Must be 'creation' or 'enhancement'")
    
    @staticmethod
    def get_all_creation_templates() -> List[str]:
        """Get all creation templates."""
        return MessageTemplates.CREATION_TEMPLATES.copy()
    
    @staticmethod
    def get_all_enhancement_templates() -> List[str]:
        """Get all enhancement templates."""
        return MessageTemplates.ENHANCEMENT_TEMPLATES.copy()
    
    @staticmethod
    def count_templates() -> dict:
        """
        Get count of templates.
        
        Returns:
            dict: Dictionary with template counts
        """
        return {
            'creation': len(MessageTemplates.CREATION_TEMPLATES),
            'enhancement': len(MessageTemplates.ENHANCEMENT_TEMPLATES),
            'total': len(MessageTemplates.CREATION_TEMPLATES) + len(MessageTemplates.ENHANCEMENT_TEMPLATES)
        }


# Convenience functions for direct access
def get_creation_template() -> str:
    """Get a random creation template."""
    return MessageTemplates.get_creation_template()


def get_enhancement_template() -> str:
    """Get a random enhancement template."""
    return MessageTemplates.get_enhancement_template()


def get_template(message_type: str) -> str:
    """Get a random template by type."""
    return MessageTemplates.get_template_by_type(message_type)


if __name__ == "__main__":
    # Test templates
    print("=== Website Creation Templates ===")
    for i, template in enumerate(MessageTemplates.CREATION_TEMPLATES, 1):
        print(f"\n{i}. {template[:100]}...")
    
    print("\n\n=== Website Enhancement Templates ===")
    for i, template in enumerate(MessageTemplates.ENHANCEMENT_TEMPLATES, 1):
        print(f"\n{i}. {template[:100]}...")
    
    print("\n\n=== Template Statistics ===")
    stats = MessageTemplates.count_templates()
    print(f"Creation templates: {stats['creation']}")
    print(f"Enhancement templates: {stats['enhancement']}")
    print(f"Total templates: {stats['total']}")
    
    print("\n\n=== Random Sample ===")
    print("Creation:", get_creation_template()[:80] + "...")
    print("Enhancement:", get_enhancement_template()[:80] + "...")
