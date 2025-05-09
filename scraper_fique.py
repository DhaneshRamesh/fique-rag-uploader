# 📝 Trigger commit: Added trivial comment for GitHub Actions testing

from playwright.sync_api import sync_playwright
import json
from urllib.parse import urljoin
import os

BASE_URL = "https://www.fique.co.uk"
BLOG_LIST_URL = f"{BASE_URL}/blogs/news"
OUTPUT_FILE = "fique_articles.jsonl"
all_articles = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Step 1: Collect all blog article links
    page.goto(BLOG_LIST_URL, wait_until="load")
    links = page.query_selector_all("a")
    article_links = set()

    for link in links:
        href = link.get_attribute("href")
        if href and href.startswith("/blogs/news/") and len(href) > len("/blogs/news/"):
            article_links.add(urljoin(BASE_URL, href))

    print(f"🧾 Found {len(article_links)} articles. Scraping...\n")

    # Step 2: Visit each blog post and extract from JSON-LD
    for url in sorted(article_links):
        try:
            page.goto(url, wait_until="load")
            page.wait_for_selector('script[type="application/ld+json"]', timeout=8000, state="attached")
            script_tags = page.query_selector_all('script[type="application/ld+json"]')

            article_json = None
            for tag in script_tags:
                try:
                    content = tag.inner_text()
                    parsed = json.loads(content)
                    if isinstance(parsed, dict) and parsed.get("@type") == "Article":
                        article_json = parsed
                        break
                except json.JSONDecodeError:
                    continue

            if not article_json or "articleBody" not in article_json:
                print(f"⚠️ Skipped (missing articleBody): {url}")
                continue

            article = {
                "title": article_json.get("headline", "Untitled"),
                "url": url,
                "article_content": article_json["articleBody"].strip()  # ✅ fixed key name
            }

            all_articles.append(article)
            print(f"✅ Scraped: {article['title']}")

        except Exception as e:
            print(f"❌ Error scraping {url}: {str(e)}")

    browser.close()

# Step 3: Save to JSONL
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for article in all_articles:
        f.write(json.dumps(article, ensure_ascii=False) + "\n")

print(f"\n🎉 Done! Scraped {len(all_articles)} articles.")
print(f"📁 Saved to: {os.path.abspath(OUTPUT_FILE)}")
