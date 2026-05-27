"""
Allure reporting utilities for enhanced test documentation.
Provides helpers for screenshots, steps, parameters, and logs in Allure reports.
"""

import allure
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AllureReporting:
    """Helper class for Allure report enhancements"""

    @staticmethod
    async def screenshot_step(page, step_name: str, full_page: bool = False):
        """
        Capture a screenshot at a test step and attach to Allure report.

        Args:
            page: Playwright page object
            step_name: Name of the step for the screenshot
            full_page: Whether to capture full page or viewport only
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f"screenshots/{step_name}_{timestamp}.png"

            Path("screenshots").mkdir(exist_ok=True)
            await page.screenshot(path=screenshot_path, full_page=full_page)

            allure.attach.file(
                screenshot_path,
                name=f"Step: {step_name}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"Screenshot captured for step: {step_name}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to capture screenshot for {step_name}: {e}")
            return None

    @staticmethod
    def add_step(step_name: str, **parameters):
        """
        Add a test step to Allure report with optional parameters.

        Args:
            step_name: Name of the test step
            **parameters: Key-value parameters to include in the step
        """
        with allure.step(step_name):
            for key, value in parameters.items():
                allure.dynamic.parameter(key, str(value))
                logger.info(f"{step_name}: {key}={value}")

    @staticmethod
    def add_test_data(data: Dict[str, Any]):
        """
        Add test data to Allure report.

        Args:
            data: Dictionary of test data to attach
        """
        for key, value in data.items():
            allure.dynamic.parameter(key, str(value))

    @staticmethod
    def attach_log(log_content: str, name: str = "Test Log"):
        """
        Attach a log file to Allure report.

        Args:
            log_content: Content of the log
            name: Name for the attachment
        """
        allure.attach(
            log_content,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )

    @staticmethod
    def attach_html(html_content: str, name: str = "HTML Report"):
        """
        Attach HTML content to Allure report.

        Args:
            html_content: HTML content to attach
            name: Name for the attachment
        """
        allure.attach(
            html_content,
            name=name,
            attachment_type=allure.attachment_type.HTML
        )

    @staticmethod
    def set_test_feature(feature_name: str):
        """Set the feature for current test."""
        allure.dynamic.feature(feature_name)

    @staticmethod
    def set_test_story(story_name: str):
        """Set the story for current test."""
        allure.dynamic.story(story_name)

    @staticmethod
    def set_test_severity(severity: str):
        """
        Set test severity level.
        Valid values: blocker, critical, normal, minor, trivial
        """
        allure.dynamic.severity(severity)

    @staticmethod
    def set_test_label(label_name: str, label_value: str):
        """Set a custom label for the test."""
        allure.dynamic.label(label_name, label_value)

    @staticmethod
    def attach_json(json_data: Dict[str, Any], name: str = "JSON Data"):
        """
        Attach JSON data to Allure report.

        Args:
            json_data: Dictionary to attach as JSON
            name: Name for the attachment
        """
        import json
        json_str = json.dumps(json_data, indent=2)
        allure.attach(
            json_str,
            name=name,
            attachment_type=allure.attachment_type.JSON
        )

    @staticmethod
    def add_assertion(assertion_description: str, assertion_result: bool, expected: Any, actual: Any):
        """
        Document an assertion in the Allure report.

        Args:
            assertion_description: Description of what is being asserted
            assertion_result: True if assertion passed, False otherwise
            expected: Expected value
            actual: Actual value
        """
        status = "✓ PASSED" if assertion_result else "✗ FAILED"
        with allure.step(f"{status}: {assertion_description}"):
            allure.dynamic.parameter("Expected", str(expected))
            allure.dynamic.parameter("Actual", str(actual))
            if not assertion_result:
                logger.error(f"Assertion failed - Expected: {expected}, Actual: {actual}")
            return assertion_result

    @staticmethod
    def log_test_result(status: str, message: str):
        """
        Log test result to Allure report.

        Args:
            status: Status level (PASSED, FAILED, SKIPPED)
            message: Result message
        """
        allure.attach(
            f"[{status}] {message}",
            name="Test Result",
            attachment_type=allure.attachment_type.TEXT
        )
        if status == "PASSED":
            logger.info(f"Test Result: {message}")
        else:
            logger.error(f"Test Result: {message}")