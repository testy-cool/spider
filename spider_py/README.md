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

## File Structure

```
spider_py/
├── __init__.py              # Package exports
├── smart_crawler.py         # Main SmartCrawler class
├── page.py                  # Page handling & smart links
├── browser.py               # Lazy browser controller
├── patterns.py              # JS detection patterns
├── configuration.py         # Configuration dataclass
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── examples/
    └── smart.py            # Example usage
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
