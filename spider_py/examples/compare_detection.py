#!/usr/bin/env python3
"""
Detection Comparison: Aggressive vs Refined

Compares the original aggressive detection with the refined version
to show the improvement in accuracy.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly to avoid Playwright dependency
import patterns
import patterns_refined

def get_aggressive_detector():
    return patterns.get_detector()

def get_refined_detector(mode="balanced"):
    return patterns_refined.get_detector(mode)


def test_page(name: str, html: str, should_render: bool):
    """
    Test a page with both detectors

    Args:
        name: Page description
        html: HTML content
        should_render: Whether this page SHOULD need rendering (ground truth)
    """
    print(f"\n{'='*75}")
    print(f"TEST: {name}")
    print(f"Ground Truth: {'SHOULD render' if should_render else 'should NOT render'}")
    print(f"{'='*75}")

    # Extract script sources (simplified)
    import re
    script_sources = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)

    # Test with aggressive detector
    aggressive = get_aggressive_detector()
    aggressive_needs = aggressive.needs_rendering(html, script_sources)

    # Test with refined detectors (all modes)
    conservative = get_refined_detector("conservative")
    balanced = get_refined_detector("balanced")

    conservative_result = conservative.analyze(html, script_sources)
    balanced_result = balanced.analyze(html, script_sources)

    # Show results
    print(f"\n🔴 Aggressive Detection:")
    print(f"   Decision: {'RENDER' if aggressive_needs else 'HTTP'}")
    print(f"   Correct:  {'✓' if aggressive_needs == should_render else '✗ WRONG'}")

    print(f"\n🟡 Balanced Detection (Recommended):")
    print(f"   Decision: {'RENDER' if balanced_result['needs_rendering'] else 'HTTP'}")
    print(f"   Reason:   {balanced_result['reason']}")
    print(f"   Correct:  {'✓' if balanced_result['needs_rendering'] == should_render else '✗ WRONG'}")

    print(f"\n🟢 Conservative Detection:")
    print(f"   Decision: {'RENDER' if conservative_result['needs_rendering'] else 'HTTP'}")
    print(f"   Reason:   {conservative_result['reason']}")
    print(f"   Correct:  {'✓' if conservative_result['needs_rendering'] == should_render else '✗ WRONG'}")

    # Return results
    return {
        "name": name,
        "should_render": should_render,
        "aggressive": aggressive_needs,
        "balanced": balanced_result["needs_rendering"],
        "conservative": conservative_result["needs_rendering"],
    }


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   DETECTION METHOD COMPARISON                             ║
╚═══════════════════════════════════════════════════════════════════════════╝

Comparing detection methods on real-world scenarios.
""")

    results = []

    # Test Case 1: Static blog (should NOT render)
    static_blog = """
    <html>
        <head><title>My Blog</title></head>
        <body>
            <nav>
                <a href="/">Home</a>
                <a href="/about">About</a>
                <a href="/posts">Posts</a>
            </nav>
            <article>
                <h1>Blog Post Title</h1>
                <p>Content here...</p>
            </article>
            <footer>
                <a href="/privacy">Privacy</a>
            </footer>
        </body>
    </html>
    """
    results.append(test_page("Static Blog", static_blog, should_render=False))

    # Test Case 2: Analytics tracking (should NOT render)
    analytics_page = """
    <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
            <script>
                // Google Analytics
                const tracker = document.getElementById('ga-tracker');
                tracker.setAttribute('data-page', window.location.pathname);
                tracker.setAttribute('data-timestamp', Date.now());
            </script>
        </body>
    </html>
    """
    results.append(test_page("Analytics/Tracking", analytics_page, should_render=False))

    # Test Case 3: Form validation (should NOT render)
    form_page = """
    <html>
        <body>
            <a href="/terms">Terms</a>
            <form action="/submit">
                <input type="email" id="email">
                <button type="submit">Submit</button>
            </form>
            <script>
                document.getElementById('email').addEventListener('input', function(e) {
                    if (!e.target.value.includes('@')) {
                        e.target.setAttribute('aria-invalid', 'true');
                    }
                });
            </script>
        </body>
    </html>
    """
    results.append(test_page("Form Validation", form_page, should_render=False))

    # Test Case 4: Next.js SPA (SHOULD render)
    nextjs_spa = """
    <html>
        <head>
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
    results.append(test_page("Next.js SPA", nextjs_spa, should_render=True))

    # Test Case 5: Dynamic content generation (SHOULD render)
    dynamic_content = """
    <html>
        <body>
            <div id="app"></div>
            <script>
                const app = document.getElementById('app');
                const nav = document.createElement('nav');
                const link1 = document.createElement('a');
                link1.href = '/dynamic1';
                nav.appendChild(link1);
                const link2 = document.createElement('a');
                link2.href = '/dynamic2';
                nav.appendChild(link2);
                app.appendChild(nav);
            </script>
        </body>
    </html>
    """
    results.append(test_page("Dynamic Content Generation", dynamic_content, should_render=True))

    # Test Case 6: React SSR (could be either, but links in HTML)
    react_ssr = """
    <html>
        <head>
            <script src="/static/js/react-dom.min.js"></script>
        </head>
        <body>
            <div id="root">
                <nav>
                    <a href="/home">Home</a>
                    <a href="/about">About</a>
                </nav>
            </div>
            <script>
                ReactDOM.hydrate(<App />, document.getElementById('root'));
            </script>
        </body>
    </html>
    """
    results.append(test_page("React SSR (Hydration)", react_ssr, should_render=False))

    # Test Case 7: Image lazy loading (should NOT render)
    lazy_images = """
    <html>
        <body>
            <a href="/gallery">Gallery</a>
            <div class="images">
                <img data-src="image1.jpg" class="lazy">
                <img data-src="image2.jpg" class="lazy">
            </div>
            <script>
                document.querySelectorAll('.lazy').forEach(img => {
                    img.setAttribute('src', img.getAttribute('data-src'));
                });
            </script>
        </body>
    </html>
    """
    results.append(test_page("Lazy Image Loading", lazy_images, should_render=False))

    # Test Case 8: Modal/dropdown interaction (should NOT render)
    ui_interactions = """
    <html>
        <body>
            <nav>
                <a href="/home">Home</a>
                <a href="/products">Products</a>
            </nav>
            <button id="menu-toggle">Menu</button>
            <div id="menu" style="display:none;">
                <a href="/option1">Option 1</a>
            </div>
            <script>
                document.getElementById('menu-toggle').addEventListener('click', function() {
                    const menu = document.getElementById('menu');
                    menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
                    menu.setAttribute('aria-expanded', menu.style.display !== 'none');
                });
            </script>
        </body>
    </html>
    """
    results.append(test_page("UI Interactions (Modal/Dropdown)", ui_interactions, should_render=False))

    # Summary
    print(f"\n{'='*75}")
    print("SUMMARY")
    print(f"{'='*75}\n")

    # Calculate accuracy
    total = len(results)
    aggressive_correct = sum(1 for r in results if r["aggressive"] == r["should_render"])
    balanced_correct = sum(1 for r in results if r["balanced"] == r["should_render"])
    conservative_correct = sum(1 for r in results if r["conservative"] == r["should_render"])

    print(f"Total test cases: {total}\n")

    print(f"🔴 Aggressive Detection:")
    print(f"   Accuracy: {aggressive_correct}/{total} ({aggressive_correct/total*100:.0f}%)")
    print(f"   False positives: {sum(1 for r in results if not r['should_render'] and r['aggressive'])}")
    print(f"   False negatives: {sum(1 for r in results if r['should_render'] and not r['aggressive'])}")

    print(f"\n🟡 Balanced Detection (Recommended):")
    print(f"   Accuracy: {balanced_correct}/{total} ({balanced_correct/total*100:.0f}%)")
    print(f"   False positives: {sum(1 for r in results if not r['should_render'] and r['balanced'])}")
    print(f"   False negatives: {sum(1 for r in results if r['should_render'] and not r['balanced'])}")

    print(f"\n🟢 Conservative Detection:")
    print(f"   Accuracy: {conservative_correct}/{total} ({conservative_correct/total*100:.0f}%)")
    print(f"   False positives: {sum(1 for r in results if not r['should_render'] and r['conservative'])}")
    print(f"   False negatives: {sum(1 for r in results if r['should_render'] and not r['conservative'])}")

    # Performance impact
    print(f"\n{'='*75}")
    print("PERFORMANCE IMPACT (on 100-page crawl)")
    print(f"{'='*75}\n")

    # Assume 60% don't need rendering, 40% do
    aggressive_renders = sum(1 for r in results if r["aggressive"])
    balanced_renders = sum(1 for r in results if r["balanced"])
    conservative_renders = sum(1 for r in results if r["conservative"])

    print(f"Pages that would be rendered (out of {total}):")
    print(f"   Aggressive:   {aggressive_renders} ({aggressive_renders/total*100:.0f}%)")
    print(f"   Balanced:     {balanced_renders} ({balanced_renders/total*100:.0f}%)")
    print(f"   Conservative: {conservative_renders} ({conservative_renders/total*100:.0f}%)")

    print(f"\nEstimated time (100 pages, 0.2s HTTP vs 2s browser):")
    http_time = 0.2
    browser_time = 2.0

    aggressive_time = (100 - aggressive_renders * 100 / total) * http_time + (aggressive_renders * 100 / total) * browser_time
    balanced_time = (100 - balanced_renders * 100 / total) * http_time + (balanced_renders * 100 / total) * browser_time
    conservative_time = (100 - conservative_renders * 100 / total) * http_time + (conservative_renders * 100 / total) * browser_time

    print(f"   Aggressive:   {aggressive_time:.1f}s")
    print(f"   Balanced:     {balanced_time:.1f}s  (saves {aggressive_time - balanced_time:.1f}s, {(aggressive_time - balanced_time)/aggressive_time*100:.0f}% faster)")
    print(f"   Conservative: {conservative_time:.1f}s  (saves {aggressive_time - conservative_time:.1f}s, {(aggressive_time - conservative_time)/aggressive_time*100:.0f}% faster)")

    # Recommendation
    print(f"\n{'='*75}")
    print("RECOMMENDATION")
    print(f"{'='*75}\n")

    if balanced_correct >= aggressive_correct:
        print("✅ Use BALANCED detection (best accuracy + performance)")
        print("\n   Benefits:")
        print("   • Better accuracy than aggressive")
        print("   • Significantly faster on typical sites")
        print("   • Good balance between speed and completeness")
        print("\n   Use: get_detector('balanced')  # Default")
    else:
        print("⚠️  Balanced detection needs tuning for your use case")

    print(f"\n{'='*75}\n")


if __name__ == "__main__":
    main()
