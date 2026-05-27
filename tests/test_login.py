"""
Login tests using fluent builder pattern.
Tests:
1. Login with wrong username - should show error
2. Login with wrong password - should show error
3. Login with correct credentials - should succeed
"""

import pytest
from config.settings import settings
from pages import LoginBuilder
import logging

logger = logging.getLogger(__name__)


class TestLogin:
    """Login test class"""

    @pytest.mark.e2e
    async def test_login_wrong_username(self, page):
        """Test login with wrong/non-existent username shows error"""
        result = await (LoginBuilder(page)
            .user(settings.INVALID_USERNAME)
            .password(settings.EBAY_PASSWORD)
            .build())

        logger.info(f"Login result: {result}")
        logger.info(f"Error message: {result.error_message}")

        assert not result.success, "Login should fail with invalid username"
        assert result.error_message is not None, "Should have error message for invalid username"
        assert len(result.error_message) > 0, "Error message should not be empty"

    @pytest.mark.e2e
    async def test_login_wrong_password(self, page):
        """Test login with wrong password shows error"""
        result = await (LoginBuilder(page)
            .user(settings.EBAY_USERNAME)
            .password(settings.INVALID_PASSWORD)
            .build())

        logger.info(f"Login result: {result}")
        logger.info(f"Error message: {result.error_message}")

        assert not result.success, "Login should fail with wrong password"
        assert result.error_message is not None, "Should have error message for wrong password"
        assert len(result.error_message) > 0, "Error message should not be empty"

    @pytest.mark.e2e
    async def test_login_success(self, page):
        """Test successful login with correct credentials"""
        result = await (LoginBuilder(page)
            .user(settings.EBAY_USERNAME)
            .password(settings.EBAY_PASSWORD)
            .build())

        logger.info(f"Login result: {result}")
        logger.info(f"Current URL: {result.current_url}")

        assert result.success, f"Login should succeed, but got error: {result.error_message}"
        assert result.error_message is None, "Should have no error message on successful login"
        logger.info(f"Successfully logged in, redirected to: {result.current_url}")