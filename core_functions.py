"""
Core test functions for eBay E2E automation.
Implements the three main test scenarios:
1. Search products by name with price filter
2. Add items to cart with variant selection
3. Assert cart total does not exceed budget
"""

from typing import List, Optional, Dict, Any
from playwright.async_api import Page
from pages import SearchPage, SearchBuilder, ProductPage, CartPage
from utils import (
    VariantSelector,
    PriceParser,
    PaginationHandler,
    TestAssertions,
    ScreenshotManager
)
import logging

logger = logging.getLogger(__name__)


async def searchItemsByNameUnderPrice(
    page: Page,
    query: str,
    max_price: float,
    limit: int = 5
) -> List[str]:
    """
    Search for products by name with price filter and pagination support.

    DEPRECATED: Use SearchBuilder for new code.

    Args:
        page: Playwright page object
        query: Search query string (e.g., "shoes")
        max_price: Maximum price threshold
        limit: Number of items to collect (default: 5)

    Returns:
        List of product URLs matching criteria

    Example (deprecated):
        urls = await searchItemsByNameUnderPrice(page, "shoes", 220, 5)

    Example (preferred):
        urls = await (SearchBuilder(page)
            .search("shoes")
            .maxPrice(220)
            .filter()
            .collect(5))
    """
    return await (SearchBuilder(page)
        .search(query)
        .maxPrice(max_price)
        .filter()
        .collect(limit))


async def addItemsToCart(
    page: Page,
    product_urls: List[str],
    select_random_variants: bool = True
) -> Dict[str, Any]:
    """
    Add items to cart with variant selection (size, color, quantity).

    Args:
        page: Playwright page object
        product_urls: List of product URLs to add
        select_random_variants: If True, select random variants; if False, use defaults

    Returns:
        Dictionary with added items count, failed count, and variant selections

    Example:
        result = await addItemsToCart(page, product_urls, select_random_variants=True)
        # Returns {"added": 5, "failed": 0, "variants": [...]}
    """
    logger.info(f"Starting add to cart: {len(product_urls)} items, random_variants={select_random_variants}")

    added_count = 0
    failed_count = 0
    added_items = []

    for idx, url in enumerate(product_urls, 1):
        try:
            logger.info(f"Processing item {idx}/{len(product_urls)}: {url}")

            # Navigate to product page
            await page.goto(url, wait_until="networkidle")
            product_page = ProductPage(page)

            # Get product details
            product_name = await product_page.get_product_name()
            product_price = await product_page.get_product_price()
            logger.info(f"Product: {product_name} - ${product_price}")

            # Select variants
            if select_random_variants:
                variants = await product_page.select_random_variants()
                logger.info(f"Selected random variants: {variants}")
            else:
                # Use first available options
                sizes = await product_page.get_available_sizes()
                colors = await product_page.get_available_colors()

                size = sizes[0] if sizes else None
                color = colors[0] if colors else None

                await product_page.select_specific_variants(size, color, quantity=1)
                variants = {"size": size, "color": color, "quantity": 1}
                logger.info(f"Selected default variants: {variants}")

            # Add to cart
            success = await product_page.add_to_cart()

            if success:
                added_count += 1
                item_data = {
                    "name": product_name,
                    "price": product_price,
                    "url": url,
                    "variants": variants
                }
                added_items.append(item_data)
                logger.info(f"✓ Item {idx} added to cart")

                # Take screenshot
                await product_page.take_product_screenshot(f"item_{idx}_{product_name.replace(' ', '_')}_added.png")
            else:
                failed_count += 1
                logger.error(f"✗ Item {idx} failed to add to cart")
                await product_page.take_screenshot(f"item_{idx}_failed.png")

        except Exception as e:
            failed_count += 1
            logger.error(f"Error processing item {idx}: {e}")
            try:
                await page.screenshot(path=f"screenshots/item_{idx}_exception.png")
            except:
                pass
            continue

    result = {
        "total": len(product_urls),
        "added": added_count,
        "failed": failed_count,
        "added_items": added_items
    }

    logger.info(f"Add to cart complete: {added_count} added, {failed_count} failed")
    return result


async def assertCartTotalNotExceeds(
    page: Page,
    budget_per_item: float,
    items_count: int,
    take_screenshot: bool = True
) -> Dict[str, Any]:
    """
    Verify that cart total does not exceed budget per item * items count.

    Args:
        page: Playwright page object
        budget_per_item: Maximum price per item
        items_count: Number of items in cart
        take_screenshot: Whether to take screenshot (default: True)

    Returns:
        Dictionary with cart summary and assertion results

    Raises:
        AssertionError: If cart total exceeds threshold

    Example:
        result = await assertCartTotalNotExceeds(page, 220, 5)
        # Asserts: cart_total <= 220 * 5 = $1100
    """
    logger.info(f"Starting cart assertion: budget_per_item=${budget_per_item}, items_count={items_count}")

    try:
        # Navigate to cart
        cart_page = CartPage(page)

        # Get cart summary
        summary = await cart_page.get_cart_summary()
        logger.info(f"Cart summary: {summary}")

        actual_total = summary["total"]
        max_threshold = budget_per_item * items_count

        logger.info(f"Assertion check: ${actual_total:.2f} <= ${max_threshold:.2f}")

        # Perform assertion
        if actual_total > max_threshold:
            logger.error(f"ASSERTION FAILED: Cart total ${actual_total:.2f} exceeds threshold ${max_threshold:.2f}")

            if take_screenshot:
                await cart_page.take_cart_screenshot("cart_assertion_failed.png")

            raise AssertionError(
                f"Cart total ${actual_total:.2f} exceeds budget threshold ${max_threshold:.2f}"
            )

        # Get all items for verification
        items = await cart_page.get_all_cart_items()
        logger.info(f"Cart items: {len(items)} items")

        # Take screenshot of successful assertion
        if take_screenshot:
            await cart_page.take_cart_screenshot("cart_assertion_passed.png")

        result = {
            "assertion_passed": True,
            "actual_total": actual_total,
            "max_threshold": max_threshold,
            "cart_summary": summary,
            "items_count": len(items),
            "items": items,
            "message": f"Cart total ${actual_total:.2f} is within budget ${max_threshold:.2f}"
        }

        logger.info(f"✓ ASSERTION PASSED: {result['message']}")
        return result

    except AssertionError as e:
        logger.error(f"Assertion error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error during cart assertion: {e}")
        await page.screenshot(path="screenshots/cart_assertion_error.png")
        raise


async def run_end_to_end_test(
    page: Page,
    search_query: str,
    max_price: float,
    items_limit: int = 5,
    select_random_variants: bool = True
) -> Dict[str, Any]:
    """
    Run complete end-to-end test scenario:
    1. Search products by name with price filter
    2. Add items to cart
    3. Verify cart total does not exceed budget

    Args:
        page: Playwright page object
        search_query: Product search query
        max_price: Maximum price per item
        items_limit: Number of items to add
        select_random_variants: Whether to select random variants

    Returns:
        Complete test results

    Example:
        result = await run_end_to_end_test(page, "shoes", 220, 5, True)
    """
    logger.info(f"Starting E2E test: search='{search_query}', max_price=${max_price}, limit={items_limit}")

    test_result = {
        "status": "PASSED",
        "search": None,
        "add_to_cart": None,
        "assertion": None,
        "errors": []
    }

    try:
        # Step 1: Search for products
        logger.info("=== STEP 1: Search Products ===")
        product_urls = await (SearchBuilder(page)
            .search(search_query)
            .maxPrice(max_price)
            .filter()
            .collect(items_limit))
        test_result["search"] = {
            "query": search_query,
            "max_price": max_price,
            "found_count": len(product_urls),
            "urls": product_urls
        }

        if not product_urls:
            raise Exception(f"No products found for query: {search_query}")

        # Step 2: Add items to cart
        logger.info("=== STEP 2: Add Items to Cart ===")
        add_result = await addItemsToCart(page, product_urls, select_random_variants)
        test_result["add_to_cart"] = add_result

        if add_result["added"] == 0:
            raise Exception("Failed to add any items to cart")

        # Step 3: Assert cart total
        logger.info("=== STEP 3: Assert Cart Total ===")
        assertion_result = await assertCartTotalNotExceeds(
            page,
            max_price,
            add_result["added"],
            take_screenshot=True
        )
        test_result["assertion"] = assertion_result

        logger.info(f"✓ E2E TEST PASSED")
        return test_result

    except Exception as e:
        logger.error(f"✗ E2E TEST FAILED: {e}")
        test_result["status"] = "FAILED"
        test_result["errors"].append(str(e))
        raise