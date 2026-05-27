from pathlib import Path
from datetime import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """Utility for managing screenshots and traces"""

    DEFAULT_SCREENSHOT_DIR = "screenshots"
    DEFAULT_TRACE_DIR = "traces"

    def __init__(self, screenshot_dir: str = DEFAULT_SCREENSHOT_DIR, trace_dir: str = DEFAULT_TRACE_DIR):
        """Initialize screenshot manager with directories"""
        self.screenshot_dir = Path(screenshot_dir)
        self.trace_dir = Path(trace_dir)

        # Create directories if they don't exist
        self.screenshot_dir.mkdir(exist_ok=True)
        self.trace_dir.mkdir(exist_ok=True)
        logger.info(f"Screenshot manager initialized: {self.screenshot_dir}, {self.trace_dir}")

    def get_timestamp(self) -> str:
        """Get current timestamp for filenames"""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    async def take_screenshot(self, page, filename: Optional[str] = None) -> str:
        """
        Take screenshot with optional custom filename.
        If filename is None, generates timestamped filename.
        """
        if filename is None:
            filename = f"screenshot_{self.get_timestamp()}.png"

        filepath = self.screenshot_dir / filename
        await page.screenshot(path=str(filepath), full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)

    async def take_screenshot_on_failure(self, page, test_name: str) -> str:
        """Take screenshot with failure prefix"""
        filename = f"FAILED_{test_name}_{self.get_timestamp()}.png"
        return await self.take_screenshot(page, filename)

    async def start_trace(self, page, name: Optional[str] = None) -> None:
        """Start recording trace"""
        if name is None:
            name = f"trace_{self.get_timestamp()}"

        await page.context.tracing.start(screenshots=True, snapshots=True, sources=True)
        logger.info(f"Trace started: {name}")

    async def stop_trace(self, page, name: Optional[str] = None) -> str:
        """Stop recording trace and save to file"""
        if name is None:
            name = f"trace_{self.get_timestamp()}"

        filepath = self.trace_dir / f"{name}.zip"
        await page.context.tracing.stop(path=str(filepath))
        logger.info(f"Trace saved: {filepath}")
        return str(filepath)

    async def take_trace(self, page, name: Optional[str] = None) -> str:
        """Start, record action, and stop trace"""
        await self.start_trace(page, name)
        # Actual action would happen after calling this
        return name or f"trace_{self.get_timestamp()}"

    @staticmethod
    def delete_screenshot(filepath: str) -> bool:
        """Delete a screenshot file"""
        try:
            Path(filepath).unlink()
            logger.info(f"Deleted screenshot: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete screenshot {filepath}: {e}")
            return False

    @staticmethod
    def get_screenshots_count(screenshot_dir: str = DEFAULT_SCREENSHOT_DIR) -> int:
        """Get count of screenshots in directory"""
        count = len(list(Path(screenshot_dir).glob("*.png")))
        logger.info(f"Found {count} screenshots in {screenshot_dir}")
        return count

    @staticmethod
    def clean_old_screenshots(screenshot_dir: str = DEFAULT_SCREENSHOT_DIR, keep_count: int = 10) -> int:
        """Delete old screenshots keeping only the most recent"""
        screenshot_path = Path(screenshot_dir)
        files = sorted(screenshot_path.glob("*.png"), key=lambda p: p.stat().st_mtime)

        to_delete = files[:-keep_count] if len(files) > keep_count else []
        deleted_count = 0

        for file in to_delete:
            try:
                file.unlink()
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete {file}: {e}")

        logger.info(f"Cleaned up {deleted_count} old screenshots")
        return deleted_count

    @staticmethod
    def get_screenshot_path(filename: str, screenshot_dir: str = DEFAULT_SCREENSHOT_DIR) -> str:
        """Get full path for screenshot file"""
        return str(Path(screenshot_dir) / filename)