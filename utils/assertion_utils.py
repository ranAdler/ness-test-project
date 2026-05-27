from typing import Any, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class TestAssertions:
    """Utility for common test assertions with logging"""

    @staticmethod
    def assert_equal(actual: Any, expected: Any, message: str = "") -> None:
        """Assert actual equals expected"""
        if actual != expected:
            error_msg = f"Expected {expected}, but got {actual}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: {actual} == {expected}")

    @staticmethod
    def assert_not_equal(actual: Any, expected: Any, message: str = "") -> None:
        """Assert actual does not equal expected"""
        if actual == expected:
            error_msg = f"Values should not be equal: {actual}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: {actual} != {expected}")

    @staticmethod
    def assert_true(condition: bool, message: str = "") -> None:
        """Assert condition is true"""
        if not condition:
            error_msg = message or "Assertion failed: condition is False"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: condition is True")

    @staticmethod
    def assert_false(condition: bool, message: str = "") -> None:
        """Assert condition is false"""
        if condition:
            error_msg = message or "Assertion failed: condition is True"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: condition is False")

    @staticmethod
    def assert_greater_than(actual: float, expected: float, message: str = "") -> None:
        """Assert actual is greater than expected"""
        if not (actual > expected):
            error_msg = f"Expected {actual} > {expected}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: {actual} > {expected}")

    @staticmethod
    def assert_less_than(actual: float, expected: float, message: str = "") -> None:
        """Assert actual is less than expected"""
        if not (actual < expected):
            error_msg = f"Expected {actual} < {expected}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: {actual} < {expected}")

    @staticmethod
    def assert_greater_equal(actual: float, expected: float, message: str = "") -> None:
        """Assert actual is greater than or equal to expected"""
        if not (actual >= expected):
            error_msg = f"Expected {actual} >= {expected}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: {actual} >= {expected}")

    @staticmethod
    def assert_less_equal(actual: float, expected: float, message: str = "") -> None:
        """Assert actual is less than or equal to expected"""
        if not (actual <= expected):
            error_msg = f"Expected {actual} <= {expected}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: {actual} <= {expected}")

    @staticmethod
    def assert_in(item: Any, container: List[Any], message: str = "") -> None:
        """Assert item is in container"""
        if item not in container:
            error_msg = f"{item} not found in {container}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: {item} in container")

    @staticmethod
    def assert_not_in(item: Any, container: List[Any], message: str = "") -> None:
        """Assert item is not in container"""
        if item in container:
            error_msg = f"{item} should not be in {container}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: {item} not in container")

    @staticmethod
    def assert_is_not_none(value: Any, message: str = "") -> None:
        """Assert value is not None"""
        if value is None:
            error_msg = message or "Value should not be None"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: value is not None")

    @staticmethod
    def assert_is_none(value: Any, message: str = "") -> None:
        """Assert value is None"""
        if value is not None:
            error_msg = f"Value should be None, but got {value}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: value is None")

    @staticmethod
    def assert_list_length(lst: List[Any], expected_length: int, message: str = "") -> None:
        """Assert list has expected length"""
        actual_length = len(lst)
        if actual_length != expected_length:
            error_msg = f"Expected list length {expected_length}, but got {actual_length}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: list length is {expected_length}")

    @staticmethod
    def assert_string_contains(text: str, substring: str, message: str = "") -> None:
        """Assert text contains substring"""
        if substring not in text:
            error_msg = f"'{substring}' not found in '{text}'"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: text contains '{substring}'")

    @staticmethod
    def assert_string_not_contains(text: str, substring: str, message: str = "") -> None:
        """Assert text does not contain substring"""
        if substring in text:
            error_msg = f"'{substring}' should not be in '{text}'"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: text does not contain '{substring}'")

    @staticmethod
    def assert_between(value: float, min_val: float, max_val: float, message: str = "") -> None:
        """Assert value is between min and max (inclusive)"""
        if not (min_val <= value <= max_val):
            error_msg = f"Expected {value} to be between {min_val} and {max_val}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: {value} is between {min_val} and {max_val}")

    @staticmethod
    def assert_callable(obj: Any, message: str = "") -> None:
        """Assert object is callable"""
        if not callable(obj):
            error_msg = f"Expected callable object, but got {type(obj)}"
            if message:
                error_msg = f"{message}: {error_msg}"
            logger.error(error_msg)
            raise AssertionError(error_msg)
        logger.info(f"Assertion passed: object is callable")