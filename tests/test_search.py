"""
Search tests using fluent builder pattern: LandingPageBuilder → ItemBuilder

Pattern:
    items = await (LandingPageBuilder(page)
        .search("query"))
        .minPrice(100)
        .maxPrice(500)
        .collect(limit=10)

Note: Navigation is handled in pytest fixture before each test.
Returns: List of dicts with "name" and "price" keys
"""

import pytest
from config.settings import settings
from pages.landing_page_builder import LandingPageBuilder
import logging

logger = logging.getLogger(__name__)


class TestSearch:
    """Search test class with parameterized scenarios"""

    @pytest.fixture(autouse=True)
    async def setup_search_page(self, page):
        """Setup: Navigate to base URL before each test"""
        logger.info("Navigating to: " + settings.BASE_URL)
        await page.goto(settings.BASE_URL)

    @pytest.mark.e2e
    @pytest.mark.smoke
    async def test_search_shoes_basic(self, page):
        """Test basic search for shoes"""
        products = await (
            await LandingPageBuilder(page).setSearch("shoes")
        ).search().collect(limit=5)

        logger.info(f"Found {len(products)} products")
        assert len(products) > 0, "Should find at least one product when searching for shoes"
        assert all(isinstance(item, dict) and "name" in item and "price" in item for item in products), \
            "All results should be dicts with name and price"

    # @pytest.mark.e2e
    # @pytest.mark.smoke
    # async def test_search_with_max_price_filter(self, page):
    #     """Test search with maximum price filter"""
    #     max_price = 220
    #     logger.info(f"Searching shoes with max price ${max_price}")
    #
    #     products = await (
    #         await LandingPageBuilder(page).setSearch("shoes")
    #     ).search().maxPrice(max_price).collect(limit=5)
    #
    #     logger.info(f"Found {len(products)} products under ${max_price}")
    #     assert len(products) > 0, "Should find at least one product under $220"
    #     assert all(isinstance(item, dict) and "name" in item and "price" in item for item in products), \
    #         "All results should be dicts with name and price"
    #
    # @pytest.mark.e2e
    # async def test_search_with_price_range_filter(self, page):
    #     """Test search with min and max price filters"""
    #     min_price = 50
    #     max_price = 200
    #     logger.info(f"Searching shoes with price range ${min_price}-${max_price}")
    #
    #     products = await (
    #         await LandingPageBuilder(page).setSearch("shoes")
    #     ).search().minPrice(min_price).maxPrice(max_price).filterByPrice().collect(limit=5)
    #
    #     logger.info(f"Found {len(products)} products in price range ${min_price}-${max_price}")
    #     assert len(products) > 0, "Should find at least one product in price range"
    #     assert all(isinstance(item, dict) and "name" in item and "price" in item for item in products), \
    #         "All results should be dicts with name and price"

    @pytest.mark.e2e
    @pytest.mark.parametrize("scenario", [
        pytest.param({"search_query": "running shoes", "max_price": 200, "limit": 5},
                     id="running_shoes_200"),
        pytest.param({"search_query": "books", "max_price": 50, "limit": 10},
                     id="books_50"),
    ])
    async def test_search_with_data_provider(self, page, scenario):
        """Test search with parameterized data"""
        search_query: str = str(scenario['search_query'])
        max_price: float = float(scenario['max_price'])
        limit: int = int(scenario['limit'])

        logger.info(f"Query: {search_query}, Max: ${max_price}, Limit: {limit}")

        products = await (
            await LandingPageBuilder(page).setSearch(search_query)
        ).search().minPrice(5).maxPrice(max_price).filterByPrice().collect(limit=limit)

        logger.info(f"Found {len(products)} products")
        assert len(products) > 0, f"Should find products for '{search_query}'"
        assert len(products) <= limit, f"Should not exceed limit of {limit} products"
        assert all(isinstance(item, dict) and "name" in item and "price" in item for item in products), \
            "All results should be dicts with name and price"

