"""
JavaScript Detection Patterns

These patterns help identify if a page uses JavaScript for DOM manipulation
and requires browser rendering for proper content extraction.
"""

import re
from typing import Set


class JSDetector:
    """Detects JavaScript usage in HTML content"""

    # DOM manipulation method signatures (from Rust implementation)
    DOM_WATCH_METHODS = [
        ".createElementNS",  # SVG element creation
        ".removeChild",  # DOM removal
        ".insertBefore",  # DOM insertion
        ".createElement",  # Element creation
        ".setAttribute",  # Attribute modification
        ".createTextNode",  # Text node creation
        ".replaceChildren",  # Content replacement
        ".prepend",  # Prepend operations
        ".append",  # Append operations
        ".appendChild",  # Child append
        ".write",  # document.write()
    ]

    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        "nextjs": "/_next/static/chunks/pages/",
        "webpack": "/webpack-runtime-",
        "gatsby": 'id="gatsby-',
        "react": "react-dom",
        "vue": "vue.js",
        "angular": "ng-version",
    }

    # Additional JavaScript indicators
    JS_INDICATORS = [
        "window.addEventListener",
        "document.addEventListener",
        "DOMContentLoaded",
        "__NEXT_DATA__",
        "__NUXT__",
        "ReactDOM.render",
        "Vue.createApp",
    ]

    def __init__(self):
        """Initialize the detector with compiled patterns"""
        # Pre-compile regex patterns for better performance
        self.dom_patterns = [re.escape(method) for method in self.DOM_WATCH_METHODS]
        self.dom_regex = re.compile("|".join(self.dom_patterns))

        self.framework_patterns = {
            name: re.compile(re.escape(pattern))
            for name, pattern in self.FRAMEWORK_PATTERNS.items()
        }

        self.js_indicator_regex = re.compile(
            "|".join(re.escape(indicator) for indicator in self.JS_INDICATORS)
        )

    def detect_dom_manipulation(self, html: str) -> bool:
        """
        Check if HTML contains DOM manipulation JavaScript methods

        Args:
            html: HTML content to analyze

        Returns:
            True if DOM manipulation patterns are found
        """
        return self.dom_regex.search(html) is not None

    def detect_frameworks(self, html: str) -> Set[str]:
        """
        Detect JavaScript frameworks used in the page

        Args:
            html: HTML content to analyze

        Returns:
            Set of detected framework names
        """
        detected = set()
        for name, pattern in self.framework_patterns.items():
            if pattern.search(html):
                detected.add(name)
        return detected

    def detect_js_indicators(self, html: str) -> bool:
        """
        Check for general JavaScript indicators

        Args:
            html: HTML content to analyze

        Returns:
            True if JavaScript indicators are found
        """
        return self.js_indicator_regex.search(html) is not None

    def needs_rendering(self, html: str, script_sources: list = None) -> bool:
        """
        Determine if a page needs browser rendering based on JavaScript detection

        Args:
            html: HTML content to analyze
            script_sources: List of script source URLs from the page

        Returns:
            True if browser rendering is recommended
        """
        # Check for DOM manipulation
        if self.detect_dom_manipulation(html):
            return True

        # Check for frameworks
        frameworks = self.detect_frameworks(html)
        if frameworks:
            # Some frameworks like Next.js, Gatsby always need rendering
            if frameworks & {"nextjs", "gatsby", "webpack"}:
                return True

        # Check for general JS indicators
        if self.detect_js_indicators(html):
            return True

        # Check script sources if provided
        if script_sources:
            for src in script_sources:
                # Check for framework-specific script patterns
                if any(pattern in src for pattern in self.FRAMEWORK_PATTERNS.values()):
                    return True

        return False


# Global singleton instance for performance
_detector = None


def get_detector() -> JSDetector:
    """Get the global JSDetector instance"""
    global _detector
    if _detector is None:
        _detector = JSDetector()
    return _detector
