#!/usr/bin/env python3
"""
JavaScript Detection Test (No Browser Required)

Quick test to see if a page would need browser rendering.
Does NOT require Playwright - only does HTTP fetch and detection.
"""

import asyncio
import sys
import re
from urllib.parse import urljoin, urlparse

try:
    import aiohttp
    from bs4 import BeautifulSoup
except ImportError:
    print("This test requires: pip install aiohttp beautifulsoup4 lxml")
    sys.exit(1)


# DOM manipulation patterns (from patterns.py)
DOM_WATCH_METHODS = [
    ".createElementNS",
    ".removeChild",
    ".insertBefore",
    ".createElement",
    ".setAttribute",
    ".createTextNode",
    ".replaceChildren",
    ".prepend",
    ".append",
    ".appendChild",
    ".write",
]

# Framework patterns
FRAMEWORK_PATTERNS = {
    "nextjs": "/_next/static/chunks/pages/",
    "webpack": "/webpack-runtime-",
    "gatsby": 'id="gatsby-',
    "react": "react-dom",
    "vue": "vue.js",
    "angular": "ng-version",
}

# JS indicators
JS_INDICATORS = [
    "window.addEventListener",
    "document.addEventListener",
    "DOMContentLoaded",
    "__NEXT_DATA__",
    "__NUXT__",
    "ReactDOM.render",
    "Vue.createApp",
]


def detect_dom_manipulation(html: str) -> tuple[bool, list]:
    """Detect DOM manipulation patterns"""
    found = []
    for method in DOM_WATCH_METHODS:
        if method in html:
            found.append(method)
    return len(found) > 0, found


def detect_frameworks(html: str) -> dict:
    """Detect JavaScript frameworks"""
    detected = {}
    for name, pattern in FRAMEWORK_PATTERNS.items():
        if pattern in html:
            detected[name] = pattern
    return detected


def detect_js_indicators(html: str) -> tuple[bool, list]:
    """Detect JS indicators"""
    found = []
    for indicator in JS_INDICATORS:
        if indicator in html:
            found.append(indicator)
    return len(found) > 0, found


def extract_scripts(html: str) -> list:
    """Extract script sources"""
    soup = BeautifulSoup(html, 'lxml')
    scripts = []
    for script in soup.find_all('script', src=True):
        scripts.append(script['src'])
    return scripts


def extract_metadata(html: str) -> dict:
    """Extract basic metadata"""
    soup = BeautifulSoup(html, 'lxml')

    title = None
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text().strip()

    description = None
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        description = meta_desc.get('content', '').strip()

    return {'title': title, 'description': description}


async def fetch_page(url: str) -> tuple[str, str]:
    """Fetch page via HTTP"""
    timeout = aiohttp.ClientTimeout(total=15)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    html = await response.text()
                    return str(response.url), html
                else:
                    return None, None
    except Exception as e:
        print(f"Error fetching: {e}")
        return None, None


async def test_page(url: str):
    """Test a single page for JavaScript detection"""

    print("\n" + "=" * 80)
    print("JAVASCRIPT DETECTION TEST (HTTP Only - No Browser)")
    print("=" * 80)
    print(f"URL: {url}")
    print("=" * 80 + "\n")

    # Fetch page
    print("📡 Fetching page via HTTP...")
    final_url, html = await fetch_page(url)

    if not html:
        print("❌ Failed to fetch page")
        return

    print(f"✓ Success! ({len(html):,} bytes)")
    if final_url != url:
        print(f"  Redirected to: {final_url}")

    # Extract metadata
    print("\n📄 Page Info:")
    metadata = extract_metadata(html)
    print(f"  Title: {metadata['title'] or 'N/A'}")
    if metadata['description']:
        desc = metadata['description'][:100] + '...' if len(metadata['description']) > 100 else metadata['description']
        print(f"  Description: {desc}")

    # Extract scripts
    print("\n📜 Scripts:")
    scripts = extract_scripts(html)
    print(f"  Total scripts: {len(scripts)}")
    if scripts:
        for i, src in enumerate(scripts[:5], 1):
            print(f"    {i}. {src}")
        if len(scripts) > 5:
            print(f"    ... and {len(scripts) - 5} more")

    # Detection
    print("\n🔍 JavaScript Detection:")
    print("-" * 80)

    # 1. DOM Manipulation
    has_dom, dom_found = detect_dom_manipulation(html)
    print(f"  1. DOM Manipulation: {'✓ DETECTED' if has_dom else '✗ Not found'}")
    if dom_found:
        print(f"     Found: {', '.join(dom_found[:3])}")
        if len(dom_found) > 3:
            print(f"     ... and {len(dom_found) - 3} more")

    # 2. Frameworks
    frameworks = detect_frameworks(html)
    print(f"  2. Frameworks: {'✓ DETECTED' if frameworks else '✗ None detected'}")
    if frameworks:
        for name, pattern in frameworks.items():
            print(f"     - {name.upper()} (found: {pattern})")

    # 3. JS Indicators
    has_indicators, indicators_found = detect_js_indicators(html)
    print(f"  3. JS Indicators: {'✓ DETECTED' if has_indicators else '✗ Not found'}")
    if indicators_found:
        print(f"     Found: {', '.join(indicators_found[:3])}")
        if len(indicators_found) > 3:
            print(f"     ... and {len(indicators_found) - 3} more")

    # Final Decision
    needs_render = has_dom or len(frameworks) > 0 or has_indicators

    print("\n" + "=" * 80)
    print("⚡ SMART CRAWL DECISION")
    print("=" * 80)

    if needs_render:
        print("🌐 RENDER WITH BROWSER")
        print("\nReason:")
        if has_dom:
            print("  ✓ DOM manipulation detected")
        if frameworks:
            print(f"  ✓ Framework detected: {', '.join(frameworks.keys())}")
        if has_indicators:
            print("  ✓ JavaScript indicators found")
        print("\nThis page would be rendered with headless Chrome.")
    else:
        print("🚀 USE HTTP (FAST PATH)")
        print("\nReason:")
        print("  ✓ No JavaScript manipulation detected")
        print("  ✓ No frameworks detected")
        print("  ✓ No JS indicators found")
        print("\nThis page would use the fast HTTP path - no browser needed!")

    print("=" * 80 + "\n")


async def interactive():
    """Interactive mode"""
    print("\n" + "=" * 80)
    print("INTERACTIVE JAVASCRIPT DETECTION")
    print("=" * 80)
    print("Test any URL to see if it needs browser rendering")
    print("Type 'quit' or 'exit' to stop")
    print("=" * 80)

    while True:
        print("\n" + "-" * 80)
        url = input("\nEnter URL to test (or 'quit'): ").strip()

        if url.lower() in ('quit', 'exit', 'q', ''):
            print("\nGoodbye!")
            break

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            await test_page(url)
        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        await test_page(url)
    else:
        await interactive()


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              JAVASCRIPT DETECTION TEST (No Browser Required)               ║
╚════════════════════════════════════════════════════════════════════════════╝

Quick test to see if a page needs browser rendering.
Only requires: pip install aiohttp beautifulsoup4 lxml

Usage:
  python test_detection_only.py                # Interactive mode
  python test_detection_only.py <url>          # Test single URL

Examples:
  python test_detection_only.py https://example.com
  python test_detection_only.py choosealicense.com
  python test_detection_only.py https://react-app.vercel.app
""")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
