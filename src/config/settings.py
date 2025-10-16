"""
Application Configuration Settings
Loads configuration from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass
class AppConfig:
    """Application configuration with all settings."""
    
    # File paths
    EXCEL_FILE_PATH: str = field(
        default_factory=lambda: os.getenv(
            'EXCEL_FILE_PATH',
            str(PROJECT_ROOT / 'data' / 'data.xlsx')
        )
    )
    LOG_FILE_PATH: str = field(
        default_factory=lambda: os.getenv(
            'LOG_FILE_PATH',
            str(PROJECT_ROOT / 'logs' / 'delivery_log.csv')
        )
    )
    CHROME_PROFILE_PATH: str = field(
        default_factory=lambda: os.getenv(
            'CHROME_PROFILE_PATH',
            str(PROJECT_ROOT / 'chrome_profile_whatsapp')
        )
    )
    
    # WhatsApp settings
    WHATSAPP_URL: str = field(
        default_factory=lambda: os.getenv('WHATSAPP_URL', 'https://web.whatsapp.com')
    )
    QR_SCAN_TIMEOUT: int = field(
        default_factory=lambda: int(os.getenv('QR_SCAN_TIMEOUT', '120'))
    )
    CHAT_LOAD_TIMEOUT: int = field(
        default_factory=lambda: int(os.getenv('CHAT_LOAD_TIMEOUT', '30'))
    )
    
    # Rate limiting
    MIN_MESSAGE_DELAY: int = field(
        default_factory=lambda: int(os.getenv('MIN_MESSAGE_DELAY', '20'))
    )
    MAX_MESSAGE_DELAY: int = field(
        default_factory=lambda: int(os.getenv('MAX_MESSAGE_DELAY', '90'))
    )
    BATCH_SIZE: int = field(
        default_factory=lambda: int(os.getenv('BATCH_SIZE', '15'))
    )
    MIN_BATCH_DELAY: int = field(
        default_factory=lambda: int(os.getenv('MIN_BATCH_DELAY', '300'))
    )
    MAX_BATCH_DELAY: int = field(
        default_factory=lambda: int(os.getenv('MAX_BATCH_DELAY', '900'))
    )
    MAX_DAILY_MESSAGES: int = field(
        default_factory=lambda: int(os.getenv('MAX_DAILY_MESSAGES', '50'))
    )
    
    # Retry settings
    MAX_RETRIES: int = field(
        default_factory=lambda: int(os.getenv('MAX_RETRIES', '3'))
    )
    RETRY_BACKOFF_FACTOR: float = field(
        default_factory=lambda: float(os.getenv('RETRY_BACKOFF_FACTOR', '2.0'))
    )
    
    # Mode
    DRY_RUN: bool = field(
        default_factory=lambda: os.getenv('DRY_RUN', 'False').lower() == 'true'
    )
    HEADLESS: bool = field(
        default_factory=lambda: os.getenv('HEADLESS', 'False').lower() == 'true'
    )
    
    # Phone number settings
    DEFAULT_COUNTRY_CODE: str = field(
        default_factory=lambda: os.getenv('DEFAULT_COUNTRY_CODE', 'US')
    )
    
    def __post_init__(self):
        """Ensure necessary directories exist."""
        # Create directories if they don't exist
        Path(self.EXCEL_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(self.LOG_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(self.CHROME_PROFILE_PATH).mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate configuration settings.
        
        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Validate delay settings
        if self.MIN_MESSAGE_DELAY >= self.MAX_MESSAGE_DELAY:
            return False, "MIN_MESSAGE_DELAY must be less than MAX_MESSAGE_DELAY"
        
        if self.MIN_BATCH_DELAY >= self.MAX_BATCH_DELAY:
            return False, "MIN_BATCH_DELAY must be less than MAX_BATCH_DELAY"
        
        if self.MAX_DAILY_MESSAGES <= 0:
            return False, "MAX_DAILY_MESSAGES must be greater than 0"
        
        if self.BATCH_SIZE <= 0:
            return False, "BATCH_SIZE must be greater than 0"
        
        if self.MAX_RETRIES < 0:
            return False, "MAX_RETRIES must be non-negative"
        
        # Validate timeouts
        if self.QR_SCAN_TIMEOUT <= 0:
            return False, "QR_SCAN_TIMEOUT must be positive"
        
        if self.CHAT_LOAD_TIMEOUT <= 0:
            return False, "CHAT_LOAD_TIMEOUT must be positive"
        
        return True, None
    
    def display(self) -> str:
        """Return a formatted string of current configuration."""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║              WhatsApp Automation Configuration               ║
╠══════════════════════════════════════════════════════════════╣
║ Files:                                                       ║
║   Excel Data: {Path(self.EXCEL_FILE_PATH).name:<44} ║
║   Log File:   {Path(self.LOG_FILE_PATH).name:<44} ║
║                                                              ║
║ Rate Limiting:                                               ║
║   Message Delay:  {self.MIN_MESSAGE_DELAY}-{self.MAX_MESSAGE_DELAY} seconds{' ' * 33}║
║   Batch Size:     {self.BATCH_SIZE} messages{' ' * 36}║
║   Batch Delay:    {self.MIN_BATCH_DELAY}-{self.MAX_BATCH_DELAY} seconds (5-15 min){' ' * 17}║
║   Daily Limit:    {self.MAX_DAILY_MESSAGES} messages{' ' * 36}║
║                                                              ║
║ Mode:                                                        ║
║   Dry Run:        {str(self.DRY_RUN):<44} ║
║   Headless:       {str(self.HEADLESS):<44} ║
╚══════════════════════════════════════════════════════════════╝
        """.strip()


# Create a singleton instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the application configuration instance."""
    return config


def reload_config() -> AppConfig:
    """Reload configuration from environment variables."""
    global config
    load_dotenv(override=True)
    config = AppConfig()
    return config


if __name__ == "__main__":
    # Test configuration
    cfg = get_config()
    is_valid, error = cfg.validate()
    
    if is_valid:
        print("✅ Configuration is valid!")
        print(cfg.display())
    else:
        print(f"❌ Configuration error: {error}")
