from playwright.async_api import Page
from .base_page import BasePage
from config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Login page object for eBay"""

    # eBay Login Locators
    SIGN_IN_BUTTON = "a[href*='signin'], button:has-text('Sign in'), a:has-text('Sign in')"
    EMAIL_INPUT = "input[type='email'], input[id*='email'], input[name='email']"
    PASSWORD_INPUT = "input[type='password'], input[id*='password'], input[name='password']"
    CONTINUE_BUTTON = "button:has-text('Continue'), button[type='submit'], input[type='submit']"
    LOGIN_BUTTON = "button:has-text('Sign in'), button[type='submit']"
    ERROR_MESSAGE = ".errorMsg, .error, [class*='error'], [data-test-id='signin_error']"

    async def click_sign_in(self) -> None:
        """Navigate to eBay login page"""
        logger.info("Navigating to eBay login page")
        await self.page.goto(settings.LOGIN_URL, wait_until="networkidle")

    async def enter_email(self, email: str) -> None:
        """Enter email/username"""
        logger.info(f"Entering email: {email}")
        await self.fill(self.EMAIL_INPUT, email)

    async def click_continue(self) -> None:
        """Click Continue button after email"""
        logger.info("Clicking Continue button")
        try:
            await self.click(self.CONTINUE_BUTTON)
            await self.page.wait_for_load_state("networkidle", timeout=10000)
        except Exception as e:
            logger.warning(f"Could not click continue: {e}")

    async def enter_password(self, password: str) -> None:
        """Enter password"""
        logger.info("Entering password")
        await self.fill(self.PASSWORD_INPUT, password)

    async def click_login(self) -> None:
        """Click Login/Sign In button"""
        logger.info("Clicking Login button")
        await self.click(self.LOGIN_BUTTON)
        await self.page.wait_for_load_state("networkidle", timeout=10000)

    async def is_error_displayed(self) -> bool:
        """Check if error message is visible"""
        return await self.is_visible(self.ERROR_MESSAGE)

    async def get_error_message(self) -> str:
        """Get error message text"""
        if await self.is_visible(self.ERROR_MESSAGE):
            return await self.get_text(self.ERROR_MESSAGE)
        return ""

    async def login(self, email: str, password: str) -> None:
        """Complete eBay login process"""
        logger.info(f"Starting eBay login for: {email}")

        try:
            # Try clicking sign in button if on homepage
            await self.click_sign_in()
        except Exception as e:
            logger.info(f"Already on login page or signin button not found: {e}")

        # Enter email/username
        await self.enter_email(email)
        await self.click_continue()

        # Enter password
        await self.enter_password(password)
        await self.click_login()

        logger.info("Login completed successfully")