# eBay E2E Test Automation

End-to-end test automation for an eBay-like e-commerce platform using Playwright and Python.

## Overview

This project implements automated testing for a complete shopping scenario:
1. **Search** - Find products by query with price filtering
2. **Add to Cart** - Select product variants and add items to shopping cart
3. **Login** - Authenticate users with comprehensive validation
4. **Verify Budget** - Assert cart total does not exceed budget threshold

The implementation follows best practices with:
- **Page Object Model (POM)** architecture for maintainability
- **Data-Driven Testing** with parametrized test scenarios
- **Async Testing** with Playwright for better performance
- **Comprehensive Logging** for debugging and reporting
- **Allure Reports** with screenshots for test execution visualization
- **Test Fixtures** with automatic setup and cleanup

---

## Minimum Requirements

### System Requirements

- **Python:** 3.10 or higher
- **OS:** Windows, macOS, or Linux
- **Git:** For cloning the repository
- **pip:** Python package manager

### Dependencies

All dependencies are defined in `requirements.txt`:

```
pytest>=8.0.0              # Test framework
pytest-asyncio>=0.24.0     # Async test support
python-dotenv>=1.0.0       # Environment variables
pydantic>=2.7.0            # Data validation
pyyaml>=6.0                # YAML parsing
allure-pytest>=2.13.0      # Test reporting
playwright>=1.40.0         # Browser automation
```

---

## Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ranAdler/ness-test-project.git
cd ness-test-project
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

### Running Tests

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test:**
```bash
pytest tests/test_search.py -v
pytest tests/test_add_item_to_cart.py -v
pytest tests/test_login.py -v
```

**Run with test markers:**
```bash
# Run only smoke tests
pytest tests/ -m smoke

# Run only e2e tests
pytest tests/ -m e2e

# Run tests excluding slow tests
pytest tests/ -m "not slow"
```

**Run with specific profile:**
```bash
# Development profile (visible browser)
pytest tests/ --env=dev

# Production profile (headless)
pytest tests/ --env=production
```

**Generate Allure reports:**
```bash
pytest tests/ --alluredir=allure-results
allure serve allure-results
```

---

## Test Files Overview

### Structure

```
tests/
├── test_search.py              # Search functionality tests
├── test_add_item_to_cart.py    # Add to cart tests
├── test_login.py               # Login tests
└── conftest.py                 # Fixtures and configuration
```

### Test Details

#### **Search Tests** (`test_search.py`)

**What it tests:**
- Page navigation to base URL
- Search functionality with queries
- Product filtering by price
- Price extraction and validation

**Supported scenarios:**
- Basic search for running shoes
- Search with price limits
- Search for various product categories (books, electronics, etc.)

**Example:**
```python
@pytest.mark.parametrize("scenario", [
    pytest.param({"search_query": "running shoes", "max_price": 200, "limit": 5},
                 id="running_shoes_200"),
    pytest.param({"search_query": "books", "max_price": 50, "limit": 10},
                 id="books_50"),
])
async def test_search(self, page, scenario):
    await page.goto(BASE_URL)
    # Search and filter logic
```

#### **Add to Cart Tests** (`test_add_item_to_cart.py`)

**What it tests:**
- Navigate to product page
- Click "Add to Cart" button
- Verify dialog appears with correct buttons
- Cart navigation and verification
- Item quantity and pricing validation

**Key Features:**
- Uses direct product URLs (pre-determined items)
- Captures screenshots on success and failure
- Validates dialog appearance and buttons

**Example:**
```
SelectedItemPage(page).add_to_cart().see_in_cart().verify_item_title("New Balance")
```

![Cart Dialog Example](screenshots/search_shoes_5_items.png)

#### **Login Tests** (`test_login.py`)

**Expected test cases:**
- `test_login_wrong_username` - Validates error handling for invalid username
- `test_login_wrong_password` - Validates error handling for incorrect password
- `test_login_success` - Validates successful login flow

**Features:**
- Comprehensive error validation
- Screenshot capture on failures
- Allure tags for test categorization

**Example Screenshots:**
![Login Error](screenshots/login_error.png)

---

## Test Architecture

### Fixtures and Setup/Teardown

The testing framework uses pytest fixtures for automatic setup and cleanup:

```python
@pytest.fixture(scope="function")
async def page(request):
    # 🏗 SETUP (Before test) - Like @BeforeEach
    browser = await p.chromium.launch(headless=False)
    context = await browser.new_context()
    page_obj = await context.new_page()
    
    yield page_obj  # ← Give page to test
    
    # 🧹 TEARDOWN (After test) - Like @AfterEach
    await page_obj.close()
    await context.close()
    await browser.close()
```

**How it works:**
- **Before yield** = Pre-test setup (initialize browser)
- **yield** = Pass page object to test
- **After yield** = Post-test cleanup (close browser)

### Automatic Test Logging

```python
@pytest.fixture(autouse=True)  # ← Runs BEFORE EACH TEST automatically
def test_logger(request):
    """Automatically log test start and end with test name"""
    print(f"\n🚀 START: {request.node.name}")
    yield
    print(f"✅ END: {request.node.name}")
```

---

## Test Strategy

### Test Classification

Tests are classified using markers for better organization and execution:

#### **E2E Tests** (`@pytest.mark.e2e`)
- Full user workflows
- Multiple steps across pages
- Can run overnight for comprehensive coverage

#### **Smoke Tests** (`@pytest.mark.smoke`)
- Quick validation tests
- Fast execution (< 1 minute)
- Critical path validation

### Test Design Philosophy

**Tests should tell a story:**
```python
# Good: Reads like a user journey
await SelectedItemPage(page)\
    .add_to_cart()\
    .see_in_cart()\
    .verify_item_title("New Balance")
```

**Why:** Makes tests easy to understand and maintain

### Avoiding Test Interdependencies

⚠️ **Important:** Each test should be independent
- Don't assume login works in every test
- Don't chain tests together
- One test failure shouldn't cascade to others

**Solution:** Use markers to prioritize
```python
@pytest.mark.e2e  # Slower, comprehensive
@pytest.mark.smoke  # Faster, critical only
```

---

## Data-Driven Testing

### Parametrized Tests

Tests can run with multiple data sets to increase coverage:

```python
@pytest.mark.parametrize("scenario", [
    pytest.param({"search_query": "running shoes", "max_price": 200, "limit": 5},
                 id="running_shoes_200"),
    pytest.param({"search_query": "books", "max_price": 50, "limit": 10},
                 id="books_50"),
])
async def test_search(self, page, scenario):
    # Same test, different data
    search_query = scenario["search_query"]
    max_price = scenario["max_price"]
    # ... test logic
```

**Benefits:**
- Single test code, multiple scenarios
- Easy to add new test cases
- Better test coverage

### CSS Selectors

We use CSS selectors for stability and performance:

**Why CSS selectors:**
- Shorter and faster to write
- More stable than XPath
- Better browser support

**Best practices:**
- Use class names and IDs when available
- Avoid generated/dynamic paths
- Stable selectors that don't change with UI updates

**Example:**
```python
# ✅ GOOD - Stable
SEARCH_INPUT = "input[data-testid='search-input']"
ADD_TO_CART_BTN = "button.add-to-cart"

# ❌ BAD - Generated paths
SEARCH_INPUT = "//*[@id='__NEXT_DATA__']/script[1]"
```

---

## Project Architecture

### Folder Structure

```
ness-test-project/
├── pages/                      # Page Object Model classes
│   ├── base_page.py           # Base page with common methods
│   ├── search_page.py         # Search page implementation
│   ├── product_page.py        # Product detail page
│   └── cart_page.py           # Shopping cart page
│
├── tests/                      # Test files
│   ├── test_search.py         # Search functionality tests
│   ├── test_add_item_to_cart.py  # Cart operation tests
│   ├── test_login.py          # Login validation tests
│   └── conftest.py            # Fixtures and configuration
│
├── utils/                      # Utility modules
│   ├── data_provider.py       # Load test data
│   ├── price_utils.py         # Price parsing
│   ├── screenshot_utils.py    # Screenshot management
│   └── assertion_utils.py     # Custom assertions
│
├── config/                     # Configuration
│   └── settings.py            # Environment settings
│
├── data/                       # Test data files
│   └── test_products.json     # Test scenarios
│
├── conftest.py                # Root pytest configuration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

### Page Object Model

Each page extends `BasePage` and encapsulates page-specific logic:

```python
class SearchPage(BasePage):
    SEARCH_INPUT = "input[placeholder='Search']"
    SEARCH_BUTTON = "button[type='submit']"
    
    async def search(self, query):
        await self.page.fill(self.SEARCH_INPUT, query)
        await self.page.click(self.SEARCH_BUTTON)
```

---

## Allure Reports

### Features

- **Screenshots:** Automatic capture on failures
- **Tags:** Organize tests by category
- **Test History:** Track execution over time
- **Detailed Logs:** Full execution details

### Viewing Reports

```bash
pytest tests/ --alluredir=allure-results
allure serve allure-results
```

The report includes:
- Test execution timeline
- Pass/fail rates
- Screenshots of failures
- Execution logs
- Test categorization by tags

---

## Environment Configuration

### Environment Files Overview

This project supports multiple environment configurations using `.env` files. Each environment has specific settings optimized for its use case.

#### Available Environments

| File | Purpose | Browser | Logging | Screenshots |
|------|---------|---------|---------|-------------|
| `.env.example` | Template for all environments | Headless | INFO | On failure |
| `.env.dev` | Local development & debugging | **Visible** | **DEBUG** | On failure |
| `.env.staging` | Staging server testing | Headless | INFO | On failure |
| `.env.production` | Production testing | Headless | **WARNING** | **Disabled** |

#### Setup Instructions

1. **Initial Setup:**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred environment settings
   ```

2. **For Development:**
   ```bash
   cp .env.dev .env
   # Now run tests with visible browser for debugging
   ```

3. **For CI/CD Pipeline:**
   ```bash
   # Use .env.staging for pre-release testing
   # Use .env.production for production validation
   ```

---

### Detailed Environment Configurations

#### 🚀 Development (`.env.dev`)

**Best for:** Local testing and debugging

```env
BROWSER=chromium
HEADLESS=false          # ← Browser window visible for debugging
SLOW_MO=500             # ← Slow down actions by 500ms to see what's happening

BASE_URL=https://ebay.com
DEMO_URL=https://ebay.com

DEFAULT_TIMEOUT=30000
IMPLICIT_WAIT=10000
EXPLICIT_WAIT=20000

LOG_LEVEL=DEBUG         # ← Verbose logging for debugging
SCREENSHOT_ON_FAILURE=true

REPORT_TYPE=allure
REPORT_DIR=allure-results

# Login Test Credentials (for local testing only)
EBAY_USERNAME=valid_user@example.com
EBAY_PASSWORD=ValidPassword123
INVALID_USERNAME=invalid_user_does_not_exist@example.com
INVALID_PASSWORD=WrongPassword123
```

**Key Features:**
- ✅ Visible browser for step-by-step debugging
- ✅ Debug logging shows detailed execution info
- ✅ Slow motion helps you see what's happening
- ✅ Includes test credentials for login testing

**Usage:**
```bash
pytest tests/ --env=dev
# OR use slow motion for specific tests
HEADLESS=false SLOW_MO=1000 pytest tests/test_search.py -v
```

---

#### 🧪 Staging (`.env.staging`)

**Best for:** Pre-release validation on staging servers

```env
BROWSER=chromium
HEADLESS=true           # ← Run in headless mode (no browser window)
SLOW_MO=0

BASE_URL=https://staging-ebay.example.com
DEMO_URL=https://staging-ebay.example.com

DEFAULT_TIMEOUT=30000
IMPLICIT_WAIT=10000
EXPLICIT_WAIT=20000

LOG_LEVEL=INFO          # ← Standard logging
SCREENSHOT_ON_FAILURE=true

REPORT_TYPE=allure
REPORT_DIR=allure-results-staging
```

**Key Features:**
- ✅ Headless mode for CI/CD pipelines
- ✅ Points to staging server (not production)
- ✅ Balanced logging (INFO level)
- ✅ Separate report directory for staging results

**Usage:**
```bash
pytest tests/ --env=staging
# With report generation
pytest tests/ --env=staging --alluredir=allure-results-staging
```

---

#### 🔒 Production (`.env.production`)

**Best for:** Production validation and monitoring

```env
BROWSER=chromium
HEADLESS=true           # ← Headless mode
SLOW_MO=0

BASE_URL=https://www.ebay.com
DEMO_URL=https://www.ebay.com

DEFAULT_TIMEOUT=30000
IMPLICIT_WAIT=10000
EXPLICIT_WAIT=20000

LOG_LEVEL=WARNING       # ← Only warnings and errors
SCREENSHOT_ON_FAILURE=false  # ← Don't capture screenshots

REPORT_TYPE=allure
REPORT_DIR=allure-results-prod
```

**Key Features:**
- ✅ Minimal logging (WARNING level only)
- ✅ Screenshots disabled to avoid data exposure
- ✅ Tests actual production environment
- ✅ Separate report directory for production results

**Usage:**
```bash
pytest tests/ --env=production
# Important: Use only for critical health checks
```

**⚠️ Warning:** Use production environment sparingly to avoid:
- Generating test data in production
- Impacting real users
- Unnecessary API calls

---

### Configuration Variables Reference

#### Browser Settings
```env
BROWSER=chromium        # chromium | firefox | webkit
HEADLESS=true           # true (headless) | false (visible window)
SLOW_MO=0               # Milliseconds to slow down actions (0 = normal speed)
```

#### URLs
```env
BASE_URL=https://www.ebay.com      # Main application URL
DEMO_URL=https://example-ebay.com  # Demo/staging URL
```

#### Timeouts (milliseconds)
```env
DEFAULT_TIMEOUT=30000   # General element timeout
IMPLICIT_WAIT=10000     # Implicit wait between actions
EXPLICIT_WAIT=20000     # Explicit wait for specific conditions
```

#### Logging & Reporting
```env
LOG_LEVEL=INFO          # DEBUG | INFO | WARNING | ERROR
SCREENSHOT_ON_FAILURE=true   # Capture screenshots on failures
REPORT_TYPE=allure      # Report format
REPORT_DIR=allure-results    # Report output directory
```

#### Test Credentials (Development Only)
```env
EBAY_USERNAME=valid_user@example.com
EBAY_PASSWORD=ValidPassword123
INVALID_USERNAME=invalid_user_does_not_exist@example.com
INVALID_PASSWORD=WrongPassword123
```

---

### Switching Between Environments

**Option 1: Copy environment file**
```bash
# Use development settings
cp .env.dev .env
pytest tests/

# Switch to staging
cp .env.staging .env
pytest tests/
```

**Option 2: Environment variable override**
```bash
# Override specific settings
HEADLESS=false LOG_LEVEL=DEBUG pytest tests/

# Override base URL
BASE_URL=https://staging.example.com pytest tests/
```

**Option 3: Command-line argument (if configured)**
```bash
pytest tests/ --env=dev
pytest tests/ --env=staging
pytest tests/ --env=production
```

---

### Best Practices

✅ **DO:**
- Use `.env.dev` locally for debugging
- Use `.env.staging` before releases
- Keep `.env.production` for critical tests only
- Commit `.env.example` (no secrets)
- Use `.gitignore` to exclude `.env` files with actual credentials

❌ **DON'T:**
- Commit actual `.env` files with real credentials
- Run unnecessary tests against production
- Enable screenshots in production (data exposure risk)
- Use DEBUG logging in production (performance impact)
- Store sensitive data in version control

---

## Key Features

✅ **Async Testing** - Better performance with async/await
✅ **Page Object Model** - Clean, maintainable code
✅ **Data-Driven Tests** - Parametrized test scenarios
✅ **Robust Selectors** - Stable CSS-based locators
✅ **Comprehensive Logging** - Debug-friendly output
✅ **Allure Reports** - Professional test reports
✅ **Screenshot Capture** - Visual failure documentation
✅ **Test Markers** - Organize tests by type (e2e, smoke)

---

## Known Bugs & Learning Points

This section documents common bugs found during test automation and their solutions.

### BUG #1 - Unused Imports ⚠️

**Problem:**
```python
from selenium import webdriver  # ❌ Unused - we use Playwright
import time
```

**Issue:** Importing Selenium when using Playwright adds unnecessary dependency bloat and confuses future developers.

**Solution:**
```python
from playwright.sync_api import sync_playwright  # ✅ Use only what you need
```

**Lesson:** Remove all unused imports. Use `pytest` fixture waits instead of `time.sleep()`.

---

### BUG #2 - Incorrect CSS Selectors 🎯

**Problem:**
```python
page.locator(".button").click()  # ❌ May not find the element
```

**Issue:** The selector `.button` might not exist or be wrong. This causes silent failures or flaky tests.

**Solution:**
```python
# Option 1: Use tag selector
page.locator("button").click()

# Option 2: Use more specific selector
page.locator("button.search-btn").click()

# Option 3: Use data-testid (most stable)
page.locator("[data-testid='search-button']").click()
```

**Best Practices:**
- ✅ Use stable selectors: `data-testid`, `id`, class names
- ❌ Avoid generated/dynamic paths
- 🔍 Verify selectors with browser DevTools (F12)
- 📋 Use CSS selectors for speed (vs XPath)

---

### BUG #3 - Missing Waits & Assertions ⏱️

**Problem:**
```python
time.sleep(3)  # ❌ Hard-coded wait - unreliable
results = page.locator(".result-item")  # May not be loaded yet
# No assertion to verify results exist
```

**Issues:**
1. `time.sleep()` is unreliable and slows down tests
2. Element may not be loaded when accessed
3. No validation that results actually appeared

**Solution:**
```python
# ✅ GOOD - Wait for element visibility
await page.locator(".result-item").wait_for()

# ✅ GOOD - Get results with assertion
results = page.locator(".result-item")
assert results.count() > 0, "No results found"

# ✅ BETTER - Use waitForNavigation or waitForLoadState
await page.wait_for_load_state('networkidle')
```

**When to Wait:**
- After navigation: `await page.wait_for_load_state()`
- Before accessing elements: `await element.wait_for()`
- After form submission: `await page.wait_for_navigation()`
- For specific conditions: `await page.wait_for_function()`

---

### Key Takeaways

**Best Practices Summary:**

| Wrong | Correct |
|------|---------|
| `time.sleep(2)` | `page.wait_for_load_state()` |
| `.button` selector | `[data-testid='button']` selector |
| No assertions | `assert element.count() > 0` |
| Selenium + Playwright | Playwright only |
| Hard-coded waits | Smart waits with conditions |

---

## Troubleshooting

### Tests not finding elements
- Use browser DevTools (F12) to verify selectors
- Run with `HEADLESS=false` to see browser in action
- Check console for JavaScript errors
- Ensure selector is stable (not generated paths)

### Timeout errors
- Increase `DEFAULT_TIMEOUT` in `.env`
- Verify page load completeness
- Check network connectivity
- Use proper wait mechanisms instead of `time.sleep()`

### Test failures
- Review Allure report screenshots
- Check test logs for detailed information
- Run with `LOG_LEVEL=DEBUG` for verbose output
- Verify selectors with F12 Developer Tools

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: playwright install
      - run: pytest tests/ --alluredir=allure-results
      - uses: actions/upload-artifact@v2
        with:
          name: allure-results
          path: allure-results
```

---

## Performance Metrics

- **Average test execution time:** ~2-3 minutes for full scenario
- **Search tests:** ~20-30 seconds
- **Add to cart (5 items):** ~60-90 seconds
- **Login tests:** ~10-20 seconds
- **Cart verification:** ~10-15 seconds

---

## Future Enhancements

- [ ] Checkout flow automation
- [ ] Payment method selection
- [ ] Order tracking
- [ ] Mobile device testing
- [ ] Performance testing (load times)
- [ ] Visual regression testing
- [ ] API integration testing
- [ ] Advanced fixture parametrization

---

## Contributing

1. Create a feature branch
2. Follow the existing test patterns
3. Add descriptive test names
4. Use appropriate markers (@pytest.mark.e2e, @pytest.mark.smoke)
5. Ensure all tests pass
6. Submit pull request

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/ranAdler/ness-test-project/issues)
- Documentation: See TESTING_GUIDE.md for detailed testing practices

---

## Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)
- [Allure Reports](https://docs.qameta.io/allure/)
- [Page Object Model](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/)

---

**Last Updated:** May 2026  
**Version:** 1.0.0