#!/usr/bin/env python3
"""
Test execution script with Allure reporting - Cross-platform version.

Usage:
    python run_tests_report.py                     # Run all tests
    python run_tests_report.py -m e2e             # Run only e2e tests
    python run_tests_report.py -m "e2e and smoke" -o  # Run and open report
"""

import argparse
import subprocess
import shutil
import sys
import platform
from pathlib import Path
from datetime import datetime
import webbrowser


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_header(text):
    """Print formatted header"""
    line = "═" * 63
    print(f"{Colors.BLUE}{line}{Colors.NC}")
    print(f"{Colors.BLUE}  {text}{Colors.NC}")
    print(f"{Colors.BLUE}{line}{Colors.NC}")


def print_section(text):
    """Print formatted section header"""
    print(f"{Colors.YELLOW}{'📋' if 'Configuration' in text else '🚀' if 'Running' in text else '📊'} {text}{Colors.NC}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}💡 {text}{Colors.NC}")


def setup_directories():
    """Create necessary directories"""
    directories = ['allure-results', 'screenshots', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def clean_previous_results():
    """Clean up previous Allure results"""
    print_section("Cleaning previous Allure results...")
    for path in ['allure-results', 'allure-report']:
        if Path(path).exists():
            try:
                if Path(path).is_dir():
                    shutil.rmtree(path)
                else:
                    Path(path).unlink()
            except Exception as e:
                print(f"  Warning: Could not remove {path}: {e}")


def run_pytest(tests_path: str, markers: str = None) -> int:
    """Run pytest with Allure plugin"""
    print_section("Running tests with Allure reporting...")

    cmd = ['pytest', tests_path, '--alluredir=allure-results', '-v']

    if markers:
        cmd.extend(['-m', markers])

    print(f"  Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode
    except Exception as e:
        print_error(f"Failed to run pytest: {e}")
        return 1


def generate_report() -> bool:
    """Generate Allure HTML report"""
    print_section("Generating Allure HTML report...")

    try:
        # Check if allure command is available
        result = subprocess.run(['allure', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError("allure command not found")

        # Generate report
        cmd = ['allure', 'generate', 'allure-results', '-o', 'allure-report', '--clean']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print_success("Report generated at: allure-report/index.html")
            return True
        else:
            print_error(f"Failed to generate report: {result.stderr}")
            return False

    except FileNotFoundError:
        print_error("Allure command not found")
        print_info("Install with: npm install -g allure-commandline")
        print_info("Or visit: https://docs.qameta.io/allure/latest/install/")
        return False
    except Exception as e:
        print_error(f"Error generating report: {e}")
        return False


def open_report():
    """Open the generated Allure report in default browser"""
    report_path = Path('allure-report/index.html')

    if not report_path.exists():
        print_error("Report file not found at allure-report/index.html")
        return False

    try:
        # Convert to file URL
        file_url = f"file://{report_path.resolve()}"

        system = platform.system()
        if system == 'Darwin':  # macOS
            subprocess.run(['open', str(report_path)])
        elif system == 'Linux':
            subprocess.run(['xdg-open', str(report_path)])
        elif system == 'Windows':
            subprocess.run(['start', str(report_path)], shell=True)
        else:
            # Fallback to webbrowser module
            webbrowser.open(file_url)

        print_success("Opening report in browser...")
        return True

    except Exception as e:
        print_error(f"Failed to open report: {e}")
        print_info(f"Open manually: {report_path.resolve()}")
        return False


def print_summary(test_result: int, markers: str = None):
    """Print execution summary"""
    print()
    print_header("Test Execution Summary")

    if test_result == 0:
        print_success("All tests completed successfully!")
    else:
        print_error(f"Tests failed with status code: {test_result}")

    # Print useful information
    print()
    print_info("Report location: allure-report/index.html")
    print_info("Logs location: logs/test_execution.log")
    print_info("Screenshots location: screenshots/")

    print()
    print("📊 Report Includes:")
    print("  • Test results summary and statistics")
    print("  • Pass/Fail breakdown")
    print("  • Screenshots for each test step")
    print("  • Execution timeline")
    print("  • Test execution logs")
    print("  • Test parameters and metadata")

    print_header("Done")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Run tests with Allure reporting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests_report.py                     # Run all tests
  python run_tests_report.py -m e2e             # Run only e2e tests
  python run_tests_report.py -m "e2e and smoke" -o  # Run and open report
  python run_tests_report.py -t tests/test_ebay_e2e.py -o  # Run specific file
        """
    )

    parser.add_argument(
        '-m', '--markers',
        help='Run tests with specific markers (e.g., "e2e", "smoke")',
        default=None
    )

    parser.add_argument(
        '-o', '--open',
        help='Open the Allure report after generation',
        action='store_true'
    )

    parser.add_argument(
        '-t', '--tests',
        help='Path to tests directory or file (default: tests)',
        default='tests'
    )

    args = parser.parse_args()

    # Print header
    print_header("Test Automation - Allure Report Generation")

    # Setup
    setup_directories()

    # Print configuration
    print_section("Test Configuration")
    print(f"  Tests: {args.tests}")
    if args.markers:
        print(f"  Markers: {args.markers}")
    print()

    # Clean previous results
    clean_previous_results()

    # Run tests
    test_result = run_pytest(args.tests, args.markers)

    print()

    # Generate report
    report_success = generate_report()

    # Open report if requested and generated successfully
    if args.open and report_success:
        open_report()

    # Print summary
    print_summary(test_result, args.markers)

    return test_result


if __name__ == '__main__':
    sys.exit(main())