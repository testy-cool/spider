"""
Page handling and smart link extraction
"""

import asyncio
from typing import Set, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import aiohttp

from .patterns import get_detector
from .browser import LazyBrowser
from .configuration import Configuration


class Page:
    """
    Represents a web page with smart link extraction capabilities.
    Mimics the Rust Page implementation.
    """

    def __init__(self, url: str, html: Optional[str] = None):
        """
        Initialize a Page

        Args:
            url: The page URL
            html: Optional HTML content (if already fetched)
        """
        self.url = url
        self.html = html
        self.links: Set[str] = set()
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self._soup: Optional[BeautifulSoup] = None

    @staticmethod
    async def fetch_http(url: str, config: Configuration) -> Optional["Page"]:
        """
        Fetch a page using HTTP (fast method)

        Args:
            url: URL to fetch
            config: Configuration object

        Returns:
            Page object or None on error
        """
        try:
            timeout = aiohttp.ClientTimeout(total=config.request_timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    url,
                    headers=config.headers,
                    allow_redirects=True,
                    max_redirects=config.max_redirects,
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        return Page(url=str(response.url), html=html)
                    else:
                        print(f"[HTTP] {url} returned status {response.status}")
                        return None

        except asyncio.TimeoutError:
            print(f"[HTTP] Timeout fetching {url}")
            return None
        except Exception as e:
            print(f"[HTTP] Error fetching {url}: {e}")
            return None

    def _get_soup(self) -> Optional[BeautifulSoup]:
        """Get or create BeautifulSoup parser"""
        if self._soup is None and self.html:
            self._soup = BeautifulSoup(self.html, "lxml")
        return self._soup

    def extract_metadata(self):
        """Extract page metadata (title, description)"""
        soup = self._get_soup()
        if not soup:
            return

        # Extract title
        title_tag = soup.find("title")
        if title_tag:
            self.title = title_tag.get_text().strip()

        # Extract description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            self.description = meta_desc.get("content", "").strip()

    def extract_links_from_html(self, html: str, base_url: Optional[str] = None) -> Set[str]:
        """
        Extract all links from HTML content

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links (defaults to self.url)

        Returns:
            Set of absolute URLs
        """
        if base_url is None:
            base_url = self.url

        soup = BeautifulSoup(html, "lxml")
        links = set()

        # Extract from <a> tags
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            absolute_url = urljoin(base_url, href)
            # Only include HTTP(S) URLs
            parsed = urlparse(absolute_url)
            if parsed.scheme in ("http", "https"):
                # Remove fragment
                clean_url = absolute_url.split("#")[0]
                if clean_url:
                    links.add(clean_url)

        return links

    def extract_script_sources(self) -> list:
        """Extract script source URLs from the page"""
        soup = self._get_soup()
        if not soup:
            return []

        script_sources = []
        for script in soup.find_all("script", src=True):
            script_sources.append(script["src"])

        return script_sources

    async def smart_links(
        self, browser: LazyBrowser, config: Configuration
    ) -> Tuple[Set[str], bool]:
        """
        Smart link extraction - the core of the smart crawl feature.

        This method:
        1. Extracts links from HTTP-fetched HTML
        2. Detects if JavaScript is used for DOM manipulation
        3. If JS detected, uses browser rendering to get final links
        4. Returns links + whether rendering was needed

        Args:
            browser: LazyBrowser instance (lazy initialization)
            config: Configuration object

        Returns:
            Tuple of (links_set, was_rendered)
        """
        if not self.html:
            return set(), False

        # Step 1: Extract metadata and initial links from HTTP response
        self.extract_metadata()
        http_links = self.extract_links_from_html(self.html)

        # Step 2: JavaScript detection
        detector = get_detector()
        script_sources = self.extract_script_sources()
        needs_render = detector.needs_rendering(self.html, script_sources)

        if not needs_render:
            # No JavaScript detected - use HTTP links (fast path)
            self.links = http_links
            return http_links, False

        # Step 3: JavaScript detected - render with browser (slow path)
        print(f"[Smart] JS detected on {self.url}, rendering with browser...")

        rendered_html, screenshot = await browser.new_page(self.url)

        if rendered_html:
            # Extract links from rendered HTML
            rendered_links = self.extract_links_from_html(rendered_html, self.url)
            self.links = rendered_links
            return rendered_links, True
        else:
            # Rendering failed - fall back to HTTP links
            print(f"[Smart] Rendering failed for {self.url}, using HTTP links")
            self.links = http_links
            return http_links, False

    def get_url(self) -> str:
        """Get the page URL"""
        return self.url

    def get_links(self) -> Set[str]:
        """Get extracted links"""
        return self.links

    def get_title(self) -> Optional[str]:
        """Get page title"""
        return self.title

    def get_description(self) -> Optional[str]:
        """Get page description"""
        return self.description

    def __repr__(self):
        return f"Page(url='{self.url}', links={len(self.links)}, title='{self.title}')"
