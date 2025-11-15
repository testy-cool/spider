"""
Lazy Browser Controller

Implements lazy initialization of headless Chrome using Playwright.
The browser is only started when needed for JavaScript rendering.
"""

import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, Playwright
from .configuration import Configuration


class LazyBrowser:
    """
    Lazy browser controller that initializes Chrome only when needed.
    Mimics the OnceBrowser pattern from Rust implementation.
    """

    def __init__(self, config: Configuration):
        """
        Initialize the lazy browser controller

        Args:
            config: Configuration object with browser settings
        """
        self.config = config
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._initialized = False
        self._init_lock = asyncio.Lock()

    async def get_or_init(self) -> Optional[Browser]:
        """
        Get the browser instance, initializing it if needed (lazy initialization).
        This is thread-safe and ensures only one initialization occurs.

        Returns:
            Browser instance or None if initialization fails
        """
        if self._initialized:
            return self._browser

        async with self._init_lock:
            # Double-check after acquiring lock
            if self._initialized:
                return self._browser

            try:
                # Initialize Playwright
                self._playwright = await async_playwright().start()

                # Launch browser
                self._browser = await self._playwright.chromium.launch(
                    headless=self.config.chrome_headless,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                    ],
                )

                self._initialized = True
                print(f"[Browser] Initialized (headless={self.config.chrome_headless})")
                return self._browser

            except Exception as e:
                print(f"[Browser] Failed to initialize: {e}")
                return None

    async def new_page(self, url: str) -> tuple[Optional[str], Optional[bytes]]:
        """
        Create a new page and navigate to URL

        Args:
            url: URL to navigate to

        Returns:
            Tuple of (html_content, screenshot_bytes) or (None, None) on error
        """
        browser = await self.get_or_init()
        if not browser:
            return None, None

        page: Optional[Page] = None
        try:
            # Create new page with viewport
            page = await browser.new_page(
                viewport={
                    "width": self.config.viewport_width,
                    "height": self.config.viewport_height,
                }
            )

            # Set extra headers
            if self.config.headers:
                await page.set_extra_http_headers(self.config.headers)

            # Navigate with timeout
            await page.goto(
                url,
                wait_until=self.config.wait_for,
                timeout=self.config.request_timeout * 1000,
            )

            # Get HTML content
            html = await page.content()

            # Optional screenshot
            screenshot = None
            if self.config.screenshot:
                screenshot = await page.screenshot(full_page=True)

            return html, screenshot

        except Exception as e:
            print(f"[Browser] Error rendering {url}: {e}")
            return None, None

        finally:
            if page:
                await page.close()

    async def close(self):
        """Close the browser and cleanup resources"""
        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

        self._initialized = False
        print("[Browser] Closed")

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup"""
        await self.close()

    def is_initialized(self) -> bool:
        """Check if browser has been initialized"""
        return self._initialized
