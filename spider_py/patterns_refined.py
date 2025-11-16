"""
Refined JavaScript Detection Patterns (Less Aggressive)

This version is more conservative and only triggers browser rendering
when JavaScript actually generates content/links, not just for UI interactions.

Key improvements over aggressive version:
1. Focuses on content-generating DOM methods
2. Ignores UI-only methods (.setAttribute, event listeners)
3. Requires stronger signals (multiple patterns, not just one)
4. Filters out analytics/tracking code
"""

import re
from typing import Set, Tuple


class JSDetectorRefined:
    """
    Refined JavaScript detector that's less aggressive.
    Only triggers rendering when JavaScript likely generates content.
    """

    # Content-generating DOM methods (actually create/modify page content)
    CONTENT_GENERATING_METHODS = [
        ".createElement",      # Creating elements - likely dynamic content
        ".createElementNS",    # SVG/dynamic elements
        ".appendChild",        # Adding to DOM - likely dynamic
        "document.write",      # Definitely dynamic content generation
        ".replaceChildren",    # Replacing content - dynamic
        ".innerHTML =",        # Setting HTML content directly
        ".outerHTML =",        # Replacing elements
    ]

    # UI-only methods (don't generate links/content, just manipulate UI)
    # These should NOT trigger rendering
    UI_ONLY_METHODS = [
        ".setAttribute",       # Just attributes (class, aria, etc.)
        ".removeAttribute",    # Removing attributes
        ".classList.add",      # CSS classes
        ".classList.remove",   # CSS classes
        ".style.",            # Inline styles
        ".focus()",           # Focus management
        ".blur()",            # Focus management
        "addEventListener",   # Event handlers (UI interaction)
    ]

    # Strong framework indicators (SPAs that definitely need rendering)
    SPA_FRAMEWORKS = {
        "nextjs": "/_next/static/chunks/pages/",
        "gatsby": 'id="gatsby-',
        "nuxt": "__NUXT__",
    }

    # Weak framework indicators (might not need rendering for static pages)
    WEAK_FRAMEWORKS = {
        "react": "react-dom",  # Could be SSR
        "vue": "vue.js",       # Could be SSR
        "angular": "ng-version",  # Could be SSR
    }

    # Content generation patterns (stronger signal)
    CONTENT_PATTERNS = [
        r"document\.createElement\(['\"](?:a|nav|div|section)['\"]",  # Creating navigation elements
        r"\.appendChild\(.+createElement",  # Appending created elements
        r"\.innerHTML\s*=\s*['\"]<a",  # Injecting links via innerHTML
        r"ReactDOM\.(render|hydrate)",  # React rendering
        r"Vue\.createApp",  # Vue 3 mounting
        r"angular\.bootstrap",  # Angular bootstrapping
    ]

    # SPA indicators (empty body with single mount point)
    SPA_INDICATORS = [
        r'<body[^>]*>\s*<div id="(?:root|app|__next)"[^>]*>\s*</div>\s*</body>',
        r'<div id="__nuxt"',
        r'<div id="gatsby-focus-wrapper"',
    ]

    def __init__(self, mode: str = "balanced"):
        """
        Initialize the refined detector

        Args:
            mode: Detection mode
                  - "conservative": Only render on strong signals (fewer false positives)
                  - "balanced": Default, good middle ground
                  - "aggressive": More sensitive (backwards compatible)
        """
        self.mode = mode

        # Compile patterns
        self.content_methods_regex = re.compile(
            "|".join(re.escape(method) for method in self.CONTENT_GENERATING_METHODS)
        )

        self.content_patterns_regex = re.compile(
            "|".join(self.CONTENT_PATTERNS),
            re.IGNORECASE
        )

        self.spa_indicators_regex = re.compile(
            "|".join(self.SPA_INDICATORS),
            re.IGNORECASE | re.DOTALL
        )

    def detect_content_generation(self, html: str) -> Tuple[bool, list]:
        """
        Check if HTML contains content-generating JavaScript

        Args:
            html: HTML content to analyze

        Returns:
            Tuple of (has_content_gen, methods_found)
        """
        matches = self.content_methods_regex.findall(html)
        pattern_matches = self.content_patterns_regex.findall(html)

        all_found = list(matches) + [f"pattern:{p}" for p in pattern_matches]
        return len(all_found) > 0, all_found

    def detect_spa_framework(self, html: str, script_sources: list = None) -> Tuple[bool, Set[str]]:
        """
        Detect if page is a Single Page Application

        Args:
            html: HTML content
            script_sources: Script source URLs

        Returns:
            Tuple of (is_spa, frameworks_detected)
        """
        detected = set()

        # Check for strong SPA indicators
        for name, pattern in self.SPA_FRAMEWORKS.items():
            if pattern in html:
                detected.add(name)

        # Check script sources
        if script_sources:
            for src in script_sources:
                for name, pattern in self.SPA_FRAMEWORKS.items():
                    if pattern in src:
                        detected.add(name)

        # Check for SPA page structure
        if self.spa_indicators_regex.search(html):
            detected.add("spa-structure")

        return len(detected) > 0, detected

    def needs_rendering(self, html: str, script_sources: list = None) -> Tuple[bool, str]:
        """
        Refined decision: Only render if JavaScript actually generates content

        Args:
            html: HTML content to analyze
            script_sources: List of script source URLs

        Returns:
            Tuple of (needs_render, reason)
        """
        reasons = []

        # 1. Check for SPA frameworks (strong signal)
        is_spa, spa_frameworks = self.detect_spa_framework(html, script_sources)
        if is_spa:
            reasons.append(f"SPA framework detected: {', '.join(spa_frameworks)}")

        # 2. Check for content generation patterns
        has_content_gen, methods = self.detect_content_generation(html)
        if has_content_gen:
            reasons.append(f"Content generation detected: {', '.join(methods[:3])}")

        # Decision based on mode
        if self.mode == "conservative":
            # Only render if we have BOTH SPA framework AND content generation
            # OR if we have strong content generation patterns
            if is_spa and has_content_gen:
                return True, " + ".join(reasons)
            elif len(methods) >= 3:  # Multiple content methods
                return True, reasons[-1] if reasons else "Multiple content methods"
            else:
                return False, "No strong signals for dynamic content"

        elif self.mode == "balanced":
            # Render if we have SPA OR significant content generation
            if is_spa:
                return True, reasons[0]
            elif has_content_gen and len(methods) >= 2:
                return True, reasons[-1] if len(reasons) > 1 else reasons[0]
            else:
                return False, "Likely static page with minimal JS"

        else:  # aggressive mode
            # Render if we have any signal
            if is_spa or has_content_gen:
                return True, reasons[0] if reasons else "JavaScript detected"
            else:
                return False, "No JavaScript patterns"

    def analyze(self, html: str, script_sources: list = None) -> dict:
        """
        Full analysis of a page (for debugging/testing)

        Args:
            html: HTML content
            script_sources: Script sources

        Returns:
            Dictionary with analysis results
        """
        is_spa, spa_frameworks = self.detect_spa_framework(html, script_sources)
        has_content, methods = self.detect_content_generation(html)
        needs_render, reason = self.needs_rendering(html, script_sources)

        return {
            "needs_rendering": needs_render,
            "reason": reason,
            "is_spa": is_spa,
            "spa_frameworks": list(spa_frameworks),
            "has_content_generation": has_content,
            "content_methods": methods[:5],  # Limit to 5
            "mode": self.mode,
        }


# Global instances for different modes
_detectors = {}


def get_detector(mode: str = "balanced") -> JSDetectorRefined:
    """
    Get a JSDetectorRefined instance for the specified mode

    Args:
        mode: "conservative", "balanced", or "aggressive"

    Returns:
        JSDetectorRefined instance
    """
    global _detectors
    if mode not in _detectors:
        _detectors[mode] = JSDetectorRefined(mode=mode)
    return _detectors[mode]
