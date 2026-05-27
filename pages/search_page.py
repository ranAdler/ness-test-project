from playwright.async_api import Page
from typing import List, Optional
from .base_page import BasePage
import logging

logger = logging.getLogger(__name__)


class SearchPage(BasePage):
    """Search page object for eBay-like e-commerce site"""

    # Locators
    SEARCH_INPUT = "#gh-ac"  # eBay search input by ID
    SEARCH_BUTTON = "#gh-search-btn"  # eBay search button by ID

    # Price Filter Locators
    MIN_PRICE_INPUT = "input[aria-label*='Minimum']"  # eBay min price input
    MAX_PRICE_INPUT = "input[aria-label*='Maximum']"  # eBay max price input
    PRICE_FILTER_BUTTON = "button[aria-label='Submit price range']"  # eBay price filter submit button

    # Product Results Locators
    PRODUCT_ITEMS = "a[href*='/itm/']"
    PRODUCT_NAME = "span[class*='product-name']"
    PRODUCT_PRICE = "span[class*='price']"
    PRODUCT_CARD = "li.s-card.s-card--vertical"
    PRODUCT_CARD_TITLE = ".s-card__title span.su-styled-text"
    PRODUCT_CARD_PRICE = ".s-card__price"

    # Pagination Locators
    NEXT_BUTTON = "a:has-text('Next')"
    PREV_BUTTON = "a:has-text('Previous')"
    PAGINATION_INFO = ".pagination-info"

    # Filters & Sort
    SORT_DROPDOWN = "select[name='sort']"
    CATEGORY_FILTER = "input[type='checkbox']"

    async def search_products(self, query: str) -> None:
        """Perform product search"""
        logger.info(f"Searching for: {query}")
        await self.fill(self.SEARCH_INPUT, query)
        await self.click(self.SEARCH_BUTTON)
        logger.info("Waiting for search results to load...")
        await self.wait_for_element(self.PRODUCT_ITEMS, timeout=15000)
        logger.info("Search results loaded")

    async def search(self, query: str) -> None:
        """
        Search for products and verify results page is loaded.

        Steps:
        1. Set the text in search input
        2. Click on search button
        3. Verify search results page is loaded
        4. Move to the next page
        """
        logger.info(f"Performing search for: {query}")

        # Step 1-2: Fill search input and click search
        await self.fill(self.SEARCH_INPUT, query)
        await self.click(self.SEARCH_BUTTON)

        # Step 3: Wait for search results to load
        logger.info("Waiting for search results page to load...")
        await self.wait_for_element(self.PRODUCT_ITEMS, timeout=15000)
        logger.info("✓ Search results page loaded")

        # Step 4: Move to next page if available
        logger.info("Moving to next page if available...")
        await self.go_to_next_page()

    async def execute_search(self) -> None:
        """
        Execute search when input is already filled.

        Steps:
        1. Click on search button
        2. Wait for page navigation
        3. Validate results page is loaded
        4. Continue to the next page if available
        """
        logger.info("🔍 Executing search (input already filled)")

        # Step 1: Click search button
        logger.info(f"Clicking search button: {self.SEARCH_BUTTON}")
        await self.click(self.SEARCH_BUTTON)

        # # Step 2: Wait for page navigation to complete
        # logger.info("Waiting for page navigation...")
        # await self.wait_for_navigation()

        # Step 3: Validate search results page is loaded
        logger.info("Waiting for search results page to load...")
        await self.wait_for_element(self.PRODUCT_ITEMS, timeout=15000)
        logger.info("✓ Search results page loaded with product items")

        # Step 4: Continue to next page if available
        logger.info("Moving to next page if available...")
        await self.go_to_next_page()

    async def scroll_to_price_filter(self) -> None:
        """Scroll to price filter inputs"""
        logger.info("Scrolling to price filter...")
        try:
            await self.scroll_to_element(self.MIN_PRICE_INPUT)
            logger.info("Price filter is now visible")
        except Exception as e:
            logger.warning(f"Could not scroll to price filter: {e}")

    async def set_min_price(self, price: float) -> None:
        """Set minimum price filter"""
        logger.info(f"💰 Setting minimum price: ${price}")

        # Scroll to price filter to make it visible
        await self.scroll_to_price_filter()

        # Click on the input to focus it
        await self.click(self.MIN_PRICE_INPUT)

        # Clear the field
        await self.page.locator(self.MIN_PRICE_INPUT).clear()

        # Fill with the price
        await self.fill(self.MIN_PRICE_INPUT, str(price))
        logger.info(f"✅ Minimum price set to: ${price}")

    async def set_max_price(self, price: float) -> None:
        """Set maximum price filter"""
        logger.info(f"💰 Setting maximum price: ${price}")

        # Scroll to price filter to make it visible
        await self.scroll_to_price_filter()

        # Click on the input to focus it
        await self.click(self.MAX_PRICE_INPUT)

        # Clear the field
        await self.page.locator(self.MAX_PRICE_INPUT).clear()

        # Fill with the price
        await self.fill(self.MAX_PRICE_INPUT, str(price))
        logger.info(f"✅ Maximum price set to: ${price}")

    async def apply_price_filter(self) -> None:
        """Apply price filter"""
        logger.info("Applying price filter")
        await self.click(self.PRICE_FILTER_BUTTON)
        logger.info("Waiting for filtered results...")
        await self.wait_for_element(self.PRODUCT_ITEMS, timeout=15000)
        logger.info("Filtered results loaded")

    async def filter_by_price_range(self, min_price: Optional[float] = None, max_price: Optional[float] = None) -> None:
        """Apply price range filter"""
        if min_price is not None:
            await self.set_min_price(min_price)
        if max_price is not None:
            await self.set_max_price(max_price)
        await self.apply_price_filter()

    async def get_product_count(self) -> int:
        """Get total number of products on current page"""
        count = await self.get_element_count(self.PRODUCT_ITEMS)
        logger.info(f"Found {count} products on page")
        return count

    async def get_product_links(self) -> List[str]:
        """Get all product links from current page"""
        logger.info("Extracting product links")
        elements = await self.page.locator(self.PRODUCT_ITEMS).all()
        links = []

        for element in elements:
            href = await element.get_attribute("href")
            if href:
                # Handle relative URLs
                if href.startswith("http"):
                    links.append(href)
                else:
                    base_url = await self.get_current_url()
                    full_url = base_url.rstrip("/") + "/" + href.lstrip("/")
                    links.append(full_url)

        logger.info(f"Extracted {len(links)} product links")
        return links

    async def get_product_prices(self) -> List[float]:
        """Extract all product prices from current page"""
        logger.info("Extracting product prices")
        price_texts = await self.get_all_texts(self.PRODUCT_PRICE)
        prices = []

        for price_text in price_texts:
            try:
                # Remove currency symbols and convert to float
                clean_price = ''.join(c for c in price_text if c.isdigit() or c == '.')
                if clean_price:
                    prices.append(float(clean_price))
            except (ValueError, AttributeError) as e:
                logger.warning(f"Could not parse price: {price_text}, error: {e}")

        logger.info(f"Extracted {len(prices)} prices")
        return prices

    async def get_products_under_price(self, max_price: Optional[float]) -> List[str]:
        """Get product links where price <= max_price (if max_price is set)"""
        all_links = await self.get_product_links()

        if max_price is None:
            logger.info(f"No price filter applied, returning all {len(all_links)} products")
            return all_links

        logger.info(f"Getting products under ${max_price}")
        all_prices = await self.get_product_prices()

        products_under_price = [
            link for link, price in zip(all_links, all_prices)
            if price <= max_price
        ]

        logger.info(f"Found {len(products_under_price)} products under ${max_price}")
        return products_under_price

    async def has_next_page(self) -> bool:
        """Check if next page button is available"""
        is_available = await self.is_visible(self.NEXT_BUTTON)
        logger.info(f"Next button available: {is_available}")
        return is_available

    async def go_to_next_page(self) -> None:
        """Navigate to next page"""
        logger.info("Going to next page")
        if await self.has_next_page():
            await self.click(self.NEXT_BUTTON)
            logger.info("Waiting for next page to load...")
            await self.wait_for_element(self.PRODUCT_ITEMS, timeout=15000)
            logger.info("Next page loaded")
        else:
            logger.warning("Next button not available")

    async def has_prev_page(self) -> bool:
        """Check if previous page button is available"""
        is_available = await self.is_visible(self.PREV_BUTTON)
        logger.info(f"Previous button available: {is_available}")
        return is_available

    async def go_to_prev_page(self) -> None:
        """Navigate to previous page"""
        logger.info("Going to previous page")
        if await self.has_prev_page():
            await self.click(self.PREV_BUTTON)
            await self.wait_for_navigation()
        else:
            logger.warning("Previous button not available")

    async def get_pagination_info(self) -> Optional[str]:
        """Get pagination information (e.g., 'Page 1 of 5')"""
        try:
            info = await self.get_text(self.PAGINATION_INFO)
            logger.info(f"Pagination info: {info}")
            return info
        except:
            logger.warning("Could not retrieve pagination info")
            return None

    async def sort_products(self, sort_option: str) -> None:
        """Sort products by option"""
        logger.info(f"Sorting by: {sort_option}")
        await self.select_option(self.SORT_DROPDOWN, sort_option)
        logger.info("Waiting for sorted results...")
        await self.wait_for_element(self.PRODUCT_ITEMS, timeout=15000)
        logger.info("Sorted results loaded")

    async def search_and_filter_by_price(self, query: str, max_price: float) -> List[str]:
        """Combined search and price filter operation"""
        logger.info(f"Searching '{query}' with max price ${max_price}")
        await self.search_products(query)
        await self.filter_by_price_range(max_price=max_price)
        return await self.get_products_under_price(max_price)

    async def get_products_paginated(self, max_price: float, limit: int = 5) -> List[str]:
        """Get products with pagination support up to limit"""
        logger.info(f"Getting products paginated (limit={limit}, max_price=${max_price})")
        all_products = []

        while len(all_products) < limit:
            # Get products from current page
            products = await self.get_products_under_price(max_price)
            all_products.extend(products)

            # Stop if we have enough products
            if len(all_products) >= limit:
                break

            # Check if next page exists
            if not await self.has_next_page():
                logger.info("No more pages available")
                break

            # Go to next page
            await self.go_to_next_page()

        # Return only up to limit
        result = all_products[:limit]
        logger.info(f"Returning {len(result)} products")
        return result

    async def get_product_names_and_prices(self, limit: int = None) -> List[dict]:
        """Extract product names and prices from cards up to limit"""
        logger.info(f"Extracting product names and prices (limit={limit})")
        items = []

        cards = await self.page.locator(self.PRODUCT_CARD).all()
        logger.info(f"Found {len(cards)} product cards")

        for i, card in enumerate(cards):
            if limit and len(items) >= limit:
                break

            try:
                # Extract name
                name_elem = card.locator(self.PRODUCT_CARD_TITLE)
                name = await name_elem.text_content() if await name_elem.is_visible() else "N/A"

                # Extract price
                price_elem = card.locator(self.PRODUCT_CARD_PRICE)
                price_text = await price_elem.text_content() if await price_elem.is_visible() else "N/A"

                items.append({
                    "name": name.strip() if name else "N/A",
                    "price": price_text.strip() if price_text else "N/A"
                })
            except Exception as e:
                logger.warning(f"Could not extract data from card {i}: {e}")

        logger.info(f"Extracted {len(items)} product items")
        return items

    async def take_search_results_screenshot(self, filename: str = "search_results.png") -> str:
        """Take screenshot of search results"""
        logger.info("Taking screenshot of search results")
        return await self.take_screenshot(filename)