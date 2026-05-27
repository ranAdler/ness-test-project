from typing import List, Optional, Callable, Any
import logging

logger = logging.getLogger(__name__)


class PaginationHandler:
    """Utility for handling pagination in test scenarios"""

    def __init__(self, items_per_page: int = 10, max_pages: Optional[int] = None):
        """Initialize pagination handler"""
        self.items_per_page = items_per_page
        self.max_pages = max_pages
        self.current_page = 1
        self.total_items_collected = 0
        logger.info(f"Pagination handler initialized: {items_per_page} items/page, max {max_pages} pages")

    async def collect_items_with_pagination(
        self,
        get_items_func: Callable,
        has_next_func: Callable,
        next_page_func: Callable,
        limit: int = 5
    ) -> List[Any]:
        """
        Collect items across multiple pages up to limit.

        Args:
            get_items_func: Async function to get items from current page
            has_next_func: Async function to check if next page exists
            next_page_func: Async function to navigate to next page
            limit: Maximum number of items to collect
        """
        logger.info(f"Starting pagination collection with limit={limit}")
        all_items = []
        self.current_page = 1

        while len(all_items) < limit:
            # Get items from current page
            current_page_items = await get_items_func()
            all_items.extend(current_page_items)

            logger.info(f"Page {self.current_page}: Got {len(current_page_items)} items (total: {len(all_items)})")

            # Stop if we have enough items
            if len(all_items) >= limit:
                break

            # Check if next page exists
            has_next = await has_next_func()
            if not has_next:
                logger.info("No more pages available")
                break

            # Check max pages limit
            if self.max_pages and self.current_page >= self.max_pages:
                logger.info(f"Reached maximum pages limit: {self.max_pages}")
                break

            # Go to next page
            await next_page_func()
            self.current_page += 1
            logger.info(f"Moving to page {self.current_page}")

        # Return only up to limit
        result = all_items[:limit]
        self.total_items_collected = len(result)
        logger.info(f"Pagination complete: Collected {len(result)} items from {self.current_page} pages")
        return result

    async def iterate_all_pages(
        self,
        process_func: Callable,
        has_next_func: Callable,
        next_page_func: Callable
    ) -> int:
        """
        Iterate through all pages and process each.

        Args:
            process_func: Async function to process items on current page
            has_next_func: Async function to check if next page exists
            next_page_func: Async function to navigate to next page

        Returns:
            Total number of pages processed
        """
        logger.info("Starting page iteration")
        self.current_page = 1

        while True:
            # Process current page
            await process_func()
            logger.info(f"Processed page {self.current_page}")

            # Check if next page exists
            has_next = await has_next_func()
            if not has_next:
                logger.info("No more pages available")
                break

            # Check max pages limit
            if self.max_pages and self.current_page >= self.max_pages:
                logger.info(f"Reached maximum pages limit: {self.max_pages}")
                break

            # Go to next page
            await next_page_func()
            self.current_page += 1

        logger.info(f"Page iteration complete: Processed {self.current_page} pages")
        return self.current_page

    @staticmethod
    def calculate_page_number(item_index: int, items_per_page: int) -> int:
        """Calculate which page an item is on"""
        page = (item_index // items_per_page) + 1
        return page

    @staticmethod
    def calculate_position_on_page(item_index: int, items_per_page: int) -> int:
        """Calculate position of item on its page"""
        position = (item_index % items_per_page) + 1
        return position

    @staticmethod
    def get_page_range(total_items: int, items_per_page: int) -> tuple:
        """Get total pages for items"""
        total_pages = (total_items + items_per_page - 1) // items_per_page
        return (1, total_pages)