#!/usr/bin/env python3
"""
Simple test to verify the smart crawler implementation works.
Tests the JavaScript detection patterns without actually crawling.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from spider_py.patterns import JSDetector


def test_dom_detection():
    """Test DOM manipulation pattern detection"""
    print("Testing DOM manipulation detection...")

    detector = JSDetector()

    # HTML with DOM manipulation
    html_with_js = """
    <html>
        <body>
            <script>
                document.createElement('div');
                element.appendChild(child);
            </script>
        </body>
    </html>
    """

    # HTML without DOM manipulation
    html_without_js = """
    <html>
        <body>
            <h1>Hello World</h1>
            <p>This is static content.</p>
        </body>
    </html>
    """

    has_js = detector.detect_dom_manipulation(html_with_js)
    no_js = detector.detect_dom_manipulation(html_without_js)

    assert has_js == True, "Should detect DOM manipulation"
    assert no_js == False, "Should not detect DOM manipulation in static HTML"

    print("  ✓ DOM detection working correctly")


def test_framework_detection():
    """Test framework detection"""
    print("Testing framework detection...")

    detector = JSDetector()

    # Next.js HTML
    nextjs_html = """
    <html>
        <body>
            <script src="/_next/static/chunks/pages/index.js"></script>
        </body>
    </html>
    """

    # React HTML
    react_html = """
    <html>
        <body>
            <script src="/static/react-dom.js"></script>
        </body>
    </html>
    """

    # Gatsby HTML
    gatsby_html = """
    <html>
        <body>
            <script id="gatsby-script-loader"></script>
        </body>
    </html>
    """

    nextjs_detected = detector.detect_frameworks(nextjs_html)
    react_detected = detector.detect_frameworks(react_html)
    gatsby_detected = detector.detect_frameworks(gatsby_html)

    assert "nextjs" in nextjs_detected, "Should detect Next.js"
    assert "react" in react_detected, "Should detect React"
    assert "gatsby" in gatsby_detected, "Should detect Gatsby"

    print(f"  ✓ Framework detection working (detected: nextjs, react, gatsby)")


def test_needs_rendering():
    """Test the main needs_rendering decision function"""
    print("Testing needs_rendering decision...")

    detector = JSDetector()

    # Static page
    static_html = "<html><body><h1>Static</h1></body></html>"

    # Dynamic page
    dynamic_html = """
    <html>
        <body>
            <script>
                document.createElement('div');
                window.addEventListener('load', function() {
                    console.log('Dynamic!');
                });
            </script>
        </body>
    </html>
    """

    static_needs = detector.needs_rendering(static_html)
    dynamic_needs = detector.needs_rendering(dynamic_html)

    assert static_needs == False, "Static page should not need rendering"
    assert dynamic_needs == True, "Dynamic page should need rendering"

    print("  ✓ Needs rendering decision working correctly")


def test_configuration():
    """Test configuration"""
    print("Testing configuration...")

    from spider_py.configuration import Configuration

    # Default config
    config = Configuration()
    assert config.max_depth == 3
    assert config.chrome_headless == True
    assert "User-Agent" in config.headers

    # Custom config
    custom_config = Configuration(
        max_depth=5, max_pages=100, request_timeout=60
    )
    assert custom_config.max_depth == 5
    assert custom_config.max_pages == 100
    assert custom_config.request_timeout == 60

    print("  ✓ Configuration working correctly")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SMART CRAWLER - SIMPLE TESTS")
    print("=" * 60 + "\n")

    try:
        test_configuration()
        test_dom_detection()
        test_framework_detection()
        test_needs_rendering()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60 + "\n")

        print("Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Install Playwright: playwright install chromium")
        print("  3. Run example: python examples/smart.py")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
