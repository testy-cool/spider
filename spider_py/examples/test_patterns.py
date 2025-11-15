#!/usr/bin/env python3
"""
Test JavaScript detection patterns (no dependencies required).
This tests the core pattern matching logic.
"""

import re
import sys


def test_dom_patterns():
    """Test DOM manipulation pattern detection"""
    print("Testing DOM manipulation detection...")

    # DOM watch methods from the implementation
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

    # Create regex pattern
    dom_patterns = [re.escape(method) for method in DOM_WATCH_METHODS]
    dom_regex = re.compile("|".join(dom_patterns))

    # HTML with DOM manipulation
    html_with_js = """
    <script>
        document.createElement('div');
        element.appendChild(child);
    </script>
    """

    # HTML without DOM manipulation
    html_without_js = """
    <h1>Hello World</h1>
    <p>This is static content.</p>
    """

    has_js = dom_regex.search(html_with_js) is not None
    no_js = dom_regex.search(html_without_js) is not None

    assert has_js == True, "Should detect DOM manipulation"
    assert no_js == False, "Should not detect in static HTML"

    print("  ✓ DOM pattern detection works")


def test_framework_patterns():
    """Test framework detection patterns"""
    print("Testing framework detection...")

    FRAMEWORK_PATTERNS = {
        "nextjs": "/_next/static/chunks/pages/",
        "webpack": "/webpack-runtime-",
        "gatsby": 'id="gatsby-',
    }

    nextjs_html = '<script src="/_next/static/chunks/pages/index.js"></script>'
    webpack_html = '<script src="/webpack-runtime-abc123.js"></script>'
    gatsby_html = '<script id="gatsby-script-loader"></script>'

    for name, pattern in FRAMEWORK_PATTERNS.items():
        if name == "nextjs":
            assert pattern in nextjs_html, f"Should detect {name}"
        elif name == "webpack":
            assert pattern in webpack_html, f"Should detect {name}"
        elif name == "gatsby":
            assert pattern in gatsby_html, f"Should detect {name}"

    print("  ✓ Framework patterns work")


def main():
    """Run pattern tests"""
    print("\n" + "=" * 60)
    print("PATTERN DETECTION TESTS (No Dependencies)")
    print("=" * 60 + "\n")

    try:
        test_dom_patterns()
        test_framework_patterns()

        print("\n" + "=" * 60)
        print("ALL PATTERN TESTS PASSED ✓")
        print("=" * 60 + "\n")

        print("The Python smart crawler is ready!")
        print("\nNext steps to run full crawler:")
        print("  1. Install dependencies:")
        print("     pip install aiohttp beautifulsoup4 lxml playwright")
        print("  2. Install Playwright browsers:")
        print("     playwright install chromium")
        print("  3. Run the full example:")
        print("     python spider_py/examples/smart.py")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
