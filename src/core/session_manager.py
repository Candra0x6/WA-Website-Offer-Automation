"""
Session Manager
Manages Chrome profile and session persistence for WhatsApp Web.
"""

from pathlib import Path
from typing import Optional
import shutil
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SessionManager:
    """Manages WhatsApp Web session persistence using Chrome profile."""
    
    def __init__(self, profile_dir: str = "chrome_profile_whatsapp"):
        """
        Initialize session manager.
        
        Args:
            profile_dir: Path to Chrome profile directory (default: chrome_profile_whatsapp)
        """
        self.profile_dir = Path(profile_dir)
        self.driver: Optional[webdriver.Chrome] = None
    
    def ensure_profile_directory(self) -> Path:
        """
        Ensure profile directory exists and return its path.
        
        Returns:
            Path: Absolute path to profile directory
        """
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        return self.profile_dir.resolve()
    
    def is_session_valid(self) -> bool:
        """
        Check if a valid WhatsApp Web session exists in the profile.
        
        Returns:
            bool: True if session files exist, False otherwise
        """
        if not self.profile_dir.exists():
            return False
        
        # Check for Chrome session files
        # WhatsApp Web stores session data in IndexedDB and localStorage
        session_indicators = [
            self.profile_dir / "Default" / "IndexedDB",
            self.profile_dir / "Default" / "Local Storage",
        ]
        
        return any(path.exists() for path in session_indicators)
    
    def get_chrome_options(self, headless: bool = False, user_agent: Optional[str] = None) -> Options:
        """
        Get Chrome options with profile configuration.
        
        Args:
            headless: Run in headless mode (default: False)
            user_agent: Custom user agent string (optional)
            
        Returns:
            Options: Configured Chrome options
        """
        options = Options()
        
        # Set profile directory
        profile_path = self.ensure_profile_directory()
        options.add_argument(f"--user-data-dir={profile_path}")
        
        # WhatsApp Web specific options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Additional options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        
        # Set custom user agent if provided
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        
        # Headless mode
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        
        # Suppress logging
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        return options
    
    def create_driver(self, headless: bool = False, user_agent: Optional[str] = None) -> webdriver.Chrome:
        """
        Create and configure Chrome WebDriver with session persistence.
        
        Args:
            headless: Run in headless mode (default: False)
            user_agent: Custom user agent string (optional)
            
        Returns:
            webdriver.Chrome: Configured Chrome driver
        """
        options = self.get_chrome_options(headless, user_agent)
        
        try:
            driver = webdriver.Chrome(options=options)
            
            # Set page load timeout
            driver.set_page_load_timeout(60)
            
            # Set implicit wait
            driver.implicitly_wait(10)
            
            # Maximize window (helps with element detection)
            if not headless:
                driver.maximize_window()
            
            self.driver = driver
            return driver
            
        except Exception as e:
            raise RuntimeError(f"Failed to create Chrome driver: {str(e)}")
    
    def wait_for_whatsapp_load(self, driver: webdriver.Chrome, timeout: int = 60) -> bool:
        """
        Wait for WhatsApp Web to load completely.
        
        Args:
            driver: Chrome WebDriver instance
            timeout: Maximum wait time in seconds (default: 60)
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            # Wait for the main app element to be present
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, "app"))
            )
            
            # Additional wait for page to stabilize
            time.sleep(2)
            
            return True
            
        except TimeoutException:
            return False
    
    def is_qr_code_present(self, driver: webdriver.Chrome) -> bool:
        """
        Check if QR code is present (indicating need to scan).
        
        Args:
            driver: Chrome WebDriver instance
            
        Returns:
            bool: True if QR code is present, False otherwise
        """
        try:
            # Look for QR code canvas element
            qr_selectors = [
                (By.CSS_SELECTOR, "canvas[aria-label*='Scan']"),
                (By.CSS_SELECTOR, "canvas[aria-label*='QR']"),
                (By.XPATH, "//canvas[contains(@aria-label, 'Scan')]"),
            ]
            
            for by, selector in qr_selectors:
                try:
                    driver.find_element(by, selector)
                    return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def is_logged_in(self, driver: webdriver.Chrome) -> bool:
        """
        Check if user is logged in to WhatsApp Web.
        
        Args:
            driver: Chrome WebDriver instance
            
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            # Check for chat list or main pane (indicates logged in)
            logged_in_selectors = [
                (By.ID, "pane-side"),
                (By.CSS_SELECTOR, "div[data-testid='chat-list']"),
                (By.CSS_SELECTOR, "[role='textbox'][data-tab='1']"),
            ]
            
            for by, selector in logged_in_selectors:
                try:
                    driver.find_element(by, selector)
                    return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def wait_for_login(self, driver: webdriver.Chrome, timeout: int = 300, check_interval: int = 5) -> bool:
        """
        Wait for user to scan QR code and login.
        
        Args:
            driver: Chrome WebDriver instance
            timeout: Maximum wait time in seconds (default: 300 = 5 minutes)
            check_interval: Time between checks in seconds (default: 5)
            
        Returns:
            bool: True if login successful, False if timeout
        """
        start_time = time.time()
        
        print("\n" + "=" * 60)
        print("⚠️  QR CODE DETECTED - Please scan with your phone")
        print("=" * 60)
        print(f"Waiting up to {timeout} seconds for login...")
        
        while time.time() - start_time < timeout:
            # Check if logged in
            if self.is_logged_in(driver):
                print("\n✅ Login successful!")
                time.sleep(3)  # Wait for session to stabilize
                return True
            
            # Check if QR code is still present
            if not self.is_qr_code_present(driver):
                # QR code disappeared, check if logged in
                if self.is_logged_in(driver):
                    print("\n✅ Login successful!")
                    time.sleep(3)
                    return True
            
            # Show progress
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            print(f"\rWaiting for login... ({remaining}s remaining)", end="", flush=True)
            
            time.sleep(check_interval)
        
        print("\n\n❌ Login timeout - QR code was not scanned in time")
        return False
    
    def clear_session(self):
        """
        Clear the Chrome profile to force new login.
        
        Warning: This will delete all session data!
        """
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
        
        if self.profile_dir.exists():
            try:
                shutil.rmtree(self.profile_dir)
                print(f"✅ Session cleared: {self.profile_dir}")
            except Exception as e:
                print(f"⚠️  Failed to clear session: {str(e)}")
    
    def close(self):
        """Close the WebDriver if it's open."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience function
def create_session_manager(profile_dir: str = "chrome_profile_whatsapp") -> SessionManager:
    """
    Create a session manager instance.
    
    Args:
        profile_dir: Path to Chrome profile directory
        
    Returns:
        SessionManager: Configured session manager
    """
    return SessionManager(profile_dir)


if __name__ == "__main__":
    # Test session manager
    print("=" * 60)
    print("Testing Session Manager")
    print("=" * 60)
    
    with SessionManager() as manager:
        print(f"\nProfile directory: {manager.ensure_profile_directory()}")
        print(f"Session valid: {manager.is_session_valid()}")
        
        print("\nCreating Chrome driver...")
        driver = manager.create_driver(headless=False)
        
        print("Loading WhatsApp Web...")
        driver.get("https://web.whatsapp.com")
        
        print("Waiting for page load...")
        if manager.wait_for_whatsapp_load(driver):
            print("✅ WhatsApp Web loaded")
            
            # Check login status
            if manager.is_qr_code_present(driver):
                print("\n⚠️  QR code detected - please scan")
                manager.wait_for_login(driver, timeout=60)
            elif manager.is_logged_in(driver):
                print("✅ Already logged in")
            else:
                print("⚠️  Unknown state")
        else:
            print("❌ Failed to load WhatsApp Web")
    
    print("\n" + "=" * 60)
    print("✅ Session manager test completed!")
    print("=" * 60)
