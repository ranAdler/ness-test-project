from playwright.async_api import Page
from typing import List, Dict, Optional
from .search_page import SearchPage
import logging

logger = logging.getLogger(__name__)


class ItemPage:
    """Item results page with filtering and collection capabilities"""

    def __init__(self, page: Page):
        self.page = page
        self.search_page = SearchPage(page)
        self.logger = logger
        self._min_price: Optional[float] = None
        self._max_price: Optional[float] = None

    async def is_loaded(self) -> bool:
        """
        Verify ItemPage (search results) is fully loaded with filters.
        Checks for filter panel that eBay displays in search results.
        """
        try:
            self.logger.info("✓ Verifying ItemPage is loaded...")

            # Wait for filter panel to be visible
            # eBay search results include a filter nav on the left
            self.logger.info("  ⏳ Waiting for filter panel...")
            await self.page.wait_for_selector(
                "ul.x-refine__left__nav",
                timeout=30000
            )
            self.logger.info("  ✓ Filter panel loaded")

            # # Wait for networkidle to ensure results are fully loaded
            # self.logger.info("  ⏳ Waiting for network idle...")
            # await self.page.wait_for_load_state("networkidle", timeout=10000)
            # self.logger.info("  ✓ Network idle")

            self.logger.info(f"✓ ItemPage is fully loaded with filters ready")
            return True

        except Exception as e:
            self.logger.error(f"✗ ItemPage failed to load: {e}")
            return False

    async def wait_for_load(self) -> None:
        """Wait for page to be fully loaded before proceeding"""
        self.logger.info("⏳ Waiting for ItemPage to load...")
        is_loaded = await self.is_loaded()
        if not is_loaded:
            self.logger.error("✗ ItemPage failed to load - no results found")
            raise Exception("ItemPage failed to load after search")
        self.logger.info("✓ ItemPage ready for interaction")

    async def get_item_count(self) -> int:
        """Get total number of items on current page"""
        count = await self.search_page.get_product_count()
        self.logger.info(f"Found {count} items on page")
        return count

    async def minPrice(self, price: float) -> 'ItemPage':
        """Set minimum price filter - returns self for chaining"""
        self._min_price = price
        self.logger.info(f"💰 Min price set to: ${price}")
        return self

    async def maxPrice(self, price: float) -> 'ItemPage':
        """Set maximum price filter - returns self for chaining"""
        self._max_price = price
        self.logger.info(f"💰 Max price set to: ${price}")
        return self

    async def apply_filters(self) -> None:
        """
        Apply all set filters on the ItemPage.
        This actually applies the filters to eBay and updates results.
        """
        self.logger.info(f"⏳ Applying price filters...")

        # Verify page is loaded before filtering
        await self.wait_for_load()

        # Get the filters that were set
        min_price = getattr(self, '_min_price', None)
        max_price = getattr(self, '_max_price', None)

        if min_price is None and max_price is None:
            self.logger.warning("No filters set to apply")
            return

        self.logger.info(f"  → Min: ${min_price}, Max: ${max_price}")

        # Use SearchPage's filter method which handles eBay's filter UI properly
        await self.search_page.filter_by_price_range(min_price, max_price)

        self.logger.info(f"✅ Filters applied successfully")

    async def filter_by_price_range(self, min_price: Optional[float] = None, max_price: Optional[float] = None) -> None:
        """
        Apply price range filters on search results.

        Args:
            min_price: Minimum price (optional)
            max_price: Maximum price (optional)
        """
        self.logger.info(f"⏳ Filtering by price range - Min: ${min_price}, Max: ${max_price}")

        # Verify page is loaded before filtering
        await self.wait_for_load()

        # Use SearchPage's filter method which handles eBay's filter UI properly
        await self.search_page.filter_by_price_range(min_price, max_price)

        self.logger.info(f"✅ Price filters applied")

    async def collect(self, limit: int) -> List[dict]:
        """
        Collect product items from ItemPage.

        If filters were set (minPrice/maxPrice), applies them first.
        Then collects product names and prices up to the specified limit.

        Args:
            limit: Maximum number of items to collect

        Returns:
            List of dicts containing product name and price
        """
        self.logger.info(f"📦 Collecting items from ItemPage (limit={limit})...")

        # If filters were set, apply them first
        if self._min_price is not None or self._max_price is not None:
            self.logger.info(f"  → Applying filters before collection")
            await self.apply_filters()

        # Verify page is loaded
        await self.wait_for_load()

        # Collect items with names and prices
        items = await self.search_page.get_product_names_and_prices(limit=limit)

        self.logger.info(f"✅ Collected {len(items)} items")
        return items

    async def get_items(self) -> List[str]:
        """
        Get all product links from current page

        Returns:
            List of product URLs
        """
        self.logger.info("📦 Getting items from page...")

        # Verify page is loaded
        await self.wait_for_load()

        # Use SearchPage's method to get product links
        items = await self.search_page.get_product_links()

        self.logger.info(f"✅ Retrieved {len(items)} product links")
        return items

    async def get_item_count_with_filters(self) -> int:
        """Get count of items currently displayed after filters"""
        count = await self.get_item_count()
        return count

    async def take_results_screenshot(self, filename: str = "item_results.png") -> str:
        """Take screenshot of item results"""
        filepath = f"screenshots/{filename}"
        await self.page.screenshot(path=filepath)
        self.logger.info(f"Screenshot saved: {filepath}")
        return filepath