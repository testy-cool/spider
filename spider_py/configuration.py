"""
Configuration for Smart Crawler
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Configuration:
    """Configuration for the smart crawler"""

    # Request settings
    request_timeout: int = 30
    max_redirects: int = 10
    user_agent: Optional[str] = None

    # Crawling settings
    max_depth: int = 3
    max_pages: Optional[int] = None
    respect_robots_txt: bool = True

    # Browser settings (for rendering)
    chrome_headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    wait_for: str = "domcontentloaded"  # 'load', 'domcontentloaded', 'networkidle'
    screenshot: bool = False

    # Performance settings
    max_concurrent_requests: int = 10
    delay_between_requests: float = 0.0

    # Headers
    headers: Optional[Dict[str, str]] = None

    def __post_init__(self):
        """Set default user agent if not provided"""
        if self.user_agent is None:
            self.user_agent = "Mozilla/5.0 (compatible; SpiderSmartCrawler/1.0)"

        if self.headers is None:
            self.headers = {}

        # Ensure User-Agent is in headers
        if "User-Agent" not in self.headers:
            self.headers["User-Agent"] = self.user_agent
