"""
Spider Smart Crawl - Python Implementation

An intelligent hybrid web crawler that combines HTTP requests with headless browser rendering.
Only uses browser rendering when JavaScript is detected on the page.
"""

from .smart_crawler import SmartCrawler
from .configuration import Configuration
from .page import Page

__version__ = "1.0.0"
__all__ = ["SmartCrawler", "Configuration", "Page"]
