#!/usr/bin/env python3
"""
Spider.cloud Cost Analysis: Aggressive vs Refined Detection

Calculates the real-world cost impact for a commercial crawling service.
"""


def calculate_spider_cloud_costs():
    """Calculate infrastructure costs for spider.cloud"""

    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║              SPIDER.CLOUD COST ANALYSIS                                   ║
║              Aggressive vs Refined Detection                              ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")

    # Assumptions based on typical commercial scraping service
    print("ASSUMPTIONS:")
    print("-" * 75)
    print("  • Commercial scraping service (spider.cloud)")
    print("  • Customers pay per page or per time")
    print("  • Infrastructure costs scale with browser usage")
    print("  • Competitive market - speed = competitive advantage")
    print()

    # Test data from our comparison
    aggressive_render_rate = 0.625  # 62.5% pages rendered
    balanced_render_rate = 0.25     # 25% pages rendered

    # Cost parameters
    http_cost_per_page = 0.0001     # $0.0001 per HTTP request (negligible)
    browser_cost_per_page = 0.005   # $0.005 per browser render (CPU intensive)

    print("COST STRUCTURE:")
    print("-" * 75)
    print(f"  HTTP request:     ${http_cost_per_page:.4f} per page (CPU minimal)")
    print(f"  Browser render:   ${browser_cost_per_page:.4f} per page (CPU + memory)")
    print(f"  Render is {browser_cost_per_page/http_cost_per_page:.0f}x more expensive than HTTP")
    print()

    # Volume scenarios
    scenarios = [
        ("Small customer", 1_000_000, "1M pages/month"),
        ("Medium customer", 10_000_000, "10M pages/month"),
        ("Large customer", 100_000_000, "100M pages/month"),
        ("Enterprise", 1_000_000_000, "1B pages/month"),
    ]

    print("COST COMPARISON BY CUSTOMER SIZE:")
    print("=" * 75)

    total_savings = 0

    for name, monthly_pages, desc in scenarios:
        print(f"\n{name.upper()} ({desc})")
        print("-" * 75)

        # Aggressive costs
        aggressive_http_pages = monthly_pages * (1 - aggressive_render_rate)
        aggressive_browser_pages = monthly_pages * aggressive_render_rate
        aggressive_cost = (aggressive_http_pages * http_cost_per_page +
                          aggressive_browser_pages * browser_cost_per_page)

        # Balanced costs
        balanced_http_pages = monthly_pages * (1 - balanced_render_rate)
        balanced_browser_pages = monthly_pages * balanced_render_rate
        balanced_cost = (balanced_http_pages * http_cost_per_page +
                        balanced_browser_pages * browser_cost_per_page)

        # Savings
        monthly_savings = aggressive_cost - balanced_cost
        annual_savings = monthly_savings * 12
        total_savings += annual_savings

        print(f"  Aggressive Detection:")
        print(f"    - HTTP pages:     {aggressive_http_pages:>15,.0f} × ${http_cost_per_page:.4f} = ${aggressive_http_pages * http_cost_per_page:>10,.2f}")
        print(f"    - Browser pages:  {aggressive_browser_pages:>15,.0f} × ${browser_cost_per_page:.4f} = ${aggressive_browser_pages * browser_cost_per_page:>10,.2f}")
        print(f"    - TOTAL:          ${aggressive_cost:>10,.2f}/month")

        print(f"\n  Balanced Detection:")
        print(f"    - HTTP pages:     {balanced_http_pages:>15,.0f} × ${http_cost_per_page:.4f} = ${balanced_http_pages * http_cost_per_page:>10,.2f}")
        print(f"    - Browser pages:  {balanced_browser_pages:>15,.0f} × ${browser_cost_per_page:.4f} = ${balanced_browser_pages * browser_cost_per_page:>10,.2f}")
        print(f"    - TOTAL:          ${balanced_cost:>10,.2f}/month")

        print(f"\n  💰 SAVINGS:")
        print(f"    - Per month:      ${monthly_savings:>10,.2f} ({(monthly_savings/aggressive_cost*100):.1f}% reduction)")
        print(f"    - Per year:       ${annual_savings:>10,.2f}")

    # Total for all customers
    print(f"\n{'=' * 75}")
    print("TOTAL POTENTIAL SAVINGS (All Customers)")
    print(f"{'=' * 75}")
    print(f"  Annual savings:   ${total_savings:>15,.2f}")
    print()

    # Time savings
    print(f"{'=' * 75}")
    print("TIME SAVINGS (Customer Experience)")
    print(f"{'=' * 75}")

    http_time = 0.2  # seconds
    browser_time = 2.0  # seconds

    for name, monthly_pages, desc in scenarios[:2]:  # Show first 2
        aggressive_time = (monthly_pages * (1 - aggressive_render_rate) * http_time +
                          monthly_pages * aggressive_render_rate * browser_time)
        balanced_time = (monthly_pages * (1 - balanced_render_rate) * http_time +
                        monthly_pages * balanced_render_rate * browser_time)

        time_saved_seconds = aggressive_time - balanced_time
        time_saved_hours = time_saved_seconds / 3600

        print(f"\n{name} ({desc}):")
        print(f"  Aggressive: {aggressive_time/3600:>10,.1f} hours/month")
        print(f"  Balanced:   {balanced_time/3600:>10,.1f} hours/month")
        print(f"  Time saved: {time_saved_hours:>10,.1f} hours/month ({time_saved_seconds/aggressive_time*100:.1f}% faster)")

    # Competitive advantage
    print(f"\n{'=' * 75}")
    print("COMPETITIVE ADVANTAGES")
    print(f"{'=' * 75}")
    print("""
1. COST SAVINGS
   ✓ 60% reduction in infrastructure costs
   ✓ Lower prices for customers (competitive edge)
   ✓ Higher profit margins

2. SPEED IMPROVEMENTS
   ✓ 51% faster crawls on average
   ✓ Better customer experience
   ✓ Can handle more customers with same infrastructure

3. SCALE EFFICIENCY
   ✓ 2.5x fewer browser instances needed
   ✓ Lower memory footprint
   ✓ Better resource utilization

4. CUSTOMER RETENTION
   ✓ Faster results = happier customers
   ✓ Lower costs = more competitive pricing
   ✓ Better accuracy = higher quality results

5. ENVIRONMENTAL IMPACT
   ✓ 60% less CPU usage
   ✓ Lower carbon footprint
   ✓ More sustainable operation
""")

    # Recommendation
    print(f"{'=' * 75}")
    print("BUSINESS RECOMMENDATION")
    print(f"{'=' * 75}")
    print("""
🎯 UPDATE THE RUST IMPLEMENTATION TOO!

Even though Rust is faster, the business case is clear:

Why update Rust spider (not just Python):
  1. Infrastructure costs are REAL money
  2. Aggressive detection wastes 60% of browser capacity
  3. Customers are charged per page/time
  4. Competitors are getting faster
  5. Scale amplifies the problem

Action Items:
  ✓ Port refined detection to Rust spider
  ✓ Make "balanced" the default mode
  ✓ Keep "aggressive" as an opt-in flag for edge cases
  ✓ Document the cost/performance trade-offs
  ✓ A/B test on spider.cloud to validate savings

Expected Impact:
  • 50-60% reduction in browser infrastructure costs
  • 40-50% faster average crawl times
  • Better customer satisfaction scores
  • Improved profit margins
  • Competitive advantage in the market

ROI: Implementing refined detection could save hundreds of thousands
     of dollars annually at scale. This is not just an optimization -
     it's a business necessity for a commercial service.
""")
    print(f"{'=' * 75}\n")


if __name__ == "__main__":
    calculate_spider_cloud_costs()
