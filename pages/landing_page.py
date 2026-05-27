from playwright.async_api import Page
from .search_page import SearchPage
import logging

logger = logging.getLogger(__name__)


class LandingPage:
    """Landing page object with search functionality"""

    def __init__(self, page: Page):
        self.page = page
        self.search_page = SearchPage(page)
        self.logger = logger

    async def is_loaded(self) -> bool:
        """
        Verify landing page is fully loaded.
        Checks for eBay search input and button
        """
        try:
            self.logger.info("✓ Verifying LandingPage is loaded...")

            # Wait for eBay search input to be available (by ID)
            await self.page.wait_for_selector(
                "#gh-ac",
                timeout=10000
            )

            # Also wait for search button
            await self.page.wait_for_selector(
                "#gh-search-btn",
                timeout=10000
            )

            self.logger.info("✓ LandingPage is fully loaded with search input and button")
            return True

        except Exception as e:
            self.logger.error(f"✗ LandingPage failed to load: {e}")
            return False

    async def navigate(self, url: str) -> None:
        """Navigate to landing page and verify it loaded"""
        self.logger.info(f"Navigating to: {url}")
        await self.page.goto(url, wait_until="networkidle", timeout=30000)

        # Verify page loaded
        is_loaded = await self.is_loaded()
        if not is_loaded:
            raise Exception("LandingPage failed to load after navigation")

        self.logger.info(f"✓ Successfully navigated to and verified LandingPage")

    async def search(self, query: str) -> None:
        """
        Perform search from landing page and navigate to ItemPage.

        This method:
        1. Verifies LandingPage is loaded
        2. Sets search text, clicks search, and verifies results page loaded
        3. Moves to next page
        4. Returns when ready
        """
        self.logger.info(f"🔍 Searching for: '{query}'")

        # Verify page is loaded before searching
        is_loaded = await self.is_loaded()
        if not is_loaded:
            raise Exception("LandingPage not loaded, cannot perform search")

        # Perform search using SearchPage (sets text, clicks search, verifies next page loaded, moves to next page)
        await self.search_page.search(query)

        self.logger.info(f"✅ Search completed with results for '{query}'")

    async def execute_search(self) -> None:
        """
        Execute search when input is already filled.

        This method:
        1. Verifies LandingPage is loaded
        2. Clicks search button, validates results page loaded
        3. Navigates to next page if available
        """
        self.logger.info("🔍 Executing search (input already filled)")

        # Verify page is loaded before searching
        is_loaded = await self.is_loaded()
        if not is_loaded:
            raise Exception("LandingPage not loaded, cannot perform search")

        # Execute search using SearchPage (clicks search, verifies results, moves to next page)
        await self.search_page.execute_search()

        self.logger.info("✅ Search executed and results page loaded")

    async def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url

    async def take_screenshot(self, filename: str = "landing_page.png") -> str:
        """Take screenshot of landing page"""
        filepath = f"screenshots/{filename}"
        await self.page.screenshot(path=filepath)
        self.logger.info(f"Screenshot saved: {filepath}")
        return filepath