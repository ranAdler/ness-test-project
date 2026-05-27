"""
Login Builder - Fluent interface for login with result handling.
Implements the builder pattern for chainable login operations.
"""

from typing import Optional, Union
from playwright.async_api import Page
from .login_page import LoginPage
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class LoginResult:
    """Result of a login attempt"""

    def __init__(self, success: bool, page: Page, error_message: Optional[str] = None):
        self.success = success
        self.page = page
        self.error_message = error_message
        self.current_url = page.url

    def __repr__(self):
        status = "✓ SUCCESS" if self.success else "✗ FAILED"
        return f"LoginResult({status}, url={self.current_url})"


class LoginBuilder:
    """
    Fluent builder for login operations.

    Example:
        result = await (LoginBuilder(page)
            .user("test@example.com")
            .password("password123")
            .build())

        if result.success:
            # Navigate to next page
        else:
            # Handle error
            error = result.error_message
    """

    def __init__(self, page: Page):
        self.page = page
        self.login_page = LoginPage(page)
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._take_screenshot: bool = True

    def user(self, username: str) -> 'LoginBuilder':
        """Set the username/email for login"""
        self._username = username
        return self

    def password(self, password: str) -> 'LoginBuilder':
        """Set the password for login"""
        self._password = password
        return self

    def withoutScreenshot(self) -> 'LoginBuilder':
        """Disable screenshot capture after login attempt"""
        self._take_screenshot = False
        return self

    async def build(self) -> LoginResult:
        """
        Execute the login and return result with page reference.

        Returns:
            LoginResult: Contains success status, page object, and error message if failed

        Raises:
            ValueError: If username or password is not set
        """
        if not self._username:
            raise ValueError("Username must be set before building (use .user())")
        if not self._password:
            raise ValueError("Password must be set before building (use .password())")

        logger.info("")
        logger.info("  🔐 LOGIN BUILDER: Starting login operation")
        logger.info(f"     → username='{self._username}'")
        logger.info(f"     → password=***")
        logger.info(f"     → Current page URL: {self.page.url}")

        try:
            logger.info("     ⏳ Attempting login...")

            # Try clicking sign in button if on homepage
            try:
                await self.login_page.click_sign_in()
            except Exception as e:
                logger.info(f"     Already on login page: {e}")

            # Enter credentials
            await self.login_page.enter_email(self._username)
            await self.login_page.click_continue()

            await self.login_page.enter_password(self._password)
            await self.login_page.click_login()

            # Check for error after login attempt
            import asyncio
            await asyncio.sleep(1)  # Wait for page to stabilize

            # Take screenshot if enabled
            if self._take_screenshot:
                logger.info("     ⏳ Taking screenshot...")
                try:
                    await self.login_page.take_screenshot("login_attempt.png")
                except:
                    pass

            # Check if login was successful by checking for error message
            error_displayed = await self.login_page.is_error_displayed()

            if error_displayed:
                error_msg = await self.login_page.get_error_message()
                logger.error(f"     ✗ Login failed with error: {error_msg}")
                logger.error(f"  ✗ LOGIN FAILED: {error_msg}")
                return LoginResult(success=False, page=self.page, error_message=error_msg)
            else:
                logger.info(f"     ✓ Login completed, no error message detected")
                logger.info(f"  ✅ LOGIN BUILDER COMPLETE: Login successful")
                return LoginResult(success=True, page=self.page)

        except Exception as e:
            logger.error(f"     ✗ Error during login: {e}")
            try:
                await self.login_page.take_screenshot("login_error.png")
                logger.error(f"     ✗ Error screenshot saved")
            except:
                pass
            logger.error(f"  ✗ LOGIN BUILDER FAILED: {str(e)}")
            return LoginResult(success=False, page=self.page, error_message=str(e))