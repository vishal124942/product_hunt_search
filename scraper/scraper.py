# scraper/scraper.py

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_PATH = Path("product_links.txt")
TARGET_LINK_COUNT = 1000 # Desired number of product links

async def scrape_product_links():
    links = set()  # Using a set to store unique links

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        print("🌐 Opening Product Hunt 'All Products' page...")
        await page.goto("https://www.producthunt.com/all")
        await page.wait_for_timeout(5000)
        print("🔁 Scrolling to load more products...")
        while len(links) < TARGET_LINK_COUNT:
            # Scroll to the bottom to trigger loading more products
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)  # Wait for new products to load

            # Extract product links
            anchors = await page.locator("a[href^='/posts/']").all()
            for a in anchors:
                href = await a.get_attribute("href")
                if href and href.startswith("/posts/"):
                    full_url = f"https://www.producthunt.com{href.strip()}"
                    links.add(full_url)
                if len(links) >= TARGET_LINK_COUNT:
                    break

        await browser.close()

    # Save the links to a text file
    with open(OUTPUT_PATH, "w") as f:
        f.write("\n".join(links))

    print(f"\n✅ Saved {len(links)} links to {OUTPUT_PATH}")
    return links

if __name__ == "__main__":
    asyncio.run(scrape_product_links())
