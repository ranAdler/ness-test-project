"""
Search Builder - Fluent interface for product search with filters.
Implements the builder pattern for chainable search operations.
"""

from typing import List, Optional
from playwright.async_api import Page
from .search_page import SearchPage
import logging

logger = logging.getLogger(__name__)


class SearchResult:
    """Awaitable result of a search operation."""

    def __init__(self, builder: 'SearchBuilder'):
        self.builder = builder

    def __await__(self):
        return self._execute().__await__()

    async def _execute(self) -> List[str]:
        """Execute the search and return product URLs."""
        if not self.builder._query:
            raise ValueError("Search query must be set before collecting")

        logger.info("")
        logger.info("  📦 SEARCH BUILDER: Starting search operation")
        logger.info(f"     → query='{self.builder._query}'")
        if self.builder._min_price is not None:
            logger.info(f"     → min_price=${self.builder._min_price}")
        if self.builder._max_price is not None:
            logger.info(f"     → max_price=${self.builder._max_price}")
        logger.info(f"     → limit={self.builder._limit}")
        logger.info(f"     → Current page URL: {self.builder.page.url}")

        try:
            # Step 1: Perform search
            logger.info("     ⏳ Performing search...")
            await self.builder.search_page.search_products(self.builder._query)
            logger.info(f"     ✓ Search completed for: {self.builder._query}")

            # Step 2: Apply price filter if specified
            if self.builder._max_price is not None or self.builder._min_price is not None:
                logger.info(f"     ⏳ Applying price filter...")
                await self.builder.search_page.filter_by_price_range(
                    min_price=self.builder._min_price,
                    max_price=self.builder._max_price
                )
                logger.info(f"     ✓ Price filter applied")

            # Step 3: Collect products with pagination
            logger.info(f"     ⏳ Collecting products with pagination...")
            products = await self.builder.search_page.get_products_paginated(
                max_price=self.builder._max_price,
                limit=self.builder._limit
            )
            logger.info(f"     ✓ Pagination complete")

            logger.info(f"     ✅ Search complete: Found {len(products)} products")
            logger.info(f"     → Product URLs: {products}")

            # Step 4: Take screenshot if enabled
            if self.builder._take_screenshot:
                logger.info(f"     ⏳ Taking screenshot of results...")
                await self.builder.search_page.take_search_results_screenshot(
                    f"search_{self.builder._query}_{len(products)}_items.png"
                )
                logger.info(f"     ✓ Screenshot saved")

            logger.info(f"  ✅ SEARCH BUILDER COMPLETE: {len(products)} product URLs")
            return products

        except Exception as e:
            logger.error(f"     ✗ Error during search: {e}")
            try:
                await self.builder.search_page.take_screenshot("search_error.png")
                logger.error(f"     ✗ Error screenshot saved")
            except:
                pass
            raise


class SearchBuilder:
    """
    Fluent builder for product searches with filters.

    Example:
        urls = await (SearchBuilder(page)
            .search("shoes")
            .minPrice(50)
            .maxPrice(220)
            .filter()
            .collect(5))
    """

    def __init__(self, page: Page):
        self.page = page
        self.search_page = SearchPage(page)
        self._query: Optional[str] = None
        self._max_price: Optional[float] = None
        self._min_price: Optional[float] = None
        self._limit: int = 5
        self._take_screenshot: bool = True


    def maxPrice(self, price: float) -> 'SearchBuilder':
        """Set maximum price filter (same page, just set value)."""
        self._max_price = price
        return self

    def minPrice(self, price: float) -> 'SearchBuilder':
        """Set minimum price filter (same page, just set value)."""
        self._min_price = price
        return self

    def filter(self) -> 'SearchBuilder':
        """Apply filters and stay on same page."""
        return self

    def filterByPrice(self) -> 'SearchBuilder':
        """Mark that price filter should be applied when collecting results."""
        if self._max_price is not None or self._min_price is not None:
            logger.info("📍 Price filter marked for submission")
        return self

    def withoutScreenshot(self) -> 'SearchBuilder':
        """Disable screenshot capture after search."""
        self._take_screenshot = False
        return self

    def collect(self, limit: int) -> SearchResult:
        """
        Set limit and return awaitable result.
        No need to call build() - just await this result.
        """
        self._limit = limit
        return SearchResult(self)