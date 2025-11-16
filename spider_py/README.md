# Spider Smart Crawl - Python Implementation

A Python implementation of the Spider smart crawl feature - an intelligent hybrid web crawler that combines the speed of HTTP requests with the rendering capabilities of a headless browser.

## Overview

**Smart Crawl** is an adaptive crawling strategy that:
- Uses **fast HTTP requests** by default for static content
- Automatically detects JavaScript usage on each page
- Falls back to **headless Chrome rendering** only when needed
- Achieves ~10x performance improvement on static sites vs full browser rendering

This is a Python port of the Rust spider library's smart crawl feature.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ 1. HTTP Request (Fast)                                      │
│    ├─ Fetch page via aiohttp                                │
│    ├─ Parse HTML with BeautifulSoup                         │
│    └─ Extract links and metadata                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. JavaScript Detection (Smart)                             │
│    ├─ Scan for DOM manipulation patterns                    │
│    ├─ Detect frameworks (Next.js, Gatsby, React, etc.)      │
│    └─ Check for JS indicators                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
           ┌───────────────┬───────────────┐
           ↓               ↓               ↓
      [No JS]         [JS Found]    [Framework]
           │               │               │
           ↓               ↓               ↓
    [Use HTTP]      [Render Browser]  [Render Browser]
    [Done ✓]        [Extract Links]   [Extract Links]
```

## Installation

### 1. Install Python dependencies

```bash
cd spider_py
pip install -r requirements.txt
```

### 2. Install Playwright browsers

```bash
playwright install chromium
```

## Usage

### Basic Example

```python
import asyncio
from spider_py import SmartCrawler, Configuration

async def main():
    # Configure crawler
    config = Configuration(
        max_depth=2,
        max_pages=20,
        max_concurrent_requests=5,
    )

    # Create crawler
    crawler = SmartCrawler(
        start_url="https://choosealicense.com",
        config=config,
    )

    # Execute smart crawl
    pages = await crawler.crawl_smart()

    # Results
    print(f"Crawled {len(pages)} pages")
    for page in pages:
        print(f"  {page.get_url()} - {len(page.get_links())} links")

if __name__ == "__main__":
    asyncio.run(main())
```

### Run Example

```bash
cd spider_py
python examples/smart.py
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_depth` | int | 3 | Maximum crawl depth |
| `max_pages` | int | None | Maximum pages to crawl |
| `max_concurrent_requests` | int | 10 | Concurrent requests limit |
| `request_timeout` | int | 30 | Request timeout (seconds) |
| `chrome_headless` | bool | True | Run browser in headless mode |
| `viewport_width` | int | 1920 | Browser viewport width |
| `viewport_height` | int | 1080 | Browser viewport height |
| `wait_for` | str | "domcontentloaded" | Page load wait condition |
| `screenshot` | bool | False | Capture screenshots |
| `delay_between_requests` | float | 0.0 | Delay between requests |

## JavaScript Detection

The crawler detects JavaScript using multiple strategies:

### 1. DOM Manipulation Patterns
Scans HTML for these method signatures:
- `.createElement`, `.appendChild`, `.removeChild`
- `.insertBefore`, `.setAttribute`, `.createTextNode`
- `.replaceChildren`, `.prepend`, `.append`
- `.write` (document.write)

### 2. Framework Detection
Identifies popular frameworks:
- **Next.js**: `/_next/static/chunks/pages/`
- **Gatsby**: `id="gatsby-"`
- **Webpack**: `/webpack-runtime-`
- **React**: `react-dom`
- **Vue**: `vue.js`
- **Angular**: `ng-version`

### 3. JavaScript Indicators
- Event listeners: `addEventListener`
- Framework globals: `__NEXT_DATA__`, `__NUXT__`
- Rendering calls: `ReactDOM.render`, `Vue.createApp`

## Components

### `SmartCrawler`
Main crawler class with BFS traversal and concurrent processing.

**Key Methods:**
- `crawl_smart()` - Execute smart crawl
- `get_pages()` - Get all crawled pages
- `get_links()` - Get all discovered URLs
- `get_stats()` - Get crawl statistics

### `Page`
Represents a web page with smart link extraction.

**Key Methods:**
- `fetch_http()` - Fetch page via HTTP (static)
- `smart_links()` - Extract links with JS detection
- `extract_metadata()` - Get title and description

### `LazyBrowser`
Lazy browser controller using Playwright.

**Features:**
- **Lazy initialization** - Only starts when needed
- **Thread-safe** - Uses asyncio.Lock
- **Reusable** - Single instance for all pages
- **Context manager** - Automatic cleanup

### `JSDetector`
JavaScript detection engine with pattern matching.

**Methods:**
- `detect_dom_manipulation()` - Check for DOM methods
- `detect_frameworks()` - Identify frameworks
- `needs_rendering()` - Decision function

## Performance Characteristics

| Metric | Smart Crawl | Full Browser Crawl |
|--------|-------------|-------------------|
| Static sites | ~10x faster | Baseline |
| Mixed sites | ~3-5x faster | Baseline |
| JS-heavy sites | Similar | Baseline |
| Memory usage | Lower | Higher |
| CPU usage | Lower | Higher |
| Browser startup | Lazy (when needed) | Always |

## Comparison with Rust Implementation

| Feature | Rust (spider) | Python (spider_py) |
|---------|---------------|-------------------|
| HTTP client | reqwest | aiohttp |
| HTML parser | lol_html (streaming) | BeautifulSoup + lxml |
| Browser | chrome_rs | Playwright |
| Concurrency | tokio | asyncio |
| Lazy browser | OnceCell | asyncio.Lock + flag |
| Pattern matching | Aho-Corasick | regex |
| Performance | ~10-100x faster | Baseline Python |

## Statistics Example

After crawling, the crawler provides detailed statistics:

```
==============================================================
CRAWL STATISTICS
==============================================================
Total pages crawled:    18
Total links discovered: 156
HTTP requests:          18
Browser renders:        3
Render rate:            16.7%
Browser initialized:    YES
==============================================================
```

This shows that only 16.7% of pages required browser rendering - the rest used the fast HTTP path!

## Testing & Validation

The implementation includes multiple testing utilities to help you understand and validate the smart crawl behavior:

### 1. Detection Demo (No Dependencies)

**File**: `examples/test_detection_demo.py`

Quick demonstration of JavaScript detection using example HTML snippets. Requires NO dependencies - runs with Python standard library only.

```bash
python examples/test_detection_demo.py
```

**What it shows**:
- How different HTML patterns are detected
- Static vs dynamic page classification
- Framework detection (Next.js, React, etc.)
- Performance comparison estimates

**Perfect for**: Understanding how the detection logic works without installing anything.

### 2. Detection on Real Pages (HTTP Only)

**File**: `examples/test_detection_only.py`

Test JavaScript detection on real URLs using HTTP only (no browser). Requires: `pip install aiohttp beautifulsoup4 lxml`

```bash
# Single page
python examples/test_detection_only.py https://example.com

# Interactive mode
python examples/test_detection_only.py
```

**What it shows**:
- Real-time fetching and analysis
- Actual script sources found
- DOM patterns in live pages
- Smart crawl decision (HTTP vs Browser)

**Perfect for**: Testing if specific sites need browser rendering before running a full crawl.

### 3. Full Single Page Test (With Browser)

**File**: `examples/test_single_page.py`

Complete single-page test including browser rendering comparison. Requires full installation.

```bash
# Test with smart decision
python examples/test_single_page.py https://example.com

# Force browser rendering for comparison
python examples/test_single_page.py https://example.com --force

# Interactive mode
python examples/test_single_page.py
```

**What it shows**:
- HTTP vs Browser link extraction comparison
- What new links are discovered by rendering
- Performance impact of browser usage
- Complete metadata extraction

**Perfect for**: Validating crawl behavior on specific pages before running full crawls.

### 4. Pattern Tests

**File**: `examples/test_patterns.py`

Basic pattern matching validation (no network required).

```bash
python examples/test_patterns.py
```

**Output**:
```
============================================================
PATTERN DETECTION TESTS (No Dependencies)
============================================================

Testing DOM manipulation detection...
  ✓ DOM pattern detection works
Testing framework detection...
  ✓ Framework patterns work

============================================================
ALL PATTERN TESTS PASSED ✓
============================================================
```

### Testing Workflow

**Recommended testing approach:**

1. **Start with demo** (`test_detection_demo.py`) - No installation needed
2. **Test detection on real sites** (`test_detection_only.py`) - Minimal deps
3. **Validate with browser** (`test_single_page.py`) - Full comparison
4. **Run full crawl** (`smart.py`) - Production usage

**Example Testing Session:**

```bash
# 1. Understand the detection logic
python examples/test_detection_demo.py

# 2. Test your target site
python examples/test_detection_only.py https://mysite.com

# 3. If it detects JS, verify with browser comparison
pip install -r requirements.txt
playwright install chromium
python examples/test_single_page.py https://mysite.com --force

# 4. Run actual crawl
python examples/smart.py
```

## File Structure

```
spider_py/
├── __init__.py              # Package exports
├── smart_crawler.py         # Main SmartCrawler class (378 lines)
├── page.py                  # Page handling & smart links (198 lines)
├── browser.py               # Lazy browser controller (156 lines)
├── patterns.py              # JS detection patterns (158 lines)
├── configuration.py         # Configuration dataclass (46 lines)
├── requirements.txt         # Python dependencies
├── setup.py                 # Package installation
├── .gitignore              # Python gitignore
├── README.md               # This file
├── QUICK_START.md          # 5-minute guide
└── examples/
    ├── smart.py                  # Full crawl example
    ├── test_single_page.py       # Single page test (with browser)
    ├── test_detection_only.py    # Detection test (HTTP only)
    ├── test_detection_demo.py    # Demo (no dependencies)
    ├── test_patterns.py          # Pattern validation
    └── test_simple.py            # Simple integration test
```

## Requirements

- Python 3.8+
- aiohttp (async HTTP client)
- BeautifulSoup4 + lxml (HTML parsing)
- Playwright (headless browser)

## License

Same as parent project (MIT License)

## Credits

Python port of the [spider](https://github.com/spider-rs/spider) Rust library's smart crawl feature.

Original Rust implementation by the Spider-RS team.
