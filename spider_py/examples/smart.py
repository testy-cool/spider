#!/usr/bin/env python3
"""
Smart Crawler Example

Demonstrates the smart crawl feature - intelligent hybrid crawling
that uses HTTP by default and browser rendering only when JavaScript is detected.

This is the Python equivalent of the Rust example at examples/smart.rs
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from spider_py import SmartCrawler, Configuration


async def main():
    """Basic smart crawl example"""

    # Configure crawler
    config = Configuration(
        max_depth=2,  # Crawl up to 2 levels deep
        max_pages=20,  # Limit to 20 pages for demo
        max_concurrent_requests=5,  # Process 5 pages concurrently
        request_timeout=15,  # 15 second timeout
        chrome_headless=True,  # Run browser in headless mode
    )

    # Create crawler
    crawler = SmartCrawler(
        start_url="https://choosealicense.com",  # Same as Rust example
        config=config,
    )

    # Execute smart crawl
    pages = await crawler.crawl_smart()

    # Display results
    print("\nCRAWLED PAGES:")
    print("-" * 80)
    for i, page in enumerate(pages, 1):
        print(f"{i}. {page.get_url()}")
        if page.get_title():
            print(f"   Title: {page.get_title()}")
        print(f"   Links found: {len(page.get_links())}")
        print()

    print(f"\nTotal unique URLs discovered: {len(crawler.get_links())}")


async def advanced_example():
    """Advanced example with custom settings"""

    config = Configuration(
        max_depth=3,
        max_pages=50,
        max_concurrent_requests=10,
        request_timeout=20,
        chrome_headless=True,
        screenshot=False,  # Enable to save screenshots
        wait_for="networkidle",  # Wait for network to be idle
        viewport_width=1920,
        viewport_height=1080,
    )

    crawler = SmartCrawler(
        start_url="https://example.com",
        config=config,
    )

    pages = await crawler.crawl_smart()

    # Get statistics
    stats = crawler.get_stats()
    print(f"\nAdvanced Crawl Results:")
    print(f"  Pages crawled: {stats['total_pages']}")
    print(f"  HTTP-only pages: {stats['http_requests'] - stats['browser_renders']}")
    print(f"  Browser-rendered pages: {stats['browser_renders']}")

    # Calculate efficiency
    if stats["http_requests"] > 0:
        http_percentage = (
            (stats["http_requests"] - stats["browser_renders"])
            / stats["http_requests"]
            * 100
        )
        print(f"  Efficiency: {http_percentage:.1f}% pages used fast HTTP path")


if __name__ == "__main__":
    print("=" * 80)
    print("SMART CRAWLER - Python Implementation")
    print("=" * 80)

    # Run basic example
    asyncio.run(main())

    # Uncomment to run advanced example:
    # print("\n\n")
    # asyncio.run(advanced_example())
