from playwright.async_api import Page, expect
from typing import Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BasePage:
    """Base page class with common methods for all page objects"""

    def __init__(self, page: Page):
        self.page = page
        self.logger = logger

    async def navigate_to(self, url: str) -> None:
        """Navigate to a specific URL"""
        self.logger.info(f"Navigating to: {url}")
        await self.page.goto(url)

    async def click(self, locator: str) -> None:
        """Click on an element"""
        self.logger.info(f"Clicking on: {locator}")
        await self.page.click(locator)

    async def fill(self, locator: str, text: str) -> None:
        """Fill input field with text"""
        self.logger.info(f"Filling {locator} with: {text}")
        await self.page.fill(locator, text)

    async def type(self, locator: str, text: str, delay: int = 100) -> None:
        """Type text character by character"""
        self.logger.info(f"Typing into {locator}: {text}")
        await self.page.type(locator, text, delay=delay)

    async def get_text(self, locator: str) -> str:
        """Get text content of an element"""
        text = await self.page.text_content(locator)
        return text.strip() if text else ""

    async def get_attribute(self, locator: str, attribute: str) -> Optional[str]:
        """Get attribute value from element"""
        return await self.page.get_attribute(locator, attribute)

    async def is_visible(self, locator: str) -> bool:
        """Check if element is visible"""
        try:
            await self.page.wait_for_selector(locator, timeout=5000)
            return True
        except:
            return False

    async def is_enabled(self, locator: str) -> bool:
        """Check if element is enabled"""
        try:
            element = self.page.locator(locator)
            return await element.is_enabled()
        except:
            return False

    async def wait_for_element(self, locator: str, timeout: int = 10000) -> None:
        """Wait for element to appear"""
        self.logger.info(f"Waiting for element: {locator}")
        await self.page.wait_for_selector(locator, timeout=timeout)

    async def wait_for_navigation(self) -> None:
        """Wait for page navigation"""
        await self.page.wait_for_load_state("networkidle")

    async def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url

    async def go_back(self) -> None:
        """Go back to previous page"""
        self.logger.info("Going back to previous page")
        await self.page.go_back()

    async def refresh(self) -> None:
        """Refresh the page"""
        self.logger.info("Refreshing page")
        await self.page.reload()

    async def select_option(self, locator: str, value: str) -> None:
        """Select option from dropdown"""
        self.logger.info(f"Selecting {value} from {locator}")
        await self.page.select_option(locator, value)

    async def get_all_texts(self, locator: str) -> List[str]:
        """Get text from all matching elements"""
        elements = await self.page.locator(locator).all()
        texts = []
        for element in elements:
            text = await element.text_content()
            if text:
                texts.append(text.strip())
        return texts

    async def get_element_count(self, locator: str) -> int:
        """Get count of elements matching locator"""
        return await self.page.locator(locator).count()

    async def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot of current page"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        filepath = f"screenshots/{filename}"
        await self.page.screenshot(path=filepath)
        self.logger.info(f"Screenshot saved: {filepath}")
        return filepath

    async def get_page_title(self) -> str:
        """Get page title"""
        return await self.page.title()

    async def switch_to_frame(self, locator: str) -> Page:
        """Switch to iframe"""
        return self.page.frame_locator(locator)

    async def scroll_to_element(self, locator: str) -> None:
        """Scroll to element"""
        await self.page.locator(locator).scroll_into_view_if_needed()

    async def hover(self, locator: str) -> None:
        """Hover over element"""
        self.logger.info(f"Hovering over: {locator}")
        await self.page.hover(locator)

    async def double_click(self, locator: str) -> None:
        """Double click on element"""
        self.logger.info(f"Double clicking: {locator}")
        await self.page.dblclick(locator)

    async def right_click(self, locator: str) -> None:
        """Right click on element"""
        self.logger.info(f"Right clicking: {locator}")
        await self.page.click(locator, button="right")

    async def press_key(self, key: str) -> None:
        """Press keyboard key"""
        self.logger.info(f"Pressing key: {key}")
        await self.page.press("body", key)

    async def wait_for_function(self, script: str, timeout: int = 10000) -> None:
        """Wait for JavaScript function to return true"""
        await self.page.wait_for_function(script, timeout=timeout)

    async def execute_script(self, script: str, *args):
        """Execute JavaScript on page"""
        return await self.page.evaluate(script, args)