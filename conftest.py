import pytest
import logging
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from config.settings import settings


try:
    import allure
    HAS_ALLURE = True
except ImportError:
    HAS_ALLURE = False

logger = logging.getLogger(__name__)

# Create logs and screenshots directories
Path("logs").mkdir(exist_ok=True)
Path("screenshots").mkdir(exist_ok=True)
if HAS_ALLURE:
    Path("allure-results").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_execution.log'),
        logging.StreamHandler()
    ]
)

# Configure Allure handler for test logs (if Allure is available)
if HAS_ALLURE:
    allure_handler = logging.FileHandler('allure-results/test_logs.log')
    allure_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(allure_handler)


@pytest.fixture(autouse=True)
def test_logger(request):
    """Automatically log test start and end with test name"""
    test_name = request.node.name
    logger.info("")
    logger.info("=" * 80)
    logger.info(f"🧪 TEST: {test_name}")
    logger.info("=" * 80)

    yield

    logger.info("✓ Test passed")
    logger.info("=" * 80)


@pytest.fixture(scope="function")
async def page(request):
    """
    Create browser and page for each test - THIS OPENS THE BROWSER
    Uses same pattern as test_browser_simple.py which works
    Captures screenshots on test failure for Allure reporting
    """
    print("\n" + "=" * 80)
    print("🚀 FIXTURE: Opening browser...")
    print("=" * 80)

    p = await async_playwright().start()
    print("📦 Playwright instance created")
    print("🌐 Launching Chromium browser (headless=False)...")

    browser = await p.chromium.launch(
        headless=False,
        slow_mo=500,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--start-maximized"
        ]
    )
    print("✓ Browser launched successfully!")

    print("📋 Creating browser context...")
    context = await browser.new_context(no_viewport=True)
    print("✓ Context created")

    print("🔖 Creating new page/tab...")
    page_obj = await context.new_page()
    print("✓ Page created")

    print(f"⏱️  Setting default timeout to {settings.DEFAULT_TIMEOUT}ms")
    page_obj.set_default_timeout(settings.DEFAULT_TIMEOUT)
    page_obj.set_default_navigation_timeout(settings.DEFAULT_TIMEOUT)
    print("✓ Timeouts configured")

    # Bring window to front on macOS
    try:
        await page_obj.bring_to_front()
        print("✓ Browser window brought to front")
    except Exception as e:
        print(f"⚠ Could not bring window to front: {e}")

    # Navigate to configured base URL
    print(f"📍 Navigating to {settings.BASE_URL}...")
    await page_obj.goto(settings.BASE_URL, wait_until="domcontentloaded", timeout=30000)
    print(f"✓ Page loaded: {page_obj.url}")

    print("✅ Browser ready for testing!")
    print("=" * 80 + "\n")

    yield page_obj

    # Capture screenshot on test failure
    test_failed = hasattr(request.node, 'rep_call') and request.node.rep_call.failed
    if test_failed:
        try:
            screenshot_path = f"screenshots/{request.node.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page_obj.screenshot(path=screenshot_path, full_page=True)
            if HAS_ALLURE:
                allure.attach.file(screenshot_path, name="Failure Screenshot",
                                 attachment_type=allure.attachment_type.PNG)
            logger.error(f"Screenshot captured at: {screenshot_path}")
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")

    # Cleanup after test
    print("\n" + "-" * 80)
    print("🔒 Closing browser...")
    await page_obj.close()
    await context.close()
    await browser.close()
    await p.stop()
    print("✓ Browser closed")
    print("-" * 80 + "\n")


@pytest.fixture(scope="function")
def test_scenarios():
    """Load test scenarios from CSV"""
    from utils.data_provider import DataProvider
    return DataProvider.get_search_scenarios()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Capture test results and attach to Allure report
    This hook captures pass/fail/skip status and execution time
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and HAS_ALLURE:
        # Attach test execution time
        if hasattr(rep, 'duration'):
            allure.dynamic.parameter("execution_time", f"{rep.duration:.2f}s")

        # Add test status to Allure
        if rep.passed:
            allure.dynamic.parameter("test_status", "PASSED")
        elif rep.failed:
            allure.dynamic.parameter("test_status", "FAILED")
        elif rep.skipped:
            allure.dynamic.parameter("test_status", "SKIPPED")

    # Store result on node for fixture access
    if not hasattr(item, 'rep_call'):
        item.rep_call = rep


def pytest_configure(config):
    """Configure pytest with Allure options"""
    if HAS_ALLURE:
        config.addinivalue_line(
            "markers",
            "allure_label(name, value): Mark test with Allure label"
        )
        config.addinivalue_line(
            "markers",
            "severity(level): Mark test with severity level"
        )
    logger.info("Allure reporting configured" if HAS_ALLURE else "Running without Allure reporting")


def pytest_collection_modifyitems(config, items):
    """Add Allure metadata to tests"""
    if not HAS_ALLURE:
        return

    for item in items:
        # Add markers for all tests
        if "e2e" in item.keywords:
            allure.dynamic.label("type", "e2e")
        if "smoke" in item.keywords:
            allure.dynamic.label("severity", "blocker")
        if "slow" in item.keywords:
            allure.dynamic.label("severity", "normal")