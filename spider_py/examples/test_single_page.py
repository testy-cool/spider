#!/usr/bin/env python3
"""
Single Page Smart Crawl Test

Test smart crawl JavaScript detection on a single page.
Shows the difference between HTTP and browser rendering.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from spider_py import Configuration
from spider_py.page import Page
from spider_py.browser import LazyBrowser
from spider_py.patterns import get_detector


async def test_single_page(url: str, force_render: bool = False):
    """
    Test smart crawl on a single page

    Args:
        url: URL to test
        force_render: If True, always render with browser for comparison
    """
    print("\n" + "=" * 80)
    print(f"SMART CRAWL - SINGLE PAGE TEST")
    print("=" * 80)
    print(f"URL: {url}")
    print(f"Force Render: {force_render}")
    print("=" * 80 + "\n")

    config = Configuration(
        request_timeout=15,
        chrome_headless=True,
    )

    # Step 1: Fetch via HTTP
    print("📡 Step 1: Fetching via HTTP...")
    page = await Page.fetch_http(url, config)

    if not page:
        print("❌ Failed to fetch page via HTTP")
        return

    print(f"✓ HTTP fetch successful ({len(page.html)} bytes)")

    # Step 2: Extract metadata
    page.extract_metadata()
    print(f"\n📄 Page Metadata:")
    print(f"  Title: {page.title or 'N/A'}")
    print(f"  Description: {page.description[:100] if page.description else 'N/A'}...")

    # Step 3: Extract HTTP links
    http_links = page.extract_links_from_html(page.html)
    print(f"\n🔗 Links from HTTP: {len(http_links)}")
    if http_links:
        for i, link in enumerate(list(http_links)[:5], 1):
            print(f"  {i}. {link}")
        if len(http_links) > 5:
            print(f"  ... and {len(http_links) - 5} more")

    # Step 4: JavaScript Detection
    print("\n🔍 Step 2: JavaScript Detection...")
    detector = get_detector()

    # Get script sources
    script_sources = page.extract_script_sources()
    print(f"  Scripts found: {len(script_sources)}")
    if script_sources:
        for i, src in enumerate(script_sources[:3], 1):
            print(f"    {i}. {src}")
        if len(script_sources) > 3:
            print(f"    ... and {len(script_sources) - 3} more")

    # DOM manipulation check
    has_dom = detector.detect_dom_manipulation(page.html)
    print(f"\n  DOM Manipulation: {'✓ DETECTED' if has_dom else '✗ Not found'}")

    # Framework detection
    frameworks = detector.detect_frameworks(page.html)
    print(f"  Frameworks: {', '.join(frameworks) if frameworks else '✗ None detected'}")

    # JS indicators
    has_js_indicators = detector.detect_js_indicators(page.html)
    print(f"  JS Indicators: {'✓ DETECTED' if has_js_indicators else '✗ Not found'}")

    # Final decision
    needs_render = detector.needs_rendering(page.html, script_sources)
    print(f"\n  ⚡ Smart Decision: {'RENDER WITH BROWSER' if needs_render else 'USE HTTP (FAST)'}")

    # Step 5: Browser rendering (if needed or forced)
    if needs_render or force_render:
        print(f"\n🌐 Step 3: {'Forced' if force_render else 'Required'} Browser Rendering...")

        async with LazyBrowser(config) as browser:
            print("  Initializing browser...")
            rendered_html, screenshot = await browser.new_page(url)

            if rendered_html:
                print(f"  ✓ Browser render successful ({len(rendered_html)} bytes)")

                # Extract links from rendered page
                browser_links = page.extract_links_from_html(rendered_html, url)
                print(f"\n🔗 Links from Browser: {len(browser_links)}")
                if browser_links:
                    for i, link in enumerate(list(browser_links)[:5], 1):
                        print(f"  {i}. {link}")
                    if len(browser_links) > 5:
                        print(f"  ... and {len(browser_links) - 5} more")

                # Compare HTTP vs Browser
                print(f"\n📊 Comparison:")
                print(f"  HTTP links:    {len(http_links)}")
                print(f"  Browser links: {len(browser_links)}")

                new_links = browser_links - http_links
                missing_links = http_links - browser_links

                print(f"  New links found by browser: {len(new_links)}")
                if new_links:
                    for i, link in enumerate(list(new_links)[:3], 1):
                        print(f"    +{i}. {link}")
                    if len(new_links) > 3:
                        print(f"    ... and {len(new_links) - 3} more")

                print(f"  Links only in HTTP: {len(missing_links)}")
                if missing_links:
                    for i, link in enumerate(list(missing_links)[:3], 1):
                        print(f"    -{i}. {link}")
                    if len(missing_links) > 3:
                        print(f"    ... and {len(missing_links) - 3} more")

                if screenshot:
                    print(f"\n📸 Screenshot captured ({len(screenshot)} bytes)")
            else:
                print("  ❌ Browser rendering failed")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"URL:              {url}")
    print(f"HTTP Success:     ✓")
    print(f"JS Detection:     {'YES - Needs rendering' if needs_render else 'NO - Static page'}")
    print(f"Browser Used:     {'YES' if (needs_render or force_render) else 'NO (saved time!)'}")
    print(f"Links (HTTP):     {len(http_links)}")
    if needs_render or force_render:
        print(f"Links (Browser):  {len(browser_links) if 'browser_links' in locals() else 'N/A'}")
    print("=" * 80 + "\n")


async def interactive_mode():
    """Interactive mode for testing multiple pages"""
    print("\n" + "=" * 80)
    print("SMART CRAWL - INTERACTIVE SINGLE PAGE TEST")
    print("=" * 80)
    print("Test how smart crawl handles different pages")
    print("Type 'quit' or 'exit' to stop")
    print("=" * 80)

    while True:
        print("\n" + "-" * 80)
        url = input("\nEnter URL to test (or 'quit'): ").strip()

        if url.lower() in ('quit', 'exit', 'q'):
            print("\nGoodbye!")
            break

        if not url:
            continue

        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        force = input("Force browser render for comparison? (y/N): ").strip().lower() == 'y'

        try:
            await test_single_page(url, force_render=force)
        except KeyboardInterrupt:
            print("\n\nInterrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Command line mode
        url = sys.argv[1]
        force_render = '--force' in sys.argv or '-f' in sys.argv
        await test_single_page(url, force_render=force_render)
    else:
        # Interactive mode
        await interactive_mode()


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    SMART CRAWL - SINGLE PAGE TESTER                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Test JavaScript detection and smart crawl behavior on individual pages.

Usage:
  python test_single_page.py                    # Interactive mode
  python test_single_page.py <url>              # Test single URL
  python test_single_page.py <url> --force      # Force browser render

Examples:
  python test_single_page.py https://example.com
  python test_single_page.py https://react-app.com --force
  python test_single_page.py choosealicense.com
""")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
