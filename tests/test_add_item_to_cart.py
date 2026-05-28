"""
Add to Cart Tests using direct URL navigation and Playwright

Test Flow:
1. Navigate directly to product URL
2. On item page, click "Add to cart" button (<span class="ux-call-to-action__text">Add to cart</span>)
3. Dialog appears with:
   - Item title and price
   - "See in cart" button (href to /cart)
   - "Checkout 1 item" button (href to /checkout)
4. Test clicking each button to verify navigation

Tests:
1. Add single item to cart and verify dialog appears with correct buttons
2. Add item and navigate to cart via "See in cart" button
3. Add item and navigate to checkout via "Checkout 1 item" button
4. Verify item details in dialog before proceeding
5. Add multiple items in sequence
"""

import pytest
from pages.selected_item_page import SelectedItemPage
from pages.cart_page import CartPage
import logging

logger = logging.getLogger(__name__)

# Direct product URL
SELECTED_ITEM_URL = "https://www.ebay.com/itm/336590678953?_skw=shoe&epid=10045638079&itmmeta=01KSM4347Z8J4TMY01B6E6AG7M&hash=item4e5e5e2ba9:g:cvgAAeSw9~BpHbEN&itmprp=enc%3AAQALAAAAwGfYFPkwiKCW4ZNSs2u11xDLEwo0fgwwiPQhhFyECFxuKtt%2FAPWmckPs0ZDIHyHEkDaPzBYWllo20nIQvEQSCjhBET6DJvvryW5iRVjKc8Mwmx%2FOLAsvpDn1MjaH%2BUGALfvkd%2BpD58WcjnoGZZcDklnA3tRWuCoQAU7TBA7yopG28Fs7No7%2BSYmNOjabMlJG2XsWJX1%2FfvGPTWcUzJWJtNI1vPnyezgsihjMYRixIVoL1aLvLBMaxFL8hSurmSo43g%3D%3D%7Ctkp%3ABlBMULDEjITNZw"


class TestAddItemToCart:
    """Add to cart test class"""

    @pytest.fixture(autouse=True)
    async def setup_selected_item_page(self, page):
        """Setup: Navigate directly to product URL before each test"""
        logger.info("Navigating directly to product: " + SELECTED_ITEM_URL)
        await page.goto(SELECTED_ITEM_URL)

    @pytest.mark.e2e
    @pytest.mark.smoke
    async def test_add_item_to_cart_dialog_appears(self, page):
        await SelectedItemPage(page).add_to_cart().see_in_cart().verify_item_title("New Balance")


    @pytest.mark.e2e
    @pytest.mark.smoke
    async def test_add_item_to_cart_dialog_appears(self, page):
        await SelectedItemPage(page).add_to_cart().see_in_cart().verify_item_price(50.36)

