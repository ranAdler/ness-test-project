#!/bin/bash
# Test execution script with Allure reporting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Test Automation - Allure Report Generation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Default values
REPORT_OPEN=false
TESTS_TO_RUN="tests"
MARKERS=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--markers)
            MARKERS="$2"
            shift 2
            ;;
        -o|--open)
            REPORT_OPEN=true
            shift
            ;;
        -t|--tests)
            TESTS_TO_RUN="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./run_tests_with_report.sh [options]"
            echo ""
            echo "Options:"
            echo "  -m, --markers MARKERS   Run tests with specific markers (e.g., 'e2e', 'smoke')"
            echo "  -o, --open              Open the Allure report after generation"
            echo "  -t, --tests PATH        Path to tests directory or file (default: tests)"
            echo "  -h, --help              Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests_with_report.sh                    # Run all tests"
            echo "  ./run_tests_with_report.sh -m e2e            # Run only e2e tests"
            echo "  ./run_tests_with_report.sh -m 'e2e and smoke' -o  # Run e2e+smoke and open report"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Create necessary directories
mkdir -p allure-results
mkdir -p screenshots
mkdir -p logs

echo -e "${YELLOW}📋 Test Configuration:${NC}"
echo "  Tests: $TESTS_TO_RUN"
if [ -n "$MARKERS" ]; then
    echo "  Markers: $MARKERS"
fi

# Clean up previous results
echo -e "${YELLOW}🧹 Cleaning previous Allure results...${NC}"
rm -rf allure-results/* allure-report 2>/dev/null || true

# Run pytest with Allure
echo -e "${YELLOW}🚀 Running tests with Allure reporting...${NC}"

if [ -n "$MARKERS" ]; then
    pytest "$TESTS_TO_RUN" -m "$MARKERS" --alluredir=allure-results -v
else
    pytest "$TESTS_TO_RUN" --alluredir=allure-results -v
fi

TEST_RESULT=$?

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Tests completed successfully${NC}"
else
    echo -e "${RED}✗ Tests failed with status code: $TEST_RESULT${NC}"
fi

# Generate Allure report
echo -e "${YELLOW}📊 Generating Allure HTML report...${NC}"

if command -v allure &> /dev/null; then
    allure generate allure-results -o allure-report --clean
    echo -e "${GREEN}✓ Report generated at: allure-report/index.html${NC}"

    if [ "$REPORT_OPEN" = true ]; then
        echo -e "${YELLOW}🌐 Opening report in browser...${NC}"
        if [ "$(uname)" == "Darwin" ]; then
            open allure-report/index.html
        elif [ "$(uname)" == "Linux" ]; then
            xdg-open allure-report/index.html
        else
            echo -e "${YELLOW}Please open allure-report/index.html in your browser${NC}"
        fi
    else
        echo -e "${BLUE}💡 To view the report, run: allure open allure-report${NC}"
    fi
else
    echo -e "${RED}✗ Allure command not found. Install with: npm install -g allure-commandline${NC}"
    echo -e "${YELLOW}Or visit: https://docs.qameta.io/allure/latest/install/${NC}"
    exit 1
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

exit $TEST_RESULT