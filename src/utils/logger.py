"""
Logging System Module
Provides comprehensive logging with console output and CSV file logging.
"""

import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class MessageLogEntry:
    """Structure for a message log entry."""
    timestamp: str
    business_name: str
    phone: str
    website: str
    message_type: str  # "creation" or "enhancement"
    status: str  # "success", "failed", "error"
    error_message: str = ""
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return asdict(self)


@dataclass
class LogSummary:
    """Summary statistics for logging session."""
    total_processed: int = 0
    successful: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    creation_messages: int = 0
    enhancement_messages: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_processed == 0:
            return 0.0
        return (self.successful / self.total_processed) * 100
    
    def display(self) -> str:
        """Return formatted summary."""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                     Session Summary                          ║
╠══════════════════════════════════════════════════════════════╣
║ Total Processed:      {self.total_processed:<39} ║
║ Successful:           {self.successful:<39} ║
║ Failed:               {self.failed:<39} ║
║ Errors:               {self.errors:<39} ║
║ Skipped:              {self.skipped:<39} ║
║                                                              ║
║ Message Types:                                               ║
║   Creation Messages:  {self.creation_messages:<39} ║
║   Enhancement:        {self.enhancement_messages:<39} ║
║                                                              ║
║ Success Rate:         {self.success_rate:.1f}%{' ' * 37} ║
╚══════════════════════════════════════════════════════════════╝
        """.strip()


class MessageLogger:
    """
    Logger for WhatsApp message operations.
    Handles both console output and CSV file logging.
    """
    
    def __init__(self, log_file: str, console_level: int = logging.INFO):
        """
        Initialize the logger.
        
        Args:
            log_file: Path to the CSV log file
            console_level: Logging level for console output
        """
        self.log_file = Path(log_file)
        self.console_level = console_level
        self.summary = LogSummary()
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Set up console logger
        self._setup_console_logger()
        
        # Initialize CSV file with headers if it doesn't exist
        self._initialize_csv()
    
    def _setup_console_logger(self):
        """Configure console logger with formatting."""
        self.logger = logging.getLogger('WhatsAppAutomation')
        self.logger.setLevel(self.console_level)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.console_level)
        
        # Colored output format
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.log_file.exists():
            headers = [
                'timestamp', 'business_name', 'phone', 'website',
                'message_type', 'status', 'error_message', 'retry_count'
            ]
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def log_message(self, entry: MessageLogEntry):
        """
        Log a message delivery attempt.
        
        Args:
            entry: MessageLogEntry object with delivery details
        """
        # Write to CSV
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=entry.to_dict().keys())
            writer.writerow(entry.to_dict())
        
        # Update summary
        self.summary.total_processed += 1
        
        if entry.status == 'success':
            self.summary.successful += 1
        elif entry.status == 'failed':
            self.summary.failed += 1
        elif entry.status == 'error':
            self.summary.errors += 1
        
        if entry.message_type == 'creation':
            self.summary.creation_messages += 1
        elif entry.message_type == 'enhancement':
            self.summary.enhancement_messages += 1
        
        # Console log
        status_emoji = {
            'success': '✅',
            'failed': '❌',
            'error': '⚠️',
            'skipped': '⏭️'
        }
        
        emoji = status_emoji.get(entry.status, '❓')
        msg = f"{emoji} {entry.business_name} ({entry.phone}) - {entry.status.upper()}"
        
        if entry.status == 'success':
            self.logger.info(msg)
        elif entry.status in ['failed', 'error']:
            self.logger.error(f"{msg} - {entry.error_message}")
        else:
            self.logger.warning(msg)
    
    def log_error(self, business_name: str, phone: str, error: Exception):
        """
        Log an error.
        
        Args:
            business_name: Name of the business
            phone: Phone number
            error: Exception that occurred
        """
        entry = MessageLogEntry(
            timestamp=datetime.now().isoformat(),
            business_name=business_name,
            phone=phone,
            website="",
            message_type="",
            status="error",
            error_message=str(error),
            retry_count=0
        )
        self.log_message(entry)
    
    def log_skip(self, business_name: str, phone: str, reason: str):
        """
        Log a skipped entry.
        
        Args:
            business_name: Name of the business
            phone: Phone number
            reason: Reason for skipping
        """
        self.summary.skipped += 1
        self.logger.warning(f"⏭️  Skipped {business_name} ({phone}): {reason}")
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
    
    def success(self, message: str):
        """Log a success message."""
        self.logger.info(f"✅ {message}")
    
    def get_summary(self) -> LogSummary:
        """Get the current session summary."""
        return self.summary
    
    def print_summary(self):
        """Print the session summary to console."""
        print("\n")
        print(self.summary.display())
    
    def print_header(self, title: str):
        """
        Print a formatted header.
        
        Args:
            title: Header title
        """
        width = 62
        print("\n" + "═" * width)
        print(f"{title:^{width}}")
        print("═" * width + "\n")
    
    def print_progress(self, current: int, total: int, business_name: str):
        """
        Print progress information.
        
        Args:
            current: Current item number
            total: Total number of items
            business_name: Current business name
        """
        percent = (current / total * 100) if total > 0 else 0
        self.info(f"[{current}/{total}] ({percent:.1f}%) Processing: {business_name}")


# Convenience function to create a logger instance
def create_logger(log_file: str, console_level: int = logging.INFO) -> MessageLogger:
    """
    Create and return a MessageLogger instance.
    
    Args:
        log_file: Path to the CSV log file
        console_level: Logging level for console output
        
    Returns:
        MessageLogger: Configured logger instance
    """
    return MessageLogger(log_file, console_level)


def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    Setup and return a basic Python logger for application use.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Only add handler if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)-8s - [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


if __name__ == "__main__":
    # Test the logger
    logger = create_logger("test_log.csv")
    
    logger.print_header("Testing Logger System")
    
    logger.info("Starting test...")
    logger.success("Successfully initialized")
    logger.warning("This is a warning")
    logger.error("This is an error")
    
    # Test logging entries
    entry1 = MessageLogEntry(
        timestamp=datetime.now().isoformat(),
        business_name="Test Business 1",
        phone="+1234567890",
        website="",
        message_type="creation",
        status="success",
        error_message="",
        retry_count=0
    )
    logger.log_message(entry1)
    
    entry2 = MessageLogEntry(
        timestamp=datetime.now().isoformat(),
        business_name="Test Business 2",
        phone="+0987654321",
        website="https://example.com",
        message_type="enhancement",
        status="failed",
        error_message="Network timeout",
        retry_count=2
    )
    logger.log_message(entry2)
    
    logger.log_skip("Test Business 3", "+1111111111", "Invalid phone number")
    
    logger.print_summary()
    
    print("\n✅ Logger test completed! Check 'test_log.csv' for output.")
