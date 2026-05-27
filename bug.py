from playwright.sync_api import sync_playwright
from selenium import webdriver
import time


class bug:
    """
    Bug Analysis: Three bugs found in the test_search_functionality code:

    BUG #1 - Unused Import:
    The line "from selenium import webdriver" imports selenium but the code
    uses Playwright instead. This is a dead import causing unnecessary dependency.
    Answer: Remove the unused selenium import - keep only Playwright imports.

    BUG #2 - Incorrect Selector:
    The line 'page.locator(".button").click()' uses class selector ".button"
    but the actual button element likely doesn't have that class or doesn't exist.
    Answer: Use proper selector like 'page.locator("button")' or the correct class name.

    BUG #3 - Missing Wait/Assertion:
    The code doesn't wait for the results element to be visible before accessing it.
    Line 'results = page.locator(".result-item")' may find an element that's not yet loaded.
    Answer: Use 'page.locator(".result-item").wait_for()' to ensure element is visible before use.
    """

    def test_search_functionality(self):
        browser = sync_playwright().start().chromium.launch()
        page = browser.new_page()
        page.goto("https://example.com")

        time.sleep(2)
        # Should be: page.wait_for_load_state() instead of hard-coded sleep

        search_box = page.locator("#search")  # #search is a CSS ID selector - finds HTML element with id="search"
        search_box.fill("playwright testing")

        page.locator(".button").click()

        time.sleep(3)

        results = page.locator(".result-item")
        # Should be: results.wait_for() to ensure element is visible before accessing
        # Also should add an assertion like: assert results.count() > 0 to verify results exist

        browser.close()