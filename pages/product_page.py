from playwright.async_api import Page
from typing import List, Optional, Dict
from .base_page import BasePage
import logging
import random

logger = logging.getLogger(__name__)


class ProductPage(BasePage):
    """Product detail page object for eBay-like e-commerce site"""

    # Product Info Locators
    PRODUCT_NAME = "h1, h1[class*='title'], .product-name, .product-title"
    PRODUCT_PRICE = "//span[@class*='price'], //div[@class*='product-price'], .price, [data-price]"
    PRODUCT_DESCRIPTION = "//div[@class*='description'], .product-description, [class*='desc']"
    PRODUCT_RATING = "//span[@class*='rating'], .rating, [class*='stars']"
    PRODUCT_SKU = "//span[@class*='sku'], .sku, [class*='product-id']"

    # Variant Selectors
    SIZE_SELECTOR = "select[name*='size'], select[id*='size'], input[name*='size'], button[class*='size']"
    COLOR_SELECTOR = "select[name*='color'], select[id*='color'], input[name*='color'], button[class*='color']"
    QUANTITY_SELECTOR = "select[name*='quantity'], select[id*='quantity'], input[type='number']"

    # Size/Color Options (when using radio buttons or buttons)
    SIZE_OPTIONS = "//label[contains(@class, 'size')] | button[class*='size-option'] | input[type='radio'][name*='size']"
    COLOR_OPTIONS = "//label[contains(@class, 'color')] | button[class*='color-option'] | input[type='radio'][name*='color']"

    # Add to Cart
    ADD_TO_CART_BUTTON = "button:has-text('Add to Cart'), button:has-text('Add to cart'), button[class*='add-cart'], button[id*='add-to-cart']"
    ADD_TO_WISHLIST_BUTTON = "button:has-text('Add to Wishlist'), button:has-text('Wishlist'), button[class*='wishlist']"

    # Notifications
    SUCCESS_MESSAGE = "//div[@class*='success'], .alert-success, [class*='toast-success']"
    ERROR_MESSAGE = "//div[@class*='error'], .alert-danger, [class*='toast-error']"

    async def get_product_name(self) -> str:
        """Get product name"""
        name = await self.get_text(self.PRODUCT_NAME)
        logger.info(f"Product name: {name}")
        return name

    async def get_product_price(self) -> float:
        """Get product price"""
        price_text = await self.get_text(self.PRODUCT_PRICE)
        try:
            # Remove currency symbols and convert to float
            clean_price = ''.join(c for c in price_text if c.isdigit() or c == '.')
            price = float(clean_price)
            logger.info(f"Product price: ${price}")
            return price
        except (ValueError, AttributeError) as e:
            logger.error(f"Could not parse price: {price_text}, error: {e}")
            raise

    async def get_product_description(self) -> str:
        """Get product description"""
        description = await self.get_text(self.PRODUCT_DESCRIPTION)
        logger.info(f"Product description: {description[:100]}...")
        return description

    async def get_product_rating(self) -> Optional[float]:
        """Get product rating"""
        try:
            rating_text = await self.get_text(self.PRODUCT_RATING)
            # Extract number from rating text (e.g., "4.5 out of 5")
            rating = float(''.join(c for c in rating_text if c.isdigit() or c == '.').split()[0])
            logger.info(f"Product rating: {rating}")
            return rating
        except:
            logger.warning("Could not retrieve product rating")
            return None

    async def get_available_sizes(self) -> List[str]:
        """Get list of available sizes"""
        try:
            sizes = await self.get_all_texts(self.SIZE_OPTIONS)
            logger.info(f"Available sizes: {sizes}")
            return sizes
        except:
            logger.warning("Could not retrieve available sizes")
            return []

    async def get_available_colors(self) -> List[str]:
        """Get list of available colors"""
        try:
            colors = await self.get_all_texts(self.COLOR_OPTIONS)
            logger.info(f"Available colors: {colors}")
            return colors
        except:
            logger.warning("Could not retrieve available colors")
            return []

    async def select_size(self, size: str) -> None:
        """Select size variant"""
        logger.info(f"Selecting size: {size}")
        try:
            # Try dropdown first
            await self.select_option(self.SIZE_SELECTOR, size)
        except:
            # Try button/radio click
            try:
                size_button = f"button:has-text('{size}'), input[value='{size}'][name*='size']"
                await self.click(size_button)
            except:
                logger.error(f"Could not select size: {size}")
                raise

    async def select_color(self, color: str) -> None:
        """Select color variant"""
        logger.info(f"Selecting color: {color}")
        try:
            # Try dropdown first
            await self.select_option(self.COLOR_SELECTOR, color)
        except:
            # Try button/radio click
            try:
                color_button = f"button:has-text('{color}'), input[value='{color}'][name*='color']"
                await self.click(color_button)
            except:
                logger.error(f"Could not select color: {color}")
                raise

    async def set_quantity(self, quantity: int) -> None:
        """Set product quantity"""
        logger.info(f"Setting quantity: {quantity}")
        await self.fill(self.QUANTITY_SELECTOR, str(quantity))

    async def select_random_size(self) -> Optional[str]:
        """Select random size from available options"""
        sizes = await self.get_available_sizes()
        if sizes:
            selected_size = random.choice(sizes)
            logger.info(f"Randomly selected size: {selected_size}")
            await self.select_size(selected_size)
            return selected_size
        logger.warning("No sizes available to select")
        return None

    async def select_random_color(self) -> Optional[str]:
        """Select random color from available options"""
        colors = await self.get_available_colors()
        if colors:
            selected_color = random.choice(colors)
            logger.info(f"Randomly selected color: {selected_color}")
            await self.select_color(selected_color)
            return selected_color
        logger.warning("No colors available to select")
        return None

    async def select_random_variants(self) -> Dict[str, Optional[str]]:
        """Select random variants (size, color, quantity)"""
        logger.info("Selecting random variants")
        variants = {
            "size": await self.select_random_size(),
            "color": await self.select_random_color(),
            "quantity": 1
        }
        await self.set_quantity(variants["quantity"])
        logger.info(f"Selected variants: {variants}")
        return variants

    async def select_specific_variants(self, size: Optional[str] = None, color: Optional[str] = None, quantity: int = 1) -> None:
        """Select specific variants"""
        logger.info(f"Selecting variants - Size: {size}, Color: {color}, Quantity: {quantity}")
        if size:
            await self.select_size(size)
        if color:
            await self.select_color(color)
        await self.set_quantity(quantity)

    async def add_to_cart(self) -> bool:
        """Click add to cart button"""
        logger.info("Adding product to cart")
        try:
            await self.click(self.ADD_TO_CART_BUTTON)
            # Wait for success message or page change
            await self.page.wait_for_load_state("networkidle", timeout=5000)
            logger.info("Product added to cart successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to add product to cart: {e}")
            return False

    async def add_to_cart_with_variants(self, size: Optional[str] = None, color: Optional[str] = None, quantity: int = 1) -> bool:
        """Select variants and add to cart"""
        logger.info(f"Adding to cart with variants - Size: {size}, Color: {color}, Quantity: {quantity}")
        await self.select_specific_variants(size, color, quantity)
        return await self.add_to_cart()

    async def add_to_cart_with_random_variants(self) -> Dict[str, Optional[str]]:
        """Select random variants and add to cart, return selected variants"""
        logger.info("Adding to cart with random variants")
        variants = await self.select_random_variants()
        success = await self.add_to_cart()
        if success:
            logger.info(f"Added to cart with variants: {variants}")
            return variants
        else:
            logger.error("Failed to add product with random variants to cart")
            raise Exception("Failed to add product to cart")

    async def add_to_wishlist(self) -> bool:
        """Click add to wishlist button"""
        logger.info("Adding product to wishlist")
        try:
            await self.click(self.ADD_TO_WISHLIST_BUTTON)
            await self.page.wait_for_load_state("networkidle", timeout=5000)
            logger.info("Product added to wishlist successfully")
            return True
        except:
            logger.warning("Could not add to wishlist")
            return False

    async def is_add_to_cart_available(self) -> bool:
        """Check if add to cart button is available"""
        is_available = await self.is_enabled(self.ADD_TO_CART_BUTTON)
        logger.info(f"Add to cart button available: {is_available}")
        return is_available

    async def get_success_message(self) -> Optional[str]:
        """Get success message after adding to cart"""
        try:
            message = await self.get_text(self.SUCCESS_MESSAGE)
            logger.info(f"Success message: {message}")
            return message
        except:
            logger.warning("No success message found")
            return None

    async def get_error_message(self) -> Optional[str]:
        """Get error message if any"""
        try:
            message = await self.get_text(self.ERROR_MESSAGE)
            logger.info(f"Error message: {message}")
            return message
        except:
            logger.warning("No error message found")
            return None

    async def scroll_to_variants(self) -> None:
        """Scroll to variant selectors"""
        logger.info("Scrolling to variants section")
        await self.scroll_to_element(self.SIZE_SELECTOR)

    async def take_product_screenshot(self, filename: str = "product_page.png") -> str:
        """Take screenshot of product page"""
        logger.info("Taking screenshot of product page")
        return await self.take_screenshot(filename)

    async def get_product_details(self) -> Dict[str, any]:
        """Get complete product details"""
        logger.info("Retrieving complete product details")
        details = {
            "name": await self.get_product_name(),
            "price": await self.get_product_price(),
            "description": await self.get_product_description(),
            "rating": await self.get_product_rating(),
            "available_sizes": await self.get_available_sizes(),
            "available_colors": await self.get_available_colors(),
            "url": await self.get_current_url()
        }
        logger.info(f"Product details: {details}")
        return details