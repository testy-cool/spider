# Quick Start Guide

Get started with Spider Smart Crawl in 5 minutes!

## Installation

### Option 1: Using pip (recommended)

```bash
cd spider_py
pip install -r requirements.txt
playwright install chromium
```

### Option 2: Using setup.py

```bash
cd spider_py
pip install -e .
playwright install chromium
```

## Verify Installation

Run the pattern test (no dependencies needed):

```bash
python examples/test_patterns.py
```

You should see:
```
ALL PATTERN TESTS PASSED ✓
```

## Your First Smart Crawl

Create a file `my_crawler.py`:

```python
import asyncio
from spider_py import SmartCrawler, Configuration

async def main():
    # Create crawler with default settings
    crawler = SmartCrawler("https://example.com")

    # Run smart crawl
    pages = await crawler.crawl_smart()

    # Show results
    print(f"\nCrawled {len(pages)} pages")
    for page in pages:
        print(f"  {page.get_url()}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python my_crawler.py
```

## Run the Example

The included example crawls https://choosealicense.com:

```bash
python examples/smart.py
```

Expected output:
```
[SmartCrawler] Starting crawl from: https://choosealicense.com
[SmartCrawler] Max depth: 2
[SmartCrawler] Max concurrent: 5

[Crawl] [0] https://choosealicense.com/
  → Found 15 links [HTTP]
[Crawl] [1] https://choosealicense.com/licenses/
  → Found 42 links [HTTP]
[Smart] JS detected on https://example.com/app, rendering with browser...
[Browser] Initialized (headless=True)
[Crawl] [1] https://example.com/app
  → Found 23 links [Browser]
...

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

## Configuration Examples

### Shallow crawl (fast)

```python
config = Configuration(
    max_depth=1,           # Only crawl start page + 1 level
    max_pages=10,          # Limit to 10 pages
    max_concurrent_requests=3,
)

crawler = SmartCrawler("https://example.com", config)
```

### Deep crawl (thorough)

```python
config = Configuration(
    max_depth=5,           # Crawl deeper
    max_pages=None,        # No limit
    max_concurrent_requests=10,  # More concurrent
    request_timeout=30,    # Longer timeout
)

crawler = SmartCrawler("https://example.com", config)
```

### With screenshots

```python
config = Configuration(
    screenshot=True,       # Capture screenshots
    wait_for="networkidle", # Wait for network idle
)

crawler = SmartCrawler("https://example.com", config)
```

## Understanding the Output

### HTTP vs Browser

- `[HTTP]` - Page crawled using fast HTTP (no browser needed)
- `[Browser]` - Page required browser rendering (JavaScript detected)

### Smart Detection Messages

- `[Smart] JS detected on <url>, rendering with browser...`
  - JavaScript was found, using browser
- `[Browser] Initialized (headless=True)`
  - Browser started (only happens once, when first needed)

## Performance Tips

1. **Start small** - Use `max_depth=1-2` for testing
2. **Limit pages** - Set `max_pages` to avoid long crawls
3. **Adjust concurrency** - Start with 5, increase if needed
4. **Monitor render rate** - High render rate = slow crawl (JS-heavy site)

## Troubleshooting

### "ModuleNotFoundError: No module named 'playwright'"

Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

### "Browser not found"

Install Playwright browsers:
```bash
playwright install chromium
```

### Crawl is slow

- Check render rate in statistics
- If high (>50%), the site is JS-heavy
- Reduce `max_concurrent_requests` to lower memory usage
- Use `max_pages` to limit scope

### Permission errors

Make sure you have permission to crawl the site. Check `robots.txt`.

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore [examples/smart.py](examples/smart.py) for advanced usage
3. Customize `Configuration` for your use case
4. Build your own crawler!

## Help

For issues or questions:
- Check the [README.md](README.md)
- Review the example code in `examples/`
- Test patterns with `examples/test_patterns.py`
