#!/usr/bin/env python3
"""
JavaScript Detection Demo (No Dependencies)

Simple demonstration of the JavaScript detection logic.
Uses example HTML snippets - no network requests needed.
"""

import re


# DOM manipulation patterns
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


def detect_dom_manipulation(html: str) -> tuple:
    """Check for DOM manipulation patterns"""
    found = []
    for method in DOM_WATCH_METHODS:
        if method in html:
            found.append(method)
    return len(found) > 0, found


def detect_frameworks(html: str) -> dict:
    """Detect JavaScript frameworks"""
    patterns = {
        "nextjs": "/_next/static/chunks/pages/",
        "webpack": "/webpack-runtime-",
        "gatsby": 'id="gatsby-',
        "react": "react-dom",
    }

    detected = {}
    for name, pattern in patterns.items():
        if pattern in html:
            detected[name] = True

    return detected


def needs_rendering(html: str) -> bool:
    """Determine if page needs browser rendering"""
    has_dom, _ = detect_dom_manipulation(html)
    frameworks = detect_frameworks(html)

    return has_dom or len(frameworks) > 0


def test_page(name: str, html: str):
    """Test a page sample"""
    print("\n" + "=" * 70)
    print(f"TEST: {name}")
    print("=" * 70)

    # Detection
    has_dom, dom_methods = detect_dom_manipulation(html)
    frameworks = detect_frameworks(html)
    needs_render = needs_rendering(html)

    print(f"HTML Size: {len(html)} chars")
    print(f"\nDetection Results:")
    print(f"  DOM Manipulation: {'✓ YES' if has_dom else '✗ NO'}")
    if dom_methods:
        print(f"    Found: {', '.join(dom_methods)}")

    print(f"  Frameworks:       {'✓ YES' if frameworks else '✗ NO'}")
    if frameworks:
        print(f"    Found: {', '.join(frameworks.keys())}")

    print(f"\n⚡ Decision: {'🌐 RENDER (Browser)' if needs_render else '🚀 HTTP (Fast)'}")

    return needs_render


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           JAVASCRIPT DETECTION DEMO (No Dependencies)                ║
╚══════════════════════════════════════════════════════════════════════╝

Demonstrates how smart crawl detects JavaScript on pages.
""")

    # Test Case 1: Static HTML
    static_html = """
    <html>
        <head>
            <title>Static Page</title>
        </head>
        <body>
            <h1>Hello World</h1>
            <p>This is a static page with no JavaScript.</p>
            <a href="/about">About</a>
        </body>
    </html>
    """

    # Test Case 2: Page with DOM manipulation
    dom_html = """
    <html>
        <head>
            <title>Dynamic Page</title>
        </head>
        <body>
            <div id="root"></div>
            <script>
                const div = document.createElement('div');
                div.appendChild(document.createTextNode('Hello'));
                document.getElementById('root').appendChild(div);
            </script>
        </body>
    </html>
    """

    # Test Case 3: Next.js Page
    nextjs_html = """
    <html>
        <head>
            <title>Next.js App</title>
            <script src="/_next/static/chunks/pages/index.js"></script>
        </head>
        <body>
            <div id="__next"></div>
            <script id="__NEXT_DATA__" type="application/json">
            {"props":{"pageProps":{}}}
            </script>
        </body>
    </html>
    """

    # Test Case 4: React Page
    react_html = """
    <html>
        <head>
            <title>React App</title>
            <script src="/static/js/react-dom.min.js"></script>
        </head>
        <body>
            <div id="root"></div>
            <script>
                ReactDOM.render(App, document.getElementById('root'));
            </script>
        </body>
    </html>
    """

    # Test Case 5: Simple page with event listener
    event_html = """
    <html>
        <head><title>Event Page</title></head>
        <body>
            <button id="btn">Click me</button>
            <script>
                document.getElementById('btn').addEventListener('click', function() {
                    console.log('clicked');
                });
            </script>
        </body>
    </html>
    """

    # Run tests
    results = []
    results.append(("Static HTML", test_page("Static HTML Page", static_html)))
    results.append(("DOM Manipulation", test_page("Page with DOM Manipulation", dom_html)))
    results.append(("Next.js", test_page("Next.js Application", nextjs_html)))
    results.append(("React", test_page("React Application", react_html)))
    results.append(("Event Listener", test_page("Page with Event Listener", event_html)))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    http_count = sum(1 for _, needs_render in results if not needs_render)
    browser_count = sum(1 for _, needs_render in results if needs_render)

    for name, needs_render in results:
        status = "Browser" if needs_render else "HTTP   "
        symbol = "🌐" if needs_render else "🚀"
        print(f"  {symbol} {status} - {name}")

    print(f"\nTotal Tests:     {len(results)}")
    print(f"HTTP (Fast):     {http_count} ({http_count/len(results)*100:.0f}%)")
    print(f"Browser (Slow):  {browser_count} ({browser_count/len(results)*100:.0f}%)")

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print("""
Smart crawl saves time by:
  ✓ Using fast HTTP for static pages (no browser overhead)
  ✓ Only using browser when JavaScript is detected
  ✓ Detecting frameworks that require rendering

In this demo:
  - Static HTML → Fast HTTP path (instant)
  - Dynamic pages → Browser rendering (slower but accurate)

On a real crawl of 100 pages with 20% requiring JS:
  - Traditional: 100 pages × 2s (browser) = 200 seconds
  - Smart crawl: 80 pages × 0.2s (HTTP) + 20 pages × 2s (browser) = 56 seconds
  - Speed up: ~3.5x faster!
""")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
