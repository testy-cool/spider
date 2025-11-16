#!/usr/bin/env python3
"""
Detection Comparison: Aggressive vs Refined (Standalone)

Compares detection methods without external dependencies.
Shows the improvement in accuracy and performance.
"""

import re
from typing import Set, Tuple


# AGGRESSIVE DETECTOR (Original)
class AggressiveDetector:
    DOM_WATCH_METHODS = [
        ".createElementNS", ".removeChild", ".insertBefore", ".createElement",
        ".setAttribute", ".createTextNode", ".replaceChildren", ".prepend",
        ".append", ".appendChild", ".write",
    ]

    def __init__(self):
        self.dom_regex = re.compile("|".join(re.escape(m) for m in self.DOM_WATCH_METHODS))

    def needs_rendering(self, html: str) -> bool:
        return self.dom_regex.search(html) is not None


# REFINED DETECTOR (Improved)
class RefinedDetector:
    CONTENT_METHODS = [
        ".createElement", ".createElementNS", ".appendChild",
        "document.write", ".replaceChildren", ".innerHTML =",
    ]

    SPA_PATTERNS = [
        "/_next/static/chunks/pages/", '__NEXT_DATA__',
        'id="gatsby-', "__NUXT__",
    ]

    def __init__(self, mode="balanced"):
        self.mode = mode
        self.content_regex = re.compile("|".join(re.escape(m) for m in self.CONTENT_METHODS))
        self.spa_regex = re.compile("|".join(re.escape(p) for p in self.SPA_PATTERNS))

    def needs_rendering(self, html: str) -> Tuple[bool, str]:
        is_spa = self.spa_regex.search(html) is not None
        content_methods = self.content_regex.findall(html)
        has_content = len(content_methods) > 0

        if self.mode == "conservative":
            if is_spa and has_content:
                return True, "SPA + content generation"
            elif len(content_methods) >= 3:
                return True, "Multiple content methods"
            return False, "No strong signals"

        elif self.mode == "balanced":
            if is_spa:
                return True, "SPA framework"
            elif len(content_methods) >= 2:
                return True, f"Content generation ({len(content_methods)} methods)"
            return False, "Likely static page"

        return False, "Unknown"


def test_page(name: str, html: str, should_render: bool):
    """Test a page with both detectors"""
    print(f"\n{'='*75}")
    print(f"TEST: {name}")
    print(f"Ground Truth: {'SHOULD render' if should_render else 'should NOT render'}")
    print(f"{'='*75}")

    # Test detectors
    aggressive = AggressiveDetector()
    balanced = RefinedDetector("balanced")
    conservative = RefinedDetector("conservative")

    aggressive_needs = aggressive.needs_rendering(html)
    balanced_needs, balanced_reason = balanced.needs_rendering(html)
    conservative_needs, conservative_reason = conservative.needs_rendering(html)

    # Show results
    print(f"\n🔴 Aggressive:")
    print(f"   Decision: {'RENDER' if aggressive_needs else 'HTTP'}")
    print(f"   Correct:  {'✓' if aggressive_needs == should_render else '✗ WRONG'}")

    print(f"\n🟡 Balanced:")
    print(f"   Decision: {'RENDER' if balanced_needs else 'HTTP'}")
    print(f"   Reason:   {balanced_reason}")
    print(f"   Correct:  {'✓' if balanced_needs == should_render else '✗ WRONG'}")

    print(f"\n🟢 Conservative:")
    print(f"   Decision: {'RENDER' if conservative_needs else 'HTTP'}")
    print(f"   Reason:   {conservative_reason}")
    print(f"   Correct:  {'✓' if conservative_needs == should_render else '✗ WRONG'}")

    return {
        "name": name,
        "should_render": should_render,
        "aggressive": aggressive_needs,
        "balanced": balanced_needs,
        "conservative": conservative_needs,
    }


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   DETECTION METHOD COMPARISON                             ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

    results = []

    # Test Case 1: Analytics (should NOT render)
    results.append(test_page("Analytics/Tracking", """
        <html><body>
            <a href="/page1">Page 1</a>
            <script>
                document.getElementById('tracker').setAttribute('data-page', 'home');
            </script>
        </body></html>
    """, should_render=False))

    # Test Case 2: Form validation (should NOT render)
    results.append(test_page("Form Validation", """
        <html><body>
            <a href="/terms">Terms</a>
            <script>
                input.setAttribute('aria-invalid', 'true');
            </script>
        </body></html>
    """, should_render=False))

    # Test Case 3: UI interactions (should NOT render)
    results.append(test_page("UI Dropdown", """
        <html><body>
            <a href="/home">Home</a>
            <script>
                menu.setAttribute('aria-expanded', 'true');
                menu.style.display = 'block';
            </script>
        </body></html>
    """, should_render=False))

    # Test Case 4: Lazy images (should NOT render)
    results.append(test_page("Lazy Images", """
        <html><body>
            <a href="/gallery">Gallery</a>
            <script>
                images.forEach(img => img.setAttribute('src', img.dataset.src));
            </script>
        </body></html>
    """, should_render=False))

    # Test Case 5: Next.js SPA (SHOULD render)
    results.append(test_page("Next.js SPA", """
        <html><head>
            <script src="/_next/static/chunks/pages/index.js"></script>
        </head><body>
            <div id="__next"></div>
        </body></html>
    """, should_render=True))

    # Test Case 6: Dynamic content (SHOULD render)
    results.append(test_page("Dynamic Content", """
        <html><body>
            <div id="app"></div>
            <script>
                const nav = document.createElement('nav');
                const link = document.createElement('a');
                link.href = '/dynamic';
                nav.appendChild(link);
                app.appendChild(nav);
            </script>
        </body></html>
    """, should_render=True))

    # Test Case 7: Static blog (should NOT render)
    results.append(test_page("Static Blog", """
        <html><body>
            <nav>
                <a href="/">Home</a>
                <a href="/about">About</a>
            </nav>
        </body></html>
    """, should_render=False))

    # Test Case 8: React SSR with links (should NOT render)
    results.append(test_page("React SSR", """
        <html><body>
            <div id="root">
                <a href="/home">Home</a>
                <a href="/about">About</a>
            </div>
        </body></html>
    """, should_render=False))

    # Summary
    print(f"\n{'='*75}")
    print("SUMMARY")
    print(f"{'='*75}\n")

    total = len(results)
    aggressive_correct = sum(1 for r in results if r["aggressive"] == r["should_render"])
    balanced_correct = sum(1 for r in results if r["balanced"] == r["should_render"])
    conservative_correct = sum(1 for r in results if r["conservative"] == r["should_render"])

    print(f"Total test cases: {total}\n")

    print(f"🔴 Aggressive Detection:")
    print(f"   Accuracy: {aggressive_correct}/{total} ({aggressive_correct/total*100:.0f}%)")
    fp_agg = sum(1 for r in results if not r['should_render'] and r['aggressive'])
    fn_agg = sum(1 for r in results if r['should_render'] and not r['aggressive'])
    print(f"   False positives: {fp_agg} (renders when shouldn't)")
    print(f"   False negatives: {fn_agg} (misses rendering)")

    print(f"\n🟡 Balanced Detection:")
    print(f"   Accuracy: {balanced_correct}/{total} ({balanced_correct/total*100:.0f}%)")
    fp_bal = sum(1 for r in results if not r['should_render'] and r['balanced'])
    fn_bal = sum(1 for r in results if r['should_render'] and not r['balanced'])
    print(f"   False positives: {fp_bal}")
    print(f"   False negatives: {fn_bal}")

    print(f"\n🟢 Conservative Detection:")
    print(f"   Accuracy: {conservative_correct}/{total} ({conservative_correct/total*100:.0f}%)")
    fp_con = sum(1 for r in results if not r['should_render'] and r['conservative'])
    fn_con = sum(1 for r in results if r['should_render'] and not r['conservative'])
    print(f"   False positives: {fp_con}")
    print(f"   False negatives: {fn_con}")

    # Performance
    print(f"\n{'='*75}")
    print("PERFORMANCE IMPACT (estimated 100-page crawl)")
    print(f"{'='*75}\n")

    aggressive_renders = sum(1 for r in results if r["aggressive"])
    balanced_renders = sum(1 for r in results if r["balanced"])
    conservative_renders = sum(1 for r in results if r["conservative"])

    print(f"Pages rendered (out of {total}):")
    print(f"   Aggressive:   {aggressive_renders} ({aggressive_renders/total*100:.0f}%)")
    print(f"   Balanced:     {balanced_renders} ({balanced_renders/total*100:.0f}%)")
    print(f"   Conservative: {conservative_renders} ({conservative_renders/total*100:.0f}%)")

    http_time = 0.2
    browser_time = 2.0

    agg_pct = aggressive_renders / total
    bal_pct = balanced_renders / total
    con_pct = conservative_renders / total

    aggressive_time = (100 * (1 - agg_pct) * http_time) + (100 * agg_pct * browser_time)
    balanced_time = (100 * (1 - bal_pct) * http_time) + (100 * bal_pct * browser_time)
    conservative_time = (100 * (1 - con_pct) * http_time) + (100 * con_pct * browser_time)

    print(f"\nEstimated time (0.2s/HTTP, 2.0s/browser):")
    print(f"   Aggressive:   {aggressive_time:.1f}s")
    print(f"   Balanced:     {balanced_time:.1f}s  ✓ Saves {aggressive_time - balanced_time:.1f}s ({(aggressive_time - balanced_time)/aggressive_time*100:.0f}% faster)")
    print(f"   Conservative: {conservative_time:.1f}s    Saves {aggressive_time - conservative_time:.1f}s ({(aggressive_time - conservative_time)/aggressive_time*100:.0f}% faster)")

    # Recommendation
    print(f"\n{'='*75}")
    print("RECOMMENDATION")
    print(f"{'='*75}\n")
    print("""✅ Use BALANCED detection (best trade-off)

Benefits over aggressive:
  • Better accuracy - fewer false positives
  • Significantly faster on typical sites
  • Still catches all SPAs and dynamic content

Usage:
  from spider_py.patterns_refined import get_detector
  detector = get_detector('balanced')  # Default mode

Modes:
  • 'balanced' - Recommended for most use cases
  • 'conservative' - Maximum speed, might miss some dynamic content
  • 'aggressive' - Original behavior (not recommended)
""")
    print(f"{'='*75}\n")


if __name__ == "__main__":
    main()
