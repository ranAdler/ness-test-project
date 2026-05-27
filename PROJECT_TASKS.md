# eBay E2E Test Automation Project - Task Breakdown

## Project Overview
Implement an end-to-end test automation scenario on an eBay demo commerce site with the following features:
- Product search with price filtering
- Add items to shopping cart
- Verify shopping cart total doesn't exceed budget

**Tech Stack**: do pha     | Reports: Allure/Extent Reports | Architecture: Page Object Model (POM)
**Timeline**: 3-4 hours implementation + 20-30 min reading/demo

---

## Phase 1: Project Setup & Infrastructure

### Task 1.1: Repository Setup
- [ ] Create GitHub repository
- [ ] Initialize project structure with POM (Page Object Model) folders
- [ ] Set up Python/TypeScript project configuration
- [ ] Create requirements.txt or package.json with dependencies
- [ ] Set up Playwright configuration

### Task 1.2: Data Setup
- [ ] Create test data file (JSON/CSV/YAML format)
  - Search queries
  - Price thresholds
  - Expected results
- [ ] Set up configuration management (ENV files, profiles)
- [ ] Create test fixtures and data providers

---

            ## d    

### Task 2.1: Page Object Model Implementation
- [ ] Create base Page class with common methods
- [ ] Implement Login/Authentication Page Object
- [ ] Implement Search Page Object
  - Product search field locators
  - Price filter locators
  - Pagination controls
  - Product item XPath locators
- [ ] Implement Product Details Page Object
  - Variant selectors (size, color, quantity)
  - Add to Cart button
  - Price display
- [ ] Implement Shopping Cart Page Object
  - Cart total/subtotal locators
  - Item quantity and price display

### Task 2.2: Utilities & Helpers
- [ ] Create price parser utility (handle currency, formatting)
- [ ] Create screenshot/trace logging utility
- [ ] Create paging handler utility
- [ ] Create random variant selector utility
- [ ] Create assertion helpers

---

## Phase 3: Core Functions Implementation

### Task 3.1: Implement `searchItemsByNameUnderPrice()`
**Signature**: `async function searchItemsByNameUnderPrice(query: string, maxPrice: number, limit = 5): Promise<string[]>`

**Functionality**:
- [ ] Perform search by query string
- [ ] Apply price filter (min/max) if available on page
- [ ] Extract up to N item links via XPath where price ≤ maxPrice
- [ ] Handle pagination:
  - [ ] If < 5 items found and "Next" button exists, go to next page
  - [ ] Continue collecting items until reach limit or no more pages
  - [ ] If no pagination, return whatever items found (even if < 5)
- [ ] Return array of URLs (up to 5 matching items)
- [ ] Handle edge cases: no results, fewer than limit items

### Task 3.2: Implement `addItemsToCart()`
**Signature**: `async function addItemsToCart(urls: string[]): Promise<void>`

**Functionality**:
- [ ] Loop through each URL
- [ ] Open product page for each URL
- [ ] Handle variant selection (if required):
  - [ ] Detect available variants (size, color, quantity)
  - [ ] Select random values from available options
- [ ] Click "Add to cart" button
- [ ] Return to search/main page
- [ ] Log and screenshot each added item

### Task 3.3: Implement `assertCartTotalNotExceeds()`
**Signature**: `async function assertCartTotalNotExceeds(budgetPerItem: number, itemsCount: number): Promise<void>`

**Functionality**:
- [ ] Open shopping cart page
- [ ] Extract cart total/subtotal amount
- [ ] Calculate expected threshold: budgetPerItem × itemsCount
- [ ] Assert actual total ≤ threshold
- [ ] Capture screenshot/trace of cart page
- [ ] Log assertion results

### Task 3.4: Implement Authentication Function
- [ ] Create login function (or Guest checkout alternative)
- [ ] Handle session management
- [ ] Create stub/mock if needed for demo purposes

---

## Phase 4: End-to-End Test Scenario

### Task 4.1: Create Main Test Flow
- [ ] Call `searchItemsByNameUnderPrice("shoes", 220, 5)` → get URLs
- [ ] Call `addItemsToCart(urls)` → add all items to cart
- [ ] Call `assertCartTotalNotExceeds(220, urls.length)` → verify budget
- [ ] Add logging at each step
- [ ] Handle test failures gracefully

### Task 4.2: Data-Driven Test Implementation
- [ ] Load test data from external file (JSON/CSV/YAML)
- [ ] Parameterize test with multiple scenarios:
  - Different search queries
  - Different budget thresholds
  - Different item counts
- [ ] Run tests for each data set

---

## Phase 5: Bug Hunt Challenge (20 minutes)

### Task 5.1: Code Review for AI-Generated Code
- [ ] Analyze provided buggy code (static review)
- [ ] Identify at least 3 bugs
- [ ] Document findings in `ReadMeAIBugs.md` file:
  - [ ] List each bug with detailed explanation
  - [ ] Show problematic code lines
  - [ ] Propose fixes for each issue

**Common Bug Categories to Look For**:
- Incorrect selectors or locators
- Missing waits/synchronization
- Incorrect price parsing/comparison
- Array index errors
- Missing null/undefined checks
- Pagination logic errors
- Race conditions

---

## Phase 6: Documentation & Reporting

### Task 6.1: Create README.md
- [ ] Installation instructions (requirements, setup)
- [ ] How to run tests (commands, prerequisites)
- [ ] Architecture explanation:
  - [ ] POM structure
  - [ ] Folder organization
  - [ ] Key classes and responsibilities
- [ ] Assumptions/Limitations:
  - [ ] Authentication method (stub/guest/real)
  - [ ] Currency handling
  - [ ] Browser/environment requirements
  - [ ] Test site availability/stability notes

### Task 6.2: Test Reporting Setup ✅
- [x] Configure Allure Reports (or Extent Reports)
- [x] Set up report generation
- [x] Add screenshots to reports
- [x] Add test execution logs
- [x] Generate HTML report with:
  - [x] Test results summary
  - [x] Pass/fail statistics
  - [x] Screenshots for each step
  - [x] Execution timeline

### Task 6.3: Create Bug Report Document
- [ ] File: `ReadMeAIBugs.md`
- [ ] Document identified bugs with:
  - [ ] Bug number and title
  - [ ] Detailed explanation
  - [ ] Affected code lines
  - [ ] Proposed solution

---

## Evaluation Criteria Checklist

### Architecture & Code Quality (45%)
- [ ] Clean POM implementation
- [ ] OOP principles followed
- [ ] Single Responsibility Principle (SRP)
- [ ] Utility classes for common operations
- [ ] No code duplication
- [ ] Proper error handling

### Robustness & Smart Locators (35%)
- [ ] Handles dynamic page elements
- [ ] Manages variant selection properly
- [ ] Handles pagination correctly
- [ ] Accurate price parsing and comparison
- [ ] Waits and synchronization implemented
- [ ] Resilient to page variations

### Data-Driven Approach (15%)
- [ ] External test data configuration
- [ ] Environment variables usage
- [ ] Test profiles/scenarios
- [ ] Parameterized test execution

### Reports & Documentation (15%)
- [ ] Clear README with setup/run instructions
- [ ] Architecture explanation
- [ ] Execution reports (Allure/HTML)
- [ ] Screenshots in reports
- [ ] Bug analysis document

---

## Deliverables Checklist

- [ ] GitHub repository link (with access)
- [ ] README.md with:
  - [ ] Run instructions
  - [ ] Architecture overview
  - [ ] Assumptions and limitations
- [ ] Test execution report (Allure/HTML/JUnit XML)
- [ ] ReadMeAIBugs.md with bug analysis
- [ ] Source code in proper structure
- [ ] All tests passing

---

## Quick Start Commands (Example - Adjust as Needed)

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ --alluredir=./allure-results

# Generate report
allure generate allure-results --clean -o allure-report

# View report
allure open allure-report
```

---

## Notes
- Focus on clean architecture first, features second
- Use proper waits and synchronization (not hard sleeps)
- Test with real eBay demo site or mock if unavailable
- Document assumptions (login method, currency, etc.)
- Ensure code is review-friendly with clear naming and structure