from playwright.async_api import Page
from typing import List, Optional, Dict
from .base_page import BasePage
import logging
import re

logger = logging.getLogger(__name__)


class CartPage(BasePage):
    """Shopping cart page object for eBay-like e-commerce site"""

    # Cart Items Locators
    CART_ITEMS = "//div[@class*='cart-item'], //li[@class*='cart-item'], .cart-item, [class*='cart-product']"
    ITEM_NAME = ".item-name, .product-name, h3, h4"
    ITEM_PRICE = ".item-price, .product-price, [class*='price']"
    ITEM_QUANTITY = ".item-quantity, input[type='number'], [class*='quantity']"
    ITEM_TOTAL = ".item-total, [class*='total']"

    # Remove/Update Item
    REMOVE_ITEM_BUTTON = "button:has-text('Remove'), button:has-text('Delete'), a:has-text('Remove')"
    UPDATE_QUANTITY_BUTTON = "button:has-text('Update'), button:has-text('Apply')"

    # Cart Totals
    SUBTOTAL = "//span[@class*='subtotal'], .subtotal, [class*='subtotal']"
    TAX = "//span[@class*='tax'], .tax, [class*='tax']"
    SHIPPING = "//span[@class*='shipping'], .shipping, [class*='shipping']"
    DISCOUNT = "//span[@class*='discount'], .discount, [class*='discount']"
    TOTAL = "//span[@class*='total'], .total, [class*='grand-total'], .order-total"

    # Checkout/Actions
    CHECKOUT_BUTTON = "button:has-text('Checkout'), button:has-text('Proceed to Checkout'), a:has-text('Checkout')"
    CONTINUE_SHOPPING_BUTTON = "button:has-text('Continue Shopping'), a:has-text('Continue Shopping')"
    COUPON_INPUT = "input[placeholder*='Coupon'], input[name*='coupon'], input[id*='coupon']"
    APPLY_COUPON_BUTTON = "button:has-text('Apply Coupon'), button:has-text('Apply')"

    # Cart Status
    EMPTY_CART_MESSAGE = "//div[@class*='empty'], .empty-cart, [class*='no-items']"
    CART_ITEM_COUNT = "//span[@class*='count'], .item-count, [class*='cart-count']"

    async def is_cart_empty(self) -> bool:
        """Check if cart is empty"""
        try:
            is_empty = await self.is_visible(self.EMPTY_CART_MESSAGE)
            logger.info(f"Cart empty: {is_empty}")
            return is_empty
        except:
            # If empty message not found, cart likely has items
            count = await self.get_cart_item_count()
            is_empty = count == 0
            logger.info(f"Cart empty (by count): {is_empty}")
            return is_empty

    async def get_cart_item_count(self) -> int:
        """Get number of items in cart"""
        try:
            count_text = await self.get_text(self.CART_ITEM_COUNT)
            count = int(''.join(c for c in count_text if c.isdigit()))
            logger.info(f"Cart item count: {count}")
            return count
        except:
            # Count cart item elements instead
            count = await self.get_element_count(self.CART_ITEMS)
            logger.info(f"Cart item count (by elements): {count}")
            return count

    async def get_all_cart_items(self) -> List[Dict[str, any]]:
        """Get details of all items in cart"""
        logger.info("Retrieving all cart items")
        items = []

        item_elements = await self.page.locator(self.CART_ITEMS).all()

        for idx, item_element in enumerate(item_elements):
            try:
                # Get item details
                name = await item_element.locator(self.ITEM_NAME).text_content()
                price_text = await item_element.locator(self.ITEM_PRICE).text_content()
                quantity_elem = await item_element.locator(self.ITEM_QUANTITY).input_value()
                total_text = await item_element.locator(self.ITEM_TOTAL).text_content()

                # Parse prices
                price = self._parse_price(price_text) if price_text else 0.0
                total = self._parse_price(total_text) if total_text else 0.0
                quantity = int(quantity_elem) if quantity_elem else 1

                item_data = {
                    "index": idx,
                    "name": name.strip() if name else "",
                    "price": price,
                    "quantity": quantity,
                    "total": total
                }
                items.append(item_data)
                logger.info(f"Item {idx + 1}: {item_data}")
            except Exception as e:
                logger.warning(f"Error retrieving item {idx}: {e}")
                continue

        logger.info(f"Retrieved {len(items)} items from cart")
        return items

    async def get_item_by_name(self, name: str) -> Optional[Dict[str, any]]:
        """Get specific item from cart by name"""
        logger.info(f"Getting item by name: {name}")
        items = await self.get_all_cart_items()
        for item in items:
            if name.lower() in item["name"].lower():
                logger.info(f"Found item: {item}")
                return item
        logger.warning(f"Item '{name}' not found in cart")
        return None

    async def get_subtotal(self) -> float:
        """Get subtotal amount"""
        try:
            subtotal_text = await self.get_text(self.SUBTOTAL)
            subtotal = self._parse_price(subtotal_text)
            logger.info(f"Subtotal: ${subtotal}")
            return subtotal
        except:
            logger.warning("Could not retrieve subtotal")
            return 0.0

    async def get_tax(self) -> float:
        """Get tax amount"""
        try:
            tax_text = await self.get_text(self.TAX)
            tax = self._parse_price(tax_text)
            logger.info(f"Tax: ${tax}")
            return tax
        except:
            logger.warning("Could not retrieve tax")
            return 0.0

    async def get_shipping(self) -> float:
        """Get shipping cost"""
        try:
            shipping_text = await self.get_text(self.SHIPPING)
            shipping = self._parse_price(shipping_text)
            logger.info(f"Shipping: ${shipping}")
            return shipping
        except:
            logger.warning("Could not retrieve shipping cost")
            return 0.0

    async def get_discount(self) -> float:
        """Get discount amount"""
        try:
            discount_text = await self.get_text(self.DISCOUNT)
            discount = self._parse_price(discount_text)
            logger.info(f"Discount: ${discount}")
            return discount
        except:
            logger.warning("Could not retrieve discount")
            return 0.0

    async def get_cart_total(self) -> float:
        """Get cart grand total"""
        try:
            total_text = await self.get_text(self.TOTAL)
            total = self._parse_price(total_text)
            logger.info(f"Cart total: ${total}")
            return total
        except Exception as e:
            logger.error(f"Could not retrieve cart total: {e}")
            raise

    async def get_cart_summary(self) -> Dict[str, float]:
        """Get complete cart summary with all totals"""
        logger.info("Retrieving cart summary")
        summary = {
            "subtotal": await self.get_subtotal(),
            "tax": await self.get_tax(),
            "shipping": await self.get_shipping(),
            "discount": await self.get_discount(),
            "total": await self.get_cart_total(),
            "item_count": await self.get_cart_item_count()
        }
        logger.info(f"Cart summary: {summary}")
        return summary

    async def update_item_quantity(self, item_index: int, new_quantity: int) -> bool:
        """Update quantity for item at index"""
        logger.info(f"Updating quantity for item {item_index} to {new_quantity}")
        try:
            items = await self.page.locator(self.CART_ITEMS).all()
            if item_index >= len(items):
                logger.error(f"Item index {item_index} out of range")
                return False

            item_element = items[item_index]
            quantity_input = item_element.locator(self.ITEM_QUANTITY)
            await quantity_input.fill(str(new_quantity))
            await self.click(self.UPDATE_QUANTITY_BUTTON)
            await self.page.wait_for_load_state("networkidle", timeout=5000)
            logger.info(f"Updated quantity successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update quantity: {e}")
            return False

    async def remove_item(self, item_index: int) -> bool:
        """Remove item from cart by index"""
        logger.info(f"Removing item at index {item_index}")
        try:
            items = await self.page.locator(self.CART_ITEMS).all()
            if item_index >= len(items):
                logger.error(f"Item index {item_index} out of range")
                return False

            item_element = items[item_index]
            remove_button = item_element.locator(self.REMOVE_ITEM_BUTTON)
            await remove_button.click()
            await self.page.wait_for_load_state("networkidle", timeout=5000)
            logger.info(f"Item removed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to remove item: {e}")
            return False

    async def remove_item_by_name(self, name: str) -> bool:
        """Remove item from cart by name"""
        logger.info(f"Removing item: {name}")
        item = await self.get_item_by_name(name)
        if item:
            return await self.remove_item(item["index"])
        logger.warning(f"Could not find item '{name}' to remove")
        return False

    async def apply_coupon(self, coupon_code: str) -> bool:
        """Apply coupon code to cart"""
        logger.info(f"Applying coupon: {coupon_code}")
        try:
            await self.fill(self.COUPON_INPUT, coupon_code)
            await self.click(self.APPLY_COUPON_BUTTON)
            await self.page.wait_for_load_state("networkidle", timeout=5000)
            logger.info("Coupon applied successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to apply coupon: {e}")
            return False

    async def proceed_to_checkout(self) -> bool:
        """Click proceed to checkout button"""
        logger.info("Proceeding to checkout")
        try:
            await self.click(self.CHECKOUT_BUTTON)
            await self.wait_for_navigation()
            logger.info("Proceeding to checkout successful")
            return True
        except Exception as e:
            logger.error(f"Failed to proceed to checkout: {e}")
            return False

    async def continue_shopping(self) -> bool:
        """Click continue shopping button"""
        logger.info("Continuing shopping")
        try:
            await self.click(self.CONTINUE_SHOPPING_BUTTON)
            await self.wait_for_navigation()
            logger.info("Continuing shopping successful")
            return True
        except Exception as e:
            logger.error(f"Failed to continue shopping: {e}")
            return False

    async def verify_cart_total_under_budget(self, budget: float) -> bool:
        """Verify cart total is under specified budget"""
        logger.info(f"Verifying cart total is under ${budget}")
        total = await self.get_cart_total()
        is_under_budget = total <= budget
        logger.info(f"Cart total ${total} is under ${budget}: {is_under_budget}")
        return is_under_budget

    async def verify_expected_items_count(self, expected_count: int) -> bool:
        """Verify cart has expected number of items"""
        logger.info(f"Verifying cart has {expected_count} items")
        actual_count = await self.get_cart_item_count()
        matches = actual_count == expected_count
        logger.info(f"Expected {expected_count} items, found {actual_count}: {matches}")
        return matches

    async def verify_item_in_cart(self, item_name: str) -> bool:
        """Verify specific item is in cart"""
        logger.info(f"Verifying item '{item_name}' is in cart")
        item = await self.get_item_by_name(item_name)
        is_present = item is not None
        logger.info(f"Item '{item_name}' in cart: {is_present}")
        return is_present

    async def take_cart_screenshot(self, filename: str = "cart_page.png") -> str:
        """Take screenshot of cart page"""
        logger.info("Taking screenshot of cart page")
        return await self.take_screenshot(filename)

    @staticmethod
    def _parse_price(price_text: str) -> float:
        """Helper method to parse price from text"""
        try:
            # Remove common currency symbols and text
            clean_text = re.sub(r'[^\d.]', '', price_text)
            # Handle multiple decimal points
            if clean_text.count('.') > 1:
                parts = clean_text.rsplit('.', 1)
                clean_text = parts[0].replace('.', '') + '.' + parts[1]
            price = float(clean_text) if clean_text else 0.0
            return price
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse price from: {price_text}")
            return 0.0

    async def assert_cart_total_not_exceeds(self, max_amount: float, items_count: int) -> None:
        """Assert cart total does not exceed max_amount * items_count"""
        logger.info(f"Asserting cart total does not exceed ${max_amount} * {items_count} = ${max_amount * items_count}")
        actual_total = await self.get_cart_total()
        max_threshold = max_amount * items_count

        if actual_total > max_threshold:
            logger.error(f"Cart total ${actual_total} exceeds threshold ${max_threshold}")
            await self.take_cart_screenshot("cart_assertion_failed.png")
            raise AssertionError(
                f"Cart total ${actual_total:.2f} exceeds threshold ${max_threshold:.2f}"
            )

        logger.info(f"Cart total ${actual_total:.2f} is within threshold ${max_threshold:.2f}")