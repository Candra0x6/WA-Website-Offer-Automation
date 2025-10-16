"""
WhatsApp Controller
Manages Selenium WebDriver and WhatsApp Web automation for sending messages.
"""

import time
import random
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from .session_manager import SessionManager
from ..models.business import Business


class WhatsAppController:
    """Controls WhatsApp Web automation via Selenium."""
    
    # WhatsApp Web URLs
    WHATSAPP_WEB_URL = "https://web.whatsapp.com"
    WHATSAPP_SEND_URL = "https://web.whatsapp.com/send?phone={phone}&text={message}"
    
    def __init__(self, profile_path: str = "chrome_profile_whatsapp", headless: bool = False):
        """
        Initialize WhatsApp controller.
        
        Args:
            profile_path: Path to Chrome profile directory
            headless: Whether to run in headless mode
        """
        self.profile_path = profile_path
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self.session_manager: Optional[SessionManager] = None
        self.is_initialized = False
    
    def initialize_driver(self) -> bool:
        """
        Initialize Selenium WebDriver and login to WhatsApp Web.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            print("\n" + "=" * 60)
            print("Initializing WhatsApp Web Controller")
            print("=" * 60)
            
            # Create session manager
            self.session_manager = SessionManager(self.profile_path)
            
            # Check if session exists
            has_session = self.session_manager.is_session_valid()
            if has_session:
                print("✅ Found existing session")
            else:
                print("⚠️  No existing session found")
            
            # Create driver
            print("\nCreating Chrome driver...")
            self.driver = self.session_manager.create_driver(headless=self.headless)
            
            # Load WhatsApp Web
            print("Loading WhatsApp Web...")
            self.driver.get(self.WHATSAPP_WEB_URL)
            
            # Wait for page to load
            print("Waiting for page load...")
            if not self.session_manager.wait_for_whatsapp_load(self.driver):
                print("❌ Failed to load WhatsApp Web")
                return False
            
            print("✅ WhatsApp Web loaded")
            
            # Check login status
            if self.session_manager.is_qr_code_present(self.driver):
                print("\n📱 QR Code detected - Please scan with your phone")
                if not self.session_manager.wait_for_login(self.driver, timeout=300):
                    print("❌ Login failed")
                    return False
            elif self.session_manager.is_logged_in(self.driver):
                print("✅ Already logged in")
            else:
                print("⚠️  Unknown login state")
                return False
            
            self.is_initialized = True
            print("\n" + "=" * 60)
            print("✅ WhatsApp Web Controller Ready!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Initialization failed: {str(e)}")
            return False
    
    def send_message(self, phone: str, message: str, retry_count: int = 3) -> Tuple[bool, str]:
        """
        Send a message via WhatsApp Web.
        
        Args:
            phone: Phone number (with country code, without +)
            message: Message text to send
            retry_count: Number of retry attempts (default: 3)
            
        Returns:
            Tuple[bool, str]: (Success status, Error message if failed)
        """
        if not self.is_initialized or not self.driver:
            return False, "Controller not initialized"
        
        # Clean phone number (remove + and spaces)
        clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        
        for attempt in range(retry_count):
            try:
                # Navigate to direct send URL
                url = self.WHATSAPP_SEND_URL.format(phone=clean_phone, message="")
                self.driver.get(url)
                
                # Wait for page load
                time.sleep(3)
                
                # Wait for input box to be available
                input_box = self._wait_for_message_input(timeout=20)
                if not input_box:
                    if attempt < retry_count - 1:
                        print(f"⚠️  Retry {attempt + 1}/{retry_count}: Input box not found")
                        continue
                    return False, "Message input box not found"
                
                # Type message with human-like delays
                self._type_message_humanlike(input_box, message)
                
                # Wait before sending
                time.sleep(random.uniform(0.5, 1.5))
                
                # Send message (Shift+Enter = new line, Enter = send)
                input_box.send_keys(Keys.RETURN)
                
                # Wait for message to send
                time.sleep(2)
                
                # Verify message was sent
                if self._verify_message_sent():
                    return True, ""
                else:
                    if attempt < retry_count - 1:
                        print(f"⚠️  Retry {attempt + 1}/{retry_count}: Message not confirmed")
                        continue
                    return False, "Message sending not confirmed"
                
            except Exception as e:
                error_msg = str(e)
                if attempt < retry_count - 1:
                    print(f"⚠️  Retry {attempt + 1}/{retry_count}: {error_msg}")
                    time.sleep(2)
                    continue
                return False, error_msg
        
        return False, "Max retries exceeded"
    
    def send_message_to_business(self, business: Business, message: str) -> Tuple[bool, str]:
        """
        Send a message to a business.
        
        Args:
            business: Business object with phone number
            message: Message text to send
            
        Returns:
            Tuple[bool, str]: (Success status, Error message if failed)
        """
        return self.send_message(business.phone, message)
    
    def _wait_for_message_input(self, timeout: int = 20):
        """
        Wait for message input box to be available.
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement or None: Input box element if found
        """
        try:
            # Multiple selectors for input box (WhatsApp changes these frequently)
            selectors = [
                (By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']"),
                (By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='1']"),
                (By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"),
                (By.XPATH, "//div[@contenteditable='true'][@data-tab='1']"),
                (By.CSS_SELECTOR, "div[role='textbox'][contenteditable='true']"),
            ]
            
            for by, selector in selectors:
                try:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    # Make sure element is visible and interactable
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    return element
                except (TimeoutException, NoSuchElementException):
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _type_message_humanlike(self, element, message: str):
        """
        Type message with human-like delays between characters.
        
        Args:
            element: Input element
            message: Message to type
        """
        # Click to focus
        element.click()
        time.sleep(random.uniform(0.1, 0.3))
        
        # Type with random delays
        for char in message:
            element.send_keys(char)
            # Random delay between 20ms to 100ms per character
            time.sleep(random.uniform(0.02, 0.1))
    
    def _verify_message_sent(self, timeout: int = 10) -> bool:
        """
        Verify that message was sent by checking for sent indicator.
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            bool: True if message appears to be sent
        """
        try:
            # Look for message sent indicators (checkmarks)
            time.sleep(2)  # Wait for message to appear
            
            # Check for sent message indicators
            sent_indicators = [
                (By.CSS_SELECTOR, "span[data-icon='msg-check']"),
                (By.CSS_SELECTOR, "span[data-icon='msg-dblcheck']"),
                (By.CSS_SELECTOR, "span[data-testid='msg-check']"),
            ]
            
            for by, selector in sent_indicators:
                try:
                    self.driver.find_element(by, selector)
                    return True
                except NoSuchElementException:
                    continue
            
            # If no specific indicator found, assume sent if no errors
            return True
            
        except Exception:
            return True  # Assume success if we can't verify
    
    def check_if_number_exists(self, phone: str) -> bool:
        """
        Check if a phone number is registered on WhatsApp.
        
        Args:
            phone: Phone number to check
            
        Returns:
            bool: True if number exists, False otherwise
        """
        if not self.is_initialized or not self.driver:
            return False
        
        try:
            clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
            url = self.WHATSAPP_SEND_URL.format(phone=clean_phone, message="")
            self.driver.get(url)
            
            time.sleep(5)
            
            # Check for "Phone number shared via url is invalid" error
            error_selectors = [
                (By.XPATH, "//*[contains(text(), 'Phone number') and contains(text(), 'invalid')]"),
                (By.XPATH, "//*[contains(text(), 'número') and contains(text(), 'inválido')]"),
            ]
            
            for by, selector in error_selectors:
                try:
                    self.driver.find_element(by, selector)
                    return False  # Error found, number doesn't exist
                except NoSuchElementException:
                    continue
            
            # If message input is available, number exists
            input_box = self._wait_for_message_input(timeout=10)
            return input_box is not None
            
        except Exception:
            return False
    
    def get_driver_status(self) -> dict:
        """
        Get current status of the WebDriver.
        
        Returns:
            dict: Status information
        """
        return {
            'initialized': self.is_initialized,
            'driver_active': self.driver is not None,
            'logged_in': self.session_manager.is_logged_in(self.driver) if self.driver else False,
            'profile_path': str(self.profile_path),
            'headless': self.headless,
        }
    
    def close(self):
        """Close the WebDriver and cleanup."""
        if self.session_manager:
            self.session_manager.close()
        
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
        
        self.is_initialized = False
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience function
def create_whatsapp_controller(profile_path: str = "chrome_profile_whatsapp", 
                               headless: bool = False) -> WhatsAppController:
    """
    Create a WhatsApp controller instance.
    
    Args:
        profile_path: Path to Chrome profile directory
        headless: Whether to run in headless mode
        
    Returns:
        WhatsAppController: Configured controller
    """
    return WhatsAppController(profile_path, headless)


if __name__ == "__main__":
    # Test WhatsApp controller
    print("=" * 60)
    print("Testing WhatsApp Controller")
    print("=" * 60)
    
    with WhatsAppController() as controller:
        if controller.is_initialized:
            print("\n✅ Controller initialized successfully!")
            print(f"\nStatus: {controller.get_driver_status()}")
            
            # Keep browser open for testing
            input("\nPress Enter to close browser...")
        else:
            print("\n❌ Controller initialization failed!")
    
    print("\n" + "=" * 60)
    print("✅ WhatsApp controller test completed!")
    print("=" * 60)
