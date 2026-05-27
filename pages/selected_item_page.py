"""
Selected Item Page - Represents a single item/product page
Handles Add to Cart functionality and dialog interactions
"""

from playwright.async_api import Page
from typing import Optional
from .base_page import BasePage
import logging

logger = logging.getLogger(__name__)


class FluentAsyncChain:
    """Enables fluent chaining of async methods without explicit await on each call"""
    def __init__(self, page_obj):
        self.page_obj = page_obj
        self._operations = []

    def _add_operation(self, method_name, *args):
        self._operations.append((method_name, args))
        return self

    def add_to_cart(self):
        return self._add_operation('add_to_cart')

    def see_in_cart(self):
        return self._add_operation('see_in_cart')

    def verify_item_title(self, title):
        return self._add_operation('verify_item_title', title)

    def verify_item_price(self, price):
        return self._add_operation('verify_item_price', price)

    async def __call__(self):
        for method_name, args in self._operations:
            method = getattr(self.page_obj, f'_{method_name}_impl')
            await method(*args)

    def __await__(self):
        return self().__await__()


class SelectedItemPage(BasePage):
    """Page object for eBay item detail page with Add to Cart functionality"""

    # Search Result Link - First product card link
    # Selector targets: <a class="s-card__link"> with href attribute
    FIRST_SEARCH_RESULT = ".s-card__link"

    # Add to Cart Button
    ADD_TO_CART_BUTTON = "//span[@class='ux-call-to-action__text'][contains(text(), 'Add to cart')]"
    ADD_TO_CART_BUTTON_ALT = "button:has(span:has-text('Add to cart'))"

    # Add to Cart Dialog
    DIALOG_CONTAINER = ".lightbox-dialog.ux-overlay > .lightbox-dialog__window"
    DIALOG_HEADER = "h2.lightbox-dialog__title"
    DIALOG_CLOSE_BUTTON = "button.lightbox-dialog__close"

    # Item Details in Dialog
    DIALOG_ITEM_IMAGE = ".x-atc-layer-v3--info img"
    DIALOG_ITEM_TITLE = "div.item-details_card--title .ux-textspans"
    DIALOG_ITEM_PRICE = ".item-details--price .ux-textspans"

    # Dialog Action Buttons
    SEE_IN_CART_BUTTON = "//a[@href='**/cart**']//span[contains(text(), 'See in cart')]"
    SEE_IN_CART_BUTTON_ALT = ".lightbox-dialog.ux-overlay a.ux-call-to-action:has-text('See in cart')"
    CHECKOUT_BUTTON = "//a[@href='**/checkout**']//span[contains(text(), 'Checkout')]"
    CHECKOUT_BUTTON_ALT = ".lightbox-dialog.ux-overlay a.ux-call-to-action:has-text('Checkout 1 item')"

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self._fluent_chain = None
        logger.info("📱 SelectedItemPage initialized")

    def add_to_cart(self) -> FluentAsyncChain:
        """Start fluent chain with add_to_cart operation"""
        if self._fluent_chain is None:
            self._fluent_chain = FluentAsyncChain(self)
        return self._fluent_chain.add_to_cart()

    async def _add_to_cart_impl(self) -> None:
        """Implementation of add to cart"""
        logger.info("⏳ Clicking Add to Cart button...")
        try:
            # Try main selector first
            try:
                await self.page.locator(self.ADD_TO_CART_BUTTON).click(timeout=5000)
                logger.info("✅ Add to Cart button clicked")
            except:
                # Try alternative selector
                await self.page.locator(self.ADD_TO_CART_BUTTON_ALT).click(timeout=5000)
                logger.info("✅ Add to Cart button clicked (alt selector)")

            # Wait for dialog to appear
            await self.is_add_to_cart_dialog_visible()
        except Exception as e:
            logger.error(f"❌ Failed to click Add to Cart button: {e}")
            raise

    async def _see_in_cart_impl(self) -> None:
        """Implementation of see in cart"""
        logger.info("📍 Clicking 'See in cart' button...")
        try:
            # Try main selector first
            try:
                await self.page.locator(self.SEE_IN_CART_BUTTON).click(timeout=5000)
                logger.info("✅ 'See in cart' button clicked")
            except:
                # Try alternative selector
                await self.page.locator(self.SEE_IN_CART_BUTTON_ALT).click(timeout=5000)
                logger.info("✅ 'See in cart' button clicked (alt selector)")

            # Wait for navigation to cart page
            await self.page.wait_for_url("**/cart**", timeout=10000)
            logger.info("✅ Navigated to cart page")
        except Exception as e:
            logger.error(f"❌ Failed to navigate to cart: {e}")
            raise

    async def _verify_item_title_impl(self, expected_title: str) -> None:
        """Implementation of verify item title on current page"""
        logger.info(f"🔍 Verifying item title contains '{expected_title}'...")
        try:
            # Look for the title text anywhere on the page
            locator = self.page.locator(f"text={expected_title}")
            is_visible = await locator.is_visible(timeout=5000)
            assert is_visible, f"Expected to find '{expected_title}' on the page"
            logger.info(f"✅ Item title verified: {expected_title}")
        except Exception as e:
            logger.error(f"❌ Failed to verify item title: {e}")
            raise

    async def _verify_item_price_impl(self, expected_price: str) -> None:
        """Implementation of verify item price on current page"""
        logger.info(f"💰 Verifying item price contains '{expected_price}'...")
        try:
            # Look for the price text anywhere on the page
            locator = self.page.locator(f"text={expected_price}")
            is_visible = await locator.is_visible(timeout=5000)
            assert is_visible, f"Expected to find '{expected_price}' on the page"
            logger.info(f"✅ Item price verified: {expected_price}")
        except Exception as e:
            logger.error(f"❌ Failed to verify item price: {e}")
            raise

    async def click_first_search_result(self) -> bool:
        """
        Navigate to the first product in search results by getting href attribute.

        Targets: <a class="s-card__link" href="https://www.ebay.com/itm/...">

        Returns:
            bool - True if navigation was successful
        """
        logger.info("🔗 Getting first search result href attribute...")
        try:
            # Get the first a.s-card__link element
            first_link = self.page.locator(self.FIRST_SEARCH_RESULT).first

            # Wait for the element to be visible
            await first_link.wait_for(state="visible", timeout=5000)
            logger.info("✅ First search result link found")

            # Get the href attribute
            href = await first_link.get_attribute("href")
            if not href:
                logger.error("❌ href attribute is empty or missing")
                return False

            logger.info(f"   📍 href: {href}")

            # Navigate to the href
            logger.info("🔗 Navigating to item page...")
            await self.page.goto(href, wait_until="domcontentloaded", timeout=10000)
            logger.info(f"✅ Item detail page loaded: {self.page.url}")

            return True
        except Exception as e:
            logger.error(f"❌ Failed to navigate to first search result: {e}")
            return False


    async def is_add_to_cart_dialog_visible(self) -> bool:
        """
        Check if the Add to Cart dialog/confirmation modal is visible

        Returns:
            bool - True if dialog is visible
        """
        logger.info("⏳ Checking if Add to Cart dialog is visible...")
        try:
            await self.page.locator(self.DIALOG_CONTAINER).wait_for(
                state="visible",
                timeout=5000
            )
            logger.info("✅ Dialog is visible")
            return True
        except Exception as e:
            logger.error(f"❌ Dialog not visible: {e}")
            return False

    async def get_dialog_item_title(self) -> Optional[str]:
        """
        Get the item title displayed in the Add to Cart dialog

        Returns:
            str - Item title or None if not found
        """
        logger.info("📋 Retrieving item title from dialog...")
        try:
            title_elements = await self.page.locator(self.DIALOG_ITEM_TITLE).all()
            if title_elements:
                title = await title_elements[0].text_content()
                logger.info(f"✅ Item title: {title}")
                return title.strip() if title else None
            logger.warning("⚠️  No title element found")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting item title: {e}")
            return None

    async def get_dialog_item_price(self) -> Optional[str]:
        """
        Get the item price displayed in the Add to Cart dialog

        Returns:
            str - Item price string or None if not found
        """
        logger.info("💰 Retrieving item price from dialog...")
        try:
            price_elements = await self.page.locator(self.DIALOG_ITEM_PRICE).all()
            for element in price_elements:
                text = await element.text_content()
                if text and ('$' in text or any(c.isdigit() for c in text)):
                    logger.info(f"✅ Item price: {text}")
                    return text.strip() if text else None
            logger.warning("⚠️  No price element found")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting item price: {e}")
            return None

    async def has_see_in_cart_button(self) -> bool:
        """
        Check if the 'See in cart' button is visible in the dialog

        Returns:
            bool - True if button exists and is visible
        """
        logger.info("🔍 Checking for 'See in cart' button...")
        try:
            # Try main selector
            try:
                button = self.page.locator(self.SEE_IN_CART_BUTTON)
                is_visible = await button.is_visible(timeout=3000)
                if is_visible:
                    logger.info("✅ 'See in cart' button found")
                    return True
            except:
                pass

            # Try alternative selector
            button = self.page.locator(self.SEE_IN_CART_BUTTON_ALT)
            is_visible = await button.is_visible(timeout=3000)
            if is_visible:
                logger.info("✅ 'See in cart' button found (alt selector)")
                return True

            logger.warning("⚠️  'See in cart' button not found")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking for 'See in cart' button: {e}")
            return False

    async def has_checkout_button(self) -> bool:
        """
        Check if the 'Checkout 1 item' button is visible in the dialog

        Returns:
            bool - True if button exists and is visible
        """
        logger.info("🔍 Checking for 'Checkout 1 item' button...")
        try:
            # Try main selector
            try:
                button = self.page.locator(self.CHECKOUT_BUTTON)
                is_visible = await button.is_visible(timeout=3000)
                if is_visible:
                    logger.info("✅ 'Checkout 1 item' button found")
                    return True
            except:
                pass

            # Try alternative selector
            button = self.page.locator(self.CHECKOUT_BUTTON_ALT)
            is_visible = await button.is_visible(timeout=3000)
            if is_visible:
                logger.info("✅ 'Checkout 1 item' button found (alt selector)")
                return True

            logger.warning("⚠️  'Checkout 1 item' button not found")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking for 'Checkout 1 item' button: {e}")
            return False

    async def click_see_in_cart(self) -> bool:
        """
        Click the 'See in cart' button in the dialog

        Returns:
            bool - True if button was clicked successfully
        """
        logger.info("📍 Clicking 'See in cart' button...")
        try:
            # Try main selector first
            try:
                await self.page.locator(self.SEE_IN_CART_BUTTON).click(timeout=5000)
                logger.info("✅ 'See in cart' button clicked")
                return True
            except:
                # Try alternative selector
                await self.page.locator(self.SEE_IN_CART_BUTTON_ALT).click(timeout=5000)
                logger.info("✅ 'See in cart' button clicked (alt selector)")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to click 'See in cart' button: {e}")
            return False


    async def click_checkout_button(self) -> bool:
        """
        Click the 'Checkout 1 item' button in the dialog

        Returns:
            bool - True if button was clicked successfully
        """
        logger.info("📍 Clicking 'Checkout 1 item' button...")
        try:
            # Try main selector first
            try:
                await self.page.locator(self.CHECKOUT_BUTTON).click(timeout=5000)
                logger.info("✅ 'Checkout 1 item' button clicked")
                return True
            except:
                # Try alternative selector
                await self.page.locator(self.CHECKOUT_BUTTON_ALT).click(timeout=5000)
                logger.info("✅ 'Checkout 1 item' button clicked (alt selector)")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to click 'Checkout 1 item' button: {e}")
            return False

    async def close_dialog(self) -> bool:
        """
        Close the Add to Cart dialog by clicking the close button

        Returns:
            bool - True if dialog was closed successfully
        """
        logger.info("📍 Closing dialog...")
        try:
            await self.page.locator(self.DIALOG_CLOSE_BUTTON).click(timeout=5000)
            logger.info("✅ Dialog closed")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to close dialog: {e}")
            return False

    async def wait_for_dialog(self, timeout: int = 10000) -> bool:
        """
        Wait for the Add to Cart dialog to appear

        Args:
            timeout - Maximum time to wait in milliseconds

        Returns:
            bool - True if dialog appeared within timeout
        """
        logger.info(f"⏳ Waiting for dialog (timeout={timeout}ms)...")
        try:
            await self.page.locator(self.DIALOG_CONTAINER).wait_for(
                state="visible",
                timeout=timeout
            )
            logger.info("✅ Dialog appeared")
            return True
        except Exception as e:
            logger.error(f"❌ Dialog did not appear: {e}")
            return False

    async def get_dialog_item_image(self) -> Optional[str]:
        """
        Get the image URL for the item displayed in the dialog

        Returns:
            str - Image src URL or None if not found
        """
        logger.info("🖼️  Retrieving item image from dialog...")
        try:
            img_element = self.page.locator(self.DIALOG_ITEM_IMAGE)
            src = await img_element.get_attribute("src")
            if src:
                logger.info(f"✅ Item image URL retrieved")
                return src
            logger.warning("⚠️  No image src found")
            return None
        except Exception as e:
            logger.error(f"❌ Error getting item image: {e}")
            return None
