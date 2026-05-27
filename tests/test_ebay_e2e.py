# """
# End-to-end tests for eBay automation.
# Tests the complete flow: search -> add to cart -> verify total
# """
#
# import pytest
# from utils import DataProvider
# from models import SearchScenario
# from pages import SearchBuilder
# from core_functions import (
#     addItemsToCart,
#     assertCartTotalNotExceeds,
#     run_end_to_end_test
# )
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# class TestEBayE2E:
#     """E2E test class for eBay shopping scenario"""
#
#     @pytest.mark.e2e
#     async def test_add_items_to_cart(self, page):
#         """Test adding items to cart with variant selection"""
#         logger.info("Test: Add items to cart")
#
#         # First search for products
#         query = "shoes"
#         max_price = 220.0
#         limit = 3
#
#         urls = await (SearchBuilder(page)
#             .search(query)
#             .maxPrice(max_price)
#             .filter()
#             .collect(limit))
#         assert len(urls) > 0, "Need products to test add to cart"
#
#         # Add items to cart
#         result = await addItemsToCart(page, urls, select_random_variants=True)
#
#         assert result["added"] > 0, "Should add at least one item"
#         assert result["failed"] == 0, "Should not have failures"
#         assert len(result["added_items"]) == result["added"]
#         logger.info(f"✓ Added {result['added']} items to cart")
#
#     @pytest.mark.e2e
#     async def test_verify_cart_total(self, page):
#         """Test verifying cart total does not exceed budget"""
#         logger.info("Test: Verify cart total")
#
#         # Search and add items
#         query = "shoes"
#         max_price = 220.0
#         limit = 3
#
#         urls = await (SearchBuilder(page)
#             .search(query)
#             .maxPrice(max_price)
#             .filter()
#             .collect(limit))
#         result = await addItemsToCart(page, urls, select_random_variants=True)
#
#         # Assert cart total
#         assertion_result = await assertCartTotalNotExceeds(
#             page,
#             max_price,
#             result["added"],
#             take_screenshot=True
#         )
#
#         assert assertion_result["assertion_passed"], "Cart assertion should pass"
#         assert assertion_result["actual_total"] <= assertion_result["max_threshold"]
#         logger.info(f"✓ Cart total within budget: ${assertion_result['actual_total']:.2f}")
#
#     @pytest.mark.e2e
#     async def test_end_to_end_scenario(self, page, test_scenario):
#         """
#         Parametrized E2E test that runs multiple scenarios.
#         Uses test data from scenarios.csv
#         """
#         logger.info(f"Test: E2E Scenario - {test_scenario['name']}")
#
#         result = await run_end_to_end_test(
#             page,
#             search_query=test_scenario["search_query"],
#             max_price=test_scenario["max_price"],
#             items_limit=test_scenario["expected_items_count"],
#             select_random_variants=True
#         )
#
#         assert result["status"] == "PASSED", "E2E test should pass"
#         assert result["search"]["found_count"] > 0
#         assert result["add_to_cart"]["added"] > 0
#         assert result["assertion"]["assertion_passed"]
#
#         logger.info(f"✓ E2E scenario passed: {test_scenario['name']}")
#
#     @pytest.mark.e2e
#     async def test_search_budget_shoes(self, page):
#         """Test scenario: Search for budget shoes under $150"""
#         logger.info("Test: Search budget shoes")
#
#         urls = await (SearchBuilder(page)
#             .query("shoes")
#             .filterBy(max_price=150)
#             .limit(3)
#             .build())
#         assert len(urls) > 0
#         logger.info(f"✓ Found {len(urls)} budget shoes")
#
#     @pytest.mark.e2e
#     async def test_search_premium_shoes(self, page):
#         """Test scenario: Search for premium shoes with high budget"""
#         logger.info("Test: Search premium shoes")
#
#         urls = await (SearchBuilder(page)
#             .query("shoes")
#             .filterBy(max_price=500)
#             .limit(5)
#             .build())
#         assert len(urls) > 0
#         logger.info(f"✓ Found {len(urls)} premium shoes")
#
#     @pytest.mark.e2e
#     @pytest.mark.slow
#     async def test_complete_shopping_flow(self, page):
#         """Complete shopping flow with multiple items"""
#         logger.info("Test: Complete shopping flow")
#
#         # Test parameters
#         search_query = "shoes"
#         max_price = 220.0
#         items_count = 5
#
#         # Run complete E2E test
#         result = await run_end_to_end_test(
#             page,
#             search_query,
#             max_price,
#             items_count,
#             select_random_variants=True
#         )
#
#         # Verify results
#         assert result["status"] == "PASSED"
#         assert result["add_to_cart"]["added"] == items_count
#         assert result["assertion"]["actual_total"] <= result["assertion"]["max_threshold"]
#
#         logger.info(f"✓ Complete shopping flow successful")
#         logger.info(f"  - Products found: {result['search']['found_count']}")
#         logger.info(f"  - Items added: {result['add_to_cart']['added']}")
#         logger.info(f"  - Cart total: ${result['assertion']['actual_total']:.2f}")
#
#     @pytest.mark.e2e
#     @pytest.mark.parametrize("scenario", DataProvider.get_search_scenarios())
#     async def test_search_with_scenario(self, page, scenario: SearchScenario):
#         """Parametrized test: Search using test scenarios from JSON"""
#         logger.info("")
#         logger.info("=" * 80)
#         logger.info(f"🧪 PARAMETRIZED TEST: {scenario.scenario_id}")
#         logger.info(f"📋 Description: {scenario.description}")
#         logger.info("=" * 80)
#         logger.info(f"🔍 Searching for: '{scenario.query}'")
#         logger.info(f"   Max Price: ${scenario.max_price}")
#         logger.info(f"   Limit: {scenario.limit} items")
#
#         urls = await (SearchBuilder(page)
#             .query(scenario.query)
#             .filterBy(max_price=scenario.max_price)
#             .limit(scenario.limit)
#             .build())
#
#         assert len(urls) > 0, f"Should find products for: {scenario.query}"
#         assert len(urls) <= scenario.limit, f"Should not exceed limit of {scenario.limit}"
#
#         logger.info(f"✅ PASSED: {scenario.scenario_id} - Found {len(urls)} products")
#         logger.info("=" * 80)