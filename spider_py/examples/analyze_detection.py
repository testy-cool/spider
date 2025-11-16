#!/usr/bin/env python3
"""
Detection Aggressiveness Analysis

Compares aggressive vs conservative detection to show the difference.
"""

import re


# Current (aggressive) patterns
AGGRESSIVE_DOM_METHODS = [
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

# Refined (conservative) patterns - only methods that likely generate content
CONSERVATIVE_DOM_METHODS = [
    ".createElement",      # Creating elements - likely dynamic content
    ".createElementNS",    # SVG/dynamic elements
    ".appendChild",        # Adding to DOM - likely dynamic
    ".write",             # document.write - definitely dynamic
    ".replaceChildren",   # Replacing content - dynamic
]

# Methods that are often just for styling/manipulation, not content generation
NON_CONTENT_METHODS = [
    ".setAttribute",      # Just setting attributes
    ".removeChild",       # Removing, not adding
    ".insertBefore",      # Could be dynamic, but often just reordering
    ".prepend",          # Often just UI manipulation
    ".append",           # Often just UI manipulation (non-content)
]


def analyze_page(name: str, html: str):
    """Analyze a page with both aggressive and conservative detection"""

    print(f"\n{'='*70}")
    print(f"PAGE: {name}")
    print(f"{'='*70}")

    # Aggressive detection
    aggressive_found = []
    for method in AGGRESSIVE_DOM_METHODS:
        if method in html:
            aggressive_found.append(method)

    aggressive_needs_render = len(aggressive_found) > 0

    # Conservative detection
    conservative_found = []
    for method in CONSERVATIVE_DOM_METHODS:
        if method in html:
            conservative_found.append(method)

    conservative_needs_render = len(conservative_found) > 0

    # Show results
    print(f"\n🔍 Aggressive Detection:")
    print(f"  Found: {', '.join(aggressive_found) if aggressive_found else 'None'}")
    print(f"  Decision: {'🌐 BROWSER' if aggressive_needs_render else '🚀 HTTP'}")

    print(f"\n🎯 Conservative Detection:")
    print(f"  Found: {', '.join(conservative_found) if conservative_found else 'None'}")
    print(f"  Decision: {'🌐 BROWSER' if conservative_needs_render else '🚀 HTTP'}")

    # Show if there's a difference
    if aggressive_needs_render != conservative_needs_render:
        print(f"\n⚠️  DIFFERENCE DETECTED!")
        print(f"  Aggressive would use BROWSER (slower)")
        print(f"  Conservative would use HTTP (faster)")
        print(f"  Potential time saved: ~2 seconds per page")
        return "DIFFERENT"
    else:
        print(f"\n✓ Both methods agree")
        return "SAME"


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║              DETECTION AGGRESSIVENESS ANALYSIS                       ║
╚══════════════════════════════════════════════════════════════════════╝

Comparing aggressive vs conservative JavaScript detection.
""")

    # Test Case 1: Analytics/Tracking (should NOT need rendering)
    analytics_html = """
    <html>
        <head><title>Blog Post</title></head>
        <body>
            <h1>My Blog Post</h1>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
            <script>
                // Google Analytics
                document.querySelector('#tracker').setAttribute('data-track', 'pageview');
            </script>
        </body>
    </html>
    """

    # Test Case 2: Simple UI interactions (should NOT need rendering)
    ui_html = """
    <html>
        <body>
            <nav>
                <a href="/home">Home</a>
                <a href="/products">Products</a>
            </nav>
            <button id="toggle">Toggle Menu</button>
            <script>
                // Just UI toggle
                document.getElementById('toggle').addEventListener('click', function() {
                    menu.setAttribute('aria-expanded', 'true');
                });
            </script>
        </body>
    </html>
    """

    # Test Case 3: Dynamic content generation (SHOULD need rendering)
    spa_html = """
    <html>
        <body>
            <div id="app"></div>
            <script>
                // Single Page App - creates ALL content
                const app = document.getElementById('app');
                const nav = document.createElement('nav');
                const link = document.createElement('a');
                link.href = '/dynamic-page';
                nav.appendChild(link);
                app.appendChild(nav);
            </script>
        </body>
    </html>
    """

    # Test Case 4: Lazy loading images (should NOT need rendering for links)
    lazy_html = """
    <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
            <img data-src="image.jpg" class="lazy">
            <script>
                // Lazy load images - doesn't affect links
                document.querySelectorAll('.lazy').forEach(img => {
                    img.setAttribute('src', img.getAttribute('data-src'));
                });
            </script>
        </body>
    </html>
    """

    # Test Case 5: Form validation (should NOT need rendering)
    form_html = """
    <html>
        <body>
            <a href="/privacy">Privacy Policy</a>
            <form>
                <input type="email" id="email">
                <button type="submit">Submit</button>
            </form>
            <script>
                // Form validation
                const input = document.getElementById('email');
                input.addEventListener('input', function() {
                    if (!input.value.includes('@')) {
                        input.setAttribute('aria-invalid', 'true');
                    }
                });
            </script>
        </body>
    </html>
    """

    # Test Case 6: React/Next.js (SHOULD need rendering)
    nextjs_html = """
    <html>
        <head>
            <script src="/_next/static/chunks/pages/index.js"></script>
        </head>
        <body>
            <div id="__next"></div>
            <script>
                const root = document.getElementById('__next');
                const app = document.createElement('div');
                root.appendChild(app);
            </script>
        </body>
    </html>
    """

    # Run analysis
    results = []
    results.append(analyze_page("Analytics/Tracking", analytics_html))
    results.append(analyze_page("UI Interactions", ui_html))
    results.append(analyze_page("SPA - Dynamic Content", spa_html))
    results.append(analyze_page("Lazy Loading", lazy_html))
    results.append(analyze_page("Form Validation", form_html))
    results.append(analyze_page("Next.js SPA", nextjs_html))

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    different_count = sum(1 for r in results if r == "DIFFERENT")
    same_count = sum(1 for r in results if r == "SAME")

    print(f"\nTotal test cases: {len(results)}")
    print(f"Cases where methods differ: {different_count}")
    print(f"Cases where methods agree: {same_count}")

    if different_count > 0:
        print(f"\n⚠️  PROBLEM IDENTIFIED:")
        print(f"  Aggressive detection triggers browser rendering on {different_count} pages")
        print(f"  that don't actually need it (just have UI JavaScript).")
        print(f"\n  Time wasted per 100-page crawl:")
        print(f"    {different_count} pages × 2 seconds = {different_count * 2} seconds wasted")
        print(f"\n  💡 SOLUTION: Use conservative detection that only triggers")
        print(f"     on DOM methods that actually generate content.")

    print(f"\n{'='*70}")
    print("RECOMMENDATION")
    print(f"{'='*70}")
    print("""
Current Implementation: TOO AGGRESSIVE ⚠️
  - Triggers on .setAttribute (just styling)
  - Triggers on .append (often just UI manipulation)
  - Triggers on .removeChild (removing, not creating content)

Better Approach: CONTENT-FOCUSED ✓
  - Only trigger on content-generating methods:
    • .createElement + .appendChild (creating new elements)
    • document.write (definitely dynamic)
    • .replaceChildren (replacing content)

  - DON'T trigger on:
    • .setAttribute (just attributes)
    • Event listeners (UI interaction)
    • Analytics/tracking code
    • Form validation

Additional Heuristics:
  1. Check if createElement is used WITH appendChild (pattern match)
  2. Look for framework indicators (Next.js, React in scripts)
  3. Check for SPA patterns (empty body with single div)
  4. Combine multiple signals, not just one method

Result: Only render when JavaScript actually generates links/content!
""")


if __name__ == "__main__":
    main()
