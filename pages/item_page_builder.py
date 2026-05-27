"""
Item Page Builder - Fluent interface for item page operations
Handles: filtering (minPrice, maxPrice) and item collection
Returned from LandingPageBuilder.search() when search is performed
"""

from typing import List, Optional
from playwright.async_api import Page
from .item_page import ItemPage
import logging

logger = logging.getLogger(__name__)


class ItemPageBuilder:
    """
    Builder for item page operations.

    Returned from LandingPageBuilder.search() after navigation.

    Example:
        # From LandingPageBuilder
        item_builder = await landing_builder.search("laptop")

        # Then use ItemPageBuilder
        items = await (item_builder
            .minPrice(100)
            .maxPrice(500)
            .collect(limit=10))

    Returns:
        List[dict] - Each dict contains "name" and "price" keys
    """

    def __init__(self, page: Page):
        self.page = page
        self.item_page = ItemPage(page)
        self._min_price: Optional[float] = None
        self._max_price: Optional[float] = None
        logger.info("📦 ItemPageBuilder initialized")

    def minPrice(self, price: float) -> 'ItemPageBuilder':
        """
        Set minimum price filter

        Args:
            price: Minimum price value

        Returns:
            self - for method chaining
        """
        self._min_price = price
        logger.info(f"💰 Min price set to: ${price}")
        return self

    def maxPrice(self, price: float) -> 'ItemPageBuilder':
        """
        Set maximum price filter

        Args:
            price: Maximum price value

        Returns:
            self - for method chaining
        """
        self._max_price = price
        logger.info(f"💰 Max price set to: ${price}")
        return self

    def filterByPrice(self) -> 'ItemPageBuilder':
        """
        Explicit marker for price filter in the chain

        Returns:
            self - for method chaining
        """
        if self._max_price is not None or self._min_price is not None:
            logger.info("📍 Price filter marked for submission")
        return self

    async def collect(self, limit: int) -> List[dict]:
        """
        Apply filters and collect items from ItemPage

        This method:
        1. Verifies ItemPage is loaded
        2. Applies minPrice/maxPrice filters if set
        3. Collects product items up to limit
        4. Returns list of product dicts with name and price

        Args:
            limit: Maximum number of items to collect

        Returns:
            List of dicts containing product name and price
        """
        final_limit = limit

        logger.info("")
        logger.info("=" * 80)
        logger.info("🏗️  ITEM PAGE BUILDER: Starting collection")
        logger.info(f"   → min_price: ${self._min_price}" if self._min_price else "   → min_price: None")
        logger.info(f"   → max_price: ${self._max_price}" if self._max_price else "   → max_price: None")
        logger.info(f"   → limit: {final_limit}")

        try:
            # Verify ItemPage is loaded
            logger.info("   ⏳ Verifying ItemPage is loaded...")
            await self.item_page.wait_for_load()
            logger.info("   ✅ ItemPage verified as loaded")

            # Apply filters if any were set
            if self._min_price is not None or self._max_price is not None:
                logger.info(f"   ⏳ Applying price filters...")
                await self.item_page.filter_by_price_range(
                    min_price=self._min_price,
                    max_price=self._max_price
                )
                logger.info(f"   ✅ Filters applied")

            # Collect items with limit
            logger.info(f"   ⏳ Collecting items (limit={final_limit})...")
            items = await self.item_page.collect(limit=final_limit)

            logger.info(f"   ✅ Collection complete: {len(items)} items collected")
            logger.info("=" * 80 + "\n")

            return items

        except Exception as e:
            logger.error(f"   ✗ Error during collection: {e}")
            logger.error("=" * 80 + "\n")
            raise

    async def get_item_count(self) -> int:
        """Get total items on current page"""
        logger.info("📊 Getting item count...")
        count = await self.item_page.get_item_count()
        logger.info(f"📊 Items on page: {count}")
        return count

    async def is_loaded(self) -> bool:
        """Verify ItemPage is loaded"""
        logger.info("⏳ Checking ItemPage load status...")
        is_loaded = await self.item_page.is_loaded()
        logger.info(f"{'✅' if is_loaded else '❌'} ItemPage is {'loaded' if is_loaded else 'not loaded'}")
        return is_loaded

    async def wait_for_load(self) -> 'ItemPageBuilder':
        """Wait for ItemPage to load with error handling"""
        logger.info("⏳ Waiting for ItemPage to load...")
        await self.item_page.wait_for_load()
        logger.info("✅ ItemPage ready")
        return self

    async def take_screenshot(self, filename: str = "item_page.png") -> str:
        """Take screenshot of item page"""
        logger.info(f"📸 Taking screenshot: {filename}")
        path = await self.item_page.take_results_screenshot(filename)
        logger.info(f"✅ Screenshot saved: {path}")
        return path