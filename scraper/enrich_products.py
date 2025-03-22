
import json
from pathlib import Path
from urllib.parse import urlparse
import asyncio
from playwright.async_api import async_playwright
LINKS_PATH = Path("product_links.txt")
OUTPUT_PATH = Path("products_data.json")
CONCURRENCY = 20  
async def scrape_product(page, url, i, total):
    print(f"🔍 [{i}/{total}] Scraping: {url}")
    product = {"url": url}
    try:
        slug = urlparse(url).path.split("/")[-1]
        product["name"] = slug.replace("-", " ").title()
    except:
        product["name"] = None

    try:
        await page.goto(url)
        await page.wait_for_timeout(1500)
        try:
            tagline = await page.locator("h1").first.text_content()
            product["tagline"] = tagline.strip()
        except:
            product["tagline"] = None

        # Description (meta tag)
        try:
            desc = await page.locator("meta[name='description']").get_attribute("content")
            product["description"] = desc.strip()
        except:
            product["description"] = None

        # Tags
        try:
            tags = await page.locator("a[href*='/topics/']").all()
            tag_texts = [await t.text_content() for t in tags if await t.text_content()]
            product["tags"] = list(set(t.strip() for t in tag_texts))
        except:
            product["tags"] = []

        # Logo
        try:
            logo = await page.locator("img[alt*='logo']").first.get_attribute("src")
            product["logo_url"] = logo
        except:
            product["logo_url"] = None

        # Upvotes
        try:
            upvote_text = await page.locator("[data-test='vote-button-count']").first.text_content()
            product["upvotes"] = int(upvote_text.replace(",", "")) if upvote_text and upvote_text.strip().isdigit() else None
        except:
            product["upvotes"] = None

        print(f" Done: {product['name']}")
        return product

    except Exception as e:
        print(f" Failed: {url} - {e}")
        return None

async def enrich_from_links():
    if not LINKS_PATH.exists():
        raise FileNotFoundError("product_links.txt not found.")
    with open(LINKS_PATH, "r") as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]

    enriched = []
    total = len(urls)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        sem = asyncio.Semaphore(CONCURRENCY)

        async def bound_scrape(i, url):
            async with sem:
                context = await browser.new_context()
                page = await context.new_page()
                result = await scrape_product(page, url, i, total)
                await context.close()
                return result

        tasks = [bound_scrape(i+1, url) for i, url in enumerate(urls)]
        results = await asyncio.gather(*tasks)
        enriched = [res for res in results if res]
        await browser.close()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2)

    print(f"\n Done! Enriched {len(enriched)} products → saved to {OUTPUT_PATH}")
if __name__ == "__main__":
    asyncio.run(enrich_from_links())
