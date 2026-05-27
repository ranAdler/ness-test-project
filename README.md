# eBay E2E Test Automation

End-to-end test automation for an eBay-like e-commerce platform using Playwright and Python.

## Overview

This project implements automated testing for a complete shopping scenario:
1. **Search** - Find products by query with price filtering
2. **Add to Cart** - Select product variants and add items to shopping cart
3. **Verify Budget** - Assert cart total does not exceed budget threshold

The implementation follows best practices with:
- **Page Object Model (POM)** architecture for maintainability
- **Data-Driven Testing** with JSON/CSV/YAML test data
- **Utility Functions** for reusable operations
- **Comprehensive Logging** for debugging and reporting
- **Allure Reports** for test execution visualization

## Quick Start

### Prerequisites

- Python 3.10+
- Git
- pip (Python package manager)

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
pytest tests/test_ebay_e2e.py::TestEBayE2E::test_search_products_under_price -v
```

**Run with specific profile:**
```bash
# Development profile (headless=false, visible browser)
pytest tests/ --env=dev

# Production profile (headless=true)
pytest tests/ --env=production
```

**Run with tags:**
```bash
# Run only smoke tests
pytest tests/ -m smoke

# Run only e2e tests
pytest tests/ -m e2e

# Run tests excluding slow tests
pytest tests/ -m "not slow"
```

**Generate reports:**
```bash
# Run tests and generate Allure report
pytest tests/ --alluredir=allure-results

# View report
allure serve allure-results
```

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
│   └── test_ebay_e2e.py       # E2E test scenarios
│
├── utils/                      # Utility modules
│   ├── data_provider.py       # Load test data (JSON/CSV)
│   ├── price_utils.py         # Price parsing and formatting
│   ├── screenshot_utils.py    # Screenshot and trace management
│   ├── pagination_utils.py    # Pagination handling
│   ├── variant_utils.py       # Variant selection helpers
│   └── assertion_utils.py     # Custom assertions
│
├── config/                     # Configuration
│   └── settings.py            # Environment and app settings
│
├── data/                       # Test data files
│   ├── test_products.json     # Products and test scenarios
│   ├── scenarios.csv          # Test scenarios in CSV
│   └── test_data.yaml         # Test data in YAML
│
├── models.py                   # Data models (Product, Variant)
├── core_functions.py          # Core test functions
├── conftest.py                # pytest configuration and fixtures
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project metadata
├── setup.py                   # Package setup
├── playwright.ini             # Playwright configuration
└── README.md                  # This file
```

### Page Object Model

Each page object extends `BasePage` and encapsulates:
- **Locators** - CSS/XPath selectors for page elements
- **Methods** - Actions specific to that page

#### SearchPage
- Search by query
- Apply price filters
- Handle pagination
- Extract product links and prices

#### ProductPage
- Get product details (name, price, rating)
- Select variants (size, color, quantity)
- Add to cart with variant handling
- Take screenshots

#### CartPage
- Get cart items and totals
- Verify item count
- Update quantities
- Assert cart total within budget

### Core Functions

#### `searchItemsByNameUnderPrice(page, query, max_price, limit=5)`
Search for products matching query with price ≤ max_price
- **Returns:** List of product URLs (up to limit)
- **Handles:** Pagination, price filtering, edge cases

#### `addItemsToCart(page, product_urls, select_random_variants=True)`
Add items to cart with optional variant selection
- **Returns:** Dict with added count, failed count, variant data
- **Handles:** Random variant selection, screenshots, logging

#### `assertCartTotalNotExceeds(page, budget_per_item, items_count)`
Verify cart total ≤ (budget_per_item × items_count)
- **Returns:** Dict with cart summary and assertion result
- **Raises:** AssertionError if assertion fails

### Data-Driven Testing

Test scenarios are defined in `data/test_products.json`:

```json
{
  "test_scenarios": [
    {
      "scenario_id": "SC001",
      "name": "Search shoes under $220",
      "search_query": "shoes",
      "max_price": 220,
      "budget_per_item": 220,
      "expected_items_count": 5,
      "tags": ["smoke", "e2e"]
    }
  ]
}
```

Tests are parametrized with these scenarios automatically.

### Utilities

#### PriceParser
- Parse prices from any format ($99.99, €150,50, etc.)
- Format prices with currency symbols
- Calculate totals, discounts, taxes
- Validate price ranges

#### VariantSelector
- Random variant selection
- Filter by patterns/keywords
- Build variant combinations
- Weighted random selection

#### TestAssertions
- Equality, comparison assertions
- String and list assertions
- Custom error messages with logging

#### ScreenshotManager
- Timestamped screenshots
- Failure screenshots
- Trace recording and playback

#### PaginationHandler
- Collect items across pages
- Iterate through all pages
- Calculate page numbers and positions

## Environment Configuration

### Environment Files

- `.env.example` - Template for all environment variables
- `.env.dev` - Development environment (headless=false)
- `.env.staging` - Staging environment (headless=true)
- `.env.production` - Production environment

### Configuration Variables

```env
# Browser
BROWSER=chromium
HEADLESS=true
SLOW_MO=0

# URLs
BASE_URL=https://www.ebay.com
DEMO_URL=https://example-ebay.com

# Timeouts (milliseconds)
DEFAULT_TIMEOUT=30000
IMPLICIT_WAIT=10000
EXPLICIT_WAIT=20000

# Logging
LOG_LEVEL=INFO
SCREENSHOT_ON_FAILURE=true

# Reports
REPORT_TYPE=allure
REPORT_DIR=allure-results
```

## Key Features

### Robust Locators
- Multiple selector strategies (CSS, XPath)
- Handles dynamic element selection
- Fallback locators for variations

### Pagination Support
- Automatic page navigation
- Collect items across multiple pages
- Respects limits and boundaries

### Variant Handling
- Auto-detect available variants
- Random or specific selection
- Variant validation

### Price Parsing
- Handles multiple currencies ($, €, £, ¥, etc.)
- Parses formatted prices (1,234.56, 1.234,56)
- Validates price ranges

### Error Handling
- Comprehensive error logging
- Failure screenshots
- Trace recording for debugging
- Graceful degradation

## Assumptions & Limitations

### Authentication
- Currently uses **Guest Checkout** (no login required)
- Can be extended with login support

### Test Environment
- Tests are designed for **demo/staging sites**
- May need locator adjustments for production eBay
- Assumes consistent page structure

### Browser Support
- **Primary:** Chromium
- **Alternative:** Firefox, WebKit available in config

### Price Handling
- Assumes prices in **USD currency**
- Handles common currency symbols
- May need extension for other currencies

### Pagination
- Handles "Next" button navigation
- Works with button-based pagination
- May need adjustment for scroll-based pagination

### Variant Selection
- Supports size, color, quantity variants
- May not work with:
  - Complex variant dependencies
  - Custom variant types
  - Out-of-stock variants (disabled)

### Test Data
- Products and scenarios defined in JSON
- CSV and YAML formats also supported
- Test data must be pre-populated

## Running Tests with Different Configurations

### Headless Mode (Default)
```bash
pytest tests/ --env=production
```

### Visible Browser (Debug Mode)
```bash
HEADLESS=false pytest tests/ --env=dev
```

### Slow Motion (Debug Playback)
```bash
SLOW_MO=1000 pytest tests/
```

### Verbose Logging
```bash
LOG_LEVEL=DEBUG pytest tests/ -v
```

### With Coverage Report
```bash
pytest tests/ --cov=. --cov-report=html
```

## Troubleshooting

### Tests not finding elements
- Check selectors in page object files
- Use `HEADLESS=false` to visually debug
- Review browser console for errors

### Timeout errors
- Increase `DEFAULT_TIMEOUT` in `.env`
- Check network connectivity
- Verify page load completeness

### Price parsing issues
- Enable debug logging: `LOG_LEVEL=DEBUG`
- Check price format in logs
- Update currency symbols if needed

### Variant selection failures
- Verify variant availability on product page
- Check variant selector locators
- Use `HEADLESS=false` to debug UI

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

## Performance Metrics

- **Average test execution time:** ~2-3 minutes for full scenario
- **Search:** ~20-30 seconds
- **Add to cart (5 items):** ~60-90 seconds
- **Cart verification:** ~10-15 seconds

## Future Enhancements

- [ ] Login/authentication testing
- [ ] Checkout flow automation
- [ ] Payment method selection
- [ ] Order tracking
- [ ] Mobile device testing
- [ ] Performance testing (load times)
- [ ] Visual regression testing
- [ ] API integration testing

## Contributing

1. Create a feature branch
2. Make changes following the existing patterns
3. Add/update tests
4. Ensure all tests pass
5. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/ranAdler/ness-test-project/issues)
- Email: test@example.com

## Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)
- [Allure Reports](https://docs.qameta.io/allure/)
- [Page Object Model](https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/)

---

**Last Updated:** May 2024
**Version:** 0.1.0