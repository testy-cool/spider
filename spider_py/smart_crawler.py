"""
Smart Crawler - Main implementation

Intelligent hybrid web crawler that combines HTTP speed with browser rendering.
Mimics the Rust spider implementation.
"""

import asyncio
from typing import Set, Optional, Dict, List
from urllib.parse import urlparse, urljoin
from collections import deque

from .configuration import Configuration
from .browser import LazyBrowser
from .page import Page


class SmartCrawler:
    """
    Smart web crawler that uses HTTP by default and browser rendering when needed.

    This is the Python equivalent of the Rust Website::crawl_smart() implementation.
    """

    def __init__(self, start_url: str, config: Optional[Configuration] = None):
        """
        Initialize the smart crawler

        Args:
            start_url: Starting URL for the crawl
            config: Configuration object (uses defaults if not provided)
        """
        self.start_url = start_url
        self.config = config or Configuration()

        # Crawl state
        self.visited_urls: Set[str] = set()
        self.pages: List[Page] = []
        self.url_depth: Dict[str, int] = {start_url: 0}

        # Statistics
        self.stats = {
            "http_requests": 0,
            "browser_renders": 0,
            "total_pages": 0,
            "total_links": 0,
        }

        # Lazy browser (not initialized until needed)
        self._browser: Optional[LazyBrowser] = None

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _is_same_domain(self, url: str) -> bool:
        """Check if URL is same domain as start URL"""
        return self._get_domain(url) == self._get_domain(self.start_url)

    def _should_crawl(self, url: str, current_depth: int) -> bool:
        """
        Determine if a URL should be crawled

        Args:
            url: URL to check
            current_depth: Current crawl depth

        Returns:
            True if URL should be crawled
        """
        # Already visited
        if url in self.visited_urls:
            return False

        # Max depth exceeded
        if current_depth >= self.config.max_depth:
            return False

        # Max pages limit reached
        if self.config.max_pages and len(self.visited_urls) >= self.config.max_pages:
            return False

        # Only crawl same domain (for safety)
        if not self._is_same_domain(url):
            return False

        return True

    async def crawl_smart(self) -> List[Page]:
        """
        Execute smart crawl starting from start_url.

        This is the main entry point, equivalent to Rust's crawl_smart() method.

        Returns:
            List of crawled Page objects
        """
        print(f"\n[SmartCrawler] Starting crawl from: {self.start_url}")
        print(f"[SmartCrawler] Max depth: {self.config.max_depth}")
        print(f"[SmartCrawler] Max concurrent: {self.config.max_concurrent_requests}\n")

        # Initialize lazy browser
        async with LazyBrowser(self.config) as browser:
            self._browser = browser

            # Start crawling
            await self._crawl_concurrent_smart()

        # Print statistics
        self._print_stats()

        return self.pages

    async def _crawl_concurrent_smart(self):
        """
        Internal concurrent smart crawl implementation.

        Equivalent to Rust's crawl_concurrent_smart() method.
        Uses BFS with concurrent request processing.
        """
        # Queue for URLs to crawl (url, depth)
        queue: deque = deque([(self.start_url, 0)])

        # Semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)

        while queue:
            # Get batch of URLs to process
            batch = []
            batch_size = min(len(queue), self.config.max_concurrent_requests)

            for _ in range(batch_size):
                if queue:
                    batch.append(queue.popleft())

            # Process batch concurrently
            tasks = [
                self._process_url(url, depth, semaphore) for url, depth in batch
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Add discovered links to queue
            for result in results:
                if isinstance(result, Exception):
                    print(f"[Error] {result}")
                    continue

                if result:
                    new_links, current_depth = result
                    for link in new_links:
                        next_depth = current_depth + 1
                        if self._should_crawl(link, next_depth):
                            queue.append((link, next_depth))
                            self.url_depth[link] = next_depth

            # Optional delay between batches
            if self.config.delay_between_requests > 0:
                await asyncio.sleep(self.config.delay_between_requests)

    async def _process_url(
        self, url: str, depth: int, semaphore: asyncio.Semaphore
    ) -> Optional[tuple]:
        """
        Process a single URL with smart link extraction

        Args:
            url: URL to process
            depth: Current depth
            semaphore: Concurrency limiter

        Returns:
            Tuple of (discovered_links, depth) or None
        """
        async with semaphore:
            # Skip if already visited
            if url in self.visited_urls:
                return None

            self.visited_urls.add(url)

            print(f"[Crawl] [{depth}] {url}")

            # Step 1: Fetch via HTTP (fast)
            page = await Page.fetch_http(url, self.config)
            if not page:
                return None

            self.stats["http_requests"] += 1

            # Step 2: Smart link extraction (with JS detection)
            links, was_rendered = await page.smart_links(self._browser, self.config)

            if was_rendered:
                self.stats["browser_renders"] += 1

            # Update statistics
            self.stats["total_pages"] += 1
            self.stats["total_links"] += len(links)

            # Store page
            self.pages.append(page)

            print(
                f"  → Found {len(links)} links "
                f"[{'Browser' if was_rendered else 'HTTP'}]"
            )

            return links, depth

    def _print_stats(self):
        """Print crawl statistics"""
        print("\n" + "=" * 60)
        print("CRAWL STATISTICS")
        print("=" * 60)
        print(f"Total pages crawled:    {self.stats['total_pages']}")
        print(f"Total links discovered: {self.stats['total_links']}")
        print(f"HTTP requests:          {self.stats['http_requests']}")
        print(f"Browser renders:        {self.stats['browser_renders']}")

        if self.stats["http_requests"] > 0:
            render_percentage = (
                self.stats["browser_renders"] / self.stats["http_requests"] * 100
            )
            print(f"Render rate:            {render_percentage:.1f}%")

        if self._browser and self._browser.is_initialized():
            print("Browser initialized:    YES")
        else:
            print("Browser initialized:    NO (all pages were static!)")

        print("=" * 60 + "\n")

    def get_pages(self) -> List[Page]:
        """Get all crawled pages"""
        return self.pages

    def get_links(self) -> Set[str]:
        """Get all discovered URLs"""
        return self.visited_urls

    def get_stats(self) -> Dict:
        """Get crawl statistics"""
        return self.stats

    def __len__(self):
        """Number of pages crawled"""
        return len(self.pages)
