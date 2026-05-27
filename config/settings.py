import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from environment variables"""

    # Browser Configuration
    BROWSER: str = os.getenv("BROWSER", "chromium")
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))

    # Base URLs
    BASE_URL: str = os.getenv("BASE_URL", "http://ebay.com")
    DEMO_URL: str = os.getenv("DEMO_URL", "http://ebay.com")
    LOGIN_URL: str = os.getenv("LOGIN_URL", "https://signin.ebay.com/ws/eBayISAPI.dll?SignIn&sgfl=gh&ru=https%3A%2F%2Fwww.ebay.com%2F")

    # Timeouts (milliseconds)
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "10000"))
    EXPLICIT_WAIT: int = int(os.getenv("EXPLICIT_WAIT", "20000"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SCREENSHOT_ON_FAILURE: bool = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"

    # Report Configuration
    REPORT_TYPE: str = os.getenv("REPORT_TYPE", "allure")
    REPORT_DIR: str = os.getenv("REPORT_DIR", "allure-results")

    # eBay Login Credentials
    EBAY_USERNAME: str = os.getenv("EBAY_USERNAME", "")
    EBAY_PASSWORD: str = os.getenv("EBAY_PASSWORD", "")
    INVALID_USERNAME: str = os.getenv("INVALID_USERNAME", "")
    INVALID_PASSWORD: str = os.getenv("INVALID_PASSWORD", "")

    @classmethod
    def get_browser_launch_args(cls) -> dict:
        """Get browser launch arguments"""
        args = {
            "headless": cls.HEADLESS,
            "slow_mo": cls.SLOW_MO if cls.SLOW_MO > 0 else 500,
        }

        if cls.BROWSER == "chromium":
            args["args"] = [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--start-maximized"
            ]

        return args


settings = Settings()