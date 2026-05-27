"""
Landing Page Builder - Fluent interface for landing page operations
Handles: navigate and search operations
Transitions to ItemPageBuilder when search is performed
"""

from typing import Optional
from playwright.async_api import Page
from .landing_page import LandingPage
from .item_page_builder import ItemPageBuilder
import logging

logger = logging.getLogger(__name__)


class SearchCoroutine(ItemPageBuilder):
    """
    Awaitable that performs search and returns ItemPageBuilder for chaining.

    Allows fluent pattern:
        items = await (LandingPageBuilder(page).search("query")).minPrice(100).collect()
    """

    def __init__(self, page: Page, query: str):
        super().__init__(page)
        self.query = query
        self.logger = logger
        self._search_performed = False

    def __await__(self):
        """Make this class awaitable"""
        return self._perform_search().__await__()

    async def _perform_search(self) -> 'ItemPageBuilder':
        """
        Execute the search and return ItemPageBuilder for chaining.

        This assumes the search input has already been filled via setSearch().
        It will click the search button, validate the results page, and navigate to next page.
        """
        self.logger.info(f"🔍 Executing search for: '{self.query}'")

        # Execute search using landing page (assumes input already filled)
        landing_page = LandingPage(self.page)
        await landing_page.execute_search()

        self.logger.info(f"✅ Search complete - navigated to ItemPage")

        # Mark search as performed
        self._search_performed = True

        # Return self (which is ItemPageBuilder) for chaining
        return self

    async def collect(self, limit: int) -> list:
        """Override collect to perform search first if not already done"""
        if not self._search_performed:
            self.logger.info(f"🔍 Performing search for: '{self.query}' before collecting")
            await self._perform_search()

        # Now call parent collect
        return await super().collect(limit)


class LandingPageBuilder:
    """
    Builder for landing page operations.

    Example:
        builder = LandingPageBuilder(page)
        item_builder = await builder.navigate(url).search("laptop")
        items = await item_builder.minPrice(100).maxPrice(500).collect(5)
    """

    def __init__(self, page: Page):
        self.page = page
        self.landing_page = LandingPage(page)
        self._url: Optional[str] = None
        self._search_query: Optional[str] = None
        logger.info(f"🏠 LandingPageBuilder initialized - page open: {page.url}")

    def set_url(self, url: str) -> 'LandingPageBuilder':
        """Set the URL to navigate to"""
        self._url = url
        logger.info(f"📍 URL set to: {url}")
        return self

    async def navigate(self, url: str) -> 'LandingPageBuilder':
        """Navigate to landing page and verify it loaded"""
        self._url = url
        logger.info(f"📍 Navigating to: {url}")
        await self.landing_page.navigate(url)
        logger.info(f"✅ Landing page loaded")
        return self

    async def setSearch(self, query: str) -> 'LandingPageBuilder':

        logger.info(f"📝 Setting search query: '{query}'")

        # Clear and fill search input with the query
        search_input = self.landing_page.search_page.SEARCH_INPUT
        logger.info(f"Clearing and filling search input: {search_input}")

        # Click on the input to focus it
        await self.landing_page.search_page.click(search_input)

        # Select all and clear
        await self.page.locator(search_input).clear()

        # Fill with the query
        await self.landing_page.search_page.fill(search_input, query)

        self._search_query = query
        logger.info(f"✅ Search input filled with: '{query}'")
        return self

    def search(self) -> 'SearchCoroutine':

        if self._search_query is None:
            raise ValueError("Search query not set. Call setSearch() first.")

        logger.info(f"🔍 Executing search for: '{self._search_query}'")
        return SearchCoroutine(self.page, self._search_query)

    def set_search_query(self, query: str) -> 'LandingPageBuilder':
        """Set the search query (doesn't execute)"""
        self._search_query = query
        logger.info(f"🔍 Search query set to: '{query}'")
        return self

    async def build_and_search(self, url: str, query: str) -> ItemPageBuilder:
        """
        Navigate and search in one call

        Args:
            url: Landing page URL
            query: Search query

        Returns:
            ItemPageBuilder - ready for filtering and collection
        """
        logger.info(f"🏠 Building: navigate + search")
        await self.navigate(url)
        return await self.search(query)

    async def get_current_url(self) -> str:
        """Get current page URL"""
        return await self.landing_page.get_current_url()

    async def is_loaded(self) -> bool:
        """Verify landing page is loaded"""
        return await self.landing_page.is_loaded()